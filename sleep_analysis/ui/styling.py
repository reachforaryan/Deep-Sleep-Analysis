import streamlit as st

def apply_custom_css():
    """Inject custom CSS for Bento Dashboard"""
    st.markdown("""
    <style>
    /* Clean up default streamlit spacing */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Utility classes for text coloring */
    .status-good { color: #09ab3b !important; }
    .status-warning { color: #ffbd45 !important; }
    .status-bad { color: #ff2b2b !important; }
    
    /* Metric styling overrides to ensure they pop */
    div[data-testid="stMetricValue"] {
        font-size: 24px;
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
