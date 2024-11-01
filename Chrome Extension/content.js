class ContentFilter {
    constructor() {
      this.observePageChanges();
      this.filterExistingContent();
    }
  
    async filterText(text) {
      const response = await chrome.runtime.sendMessage({
        type: 'FILTER_TEXT',
        text: text
      });
      return response;
    }
  
    async checkImage(imageUrl) {
      const response = await chrome.runtime.sendMessage({
        type: 'CHECK_IMAGE',
        imageUrl: imageUrl
      });
      return response;
    }
  
    async filterNode(node) {
      if (node.nodeType === Node.TEXT_NODE && node.parentNode.tagName !== 'SCRIPT' && node.parentNode.tagName !== 'STYLE') {
        const originalText = node.textContent;
        const filteredText = await this.filterText(originalText);
        if (originalText !== filteredText) {
          node.textContent = filteredText;
        }
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        // Handle images
        if (node.tagName === 'IMG') {
          const imageUrl = node.src;
          const imageCheck = await this.checkImage(imageUrl);
          if (imageCheck.is_profane) {
            if (imageCheck.censored_url) {
              node.src = imageCheck.censored_url;
            } else {
              node.style.filter = 'blur(10px)';
            }
          }
        }
        
        // Process child nodes
        for (const childNode of node.childNodes) {
          await this.filterNode(childNode);
        }
      }
    }
  
    async filterExistingContent() {
      await this.filterNode(document.body);
    }
  
    observePageChanges() {
      const observer = new MutationObserver(async (mutations) => {
        for (const mutation of mutations) {
          for (const node of mutation.addedNodes) {
            await this.filterNode(node);
          }
        }
      });
  
      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }
  }
  
  new ContentFilter();