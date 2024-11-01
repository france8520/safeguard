from utils import (get_complete_path, read_wordList)
import requests
from PIL import Image, ImageFilter
from io import BytesIO
from trie import Trie
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import time
from datetime import datetime
import hashlib
from PIL import Image
import logging

def get_image_profanity_score(image_url):
    r = requests.post(
        "https://api.deepai.org/api/nsfw-detector",
        data={
            'image': image_url,
        },
        headers={'api-key': 'e0a51dac-16ce-46d9-a235-d7972bfadb65'}
    )
    # if nsfw_score is more than 0.7 it is definitely profane
    return r.json()['output']['nsfw-score']


def get_image_analysis(url):
    r = requests.post(
        "https://api.deepai.org/api/nsfw-detector",
        data={
            'image': url,
        },
        headers={'api-key': 'e0a51dac-16ce-46d9-a235-d7972bfadb65'}
    )
    return r.json()['output']


def censor_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Applying GaussianBlur filter
    gaussImage = img.filter(ImageFilter.GaussianBlur(100))
    # gaussImage.show()

    # Save Gaussian Blur Image
    image_name = hash(image_url)
    gaussImage.save('images/'+str(image_name)+'.jpg')

class ImageProcessor:
    def __init__(self):
        self.temp_dir = "images/temp"
        self.permanent_dir = "images"
        self.ensure_directories()
        self.setup_logging()

    def ensure_directories(self):
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.permanent_dir, exist_ok=True)

    def setup_logging(self):
        logging.basicConfig(
            filename=os.path.join(self.temp_dir, 'processing_log.txt'),
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def generate_temp_filename(self, url, step):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
        return f"{timestamp}_{step}_{url_hash}.jpg"

    def cleanup_old_files(self, max_age=86400):  # 24 hours in seconds
        current_time = time.time()
        for filename in os.listdir(self.temp_dir):
            if filename == 'processing_log.txt' or filename == 'README.md':
                continue
            filepath = os.path.join(self.temp_dir, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age:
                    os.remove(filepath)
                    logging.info(f"Removed old temporary file: {filename}")

    async def process_image(self, image_url):
        logging.info(f"Starting processing for image: {image_url}")
        
        # Generate hash for tracking
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:6]
        logging.info(f"Hash generated: {url_hash}")

        # Download image
        temp_download = self.generate_temp_filename(image_url, "download")
        download_path = os.path.join(self.temp_dir, temp_download)
        
        try:
            # Download logic here...
            logging.info(f"Download completed: {os.path.getsize(download_path)/1024:.0f}KB")

            # Analysis
            temp_analysis = self.generate_temp_filename(image_url, "analyzing")
            analysis_path = os.path.join(self.temp_dir, temp_analysis)
            os.rename(download_path, analysis_path)
            
            logging.info("Running AI analysis...")
            score = get_image_profanity_score(image_url)
            logging.info(f"Analysis complete - Score: {score}")

            if score > 0.7:
                # Blur processing
                temp_blur = self.generate_temp_filename(image_url, "blurring")
                blur_path = os.path.join(self.temp_dir, temp_blur)
                
                img = Image.open(analysis_path)
                blurred = img.filter(ImageFilter.GaussianBlur(100))
                blurred.save(blur_path)
                logging.info("Blur complete - Gaussian radius: 100")

                # Move to permanent storage
                final_path = os.path.join(self.permanent_dir, f"{url_hash}.jpg")
                os.rename(blur_path, final_path)
                logging.info(f"Moving to permanent storage: {final_path}")

            self.cleanup_temp_files(url_hash)
            
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            self.cleanup_temp_files(url_hash)
            raise

    def cleanup_temp_files(self, url_hash):
        logging.info("Cleanup started")
        count = 0
        for filename in os.listdir(self.temp_dir):
            if url_hash in filename:
                os.remove(os.path.join(self.temp_dir, filename))
                count += 1
        logging.info(f"Cleanup complete - removed {count} temporary files")
class ProfanityFilter:
    def __init__(self):
        self.CHARS_MAPPING = {
            "a": ("a", "@", "*", "4"),
            "i": ("i", "*", "l", "1"),
            "o": ("o", "*", "0", "@"),
            "u": ("u", "*", "v"),
            "v": ("v", "*", "u"),
            "l": ("l", "1"),
            "e": ("e", "*", "3"),
            "s": ("s", "$", "5"),
            "t": ("t", "7")
        }
        self.censor_urls = set()
        self.profane_trie = Trie()
        self.default_wordlist_filename = get_complete_path('data/profanity_wordlist.txt')
        self.default_urls_filename = get_complete_path('data/profane_sites.txt')

        self.load_profane_words(profane_words=None, whitelist_words=None)
        self.load_profane_urls()

    def load_profane_words(self, profane_words, whitelist_words):
        self.profane_trie = Trie()
        if profane_words is None:
            profane_words = read_wordList(self.default_wordlist_filename)
        self.generate_possible_profane_words(profane_words, whitelist_words)

    def generate_possible_profane_words(self, profane_words, whitelist_words):
        for profane_word in profane_words:
            self.dfs(profane_word, 0, [], whitelist_words)

    def dfs(self, profane_word, idx, char_list, whitelist_words):
        if idx == len(profane_word):
            possible_profane_word = ''
            for char in char_list:
                possible_profane_word += char
            if whitelist_words is None or possible_profane_word not in whitelist_words:
                self.profane_trie.insert(possible_profane_word)
            return

        if profane_word[idx] not in self.CHARS_MAPPING:
            char_list.append(profane_word[idx])
            self.dfs(profane_word, idx + 1, char_list, whitelist_words)
            char_list.pop(len(char_list) - 1)

        else:
            for char in self.CHARS_MAPPING[profane_word[idx]]:
                char_list.append(char)
                self.dfs(profane_word, idx + 1, char_list, whitelist_words)
                char_list.pop(len(char_list) - 1)

    def load_profane_urls(self):
        profane_urls = read_wordList(self.default_urls_filename)
        for url in profane_urls:
            self.censor_urls.add(url)

    def censor_url(self, url):
        if self.censor_urls.__contains__(url):
            return '*'*len(url)
        return url

    def censor(self, text, censor_char="*"):

        if type(text) != str:
            text = str(text)
        if type(censor_char) != str:
            censor_char = str(censor_char)

        if self.profane_trie.root is None:
            self.load_profane_words()

        return self.censor_profane_words(text, censor_char)

    def censor_profane_words(self, message, censor_char):
        message = message.split()
        clean_message = ''
        for word in message:
            curr_word = ''
            if self.profane_trie.hasPrefix(word.lower()):
                for i in range(len(word)):
                    curr_word += censor_char
            else:
                curr_word = word
            clean_message += curr_word + ' '
        return clean_message

    def isProfane(self, word):
        if self.profane_trie.hasPrefix(word):
            return True
        return False

    def add_profane_words(self, words):
        for word in words:
            self.profane_trie.insert(word)

    def add_whitelist_words(self, words):
        for word in words:
            self.whiteList_trie.insert(word)

class WebPageProfanityFilter(ProfanityFilter):
    def __init__(self):
        super().__init__()
        
    def filter_webpage(self, url):
        try:
            # Fetch webpage content
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Filter text content
            for text_element in soup.find_all(text=True):
                if text_element.parent.name not in ['script', 'style']:
                    cleaned_text = self.censor(text_element.string)
                    text_element.replace_with(cleaned_text)
            
            # Filter image alt texts
            for img in soup.find_all('img'):
                if img.get('alt'):
                    img['alt'] = self.censor(img['alt'])
            
            # Check and filter links
            for link in soup.find_all('a'):
                if link.get('href'):
                    full_url = urljoin(url, link['href'])
                    link['href'] = self.censor_url(full_url)
            
            return str(soup)
        except Exception as e:
            print(f"An error occurred while filtering the webpage: {e}")
            return None            
    def save_filtered_webpage(self, url, output_path):
        filtered_content = self.filter_webpage(url)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(filtered_content)
