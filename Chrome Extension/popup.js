document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('filterToggle');
  
  chrome.storage.sync.get(['enabled'], (result) => {
    toggle.checked = result.enabled !== false;
  });

  toggle.addEventListener('change', (e) => {
    const enabled = e.target.checked;
    chrome.storage.sync.set({ enabled });
    
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.reload(tabs[0].id);
    });
  });
});
