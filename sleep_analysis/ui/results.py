import streamlit as st
import pandas as pd
import os
from .visualizations import render_disorder_chart, render_snoring_results
from .styling import apply_custom_css, card_container


def render_metric_card(label, value, sub_value=None, status="neutral", icon=None):
    """Helper to render a styled metric card using HTML"""
    color = "#ffffff"
    if status == "good": color = "#4ade80"
    elif status == "warning": color = "#fbbf24"
    elif status == "bad": color = "#f87171"
    
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 8px;">{icon}</span>' if icon else ""
    sub_html = f'<div style="font-size: 0.8rem; color: #888; margin-top: 4px;">{sub_value}</div>' if sub_value else ""
    
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color}">{icon_html}{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def render_results_tab(analyzer):
    """Orchestrate the rendering of all results"""
    
    # Check if any analysis has been done
    if not st.session_state.disorder_results and not st.session_state.quality_results and not st.session_state.audio_results:
        st.info("No analysis results available yet. Complete at least one analysis in the Input Data tab.")
        return
    
    # Generate comprehensive suggestions if they don't exist but we have results
    if (st.session_state.disorder_results or st.session_state.quality_results or st.session_state.audio_results) and not st.session_state.combined_suggestions:
        st.session_state.combined_suggestions = analyzer.generate_suggestions(
            st.session_state.audio_results,
            st.session_state.disorder_results,
            st.session_state.quality_results,
            st.session_state.shared_inputs
        )
    
    # Apply CSS
    apply_custom_css()
    
    st.markdown('<h1 class="gradient-text">Your Sleep Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- HERO ROW: The Big Numbers ---
    col1, col2, col3 = st.columns(3)
    
    # 1. Main Disorder Prediction
    with col1:
        if st.session_state.disorder_results:
            disorder = st.session_state.disorder_results['prediction']
            status = "good"
            if disorder == "Insomnia": status = "warning"
            elif disorder == "Sleep Apnea": status = "bad"
            
            # Get probability confidence
            conf_msg = ""
            if 'probabilities' in st.session_state.disorder_results:
                     probs = st.session_state.disorder_results['probabilities']
                     max_p = probs.get(disorder, 0) * 100
                     conf_msg = f"{max_p:.1f}% Confidence Model"

            render_metric_card("Primary Assessment", disorder, conf_msg, status, icon="🏥")
        else:
            render_metric_card("Primary Assessment", "Pending", "Run analysis to see", "neutral")

    # 2. Sleep Quality Score
    with col2:
        if st.session_state.quality_results:
            score = st.session_state.quality_results['score']
            # Using the new gauge visualization
            with card_container():
                from .visualizations import render_gauge_chart
                render_gauge_chart(score)
        else:
            render_metric_card("Sleep Quality", "Pending", "Run analysis to see", "neutral")
        
    # 3. Snoring Severity
    with col3:
        if st.session_state.audio_results:
            res = st.session_state.audio_results
            pct = res['snoring_percentage']
            status = "good"
            if pct > 50: status = "bad"
            elif pct > 30: status = "warning"
            
            duration_mins = res['total_snoring_duration']/60
            render_metric_card("Snoring Load", f"{pct:.1f}%", f"{duration_mins:.1f} mins detected", status, icon="😴")
        else:
             render_metric_card("Snoring Load", "N/A", "Upload audio to analyze", "neutral")

    # --- ROW 2: VISUALIZATIONS ---
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Using a 2/3 + 1/3 split for charts
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader(":material/show_chart: Audio Timeline")
        with card_container():
            if st.session_state.audio_results:
                 render_snoring_results(st.session_state.audio_results, st.session_state.get('audio_fig'))
            else:
                 st.info("Additional audio insights will appear here.")
    
    with c_right:
        st.subheader(":material/pie_chart: Risk Factors")
        with card_container():
            if st.session_state.disorder_results:
                render_disorder_chart(st.session_state.disorder_results)
            else:
                st.info("Risk distribution will appear here.")
    
    # --- ROW 3: Vitals Grid ---
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.subheader(":material/ecg_heart: Physiological Vitals")
    
    inputs = st.session_state.shared_inputs
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric(":material/schedule: Duration", f"{inputs.get('Sleep Duration', 0):.1f}h")
    with m2:
        st.metric(":material/favorite: Heart Rate", f"{inputs.get('Heart Rate', 0)} bpm")
    with m3:
         st.metric(":material/psychology: Stress", f"{inputs.get('Stress Level', 0)}/10")
    with m4:
         st.metric(":material/directions_run: Activity", f"{inputs.get('Physical Activity Level', 0)} min")

    # --- ROW 4: AI Insights & Recs ---
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    with st.expander("✨ AI & Recommendations", expanded=True, icon=":material/lightbulb:"):
         # 1. Base Recommendations
         render_recommendations_section()
         
         st.markdown("---")
         st.markdown("### :material/smart_toy: AI Coach Analysis")
         
         # API Key Logic reused
         api_key = None
         if "GEMINI_API_KEY" in st.secrets:
             api_key = st.secrets["GEMINI_API_KEY"]
         else:
             api_key = st.text_input("Enter Gemini API Key", type="password")
             
         if st.button("Generate Deep Dive Insight", type="primary", disabled=not api_key, use_container_width=True):
             with st.spinner("Analyzing complex patterns..."):
                  insight = analyzer.generate_ai_insight(
                       api_key, 
                       st.session_state.shared_inputs,
                       {
                           'disorder_results': st.session_state.disorder_results,
                           'quality_results': st.session_state.quality_results,
                           'audio_results': st.session_state.audio_results
                       }
                  )
                  st.success("Insight Generated!")
                  st.markdown(insight)

    # Footer Action
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear Dashboard", type="secondary"):
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
