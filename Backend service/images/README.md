images/
├── README.md
    Content:
    """
    This directory stores censored versions of detected inappropriate images.
    
    Naming convention:
    - Censored images are stored with their URL hash as filename
    - Format: {url_hash}.jpg
    
    Example:
    - Original URL: https://example.com/inappropriate.jpg
    - Stored as: images/1a2b3c4d5e6f.jpg
    
    The hashing helps:
    1. Avoid filename conflicts
    2. Maintain privacy
    3. Enable quick lookups
    
    Images in this folder are automatically managed by the profanity_filter.py script:
    - Created when new inappropriate images are detected
    - Applied with Gaussian blur (radius=100)
    - Cached for future use
    """

Example directory structure:
└── images/
    ├── README.md
    ├── 1a2b3c4d5e6f.jpg  # Censored version of image 1
    ├── 2b3c4d5e6f7g.jpg  # Censored version of image 2
    └── temp/             # Temporary processing directory