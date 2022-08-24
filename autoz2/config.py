import os
from pathlib import Path

RANGER_ROOT_DIR = Path(os.path.expanduser("~"))/"Documents"/"ranger"

# Where records will be saved and loaded from
APPROACH_DIR = RANGER_ROOT_DIR/"approaches"

# Sample videos are used for testing / debugging, especially on systems where IC is not supported.
SAMPLE_VIDEOS_DIR = RANGER_ROOT_DIR/"sample_videos"

# Place to cache configs for things.
CONFIGS_DIR = RANGER_ROOT_DIR/"configs"


