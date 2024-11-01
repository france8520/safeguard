const API_BASE_URL = 'http://localhost:5000/api';

async function filterText(text) {
  try {
    const response = await fetch(`${API_BASE_URL}/filter-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text })
    });
    const data = await response.json();
    return data.filtered_text;
  } catch (error) {
    console.error('Error filtering text:', error);
    return text;
  }
}

async function checkImage(imageUrl) {
  try {
    const response = await fetch(`${API_BASE_URL}/check-image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image_url: imageUrl })
    });
    return await response.json();
  } catch (error) {
    console.error('Error checking image:', error);
    return { is_profane: false, error: error.message };
  }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'FILTER_TEXT') {
    filterText(request.text).then(sendResponse);
    return true;
  }
  if (request.type === 'CHECK_IMAGE') {
    checkImage(request.imageUrl).then(sendResponse);
    return true;
  }
});
