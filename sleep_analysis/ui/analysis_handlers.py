import streamlit as st
import pandas as pd
from .visualizations import create_visualization

def render_analysis_buttons(analyzer):
    """Render buttons to trigger different analyses"""
    st.markdown("### Actions")
    
    # Primary Action
    if st.button("Run Full Analysis", icon=":material/rocket_launch:", key="full_analysis_btn", type="primary", use_container_width=True):
        run_full_analysis(analyzer)
        return True

    with st.expander("Component Analysis"):
        if st.button("Analyze Disorder Risk Only", key="analyze_disorder_btn", use_container_width=True):
            analyze_disorder(analyzer)
            return True
    
        if st.button("Analyze Quality Only", key="analyze_quality_btn", use_container_width=True):
            analyze_quality(analyzer)
            return True
    
        if 'temp_audio_path' in st.session_state:
            if st.button("Analyze Audio Only", key="analyze_audio_btn", use_container_width=True):
                analyze_audio(analyzer)
                return True
        else:
            st.button("Analyze Audio Only", disabled=True, key="analyze_audio_btn_disabled", use_container_width=True)
            
    return False

def analyze_disorder(analyzer):
    """Run sleep disorder analysis"""
    # Prepare data for model
    input_dict = {
        'Age': st.session_state.shared_inputs['Age'],
        'Gender': st.session_state.shared_inputs['Gender'],
        'Sleep Duration': st.session_state.shared_inputs['Sleep Duration'],
        'Quality of Sleep': st.session_state.shared_inputs['Quality of Sleep'],
        'Physical Activity Level': st.session_state.shared_inputs['Physical Activity Level'],
        'Stress Level': st.session_state.shared_inputs['Stress Level'],
        'BMI Category': st.session_state.shared_inputs['BMI Category'],
        'Heart Rate': st.session_state.shared_inputs['Heart Rate'],
        'Daily Steps': st.session_state.shared_inputs['Daily Steps'],
        'Systolic BP': st.session_state.shared_inputs['Systolic BP'],
        'Diastolic BP': st.session_state.shared_inputs['Diastolic BP'],
        'Occupation': st.session_state.shared_inputs['Occupation']
    }
    
    # Convert to DataFrame
    df = pd.DataFrame([input_dict])
    
    # Make prediction
    with st.spinner("Analyzing sleep disorder risk..."):
        result = analyzer.predict_sleep_disorder(df)
        st.session_state.disorder_results = result
        
        if st.session_state.disorder_results:
            st.success("Sleep disorder analysis complete! Check the Results tab.")
        else:
            st.error("Failed to analyze sleep disorder. Please check logs.")

def analyze_quality(analyzer):
    """Run sleep quality analysis"""
    # Prepare data for model
    quality_df = pd.DataFrame([{
        'Heart_Rate_Variability': st.session_state.shared_inputs['Heart_Rate_Variability'],
        'Body_Temperature': st.session_state.shared_inputs['Body_Temperature'],
        'Movement_During_Sleep': st.session_state.shared_inputs['Movement_During_Sleep'],
        'Sleep_Duration': st.session_state.shared_inputs['Sleep Duration'],
        'Caffeine_Intake_mg': st.session_state.shared_inputs['Caffeine_Intake_mg'],
        'Stress_Level': st.session_state.shared_inputs['Stress Level'],
        'Bedtime_Consistency': st.session_state.shared_inputs['Bedtime_Consistency'],
        'Light_Exposure_hours': st.session_state.shared_inputs['Light_Exposure_hours']
    }])
    
    # Make prediction
    with st.spinner("Analyzing sleep quality..."):
        result = analyzer.predict_sleep_quality(quality_df)
        st.session_state.quality_results = result
        
        if st.session_state.quality_results:
            st.success("Sleep quality analysis complete! Check the Results tab.")
        else:
            st.error("Failed to analyze sleep quality. Please check logs.")

def analyze_audio(analyzer):
    """Run sleep audio analysis"""
    with st.spinner("Analyzing sleep audio... This may take several minutes for long recordings."):
        # Define progress callback
        progress_bar = st.progress(0)
        def update_progress(p):
            progress_bar.progress(p)
        
        # Process audio
        result = analyzer.analyze_audio(
            st.session_state.temp_audio_path, 
            progress_callback=update_progress
        )
        st.session_state.audio_results = result
        progress_bar.empty()
        
        if st.session_state.audio_results:
            # Create visualization
            fig = create_visualization(st.session_state.temp_audio_path, st.session_state.audio_results)
            if fig:
                st.session_state.audio_fig = fig
            
            st.success("Audio analysis complete! Check the Results tab.")
        else:
            st.error("Failed to analyze audio. Please check logs.")

def run_full_analysis(analyzer):
    """Run all analyses sequentially"""
    # Check if audio file is available
    has_audio = 'temp_audio_path' in st.session_state
    
    with st.spinner("Running comprehensive sleep analysis..."):
        # 1. Sleep disorder
        analyze_disorder(analyzer)
        
        # 2. Sleep quality
        analyze_quality(analyzer)
        
        # 3. Audio analysis if available
        if has_audio:
            # We need to call the internal logic of analyze_audio but adapt it to not re-create spinners/success messages
            # Or we can just call the method directly to reuse code, but suppress individual success messages?
            # For simplicity, let's reuse the logic blocks by extracting them if needed, but here I'll just
            # call the analyzer directly to have cleaner flow without multiple spinners.
            
            # Re-implementing simplified version to avoid UI clutter
            progress_bar = st.progress(0)
            def update_progress(p):
                    progress_bar.progress(p)
                    
            st.session_state.audio_results = analyzer.analyze_audio(
                st.session_state.temp_audio_path,
                progress_callback=update_progress
            )
            progress_bar.empty()
            
            if st.session_state.audio_results:
                fig = create_visualization(st.session_state.temp_audio_path, st.session_state.audio_results)
                if fig:
                    st.session_state.audio_fig = fig
        
        # Generate comprehensive suggestions
        st.session_state.combined_suggestions = analyzer.generate_suggestions(
            st.session_state.audio_results,
            st.session_state.disorder_results,
            st.session_state.quality_results
        )
        
        st.success("Comprehensive analysis complete! Check the Results tab.")
