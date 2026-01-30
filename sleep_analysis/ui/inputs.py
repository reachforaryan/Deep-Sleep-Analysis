import streamlit as st
import tempfile
import os

def render_section_header(title, icon=None, description=None):
    """Helper to render consistent section headers"""
    st.markdown("---")
    if icon:
        # Use Streamlit's material icon syntax if available, fallback or use as is
        # Streamlit 1.40+ supports :material/icon_name:
        st.subheader(f"{icon} {title}")
    else:
        st.subheader(title)
        
    if description:
        st.caption(description)

def load_profile_data(profile_type):
    """Load specific profile data into session state"""
    
    profiles = {
        "good": {
            'Gender': "Male", 'Age': 28, 'Occupation': "Athlete",
            'BMI Category': "Normal", 'Physical Activity Level': 90, 'Daily Steps': 12000,
            'Systolic BP': 115, 'Diastolic BP': 75, 'Heart Rate': 55,
            'Sleep Duration': 8.0, 'Quality of Sleep': 9, 'Stress Level': 3,
            'Heart_Rate_Variability': 85.0, 'Movement_During_Sleep': 0.5,
            'Light_Exposure_hours': 2.0, 'Body_Temperature': 36.5,
            'Caffeine_Intake_mg': 50, 'Bedtime_Consistency': 0.95
        },
        "average": {
            'Gender': "Male", 'Age': 35, 'Occupation': "Software Engineer",
            'BMI Category': "Overweight", 'Physical Activity Level': 30, 'Daily Steps': 6000,
            'Systolic BP': 125, 'Diastolic BP': 82, 'Heart Rate': 72,
            'Sleep Duration': 6.5, 'Quality of Sleep': 6, 'Stress Level': 7,
            'Heart_Rate_Variability': 45.0, 'Movement_During_Sleep': 1.8,
            'Light_Exposure_hours': 6.0, 'Body_Temperature': 36.9,
            'Caffeine_Intake_mg': 200, 'Bedtime_Consistency': 0.6
        },
        "poor": {
            'Gender': "Male", 'Age': 45, 'Occupation': "Manager",
            'BMI Category': "Obese", 'Physical Activity Level': 10, 'Daily Steps': 3000,
            'Systolic BP': 145, 'Diastolic BP': 95, 'Heart Rate': 88,
            'Sleep Duration': 4.5, 'Quality of Sleep': 3, 'Stress Level': 9,
            'Heart_Rate_Variability': 20.0, 'Movement_During_Sleep': 4.2,
            'Light_Exposure_hours': 10.0, 'Body_Temperature': 37.2,
            'Caffeine_Intake_mg': 450, 'Bedtime_Consistency': 0.2
        }
    }
    
    # Map data keys to widget keys
    key_mapping = {
        'Gender': 'gender',
        'Age': 'age',
        'Occupation': 'occupation',
        'BMI Category': 'bmi_category',
        'Physical Activity Level': 'physical_activity',
        'Daily Steps': 'daily_steps',
        'Systolic BP': 'systolic_bp',
        'Diastolic BP': 'diastolic_bp',
        'Heart Rate': 'heart_rate',
        'Sleep Duration': 'sleep_duration',
        'Quality of Sleep': 'quality_of_sleep',
        'Stress Level': 'stress_level',
        'Heart_Rate_Variability': 'hrv_quality',
        'Movement_During_Sleep': 'movement_quality',
        'Light_Exposure_hours': 'light_exposure_quality',
        'Body_Temperature': 'body_temp_quality',
        'Caffeine_Intake_mg': 'caffeine_quality',
        'Bedtime_Consistency': 'bedtime_consistency_quality'
    }
    
    if profile_type in profiles:
        data = profiles[profile_type]
        # Update shared inputs
        st.session_state.shared_inputs.update(data)
        
        # Update widget keys explicitly to force UI refresh
        for data_key, widget_key in key_mapping.items():
            if data_key in data:
                st.session_state[widget_key] = data[data_key]
        
        st.rerun()

def render_personal_data_form():
    """Render form for personal and sleep data"""
    # Create a nice card-like container
    with st.container():
        # Quick Fill Buttons
        col_header, col_btns = st.columns([0.4, 0.6])
        with col_header:
            render_section_header("Personal Profile", ":material/person:", "Tell us about yourself.")
        
        with col_btns:
            st.markdown("<div style='height: 25px'></div>", unsafe_allow_html=True) # Spacer
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("🟢 Good", help="Load healthy sleep profile", use_container_width=True):
                    load_profile_data("good")
            with b2:
                if st.button("🟡 Avg", help="Load average sleep profile", use_container_width=True):
                    load_profile_data("average")
            with b3:
                if st.button("🔴 Poor", help="Load unhealthy sleep profile", use_container_width=True):
                    load_profile_data("poor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### **Basic Info**")
            
            gender_options = ["Male", "Female"]
            gender = st.pills("Gender", gender_options, 
                              selection_mode="single",
                              default=st.session_state.shared_inputs.get('Gender', "Male"),
                              key="gender")
            # Handle potential None from pills if deselected
            if not gender: gender = st.session_state.shared_inputs.get('Gender', "Male")
            st.session_state.shared_inputs['Gender'] = gender
            
            age = st.number_input("Age", min_value=18, max_value=100, 
                              value=st.session_state.shared_inputs.get('Age', 30),
                              key="age",
                              help="Age is a key factor in sleep patterns and ideal sleep duration.")
            st.session_state.shared_inputs['Age'] = age
            
            occupation_options = ["Software Engineer", "Doctor", "Sales Representative", "Teacher",
                    "Nurse", "Engineer", "Accountant", "Scientist", "Lawyer",
                    "Salesperson", "Manager"]
            
            # Smart index finding
            current_occ = st.session_state.shared_inputs.get('Occupation', "Software Engineer")
            idx = occupation_options.index(current_occ) if current_occ in occupation_options else 0
            
            occupation = st.selectbox("Occupation", occupation_options,
                                  index=idx,
                                  key="occupation",
                                  help="Work stress and schedule often correlate with sleep quality.")
            st.session_state.shared_inputs['Occupation'] = occupation

        with col2:
            st.markdown("#### **Health Metrics**")
            
            bmi_options = ["Normal", "Overweight", "Obese", "Underweight"]
            bmi_category = st.select_slider("BMI Category", options=bmi_options,
                                    value=st.session_state.shared_inputs.get('BMI Category', "Normal"),
                                    key="bmi_category")
            st.session_state.shared_inputs['BMI Category'] = bmi_category
            
            physical_activity = st.slider("Daily Physical Activity (mins)", 0, 120, 
                                      st.session_state.shared_inputs.get('Physical Activity Level', 30),
                                      key="physical_activity",
                                      help="Regular exercise can improve sleep quality.")
            st.session_state.shared_inputs['Physical Activity Level'] = physical_activity
            
            daily_steps = st.number_input("Daily Steps", min_value=0, max_value=30000, step=500,
                                     value=st.session_state.shared_inputs.get('Daily Steps', 7000),
                                     key="daily_steps")
            st.session_state.shared_inputs['Daily Steps'] = daily_steps

    with st.container():
        st.markdown("") # Spacer
        col1, col2 = st.columns(2)
        with col1: 
             st.markdown("#### **Vitals**")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            systolic = st.number_input("Systolic BP", min_value=90, max_value=200, 
                                  value=st.session_state.shared_inputs.get('Systolic BP', 120),
                                  key="systolic_bp", help="Upper number (mmHg)")
            st.session_state.shared_inputs['Systolic BP'] = systolic
        with c2:
            diastolic = st.number_input("Diastolic BP", min_value=40, max_value=120, 
                                   value=st.session_state.shared_inputs.get('Diastolic BP', 80),
                                   key="diastolic_bp", help="Lower number (mmHg)")
            st.session_state.shared_inputs['Diastolic BP'] = diastolic
        with c3:
            heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, 
                                    value=st.session_state.shared_inputs.get('Heart Rate', 75),
                                    key="heart_rate")
            st.session_state.shared_inputs['Heart Rate'] = heart_rate

    with st.container():
        render_section_header("Sleep Habits", ":material/bed:", "Your typical sleep routine.")
        
        c1, c2 = st.columns(2)
        
        with c1:
            sleep_duration = st.slider("Avg. Sleep Duration (hours)", 3.0, 12.0, 
                                   st.session_state.shared_inputs.get('Sleep Duration', 7.0), 0.1,
                                   key="sleep_duration")
            st.session_state.shared_inputs['Sleep Duration'] = sleep_duration
            
            quality_of_sleep = st.slider("Perceived Quality (1-10)", 1, 10, 
                                     st.session_state.shared_inputs.get('Quality of Sleep', 7),
                                     key="quality_of_sleep", help="How refreshed do you feel?")
            st.session_state.shared_inputs['Quality of Sleep'] = quality_of_sleep
            
        with c2:
            stress_level = st.slider("Stress Level (1-10)", 1, 10, 
                                 st.session_state.shared_inputs.get('Stress Level', 5),
                                 key="stress_level")
            st.session_state.shared_inputs['Stress Level'] = stress_level


def render_physiological_metrics_form():
    """Render form for physiological sleep metrics"""
    render_section_header("Advanced Physiological Metrics", ":material/biotech:", "Data typically measured by wearables.")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("💡 **Sleep Quality Factors**", icon=":material/lightbulb:")
            
            hrv = st.number_input("Heart Rate Variability (ms)", min_value=0.0, max_value=200.0, 
                              value=st.session_state.shared_inputs.get('Heart_Rate_Variability', 70.0),
                              key="hrv_quality",
                              help="Higher HRV generally indicates better recovery.")
            st.session_state.shared_inputs['Heart_Rate_Variability'] = hrv
            
            movement = st.number_input("Movement Index (0-5)", min_value=0.0, max_value=5.0, 
                                  value=st.session_state.shared_inputs.get('Movement_During_Sleep', 1.5),
                                  key="movement_quality", help="0 = Still, 5 = Restless")
            st.session_state.shared_inputs['Movement_During_Sleep'] = movement
            
            light_exposure = st.number_input("Daytime Light Exposure (hours)", min_value=0.0, max_value=24.0, 
                                        value=st.session_state.shared_inputs.get('Light_Exposure_hours', 8.0),
                                        key="light_exposure_quality")
            st.session_state.shared_inputs['Light_Exposure_hours'] = light_exposure
        
        with col2:
            st.info("💡 **Environmental Factors**", icon=":material/thermostat:")
            
            body_temp = st.number_input("Avg Body Temp during Sleep (°C)", min_value=35.0, max_value=40.0, 
                                   value=st.session_state.shared_inputs.get('Body_Temperature', 36.8), 
                                   format="%.1f",
                                   key="body_temp_quality")
            st.session_state.shared_inputs['Body_Temperature'] = body_temp
            
            caffeine = st.number_input("Caffeine Intake (mg)", min_value=0, max_value=1000, 
                                   value=st.session_state.shared_inputs.get('Caffeine_Intake_mg', 100),
                                   key="caffeine_quality", help="Approx 1 coffee = 95mg")
            st.session_state.shared_inputs['Caffeine_Intake_mg'] = caffeine
            
            bedtime_consistency = st.slider("Bedtime Consistency Score", 0.0, 1.0, 
                                       st.session_state.shared_inputs.get('Bedtime_Consistency', 0.7), 0.01,
                                       key="bedtime_consistency_quality",
                                       help="1.0 means you go to bed at the exact same time every night.")
            st.session_state.shared_inputs['Bedtime_Consistency'] = bedtime_consistency

def render_audio_upload():
    """Render file uploader to accept audio"""
    render_section_header("Audio Analysis", ":material/mic:", "Upload sleep recording for snoring detection.")
    
    with st.container():
        # Clean file uploader area
        uploaded_file = st.file_uploader("Upload .wav or .mp3 file", type=["wav", "mp3"], key="audio_uploader")
        
        if uploaded_file is not None:
            st.success("Audio uploaded successfully!")
            # Display audio player with a bit more style
            st.audio(uploaded_file, format="audio/wav")

            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name
            
            # Store path in session state
            st.session_state.temp_audio_path = temp_path

def render_inputs():
    """Orchestrate all input forms"""
    # st.header("Sleep Analysis Input Data") # Removed redundant header if using tabs
    
    render_personal_data_form()
    render_physiological_metrics_form()
    render_audio_upload()

