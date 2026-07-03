"""
Custom CSS styles for the English Listening App.
"""

import streamlit as st


def apply_global_styles():
    """Apply global CSS styles to the Streamlit app."""
    st.markdown(
        """
        <style>
        /* Global styles */
        .main > div {
            padding-top: 0.5rem;
        }
        
        /* Header styling */
        .app-header {
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 1rem;
        }
        
        .app-header h1 {
            font-size: 2rem;
            font-weight: 600;
            color: #1f1f1f;
            margin-bottom: 0.25rem;
        }
        
        .app-header p {
            font-size: 0.9rem;
            color: #666;
        }
        
        /* Upload area styling */
        .upload-container {
            border: 2px dashed #cccccc;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin: 1rem 0;
            background-color: #fafafa;
            transition: border-color 0.3s;
        }
        
        .upload-container:hover {
            border-color: #ff4b4b;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* Cut button - primary action */
        .cut-button button {
            background-color: #ff4b4b;
            color: white;
            border: none;
            font-size: 1.1rem;
            padding: 0.5rem 2rem;
        }
        
        .cut-button button:hover {
            background-color: #e04343;
        }
        
        /* Clip list styling */
        .clip-item {
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid #e0e0e0;
            background-color: white;
        }
        
        .clip-item:hover {
            background-color: #f0f0f0;
            border-color: #ff4b4b;
        }
        
        .clip-item.active {
            background-color: #ffe0e0;
            border-color: #ff4b4b;
            border-left: 4px solid #ff4b4b;
        }
        
        .clip-name {
            font-weight: 600;
            color: #333;
        }
        
        .clip-time {
            font-size: 0.8rem;
            color: #888;
        }
        
        /* Section headers */
        .section-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
            padding: 0.5rem 0;
            border-bottom: 2px solid #eee;
            margin-bottom: 0.75rem;
        }
        
        /* Info cards */
        .info-card {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .info-label {
            font-size: 0.8rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .info-value {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
        }
        
        /* Control buttons row */
        .controls-row {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            flex-wrap: wrap;
        }
        
        /* Mode selector */
        .mode-selector {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .mode-btn {
            padding: 0.5rem 1.5rem;
            border-radius: 20px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .mode-btn.active {
            background: #ff4b4b;
            color: white;
            border-color: #ff4b4b;
        }
        
        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: #888;
        }
        
        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .app-header h1 {
                font-size: 1.5rem;
            }
            
            .upload-container {
                padding: 1rem;
            }
            
            .clip-item {
                padding: 0.5rem 0.75rem;
            }
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        
        /* Toast/notification styling */
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        }
        
        .toast.success {
            background-color: #28a745;
        }
        
        .toast.error {
            background-color: #dc3545;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        /* Pulse animation for recording indicator */
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }
        
        .pulse {
            animation: pulse 1.5s infinite;
        }
        
        /* Card styling */
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            margin-bottom: 1rem;
        }
        
        /* Time input styling */
        .time-input {
            font-family: monospace;
            font-size: 1.1rem;
        }
        
        /* Delete button */
        .delete-btn {
            color: #dc3545;
            cursor: pointer;
            padding: 0.25rem;
            border-radius: 4px;
            transition: background 0.2s;
        }
        
        .delete-btn:hover {
            background-color: #ffe0e0;
        }
        
        /* Navigation pills */
        .nav-pills {
            display: flex;
            gap: 0.5rem;
            padding: 0.5rem;
            background: #f0f0f0;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        
        .nav-pill {
            padding: 0.5rem 1.25rem;
            border-radius: 8px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .nav-pill.active {
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Slider styling */
        .stSlider > div > div > div {
            background-color: #ff4b4b;
        }
        
        /* Progress bar */
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #e0e0e0;
            border-radius: 2px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: #ff4b4b;
            border-radius: 2px;
            transition: width 0.3s;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_mode_selector_html(current_mode: str) -> str:
    """
    Get HTML for mode selector buttons.
    
    Args:
        current_mode: Current mode ("full" or "clip")
        
    Returns:
        HTML string
    """
    full_active = "active" if current_mode == "full" else ""
    clip_active = "active" if current_mode == "clip" else ""
    
    return f"""
    <div class="nav-pills">
        <button class="nav-pill {full_active}" onclick="window.parent.postMessage({{mode: 'full'}}, '*')">
            📹 Full Video
        </button>
        <button class="nav-pill {clip_active}" onclick="window.parent.postMessage({{mode: 'clip'}}, '*')">
            ✂️ Clip Learning
        </button>
    </div>
    """


def render_clip_item_html(clip: dict, is_active: bool, index: int) -> str:
    """
    Render a clip item as HTML.
    
    Args:
        clip: Clip dictionary
        is_active: Whether this clip is currently active
        is_current: Whether this is the current playing clip
        
    Returns:
        HTML string
    """
    from utils import format_time
    
    active_class = "active" if is_active else ""
    start_str = format_time(clip["start"])
    end_str = format_time(clip["end"])
    duration = clip["end"] - clip["start"]
    duration_str = format_time(duration)
    
    return f"""
    <div class="clip-item {active_class}" id="clip-{clip['index']}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span class="clip-name">{clip['name']}</span>
                <span class="clip-time"> {start_str} - {end_str} ({duration_str})</span>
            </div>
        </div>
    </div>
    """
