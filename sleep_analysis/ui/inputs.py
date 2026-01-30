import streamlit as st
import tempfile
import os

def render_personal_data_form():
    """Render form for personal and sleep data"""
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

def render_physiological_metrics_form():
    """Render form for physiological sleep metrics"""
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

def render_audio_upload():
    """Render file uploader to accept audio"""
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

def render_inputs():
    """Orchestrate all input forms"""
    st.header("Sleep Analysis Input Data")
    render_personal_data_form()
    render_physiological_metrics_form()
    render_audio_upload()
