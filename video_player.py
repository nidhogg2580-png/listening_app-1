"""
Custom video player component wrapper for Streamlit.

Uses streamlit.components.v1.declare_component to create a bidirectional
communication channel between Python and the HTML5 video player.

The component source is at: components/video_player/index.html
"""

import os
import streamlit as st
import streamlit.components.v1 as components
from config import PLAYER_HEIGHT_DESKTOP, PLAYER_HEIGHT_MOBILE

# Get the directory containing this file
_COMPONENT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "components",
    "video_player"
)

# Declare the custom component
_player_component = components.declare_component(
    "video_player",
    path=_COMPONENT_PATH,
)


def render_video_player(
    video_base64: str,
    mime_type: str = "video/mp4",
    mode: str = "full",
    clip_start: float = 0,
    clip_end: float = 0,
    loop_enabled: bool = True,
    current_index: int = 0,
    total_clips: int = 0,
    subtitle_en: str = "",
    subtitle_zh: str = "",
    key: str = "video_player",
):
    """
    Render the custom video player component.

    This creates an iframe with a custom HTML5 video player that supports:
    - Full-area click to play/pause
    - Custom progress bar
    - Loop playback in clip mode
    - Subtitle display
    - Bidirectional communication with Python

    Args:
        video_base64: Base64 encoded video data
        mime_type: MIME type of the video
        mode: "full" for full video, "clip" for clip learning
        clip_start: Start time of current clip (clip mode only)
        clip_end: End time of current clip (clip mode only)
        loop_enabled: Whether looping is enabled (clip mode only)
        current_index: Current clip index (clip mode only)
        total_clips: Total number of clips (clip mode only)
        subtitle_en: English subtitle text
        subtitle_zh: Chinese subtitle text
        key: Unique key for the component instance

    Returns:
        Dictionary with event data from the component, or None.
        Possible event types:
        - {"event": "pause", "currentTime": float, "isPaused": bool}
        - {"event": "seeked", "currentTime": float, "isPaused": bool}
        - {"event": "navigate", "direction": "prev"|"next", "currentIndex": int}
        - {"event": "toggle_loop", "currentIndex": int}
    """
    result = _player_component(
        video_base64=video_base64,
        mime_type=mime_type,
        mode=mode,
        clip_start=clip_start,
        clip_end=clip_end,
        loop_enabled=loop_enabled,
        current_index=current_index,
        total_clips=total_clips,
        subtitle_en=subtitle_en,
        subtitle_zh=subtitle_zh,
        key=key,
        default=None,
    )
    return result
