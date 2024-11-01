images/temp/
├── README.md
    """
    Temporary Processing Directory
    This directory contains images during the processing pipeline:
    
    Naming convention:
    {timestamp}_{operation}_{url_hash}.{extension}
    
    Examples:
    - 20241101_153022_download_1a2b3c.jpg     # Downloaded original image
    - 20241101_153022_analyzing_1a2b3c.jpg    # Image being analyzed
    - 20241101_153022_blurring_1a2b3c.jpg     # Image during blur processing
    
    Files in this directory are automatically cleaned up after processing
    or after 24 hours, whichever comes first.
    """

Example contents during processing:
└── temp/
    ├── README.md
    ├── 20241101_153022_download_1a2b3c.jpg   # Step 1: Downloaded image
    ├── 20241101_153022_analyzing_1a2b3c.jpg  # Step 2: Analysis in progress
    ├── 20241101_153022_blurring_1a2b3c.jpg   # Step 3: Applying blur
    └── processing_log.txt                     # Processing status log