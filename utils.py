"""
Utility functions for the English Listening App.
"""

import os
import base64
import subprocess
import json
from datetime import datetime
from typing import Optional, List, Dict, Any


def format_time(seconds: float) -> str:
    """
    Format seconds to HH:MM:SS or MM:SS string.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string (e.g., "01:23" or "01:23:45")
    """
    if seconds is None or seconds < 0:
        return "00:00"

    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def parse_time(time_str: str) -> float:
    """
    Parse time string to seconds.

    Args:
        time_str: Time string in "HH:MM:SS", "MM:SS", or seconds

    Returns:
        Time in seconds
    """
    time_str = time_str.strip()

    # Try parsing as float (seconds)
    try:
        return float(time_str)
    except ValueError:
        pass

    # Try parsing as MM:SS or HH:MM:SS
    parts = time_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

    return 0.0


def get_video_duration(video_path: str) -> float:
    """
    Get video duration in seconds using ffprobe or ffmpeg.

    Args:
        video_path: Path to video file

    Returns:
        Duration in seconds, or 0 if failed
    """
    # Try ffprobe first
    duration = _get_duration_ffprobe(video_path)
    if duration > 0:
        return duration

    # Fallback to ffmpeg
    duration = _get_duration_ffmpeg(video_path)
    if duration > 0:
        return duration

    return 0.0


def _get_duration_ffprobe(video_path: str) -> float:
    """Get duration using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                video_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration_str = data.get("format", {}).get("duration", "0")
            return float(duration_str)
    except Exception:
        pass
    return 0.0


def _get_duration_ffmpeg(video_path: str) -> float:
    """Get duration using ffmpeg as fallback."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", video_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stderr
        for line in output.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip()
                return parse_time(parts)
    except Exception:
        pass
    return 0.0


def video_to_base64(video_path: str) -> str:
    """
    Convert video file to base64 string.

    Args:
        video_path: Path to video file

    Returns:
        Base64 encoded string
    """
    with open(video_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase."""
    return os.path.splitext(filename)[1][1:].lower()


def get_mime_type(filename: str) -> str:
    """Get MIME type for video file."""
    from config import MIME_TYPES
    ext = get_file_extension(filename)
    return MIME_TYPES.get(ext, "video/mp4")


def create_clip(
    start: float,
    end: float,
    index: int,
    subtitle_en: str = "",
    subtitle_zh: str = "",
) -> Dict[str, Any]:
    """
    Create a single clip dictionary.

    Args:
        start: Start time in seconds
        end: End time in seconds
        index: Clip index (1-based)
        subtitle_en: English subtitle
        subtitle_zh: Chinese subtitle

    Returns:
        Clip dictionary
    """
    return {
        "index": index,
        "start": round(start, 2),
        "end": round(end, 2),
        "name": f"Clip{index}",
        "subtitle_en": subtitle_en,
        "subtitle_zh": subtitle_zh,
    }


def generate_clips_from_cut_points(
    cut_points: List[float],
    video_duration: float,
) -> List[Dict[str, Any]]:
    """
    Generate clip list from cut points (legacy method, kept for compatibility).

    Args:
        cut_points: List of cut point times in seconds
        video_duration: Total video duration in seconds

    Returns:
        List of clip dictionaries
    """
    if not cut_points or video_duration <= 0:
        return [create_clip(0, video_duration, 1)]

    sorted_points = sorted([p for p in cut_points if 0 < p < video_duration])

    clips = []
    start_time = 0.0

    for i, point in enumerate(sorted_points):
        clips.append(create_clip(start_time, point, i + 1))
        start_time = point

    if start_time < video_duration:
        clips.append(create_clip(start_time, video_duration, len(clips) + 1))

    return clips


def renumber_clips(clips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Renumber clips after deletion.

    Args:
        clips: List of clip dictionaries

    Returns:
        Renumbered clip list
    """
    for i, clip in enumerate(clips):
        clip["index"] = i + 1
        clip["name"] = f"Clip{i + 1}"
    return clips


def save_uploaded_file(uploaded_file, save_dir: str = "uploads") -> str:
    """
    Save uploaded file to disk.

    Args:
        uploaded_file: Streamlit UploadedFile object
        save_dir: Directory to save file

    Returns:
        Path to saved file
    """
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def delete_file(file_path: str) -> bool:
    """
    Safely delete a file.

    Args:
        file_path: Path to file

    Returns:
        True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False


def get_safe_filename(name: str) -> str:
    """
    Convert a string to a safe filename.

    Args:
        name: Original name

    Returns:
        Safe filename
    """
    unsafe = '<>:"/\\|?*'
    for char in unsafe:
        name = name.replace(char, "_")
    return name.strip()


def get_current_timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def is_video_file(filename: str) -> bool:
    """
    Check if file is a supported video file.

    Args:
        filename: Name of file

    Returns:
        True if supported video format
    """
    from config import SUPPORTED_VIDEO_FORMATS
    ext = get_file_extension(filename)
    return ext in SUPPORTED_VIDEO_FORMATS
