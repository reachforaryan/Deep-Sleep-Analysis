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
    
    st.title("Comprehensive Sleep Analysis")
    
    # Initialize analyzer
    @st.cache_resource
    def get_analyzer():
        return SleepAnalyzer(
            audio_model_path='models/sleep_audio_model.h5',
            disorder_model_path='models/sleep_disorder_model.pkl',
            quality_model_path='models/sleep_quality_model.pkl'
        )
    
    analyzer = get_analyzer()
    
    # Display information
    st.write("This app provides a comprehensive analysis of your sleep quality, sleep disorders, and snoring patterns.")
    st.write("Please provide the required information and upload an audio recording of your sleep for analysis.")

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
    
    # Create tabs
    tab1, tab2 = st.tabs(["Input Data", "Analysis Results"])
    
    #############
    # Tab 1: Input Data
    #############
    with tab1:
        render_inputs()
        render_analysis_buttons(analyzer)
    
    #############
    # Tab 2: Results & Recommendations
    #############
    with tab2:
        render_results_tab(analyzer)

if __name__ == "__main__":
    main()