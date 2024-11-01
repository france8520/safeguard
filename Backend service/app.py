from flask import Flask, request, jsonify
from flask_cors import CORS
from profanity_filter import ProfanityFilter, get_image_profanity_score, censor_image
import base64

app = Flask(__name__)
CORS(app)

# Initialize the profanity filter
profanity_filter = ProfanityFilter()

@app.route('/api/filter-text', methods=['POST'])
def filter_text():
    data = request.json
    text = data.get('text', '')
    filtered_text = profanity_filter.censor(text)
    return jsonify({'filtered_text': filtered_text})

@app.route('/api/check-image', methods=['POST'])
def check_image():
    data = request.json
    image_url = data.get('image_url', '')
    try:
        score = get_image_profanity_score(image_url)
        if score > 0.7:  # Threshold from your original code
            censored_url = censor_image(image_url)
            return jsonify({
                'is_profane': True,
                'score': score,
                'censored_url': censored_url
            })
        return jsonify({
            'is_profane': False,
            'score': score
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
