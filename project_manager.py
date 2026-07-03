"""
Configuration constants for the English Listening App.
"""

import os

# App info
APP_NAME = "English Repeated Listening"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "English Listening Practice with Repeated Listening"

# File paths
UPLOAD_DIR = "uploads"
TEMP_DIR = "temp"

# Video formats
SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv"]
SUPPORTED_VIDEO_TYPES = {
    "mp4": "video/mp4",
    "mov": "video/quicktime",
    "avi": "video/x-msvideo",
    "mkv": "video/x-matroska",
}

# MIME type mapping
MIME_TYPES = {
    "mp4": "video/mp4",
    "mov": "video/quicktime",
    "avi": "video/x-msvideo",
    "mkv": "video/webm",
}

# UI constants
CLIP_PREFIX = "Clip"

# Session state keys
SS_VIDEO_FILE = "video_file"
SS_VIDEO_PATH = "video_path"
SS_VIDEO_DURATION = "video_duration"
SS_VIDEO_MIME = "video_mime"
SS_CLIPS = "clips"
SS_CURRENT_CLIP = "current_clip_index"
SS_MODE = "mode"
SS_LOOP = "loop_enabled"
SS_PAGE = "page"
SS_PROJECT_NAME = "project_name"
SS_FORCE_REFRESH = "force_refresh"
SS_VIDEO_BASE64 = "video_base64"
SS_CLIP_START_MARKER = "clip_start_marker"
SS_CLIP_END_MARKER = "clip_end_marker"
SS_SUBTITLE_EDIT = "subtitle_edit_index"
SS_PLAYER_KEY = "player_component_key"

# Default values
DEFAULT_CLIP_DURATION = 3.0  # seconds

# Player dimensions
PLAYER_HEIGHT_DESKTOP = 480
PLAYER_HEIGHT_MOBILE = 260

# Responsive breakpoints
MOBILE_MAX_WIDTH = 768

# Ensure upload directory exists
def ensure_directories():
    """Create necessary directories if they don't exist."""
    for directory in [UPLOAD_DIR, TEMP_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
