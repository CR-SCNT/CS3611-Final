# Configuration settings for the server
HOST = '0.0.0.0'
PORT = 9000
SEGMENT_DIR = 'data/segments'
BUFFER_SIZE = 4096

# Configuration settings for video segmentation
INPUT_DIR = 'data/raw'
OUTPUT_DIR = 'data/segments'
PROFILES = [
    ("1080p", "1920x1080", 2500),
    ("720p", "1280x720", 1500),
    ("480p", "854x480", 1000),
    ("360p", "640x360", 500)
]
DURATION = 5