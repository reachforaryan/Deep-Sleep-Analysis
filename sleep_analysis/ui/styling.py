import streamlit as st

def apply_custom_css():
    """Inject custom CSS for Bento Dashboard"""
    st.markdown("""
    <style>
    /* Clean up default streamlit spacing */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Modern Card Styling */
    .dashboard-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        border: 1px solid #3d3d3d;
        transition: transform 0.2s;
    }
    
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        border-color: #5d5d5d;
    }

    /* Gradient Text for Headlines */
    .gradient-text {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* Metric Value Styling */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #a0a0a0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Utility classes for status colors */
    .status-good { color: #4ade80 !important; }
    .status-warning { color: #fbbf24 !important; }
    .status-bad { color: #f87171 !important; }
    
    /* Custom separator */
    .separator {
        height: 1px;
        background: linear-gradient(90deg, transparent, #444, transparent);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def card_container(key=None):
    """
    Helper to create a bordered container.
    Result is a context manager.
    """
    try:
        # Try using the border parameter (Streamlit 1.30+)
        return st.container(border=True)
    except TypeError:
        # Fallback for older Streamlit versions
        return st.container()
