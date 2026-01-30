import streamlit as st
import pandas as pd
import os
import json
from .visualizations import render_disorder_chart, render_snoring_results
from .styling import apply_custom_css, card_container


def render_metric_card(label, value, sub_value=None, status="neutral", icon=None):
    """Helper to render a styled metric card using HTML"""
    color = "#ffffff"
    if status == "good": color = "#4ade80"
    elif status == "warning": color = "#fbbf24"
    elif status == "bad": color = "#f87171"
    
    # Clean icon string if it comes in format :material/icon_name:
    clean_icon = icon
    if icon and ":material/" in icon:
        clean_icon = icon.replace(":material/", "").replace(":", "")
    
    # Use the Google Font class we injected in styling.py
    icon_html = f'<span class="material-symbols-rounded">{clean_icon}</span>' if clean_icon else ""
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

            render_metric_card("Primary Assessment", disorder, conf_msg, status, icon="local_hospital")
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
            render_metric_card("Snoring Load", f"{pct:.1f}%", f"{duration_mins:.1f} mins detected", status, icon="graphic_eq")
        else:
             render_metric_card("Snoring Load", "N/A", "Upload audio to analyze", "neutral")

    # --- ROW 2: UNIFIED DIAGNOSTIC SUITE ---
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    st.subheader(":material/ecg_heart: Synchronized Signal Diagnosis")
    with card_container():
        if st.session_state.audio_results:
             from .visualizations import create_unified_dashboard
             
             # View Mode Toggle
             c_title, c_toggle = st.columns([0.7, 0.3])
             with c_title:
                 st.caption("Synchronized view of Audio, Heart Rate, and Snoring Probability.")
             with c_toggle:
                 view_mode = st.radio("Signal Mode", ["Waveform", "Spectrogram"], horizontal=True, label_visibility="collapsed")

             # Create and display the unified dashboard
             unified_fig = create_unified_dashboard(
                 st.session_state.temp_audio_path, 
                 st.session_state.audio_results, 
                 st.session_state.shared_inputs,
                 view_mode=view_mode
             )
             
             if unified_fig:
                 st.plotly_chart(unified_fig, use_container_width=True, config={'displayModeBar': False})
        else:
             st.info("Upload audio to see the unified diagnostic view.")
    
    # --- ROW 3: Risk Factors & Feature Importance ---
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    col_risk, col_vitals = st.columns([1, 2])
    
    with col_risk:
        st.subheader(":material/pie_chart: Risk Distribution")
        with card_container():
            if st.session_state.disorder_results:
                render_disorder_chart(st.session_state.disorder_results)
            else:
                st.info("Risk distribution will appear here.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(":material/bar_chart: Key Drivers")
        with card_container():
             # Feature Importance / Normalized Input Visualization (The "Logic")
             # Normalize current inputs against standard ranges to show what's "high" or "low"
             
             inputs = st.session_state.shared_inputs
             
             # Simple normalization for display: (Value - Min) / (Max - Min)
             # Ranges based on config or typical medical ranges
             features_norm = {
                 'HR': (inputs.get('Heart Rate', 70) - 40) / (120 - 40),
                 'Stress': (inputs.get('Stress Level', 5) - 0) / (10 - 0),
                 'BMI': 0.5, # Placeholder, need real BMI calc if possible or map category
                 'Sleep': (inputs.get('Sleep Duration', 7) - 3) / (12 - 3),
                 'Activity': (inputs.get('Physical Activity Level', 30) - 0) / (120 - 0)
             }
             
             # Adjust BMI manually for viz
             bmi_cat = inputs.get('BMI Category', "Normal")
             if bmi_cat == "Normal": features_norm['BMI'] = 0.3
             elif bmi_cat == "Overweight": features_norm['BMI'] = 0.6
             elif bmi_cat == "Obese": features_norm['BMI'] = 0.9
             
             # Create DataFrame
             feat_df = pd.DataFrame({
                 'Feature': features_norm.keys(),
                 'Normalized Intensity': features_norm.values()
             })
             
             st.bar_chart(feat_df.set_index('Feature'), color="#4facfe", height=200)
             st.caption("Normalized feature intensity contributing to prediction.")

    # --- ROW 3b: Vitals Grid with Deltas ---
    # Moved to right column for better density
    with col_vitals:
        st.subheader(":material/monitor_heart: Physiological Metrics (vs Avg)")
        
        # Calculate Delta Metrics
        import sleep_analysis.config as config
        baseline = config.SLEEP_PROFILES['average']
        
        def calculate_delta(key, current_val, unit=""):
            base_val = baseline.get(key, current_val)
            if base_val == 0: return ""
            delta = ((current_val - base_val) / base_val) * 100
            
            arrow = "↑" if delta > 0 else "↓"
            color = "#f87171" if delta > 10 or delta < -10 else "#4ade80" # Red if variance > 10%
            
            # Contextual logic: More sleep is good, high stress is bad
            if key in ['Sleep Duration', 'Physical Activity Level']:
                 color = "#4ade80" if delta > 0 else "#f87171"
            elif key in ['Heart Rate', 'Stress Level', 'BMI']:
                 color = "#f87171" if delta > 0 else "#4ade80"
                 
            return f'<span style="color:{color}; font-size: 0.8em;">{arrow} {abs(delta):.0f}%</span>'

        m1, m2 = st.columns(2)
        with m1:
             val = inputs.get('Sleep Duration', 0)
             delta = calculate_delta('Sleep Duration', val)
             render_metric_card("Duration", f"{val:.1f}h", delta, "neutral", icon="schedule")
             
             val = inputs.get('Heart Rate', 0)
             delta = calculate_delta('Heart Rate', val)
             render_metric_card("Heart Rate", f"{val} bpm", delta, "neutral", icon="favorite")
             
        with m2:
             val = inputs.get('Stress Level', 0)
             delta = calculate_delta('Stress Level', val)
             render_metric_card("Stress", f"{val}/10", delta, "neutral", icon="psychology")
             
             val = inputs.get('Physical Activity Level', 0)
             delta = calculate_delta('Physical Activity Level', val)
             render_metric_card("Activity", f"{val} min", delta, "neutral", icon="directions_run")

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
                  raw_response = analyzer.generate_ai_insight(
                       api_key, 
                       st.session_state.shared_inputs,
                       {
                           'disorder_results': st.session_state.disorder_results,
                           'quality_results': st.session_state.quality_results,
                           'audio_results': st.session_state.audio_results
                       }
                  )
                  
                  try:
                      # Parse JSON
                      # cleaning potential markdown code blocks if gemini disobeys
                      clean_json = raw_response.replace("```json", "").replace("```", "").strip()
                      insight_data = json.loads(clean_json)
                      
                      st.success("Analysis Complete")
                      
                      # structured UI
                      st.markdown(f"**Assessment:** {insight_data.get('summary', 'No summary provided.')}")
                      
                      c1, c2 = st.columns(2)
                      with c1:
                          st.markdown("##### :material/warning: Risk Correlations")
                          for risk in insight_data.get('risk_factors', []):
                              st.warning(risk, icon=":material/warning_amber:")
                              
                      with c2:
                          st.markdown("##### :material/shield: Corrective Actions")
                          for action in insight_data.get('action_items', []):
                              st.info(action, icon=":material/check_circle:")
                              
                      if insight_data.get('urgency'):
                          st.caption(f"**Medical Note**: {insight_data['urgency']}")
                          
                  except json.JSONDecodeError:
                      st.warning("Could not parse AI response as structured data. Showing raw text:")
                      st.markdown(raw_response)

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
