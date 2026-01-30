import streamlit as st
import pandas as pd
import os
from .visualizations import render_disorder_chart, render_snoring_results
from .styling import apply_custom_css, card_container


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
    

    # Apply CSS
    apply_custom_css()
    
    # --- Row 1: Hero Metrics ---
    col1, col2, col3 = st.columns(3)
    
    # 1. Main Disorder Prediction
    with col1:
        with card_container():
            if st.session_state.disorder_results:
                disorder = st.session_state.disorder_results['prediction']
                st.caption("SLEEP DISORDER RISK")
                
                color_class = "status-good"
                if disorder == "Insomnia": color_class = "status-warning"
                elif disorder == "Sleep Apnea": color_class = "status-bad"
                
                # Using markdown with class for color
                st.markdown(f'<h2 class="{color_class}">{disorder}</h2>', unsafe_allow_html=True)
                
                # Show max probability
                if 'probabilities' in st.session_state.disorder_results:
                     probs = st.session_state.disorder_results['probabilities']
                     max_p = probs.get(disorder, 0) * 100
                     st.caption(f"Confidence: {max_p:.1f}%")
            else:
                st.caption("SLEEP DISORDER RISK")
                st.info("Analysis pending")

        
    # 2. Sleep Quality Score
    with col2:
        with card_container():
            if st.session_state.quality_results:
                score = st.session_state.quality_results['score']
                st.caption("SLEEP QUALITY SCORE")
                
                color_class = "status-good"
                if score <= 3: color_class = "status-bad"
                elif score <= 7: color_class = "status-warning"
                
                st.markdown(f'<h2 class="{color_class}">{score:.1f} <span style="font-size:1rem;color:#999">/10</span></h2>', unsafe_allow_html=True)
                st.progress(min(score/10, 1.0))
            else:
                st.caption("SLEEP QUALITY SCORE")
                st.info("Analysis pending")
        
    # 3. Snoring Severity
    with col3:
        with card_container():
            if st.session_state.audio_results:
                res = st.session_state.audio_results
                pct = res['snoring_percentage']
                st.caption("SNORING SEVERITY")
                
                color_class = "status-good"
                if pct > 50: color_class = "status-bad"
                elif pct > 30: color_class = "status-warning"
                
                st.markdown(f'<h2 class="{color_class}">{pct:.1f}%</h2>', unsafe_allow_html=True)
                st.caption(f"{res['total_snoring_duration']/60:.1f} mins of snoring")
            else:
                st.caption("SNORING SEVERITY")
                st.info("Analysis pending")

    # --- Row 2: Deep Dive ---
    # Using st.columns for layout, individual cards for content
    col_wide, col_narrow = st.columns([2, 1])
    
    with col_wide:
        with card_container():
            st.subheader("Audio Analysis")
            if st.session_state.audio_results:
                 render_snoring_results(st.session_state.audio_results, st.session_state.get('audio_fig'))
            else:
                 st.info("No audio analysis available")
        
    with col_narrow:
        with card_container():
            st.subheader("Disorder Probabilities")
            if st.session_state.disorder_results:
                render_disorder_chart(st.session_state.disorder_results)
            else:
                st.info("No disorder analysis available")

    # --- Row 3: Metrics Grid ---
    st.markdown("### Key Physiological Metrics")
    m1, m2, m3, m4 = st.columns(4)
    
    inputs = st.session_state.shared_inputs
    
    with m1:
        with card_container():
            st.metric("Sleep Duration", f"{inputs.get('Sleep Duration', 0):.1f}h")
    with m2:
        with card_container():
            st.metric("Heart Rate", f"{inputs.get('Heart Rate', 0)} bpm")
    with m3:
        with card_container():
            st.metric("Stress Level", f"{inputs.get('Stress Level', 0)}/10")
    with m4:
        with card_container():
            st.metric("Physical Activity", f"{inputs.get('Physical Activity Level', 0)} m/day")

    # --- Row 4: Recommendations ---
    with card_container():
        st.subheader("Personalized Recommendations")
        render_recommendations_section()
    
    # Clear all results button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear All Results", key="clear_results_btn"):
        clear_results()






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
