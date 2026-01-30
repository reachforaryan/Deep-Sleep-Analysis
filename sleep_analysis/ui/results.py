import streamlit as st
import pandas as pd
import os
from .visualizations import render_disorder_chart, render_snoring_results

def render_results_tab(analyzer):
    """Orchestrate the rendering of all results"""
    st.header("Comprehensive Sleep Analysis Results")
    
    # Check if any analysis has been done
    if not st.session_state.disorder_results and not st.session_state.quality_results and not st.session_state.audio_results:
        st.info("No analysis results available yet. Complete at least one analysis in the Input Data tab.")
        return
    
    # Generate comprehensive suggestions if they don't exist but we have results
    if (st.session_state.disorder_results or st.session_state.quality_results or st.session_state.audio_results) and not st.session_state.combined_suggestions:
        st.session_state.combined_suggestions = analyzer.generate_suggestions(
            st.session_state.audio_results,
            st.session_state.disorder_results,
            st.session_state.quality_results
        )
    
    # Display results in expandable sections
    with st.expander("Sleep Disorder Analysis", expanded=True):
        render_disorder_section()
    
    with st.expander("Sleep Quality Analysis", expanded=True):
        render_quality_section()
    
    with st.expander("Snoring Analysis", expanded=True):
        render_snoring_results(st.session_state.audio_results, st.session_state.get('audio_fig'))
    
    # Display comprehensive recommendations
    with st.expander("Personalized Sleep Recommendations", expanded=True):
        render_recommendations_section()
    
    # Clear all results button
    if st.button("Clear All Results", key="clear_results_btn"):
        clear_results()

def render_disorder_section():
    """Render details for disorder analysis"""
    if st.session_state.disorder_results:
        disorder = st.session_state.disorder_results['prediction']
        
        # Display disorder prediction prominently
        if disorder == "None":
            st.success("### No Sleep Disorder Detected")
        elif disorder == "Insomnia":
            st.warning("### Insomnia Detected")
        elif disorder == "Sleep Apnea":
            st.error("### Sleep Apnea Detected")
        else:
            st.info(f"### Predicted: {disorder}")
        
        # Chart
        render_disorder_chart(st.session_state.disorder_results)
        
        # Show input summary
        st.write("#### Key Risk Factors")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sleep Duration", f"{st.session_state.shared_inputs.get('Sleep Duration', 0):.1f} hrs")
            st.metric("BMI Category", st.session_state.shared_inputs.get('BMI Category', 'Unknown'))
        with col2:
            st.metric("Physical Activity", f"{st.session_state.shared_inputs.get('Physical Activity Level', 0)} min/day")
        with col3:
            st.metric("Stress Level", f"{st.session_state.shared_inputs.get('Stress Level', 0)}/10")
            st.metric("Heart Rate", f"{st.session_state.shared_inputs.get('Heart Rate', 0)} bpm")
    else:
        st.info("Sleep disorder analysis not completed.")

def render_quality_section():
    """Render details for quality analysis"""
    if st.session_state.quality_results:
        quality_score = st.session_state.quality_results['score']
        
        # Display result prominently
        if quality_score <= 3:
            st.error(f"### Poor Sleep Quality: {quality_score:.2f}/10")
        elif quality_score <= 7:
            st.warning(f"### Moderate Sleep Quality: {quality_score:.2f}/10")
        else:
            st.success(f"### Good Sleep Quality: {quality_score:.2f}/10")
        
        # Display quality score
        st.slider("Sleep Quality Score", 1, 10, int(quality_score) if int(quality_score) >= 1 else 1, disabled=True, key="result_quality_score")
        
        # Show key metrics
        st.write("#### Key Physiological Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Heart Rate Variability", f"{st.session_state.shared_inputs.get('Heart_Rate_Variability', 0):.1f} ms")
        with col2:
            st.metric("Body Temperature", f"{st.session_state.shared_inputs.get('Body_Temperature', 0):.1f} °C")
        with col3:
            st.metric("Movement", f"{st.session_state.shared_inputs.get('Movement_During_Sleep', 0):.2f} index")
        with col4:
            st.metric("Sleep Duration", f"{st.session_state.shared_inputs.get('Sleep Duration', 0):.1f} hrs")
    else:
        st.info("Sleep quality analysis not completed.")

def render_recommendations_section():
    """Render recommendations"""
    combined_suggestions = st.session_state.combined_suggestions
    if combined_suggestions:
        # Display specific recommendations
        st.markdown("### Specific Recommendations")
        for suggestion in combined_suggestions['specific_suggestions']:
            st.write(f"• {suggestion}")
        
        # Display general recommendations
        st.markdown("### General Sleep Hygiene Tips")
        for suggestion in combined_suggestions['general_suggestions']:
            st.write(f"• {suggestion}")
    else:
        st.info("Complete at least one analysis to get personalized recommendations.")

def clear_results():
    """Reset all results and rerun"""
    # Reset all session state values
    st.session_state.shared_inputs = {}
    st.session_state.audio_results = None
    st.session_state.disorder_results = None
    st.session_state.quality_results = None
    st.session_state.combined_suggestions = None
    
    # Clean up temp files
    if 'temp_audio_path' in st.session_state and os.path.exists(st.session_state.temp_audio_path):
        try:
            os.unlink(st.session_state.temp_audio_path)
        except:
            pass
    
    st.rerun()
