import streamlit as st
import os
import sys

# Add the current directory to path to ensure we can import the local package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sleep_analysis.analyzer import SleepAnalyzer
from sleep_analysis.ui.inputs import render_inputs
from sleep_analysis.ui.analysis_handlers import render_analysis_buttons
from sleep_analysis.ui.results import render_results_tab

# Streamlit application
def main():
    st.set_page_config(page_title="Comprehensive Sleep Analysis", layout="wide")
    
    # Initialize analyzer
    @st.cache_resource
    def get_analyzer_v2():
        return SleepAnalyzer(
            audio_model_path='models/sleep_audio_model.h5',
            disorder_model_path='models/sleep_disorder_model.pkl',
            quality_model_path='models/sleep_quality_model.pkl'
        )
    
    analyzer = get_analyzer_v2()
    
    # Initialize Session State
    if 'shared_inputs' not in st.session_state:
        st.session_state.shared_inputs = {}
    if 'audio_results' not in st.session_state:
        st.session_state.audio_results = None
    if 'disorder_results' not in st.session_state:
        st.session_state.disorder_results = None
    if 'quality_results' not in st.session_state:
        st.session_state.quality_results = None
    if 'combined_suggestions' not in st.session_state:
        st.session_state.combined_suggestions = None
    if 'has_run_analysis' not in st.session_state:
        st.session_state.has_run_analysis = False
    
    # --- Sidebar: Input Configuration ---
    with st.sidebar:
        st.title("Sleep Profile")
        render_inputs()
        st.markdown("---")
        # Pass a callback or handle button click to set 'has_run_analysis'
        if render_analysis_buttons(analyzer):
            st.session_state.has_run_analysis = True
            # No need to rerun explicitly if the button triggers the analysis and updates state, 
            # streamlits render loop will catch it.
    
    # --- Main Area: Results or Welcome ---
    if st.session_state.has_run_analysis:
        st.markdown("# Analysis Results")
        render_results_tab(analyzer)
    else:
        # Welcome / Empty State
        st.title("Comprehensive Sleep Analysis")
        st.markdown("""
        ### :material/waving_hand: Welcome!
        
        This application analyzes your sleep patterns using advanced physiological metrics and audio analysis.
        
        **How to use:**
        1.  **Configure Profile**: Use the sidebar to enter your personal data and sleep habits.
        2.  **Upload Audio**: Upload a sleep recording for snoring detection.
        3.  **Analyze**: Click the button in the sidebar to generate insights.
        
        ---
        <br>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("**Advanced Metrics**\n\nAnalyzes medical-grade data like HRV and Body Temp.")
        with c2:
            st.info("**Audio Analysis**\n\nDetects storing and environmental noise patterns.")
        with c3:
            st.info("**Personalized Tips**\n\nGet actionable advice to improve your sleep quality.")

if __name__ == "__main__":
    main()