import streamlit as st
import pandas as pd
import tempfile
import os
import sys

# Add the current directory to path to ensure we can import the local package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sleep_analysis.analyzer import SleepAnalyzer
from sleep_analysis.ui_components import (
    create_visualization, 
    render_disorder_results, 
    render_quality_results, 
    render_snoring_results, 
    render_recommendations
)

# Streamlit application
def main():
    st.set_page_config(page_title="Comprehensive Sleep Analysis", layout="wide")
    
    st.title("Comprehensive Sleep Analysis")
    
    # Initialize analyzer
    # Using st.cache_resource for the analyzer to avoid reloading models on every rerun
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

    # Create tabs
    tab1, tab2 = st.tabs(["Input Data", "Analysis Results"])
    
    # Variables to store inputs and results
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
    
    #############
    # Tab 1: Input Data (combined personal data and audio)
    #############
    with tab1:
        st.header("Sleep Analysis Input Data")
        
        # Create sections with expanders
        with st.expander("Personal & Sleep Data", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Basic information
                gender_options = ["Male", "Female"]
                gender = st.selectbox("Gender", gender_options, 
                                  index=gender_options.index(st.session_state.shared_inputs.get('Gender', "Male")),
                                  key="gender")
                st.session_state.shared_inputs['Gender'] = gender
                
                age = st.number_input("Age", min_value=18, max_value=100, 
                                  value=st.session_state.shared_inputs.get('Age', 30),
                                  key="age")
                st.session_state.shared_inputs['Age'] = age
                
                # Use the occupation list from the data
                occupation_options = ["Software Engineer", "Doctor", "Sales Representative", "Teacher",
                        "Nurse", "Engineer", "Accountant", "Scientist", "Lawyer",
                        "Salesperson", "Manager"]
                        
                occupation = st.selectbox("Occupation", occupation_options,
                                      index=occupation_options.index(st.session_state.shared_inputs.get('Occupation', "Software Engineer")) if st.session_state.shared_inputs.get('Occupation') in occupation_options else 0,
                                      key="occupation")
                st.session_state.shared_inputs['Occupation'] = occupation
                
                sleep_duration = st.slider("Sleep Duration (hours)", 3.0, 12.0, 
                                       st.session_state.shared_inputs.get('Sleep Duration', 7.0), 0.1,
                                       key="sleep_duration")
                st.session_state.shared_inputs['Sleep Duration'] = sleep_duration
                
                quality_of_sleep = st.slider("Quality of Sleep (1-10)", 1, 10, 
                                         st.session_state.shared_inputs.get('Quality of Sleep', 7),
                                         key="quality_of_sleep")
                st.session_state.shared_inputs['Quality of Sleep'] = quality_of_sleep
                
                stress_level = st.slider("Stress Level (1-10)", 1, 10, 
                                     st.session_state.shared_inputs.get('Stress Level', 5),
                                     key="stress_level")
                st.session_state.shared_inputs['Stress Level'] = stress_level
                
            with col2:
                # Health metrics
                physical_activity = st.slider("Physical Activity Level (minutes/day)", 0, 120, 
                                          st.session_state.shared_inputs.get('Physical Activity Level', 30),
                                          key="physical_activity")
                st.session_state.shared_inputs['Physical Activity Level'] = physical_activity
                
                bmi_options = ["Normal", "Overweight", "Obese", "Underweight"]
                bmi_category = st.selectbox("BMI Category", bmi_options,
                                        index=bmi_options.index(st.session_state.shared_inputs.get('BMI Category', "Normal")),
                                        key="bmi_category")
                st.session_state.shared_inputs['BMI Category'] = bmi_category
                
                # Blood pressure input (systolic/diastolic)
                col2a, col2b = st.columns(2)
                with col2a:
                    systolic = st.number_input("Systolic BP (mmHg)", min_value=90, max_value=200, 
                                          value=st.session_state.shared_inputs.get('Systolic BP', 120),
                                          key="systolic_bp")
                    st.session_state.shared_inputs['Systolic BP'] = systolic
                
                with col2b:
                    diastolic = st.number_input("Diastolic BP (mmHg)", min_value=40, max_value=120, 
                                           value=st.session_state.shared_inputs.get('Diastolic BP', 80),
                                           key="diastolic_bp")
                    st.session_state.shared_inputs['Diastolic BP'] = diastolic
                
                heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, 
                                        value=st.session_state.shared_inputs.get('Heart Rate', 75),
                                        key="heart_rate")
                st.session_state.shared_inputs['Heart Rate'] = heart_rate
                
                daily_steps = st.number_input("Daily Steps", min_value=0, max_value=30000, 
                                         value=st.session_state.shared_inputs.get('Daily Steps', 7000),
                                         key="daily_steps")
                st.session_state.shared_inputs['Daily Steps'] = daily_steps
        
        with st.expander("Physiological Sleep Metrics", expanded=True):
            st.write("Enter your physiological sleep metrics for sleep quality assessment:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Collect input for quality model based on your preprocessing
                hrv = st.number_input("Heart Rate Variability (ms)", min_value=40.0, max_value=120.0, 
                                  value=st.session_state.shared_inputs.get('Heart_Rate_Variability', 70.0),
                                  key="hrv_quality")
                st.session_state.shared_inputs['Heart_Rate_Variability'] = hrv
                
                body_temp = st.number_input("Body Temperature (°C)", min_value=36.0, max_value=38.0, 
                                       value=st.session_state.shared_inputs.get('Body_Temperature', 36.8), 
                                       format="%.1f",
                                       key="body_temp_quality")
                st.session_state.shared_inputs['Body_Temperature'] = body_temp
                
                movement = st.number_input("Movement During Sleep (index)", min_value=0.0, max_value=5.0, 
                                      value=st.session_state.shared_inputs.get('Movement_During_Sleep', 1.5),
                                      key="movement_quality")
                st.session_state.shared_inputs['Movement_During_Sleep'] = movement
            
            with col2:
                caffeine = st.number_input("Caffeine Intake (mg)", min_value=0, max_value=500, 
                                       value=st.session_state.shared_inputs.get('Caffeine_Intake_mg', 100),
                                       key="caffeine_quality")
                st.session_state.shared_inputs['Caffeine_Intake_mg'] = caffeine
                
                bedtime_consistency = st.slider("Bedtime Consistency (0-1)", 0.0, 1.0, 
                                           st.session_state.shared_inputs.get('Bedtime_Consistency', 0.7), 0.01,
                                           key="bedtime_consistency_quality")
                st.session_state.shared_inputs['Bedtime_Consistency'] = bedtime_consistency
                
                light_exposure = st.number_input("Light Exposure (hours)", min_value=0.0, max_value=16.0, 
                                            value=st.session_state.shared_inputs.get('Light_Exposure_hours', 8.0),
                                            key="light_exposure_quality")
                st.session_state.shared_inputs['Light_Exposure_hours'] = light_exposure
        
        with st.expander("Sleep Audio Recording", expanded=True):
            st.write("Upload an audio recording of your sleep to analyze snoring patterns:")
            
            # File uploader
            uploaded_file = st.file_uploader("Choose a sleep audio file", type=["wav", "mp3"], key="audio_uploader")
            
            if uploaded_file is not None:
                # Display audio player
                st.audio(uploaded_file, format="audio/wav")
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_path = tmp_file.name
                
                # Store path in session state
                st.session_state.temp_audio_path = temp_path
        
        # Analysis buttons - centralized
        st.write("### Run Analysis")
        col1, col2, col3 = st.columns(3)
        
        # Button to process sleep disorder prediction
        with col1:
            if st.button("Analyze Sleep Disorder Risk", key="analyze_disorder_btn"):
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
        
        # Button to process sleep quality prediction
        with col2:
            if st.button("Analyze Sleep Quality", key="analyze_quality_btn"):
                # Prepare data for model - using shared inputs where appropriate
                quality_df = pd.DataFrame([{
                    'Heart_Rate_Variability': st.session_state.shared_inputs['Heart_Rate_Variability'],
                    'Body_Temperature': st.session_state.shared_inputs['Body_Temperature'],
                    'Movement_During_Sleep': st.session_state.shared_inputs['Movement_During_Sleep'],
                    'Sleep_Duration': st.session_state.shared_inputs['Sleep Duration'],  # Using shared input
                    'Caffeine_Intake_mg': st.session_state.shared_inputs['Caffeine_Intake_mg'],
                    'Stress_Level': st.session_state.shared_inputs['Stress Level'],  # Using shared input
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
        
        # Button for audio analysis
        with col3:
            if 'temp_audio_path' in st.session_state:
                if st.button("Analyze Audio Recording", key="analyze_audio_btn"):
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
            else:
                st.button("Analyze Audio Recording", disabled=True, key="analyze_audio_btn_disabled")
                st.info("Upload an audio file first")
        
        # Run all analyses at once
        if st.button("Complete Full Analysis", key="full_analysis_btn", type="primary"):
            # Check if audio file is available
            has_audio = 'temp_audio_path' in st.session_state
            
            with st.spinner("Running comprehensive sleep analysis..."):
                # 1. Sleep disorder prediction
                disorder_input = pd.DataFrame([{
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
                }])
                
                st.session_state.disorder_results = analyzer.predict_sleep_disorder(disorder_input)
                
            
                # 2. Sleep quality prediction
                quality_input = pd.DataFrame([{
                    'Heart_Rate_Variability': st.session_state.shared_inputs['Heart_Rate_Variability'],
                    'Body_Temperature': st.session_state.shared_inputs['Body_Temperature'],
                    'Movement_During_Sleep': st.session_state.shared_inputs['Movement_During_Sleep'],
                    'Sleep_Duration': st.session_state.shared_inputs['Sleep Duration'],
                    'Caffeine_Intake_mg': st.session_state.shared_inputs['Caffeine_Intake_mg'],
                    'Stress_Level': st.session_state.shared_inputs['Stress Level'],
                    'Bedtime_Consistency': st.session_state.shared_inputs['Bedtime_Consistency'],
                    'Light_Exposure_hours': st.session_state.shared_inputs['Light_Exposure_hours']
                }])
                
                st.session_state.quality_results = analyzer.predict_sleep_quality(quality_input)
                
                # 3. Audio analysis if audio file available
                if has_audio:
                    # Define progress callback
                    progress_bar = st.progress(0)
                    def update_progress(p):
                         progress_bar.progress(p)
                         
                    st.session_state.audio_results = analyzer.analyze_audio(
                        st.session_state.temp_audio_path,
                        progress_callback=update_progress
                    )
                    progress_bar.empty()
                    
                    if st.session_state.audio_results:
                        # Create visualization
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
    
    #############
    # Tab 2: Results & Recommendations
    #############
    with tab2:
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
        
        # Display results in expandable sections using UI components
        with st.expander("Sleep Disorder Analysis", expanded=True):
            render_disorder_results(st.session_state.disorder_results, st.session_state.shared_inputs)
        
        with st.expander("Sleep Quality Analysis", expanded=True):
            render_quality_results(st.session_state.quality_results, st.session_state.shared_inputs)
        
        with st.expander("Snoring Analysis", expanded=True):
            render_snoring_results(st.session_state.audio_results, st.session_state.get('audio_fig'))
        
        # Display comprehensive recommendations
        with st.expander("Personalized Sleep Recommendations", expanded=True):
            render_recommendations(st.session_state.combined_suggestions)
        
        # Clear all results button
        if st.button("Clear All Results", key="clear_results_btn"):
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

if __name__ == "__main__":
    main()