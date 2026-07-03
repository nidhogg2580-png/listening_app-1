"""
English Repeated Listening - Main Application

A Streamlit-based web application for English listening practice.

Features:
- Upload local videos (mp4, mov, avi, mkv)
- Full-area clickable video player
- Frame-accurate clip creation: play -> pause -> mark start -> play -> pause -> mark end
- Loop playback for each clip
- Bilingual subtitles (EN/ZH) for each clip
- Save/Load projects

Usage:
    streamlit run app.py

Deployment:
    1. Push code to GitHub
    2. Connect repository to Streamlit Community Cloud
    3. Deploy with default settings
"""

import os
import time
import streamlit as st

# Set page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="English Repeated Listening",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from config import (
    UPLOAD_DIR,
    TEMP_DIR,
    SUPPORTED_VIDEO_FORMATS,
    SS_VIDEO_FILE,
    SS_VIDEO_PATH,
    SS_VIDEO_DURATION,
    SS_VIDEO_MIME,
    SS_CLIPS,
    SS_CURRENT_CLIP,
    SS_MODE,
    SS_LOOP,
    SS_PAGE,
    SS_PROJECT_NAME,
    SS_VIDEO_BASE64,
    SS_CLIP_START_MARKER,
    SS_CLIP_END_MARKER,
    SS_SUBTITLE_EDIT,
    SS_PLAYER_KEY,
    ensure_directories,
)
from utils import (
    format_time,
    get_video_duration,
    video_to_base64,
    save_uploaded_file,
    delete_file,
    create_clip,
    renumber_clips,
    get_mime_type,
    create_clip,
)
from project_manager import (
    create_project,
    save_project_to_file,
    load_project_from_file,
    generate_project_filename,
    validate_project,
    migrate_project,
)
from video_player import render_video_player
from styles import apply_global_styles


# ============================================================================
# Initialization
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        SS_VIDEO_FILE: None,
        SS_VIDEO_PATH: None,
        SS_VIDEO_DURATION: 0.0,
        SS_VIDEO_MIME: "video/mp4",
        SS_CLIPS: [],
        SS_CURRENT_CLIP: 0,
        SS_MODE: "full",
        SS_LOOP: True,
        SS_PAGE: "home",
        SS_PROJECT_NAME: "",
        SS_VIDEO_BASE64: None,
        SS_CLIP_START_MARKER: None,
        SS_CLIP_END_MARKER: None,
        SS_SUBTITLE_EDIT: -1,
        SS_PLAYER_KEY: 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================================
# Video Handling
# ============================================================================

def handle_video_upload(uploaded_file):
    """Handle video file upload."""
    if uploaded_file is None:
        return

    ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    if ext not in SUPPORTED_VIDEO_FORMATS:
        st.error(f"Unsupported format: .{ext}. Please use: {', '.join(SUPPORTED_VIDEO_FORMATS)}")
        return

    ensure_directories()
    video_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
    mime_type = get_mime_type(uploaded_file.name)
    duration = get_video_duration(video_path)

    if duration <= 0:
        file_size = os.path.getsize(video_path)
        duration = max(file_size / (1024 * 1024) * 10, 60)
        st.warning("Could not detect video duration. Using estimate.")

    # Reset all state
    st.session_state[SS_VIDEO_FILE] = uploaded_file
    st.session_state[SS_VIDEO_PATH] = video_path
    st.session_state[SS_VIDEO_DURATION] = duration
    st.session_state[SS_VIDEO_MIME] = mime_type
    st.session_state[SS_CLIPS] = []
    st.session_state[SS_CURRENT_CLIP] = 0
    st.session_state[SS_MODE] = "full"
    st.session_state[SS_LOOP] = True
    st.session_state[SS_PAGE] = "edit"
    st.session_state[SS_PROJECT_NAME] = os.path.splitext(uploaded_file.name)[0]
    st.session_state[SS_VIDEO_BASE64] = None
    st.session_state[SS_CLIP_START_MARKER] = None
    st.session_state[SS_CLIP_END_MARKER] = None
    st.session_state[SS_SUBTITLE_EDIT] = -1
    st.session_state[SS_PLAYER_KEY] = 0

    st.rerun()


def get_video_base64_cached() -> str:
    """Get base64 encoded video, with caching in session state."""
    if st.session_state[SS_VIDEO_BASE64] is not None:
        return st.session_state[SS_VIDEO_BASE64]

    video_path = st.session_state[SS_VIDEO_PATH]
    if not video_path or not os.path.exists(video_path):
        return ""

    try:
        base64_data = video_to_base64(video_path)
        st.session_state[SS_VIDEO_BASE64] = base64_data
        return base64_data
    except Exception as e:
        st.error(f"Error encoding video: {e}")
        return ""


def clear_video_data():
    """Clear all video-related session state and return to home."""
    video_path = st.session_state.get(SS_VIDEO_PATH)
    if video_path and os.path.exists(video_path):
        delete_file(video_path)

    st.session_state[SS_VIDEO_FILE] = None
    st.session_state[SS_VIDEO_PATH] = None
    st.session_state[SS_VIDEO_DURATION] = 0.0
    st.session_state[SS_VIDEO_MIME] = "video/mp4"
    st.session_state[SS_CLIPS] = []
    st.session_state[SS_CURRENT_CLIP] = 0
    st.session_state[SS_MODE] = "full"
    st.session_state[SS_LOOP] = True
    st.session_state[SS_PAGE] = "home"
    st.session_state[SS_PROJECT_NAME] = ""
    st.session_state[SS_VIDEO_BASE64] = None
    st.session_state[SS_CLIP_START_MARKER] = None
    st.session_state[SS_CLIP_END_MARKER] = None
    st.session_state[SS_SUBTITLE_EDIT] = -1
    st.session_state[SS_PLAYER_KEY] = 0


# ============================================================================
# Clip Management - New frame-accurate approach
# ============================================================================

def get_player_time() -> float:
    """Get the current time from the video player component."""
    return st.session_state.get("_player_reported_time", 0.0)


def mark_start():
    """Mark the current pause position as clip start."""
    t = get_player_time()
    duration = st.session_state[SS_VIDEO_DURATION]

    if t < 0 or t > duration:
        st.warning("Invalid time position. Please play and pause the video first.")
        return

    # Ensure start < end (if end is already marked)
    end_marker = st.session_state[SS_CLIP_END_MARKER]
    if end_marker is not None and t >= end_marker:
        st.warning("Start time must be before end time. Please re-mark.")
        st.session_state[SS_CLIP_END_MARKER] = None
        return

    st.session_state[SS_CLIP_START_MARKER] = round(t, 2)
    st.success(f"Start marked at {format_time(t)}")
    time.sleep(0.2)
    st.rerun()


def mark_end():
    """Mark the current pause position as clip end."""
    t = get_player_time()
    duration = st.session_state[SS_VIDEO_DURATION]
    start_marker = st.session_state[SS_CLIP_START_MARKER]

    if t < 0 or t > duration:
        st.warning("Invalid time position. Please play and pause the video first.")
        return

    if start_marker is None:
        st.warning("Please mark a start point first.")
        return

    if t <= start_marker:
        st.warning(f"End time ({format_time(t)}) must be after start time ({format_time(start_marker)}).")
        return

    st.session_state[SS_CLIP_END_MARKER] = round(t, 2)
    st.success(f"End marked at {format_time(t)}")
    time.sleep(0.2)
    st.rerun()


def create_new_clip():
    """Create a new clip from the marked start and end points."""
    start = st.session_state[SS_CLIP_START_MARKER]
    end = st.session_state[SS_CLIP_END_MARKER]
    duration = st.session_state[SS_VIDEO_DURATION]

    if start is None:
        st.warning("Please mark a start point first.")
        return

    if end is None:
        st.warning("Please mark an end point.")
        return

    if start < 0 or end > duration or start >= end:
        st.error("Invalid clip boundaries. Please re-mark.")
        return

    clips = st.session_state[SS_CLIPS]
    new_clip = create_clip(start, end, len(clips) + 1)
    clips.append(new_clip)
    st.session_state[SS_CLIPS] = clips

    # Clear markers for next clip
    st.session_state[SS_CLIP_START_MARKER] = None
    st.session_state[SS_CLIP_END_MARKER] = None

    st.success(f"Created Clip{len(clips)}: {format_time(start)} - {format_time(end)}")
    time.sleep(0.2)
    st.rerun()


def clear_markers():
    """Clear start and end markers."""
    st.session_state[SS_CLIP_START_MARKER] = None
    st.session_state[SS_CLIP_END_MARKER] = None
    st.rerun()


def delete_clip(clip_index: int):
    """Delete a clip by index."""
    clips = st.session_state[SS_CLIPS]

    if not clips or clip_index < 0 or clip_index >= len(clips):
        return

    clips.pop(clip_index)
    clips = renumber_clips(clips)
    st.session_state[SS_CLIPS] = clips

    # Adjust current clip index
    current = st.session_state[SS_CURRENT_CLIP]
    if current >= len(clips):
        st.session_state[SS_CURRENT_CLIP] = max(0, len(clips) - 1)

    # If editing subtitle for deleted clip, clear
    if st.session_state[SS_SUBTITLE_EDIT] == clip_index:
        st.session_state[SS_SUBTITLE_EDIT] = -1

    st.rerun()


def select_clip(clip_index: int):
    """Select a clip to play in clip learning mode."""
    clips = st.session_state[SS_CLIPS]
    if not clips or clip_index < 0 or clip_index >= len(clips):
        return

    st.session_state[SS_CURRENT_CLIP] = clip_index
    st.session_state[SS_MODE] = "clip"
    st.session_state[SS_LOOP] = True
    st.session_state[SS_SUBTITLE_EDIT] = -1
    # Change player key to force re-render with new clip
    st.session_state[SS_PLAYER_KEY] = st.session_state.get(SS_PLAYER_KEY, 0) + 1
    st.rerun()


def prev_clip():
    """Go to previous clip."""
    current = st.session_state[SS_CURRENT_CLIP]
    if current > 0:
        st.session_state[SS_CURRENT_CLIP] = current - 1
        st.session_state[SS_LOOP] = True
        st.session_state[SS_SUBTITLE_EDIT] = -1
        st.session_state[SS_PLAYER_KEY] = st.session_state.get(SS_PLAYER_KEY, 0) + 1
        st.rerun()


def next_clip():
    """Go to next clip."""
    current = st.session_state[SS_CURRENT_CLIP]
    clips = st.session_state[SS_CLIPS]
    if current < len(clips) - 1:
        st.session_state[SS_CURRENT_CLIP] = current + 1
        st.session_state[SS_LOOP] = True
        st.session_state[SS_SUBTITLE_EDIT] = -1
        st.session_state[SS_PLAYER_KEY] = st.session_state.get(SS_PLAYER_KEY, 0) + 1
        st.rerun()


def toggle_loop():
    """Toggle loop mode."""
    st.session_state[SS_LOOP] = not st.session_state[SS_LOOP]
    st.rerun()


# ============================================================================
# Subtitle Management
# ============================================================================

def save_subtitle(clip_index: int, en_text: str, zh_text: str):
    """Save subtitle for a clip."""
    clips = st.session_state[SS_CLIPS]
    if 0 <= clip_index < len(clips):
        clips[clip_index]["subtitle_en"] = en_text.strip()
        clips[clip_index]["subtitle_zh"] = zh_text.strip()
        st.session_state[SS_CLIPS] = clips
        st.session_state[SS_SUBTITLE_EDIT] = -1
        st.success("Subtitle saved!")
        time.sleep(0.2)
        st.rerun()


def toggle_subtitle_edit(clip_index: int):
    """Toggle subtitle edit mode for a clip."""
    current = st.session_state[SS_SUBTITLE_EDIT]
    if current == clip_index:
        st.session_state[SS_SUBTITLE_EDIT] = -1
    else:
        st.session_state[SS_SUBTITLE_EDIT] = clip_index
    st.rerun()


# ============================================================================
# Project Save/Load
# ============================================================================

def save_project():
    """Save current project to JSON file."""
    video_path = st.session_state[SS_VIDEO_PATH]
    if not video_path:
        st.error("No video loaded!")
        return

    video_filename = os.path.basename(video_path)
    duration = st.session_state[SS_VIDEO_DURATION]
    clips = st.session_state[SS_CLIPS]
    project_name = st.session_state[SS_PROJECT_NAME] or "Untitled Project"

    project = create_project(
        video_filename=video_filename,
        video_duration=duration,
        clips=clips,
        project_name=project_name,
    )

    filename = generate_project_filename(project_name)
    ensure_directories()
    file_path = os.path.join(TEMP_DIR, filename)

    if save_project_to_file(project, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            json_content = f.read()

        st.download_button(
            label="📥 Download Project",
            data=json_content,
            file_name=filename,
            mime="application/json",
            key="download_project_btn",
        )
        st.success(f"Project ready: {filename}")
    else:
        st.error("Failed to save project!")


def load_project(uploaded_file):
    """Load project from uploaded JSON file."""
    if uploaded_file is None:
        return

    try:
        import json
        project = json.loads(uploaded_file.getvalue().decode("utf-8"))
        project = migrate_project(project)

        is_valid, message = validate_project(project, UPLOAD_DIR)
        if not is_valid:
            st.error(f"Invalid project: {message}")
            return

        video_filename = project["video_filename"]
        video_path = os.path.join(UPLOAD_DIR, video_filename)

        st.session_state[SS_VIDEO_PATH] = video_path
        st.session_state[SS_VIDEO_DURATION] = project["video_duration"]
        st.session_state[SS_VIDEO_MIME] = get_mime_type(video_filename)
        st.session_state[SS_CLIPS] = project["clips"]
        st.session_state[SS_CURRENT_CLIP] = 0
        st.session_state[SS_MODE] = "clip"
        st.session_state[SS_LOOP] = True
        st.session_state[SS_PAGE] = "edit"
        st.session_state[SS_PROJECT_NAME] = project.get("project_name", "Loaded Project")
        st.session_state[SS_VIDEO_BASE64] = None
        st.session_state[SS_CLIP_START_MARKER] = None
        st.session_state[SS_CLIP_END_MARKER] = None
        st.session_state[SS_SUBTITLE_EDIT] = -1
        st.session_state[SS_PLAYER_KEY] = 0

        st.success(f"Project loaded: {project.get('project_name', 'Untitled')}")
        time.sleep(0.5)
        st.rerun()

    except Exception as e:
        st.error(f"Error loading project: {e}")


# ============================================================================
# Handle Player Component Events
# ============================================================================

def handle_player_event(event_data: dict):
    """Handle events sent back from the video player component."""
    if not event_data or not isinstance(event_data, dict):
        return

    event_type = event_data.get("event", "")
    current_time = event_data.get("currentTime", 0)

    # Store reported time in a non-persistent key
    st.session_state["_player_reported_time"] = current_time

    if event_type == "navigate":
        direction = event_data.get("direction", "")
        if direction == "prev":
            prev_clip()
        elif direction == "next":
            next_clip()

    elif event_type == "toggle_loop":
        toggle_loop()


# ============================================================================
# UI Components
# ============================================================================

def render_header():
    """Render app header."""
    st.markdown(
        """
        <div class="app-header">
            <h1>🎧 English Repeated Listening</h1>
            <p>Master English through intensive listening practice</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_page():
    """Render the home page with upload and project loading."""
    render_header()

    # Upload Section
    st.markdown("""
        <div class="section-header">📹 Upload Video</div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; padding: 1rem; color: #666; font-size: 0.9rem;">
            Supported formats: <b>MP4</b>, <b>MOV</b>, <b>AVI</b>, <b>MKV</b><br>
            Upload a video to start your listening practice
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=SUPPORTED_VIDEO_FORMATS,
        label_visibility="collapsed",
        key="video_uploader",
    )

    if uploaded_file is not None:
        with st.spinner("Processing video..."):
            handle_video_upload(uploaded_file)

    st.markdown("---")

    # Load Project Section
    st.markdown("""
        <div class="section-header">📂 Load Project</div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; padding: 0.5rem; color: #666; font-size: 0.9rem;">
            Load a previously saved project file (.json)<br>
            Make sure the video file is in the <code>uploads/</code> folder
        </div>
    """, unsafe_allow_html=True)

    project_file = st.file_uploader(
        "Choose a project file",
        type=["json"],
        label_visibility="collapsed",
        key="project_uploader",
    )

    if project_file is not None:
        load_project(project_file)

    # Quick guide
    st.markdown("---")
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Getting Started

        1. **Upload a Video**: Select a video file (MP4, MOV, AVI, MKV)

        2. **Create Clips** (Frame-accurate):
           - In **Full Video** mode, play the video
           - Pause at the sentence/phrase **start** position
           - Click **⏹ Mark Start** to record the start time
           - Play again, pause at the **end** position
           - Click **⏹ Mark End** to record the end time
           - Click **✚ Create Clip** to save the segment

        3. **Practice Listening**:
           - Switch to **Clip Learning** mode
           - Click on any clip to play it
           - The clip loops automatically for repeated listening
           - Read the bilingual subtitles while listening

        4. **Add Subtitles**:
           - In Clip Learning mode, click **📝 Edit Subtitle** for each clip
           - Enter English and Chinese text
           - Subtitles display while the clip plays

        5. **Navigate & Control**:
           - **Prev** / **Next** buttons to switch between clips
           - **Loop** button to toggle auto-repeat
           - Click anywhere on the video to play/pause

        6. **Save Your Work**:
           - Click **💾 Save** to download a JSON project file
           - Later, load the project and re-upload the same video
        """)


def render_edit_page():
    """Render the video editing/learning page."""
    video_path = st.session_state[SS_VIDEO_PATH]
    duration = st.session_state[SS_VIDEO_DURATION]
    clips = st.session_state[SS_CLIPS]
    current_index = st.session_state[SS_CURRENT_CLIP]
    mode = st.session_state[SS_MODE]
    loop_enabled = st.session_state[SS_LOOP]
    project_name = st.session_state[SS_PROJECT_NAME]

    if not video_path or not os.path.exists(video_path):
        st.error("Video file not found! Please upload again.")
        if st.button("← Back to Home"):
            clear_video_data()
            st.rerun()
        return

    # ===== Top navigation bar =====
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("← Home", key="back_home"):
            clear_video_data()
            st.rerun()

    with col2:
        st.markdown(f"""
            <div style="text-align: center;">
                <span style="font-size: 1.1rem; font-weight: 600;">{project_name or 'Untitled'}</span>
                <span style="font-size: 0.8rem; color: #888;"> ({format_time(duration)})</span>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        save_col1, save_col2 = st.columns(2)
        with save_col1:
            if st.button("💾 Save", key="save_btn"):
                save_project()
        with save_col2:
            if st.button("🗑️ Clear", key="clear_btn"):
                clear_video_data()
                st.rerun()

    # ===== Mode selector =====
    st.markdown("---")
    mode_col1, mode_col2, mode_col3 = st.columns([1, 1, 2])

    with mode_col1:
        if st.button(
            "📹 Full Video",
            key="mode_full",
            type="primary" if mode == "full" else "secondary",
            use_container_width=True,
        ):
            st.session_state[SS_MODE] = "full"
            st.session_state[SS_SUBTITLE_EDIT] = -1
            st.rerun()

    with mode_col2:
        if st.button(
            "✂️ Clip Learning",
            key="mode_clip",
            type="primary" if mode == "clip" else "secondary",
            use_container_width=True,
        ):
            st.session_state[SS_MODE] = "clip"
            st.rerun()

    with mode_col3:
        if mode == "clip" and clips and 0 <= current_index < len(clips):
            clip = clips[current_index]
            st.markdown(f"""
                <div style="text-align: right; padding-top: 0.5rem;">
                    <span style="background: #ff4b4b; color: white; padding: 0.25rem 0.75rem;
                                 border-radius: 12px; font-size: 0.85rem; font-weight: 500;">
                        {clip['name']}: {format_time(clip['start'])} - {format_time(clip['end'])}
                    </span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ===== Main content =====
    if mode == "full":
        render_full_mode(video_path, duration)
    else:
        render_clip_mode(video_path, duration, clips, current_index, loop_enabled)


def render_full_mode(video_path: str, duration: float):
    """
    Render FULL VIDEO mode:
    - Custom video player (full-area clickable)
    - Frame-accurate clip creation: play -> pause -> mark start/end -> create
    """
    video_base64 = get_video_base64_cached()
    if not video_base64:
        st.error("Failed to load video data.")
        return

    # ===== Video Player =====
    player_key = f"full_player_{st.session_state.get(SS_PLAYER_KEY, 0)}"
    event = render_video_player(
        video_base64=video_base64,
        mime_type=st.session_state[SS_VIDEO_MIME],
        mode="full",
        key=player_key,
    )

    # Handle player events (store reported time)
    if event:
        handle_player_event(event)

    # ===== Clip Creation Controls =====
    st.markdown("""
        <div class="section-header" style="margin-top: 1rem;">✂️ Create Clip</div>
    """, unsafe_allow_html=True)

    # Show current player time
    reported_time = st.session_state.get("_player_reported_time", 0)

    # Show markers status
    start_marker = st.session_state[SS_CLIP_START_MARKER]
    end_marker = st.session_state[SS_CLIP_END_MARKER]

    # Instruction
    if start_marker is None:
        st.info("**Step 1:** Play the video, pause at the **start** of a sentence, then click **Mark Start**.")
    elif end_marker is None:
        st.info("**Step 2:** Play the video, pause at the **end** of the sentence, then click **Mark End**.")
    else:
        st.success(f"**Ready:** Clip from {format_time(start_marker)} to {format_time(end_marker)}")

    # Action buttons
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])

    with btn_col1:
        st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; background: #f0f0f0; border-radius: 6px;">
                <div style="font-size: 0.75rem; color: #888;">Current Position</div>
                <div style="font-size: 1.2rem; font-weight: 600; font-family: monospace;">
                    {format_time(reported_time)}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with btn_col2:
        start_label = "⏹ Mark Start"
        if start_marker is not None:
            start_label = f"✓ Start: {format_time(start_marker)}"
        if st.button(start_label, type="primary" if start_marker is None else "secondary",
                     key="mark_start_btn", use_container_width=True):
            mark_start()

    with btn_col3:
        end_label = "⏹ Mark End"
        if end_marker is not None:
            end_label = f"✓ End: {format_time(end_marker)}"
        disabled = start_marker is None
        if st.button(end_label, type="primary" if (start_marker is not None and end_marker is None) else "secondary",
                     key="mark_end_btn", use_container_width=True, disabled=disabled):
            mark_end()

    with btn_col4:
        create_disabled = (start_marker is None or end_marker is None)
        if st.button("✚ Create Clip", type="primary", key="create_clip_btn",
                     use_container_width=True, disabled=create_disabled):
            create_new_clip()

    # Clear markers button
    if start_marker is not None or end_marker is not None:
        if st.button("🗑️ Clear Markers", key="clear_markers_btn"):
            clear_markers()

    # ===== Clip List =====
    st.markdown("---")
    render_full_mode_clip_list(clips=st.session_state[SS_CLIPS])


def render_clip_mode(
    video_path: str,
    duration: float,
    clips: list,
    current_index: int,
    loop_enabled: bool,
):
    """
    Render CLIP LEARNING mode:
    - Loop playback of selected clip
    - Bilingual subtitle display
    - Subtitle editing
    - Prev/Next navigation
    """
    if not clips:
        st.warning("No clips yet! Switch to Full Video mode and create some clips first.")
        return

    if current_index < 0:
        current_index = 0
    if current_index >= len(clips):
        current_index = len(clips) - 1

    current_clip = clips[current_index]
    video_base64 = get_video_base64_cached()

    if not video_base64:
        st.error("Failed to load video data.")
        return

    # ===== Layout: video player + clip list =====
    video_col, list_col = st.columns([3, 1])

    with video_col:
        # Video player with subtitles
        player_key = f"clip_player_{current_index}_{st.session_state.get(SS_PLAYER_KEY, 0)}"
        event = render_video_player(
            video_base64=video_base64,
            mime_type=st.session_state[SS_VIDEO_MIME],
            mode="clip",
            clip_start=current_clip["start"],
            clip_end=current_clip["end"],
            loop_enabled=loop_enabled,
            current_index=current_index,
            total_clips=len(clips),
            subtitle_en=current_clip.get("subtitle_en", ""),
            subtitle_zh=current_clip.get("subtitle_zh", ""),
            key=player_key,
        )

        if event:
            handle_player_event(event)

        # ===== Subtitle Editing Section =====
        st.markdown("---")
        render_subtitle_editor(clips, current_index)

    with list_col:
        st.markdown(f"""
            <div class="section-header">📋 Clips ({len(clips)})</div>
        """, unsafe_allow_html=True)

        render_clip_learning_list(clips, current_index)


def render_subtitle_editor(clips: list, current_index: int):
    """Render subtitle editing section for the current clip."""
    current_clip = clips[current_index]
    edit_index = st.session_state[SS_SUBTITLE_EDIT]

    # Show current subtitle (read-only display)
    has_subtitle = current_clip.get("subtitle_en") or current_clip.get("subtitle_zh")

    if has_subtitle and edit_index != current_index:
        st.markdown("#### 📝 Current Subtitle")
        if current_clip.get("subtitle_en"):
            st.markdown(f"**EN:** {current_clip['subtitle_en']}")
        if current_clip.get("subtitle_zh"):
            st.markdown(f"**ZH:** {current_clip['subtitle_zh']}")

    # Edit button
    if edit_index != current_index:
        if st.button("📝 Edit Subtitle", key=f"edit_sub_btn_{current_index}"):
            st.session_state[SS_SUBTITLE_EDIT] = current_index
            st.rerun()
    else:
        # Editing mode
        st.markdown("#### ✏️ Edit Subtitle")

        en_text = st.text_area(
            "English",
            value=current_clip.get("subtitle_en", ""),
            height=80,
            key=f"sub_en_{current_index}",
            placeholder="Enter English subtitle text...",
        )

        zh_text = st.text_area(
            "中文",
            value=current_clip.get("subtitle_zh", ""),
            height=80,
            key=f"sub_zh_{current_index}",
            placeholder="输入中文字幕...",
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾 Save Subtitle", type="primary", key=f"save_sub_btn_{current_index}"):
                save_subtitle(current_index, en_text, zh_text)
        with col2:
            if st.button("❌ Cancel", key=f"cancel_sub_btn_{current_index}"):
                st.session_state[SS_SUBTITLE_EDIT] = -1
                st.rerun()


def render_full_mode_clip_list(clips: list):
    """Render clip list in Full Video mode (with switch-to-clip button)."""
    if not clips:
        st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #888;">
                <p>No clips created yet.</p>
                <p style="font-size: 0.85rem;">Use the controls above to create clips.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""<div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
        {len(clips)} clip(s) created. Click a clip to switch to Clip Learning mode.
    </div>""", unsafe_allow_html=True)

    for i, clip in enumerate(clips):
        item_col, del_col = st.columns([4, 1])

        with item_col:
            label = f"{clip['name']}: {format_time(clip['start'])} - {format_time(clip['end'])}"
            has_sub = "📝" if (clip.get("subtitle_en") or clip.get("subtitle_zh")) else ""
            if st.button(
                f"{label} {has_sub}",
                key=f"full_clip_btn_{i}",
                use_container_width=True,
            ):
                st.session_state[SS_CURRENT_CLIP] = i
                st.session_state[SS_MODE] = "clip"
                st.session_state[SS_LOOP] = True
                st.session_state[SS_SUBTITLE_EDIT] = -1
                st.session_state[SS_PLAYER_KEY] = st.session_state.get(SS_PLAYER_KEY, 0) + 1
                st.rerun()

        with del_col:
            if st.button("🗑️", key=f"full_del_clip_{i}", help=f"Delete {clip['name']}", use_container_width=True):
                delete_clip(i)


def render_clip_learning_list(clips: list, active_index: int):
    """Render clip list in Clip Learning mode."""
    if not clips:
        return

    for i, clip in enumerate(clips):
        is_active = i == active_index

        # Show subtitle indicator
        has_sub = "📝" if (clip.get("subtitle_en") or clip.get("subtitle_zh")) else ""

        item_col, del_col = st.columns([4, 1])

        with item_col:
            label = f"{clip['name']}: {format_time(clip['start'])} - {format_time(clip['end'])} {has_sub}"
            btn_type = "primary" if is_active else "secondary"

            if st.button(label, key=f"clip_btn_{i}", type=btn_type, use_container_width=True):
                select_clip(i)

        with del_col:
            if st.button("🗑️", key=f"del_clip_{i}", help=f"Delete {clip['name']}", use_container_width=True):
                delete_clip(i)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    ensure_directories()
    apply_global_styles()

    page = st.session_state[SS_PAGE]

    if page == "home":
        render_home_page()
    elif page == "edit":
        render_edit_page()
    else:
        st.session_state[SS_PAGE] = "home"
        st.rerun()


if __name__ == "__main__":
    main()
