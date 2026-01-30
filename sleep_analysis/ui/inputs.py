import streamlit as st
import tempfile
import sleep_analysis.config as config



def load_profile_data(profile_type):
    """Load specific profile data into session state"""
    
    profiles = config.SLEEP_PROFILES
    
    if profile_type in profiles:
        data = profiles[profile_type]
        # Update shared inputs
        st.session_state.shared_inputs.update(data)
        
        # Update widget keys explicitly to force UI refresh
        for data_key, widget_key in config.WIDGET_KEY_MAPPING.items():
            if data_key in data:
                st.session_state[widget_key] = data[data_key]
        
        st.rerun()

def render_personal_data_form():
    """Render form for personal and sleep data"""
    ui = config.UI_TEXT
    
    # 1. Profile Loaders (Always visible at top)
    st.markdown("### Quick Load Profile")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Good", icon=":material/thumb_up:", help=ui["help"]["good_profile"], use_container_width=True):
            load_profile_data("good")
    with b2:
        if st.button("Avg", icon=":material/sentiment_neutral:", help=ui["help"]["avg_profile"], use_container_width=True):
            load_profile_data("average")
    with b3:
        if st.button("Poor", icon=":material/thumb_down:", help=ui["help"]["poor_profile"], use_container_width=True):
            load_profile_data("poor")

    # 2. Personal Info (Expander)
    with st.expander("Personal Info", icon=":material/person:", expanded=True):
        gender_options = config.GENDER_OPTIONS
        gender = st.pills("Gender", gender_options, 
                            selection_mode="single",
                            default=st.session_state.shared_inputs.get('Gender', "Male"),
                            key="gender")
        if not gender: gender = st.session_state.shared_inputs.get('Gender', "Male")
        st.session_state.shared_inputs['Gender'] = gender
        
        age = st.number_input(ui["labels"]["age"], min_value=18, max_value=100, 
                            value=st.session_state.shared_inputs.get('Age', 30),
                            key="age",
                            help=ui["help"]["age"])
        st.session_state.shared_inputs['Age'] = age
        
        occupation_options = config.OCCUPATION_OPTIONS
        current_occ = st.session_state.shared_inputs.get('Occupation', "Software Engineer")
        idx = occupation_options.index(current_occ) if current_occ in occupation_options else 0
        occupation = st.selectbox(ui["labels"]["occupation"], occupation_options,
                                index=idx,
                                key="occupation",
                                help=ui["help"]["occupation"])
        st.session_state.shared_inputs['Occupation'] = occupation

    # 3. Health & Vitals (Expander)
    with st.expander("Health & Vitals", icon=":material/favorite:", expanded=False):
        bmi_options = config.BMI_OPTIONS
        bmi_category = st.select_slider("BMI", options=bmi_options,
                                value=st.session_state.shared_inputs.get('BMI Category', "Normal"),
                                key="bmi_category")
        st.session_state.shared_inputs['BMI Category'] = bmi_category
        
        # Vitals - stacked or 2 cols
        c1, c2 = st.columns(2)
        with c1:
            systolic = st.number_input("Sys BP", min_value=90, max_value=200, 
                                    value=st.session_state.shared_inputs.get('Systolic BP', 120),
                                    key="systolic_bp")
            st.session_state.shared_inputs['Systolic BP'] = systolic
        with c2:
            diastolic = st.number_input("Dia BP", min_value=40, max_value=120, 
                                    value=st.session_state.shared_inputs.get('Diastolic BP', 80),
                                    key="diastolic_bp")
            st.session_state.shared_inputs['Diastolic BP'] = diastolic
            
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, 
                                value=st.session_state.shared_inputs.get('Heart Rate', 75),
                                key="heart_rate")
        st.session_state.shared_inputs['Heart Rate'] = heart_rate
        
        physical_activity = st.slider("Activity (mins/day)", 0, 120, 
                                    st.session_state.shared_inputs.get('Physical Activity Level', 30),
                                    key="physical_activity",
                                    help=ui["help"]["regular_exercise"])
        st.session_state.shared_inputs['Physical Activity Level'] = physical_activity
        
        daily_steps = st.number_input("Daily Steps", min_value=0, max_value=30000, step=500,
                                    value=st.session_state.shared_inputs.get('Daily Steps', 7000),
                                    key="daily_steps")
        st.session_state.shared_inputs['Daily Steps'] = daily_steps

    # 4. Sleep Habits (Expander)
    with st.expander("Sleep Habits", icon=":material/bed:", expanded=True):
        sleep_duration = st.slider("Duration (hours)", 3.0, 12.0, 
                                st.session_state.shared_inputs.get('Sleep Duration', 7.0), 0.1,
                                key="sleep_duration")
        st.session_state.shared_inputs['Sleep Duration'] = sleep_duration
        
        quality_of_sleep = st.slider("Quality (1-10)", 1, 10, 
                                    st.session_state.shared_inputs.get('Quality of Sleep', 7),
                                    key="quality_of_sleep")
        st.session_state.shared_inputs['Quality of Sleep'] = quality_of_sleep
        
        stress_level = st.slider("Stress (1-10)", 1, 10, 
                                st.session_state.shared_inputs.get('Stress Level', 5),
                                key="stress_level")
        st.session_state.shared_inputs['Stress Level'] = stress_level


def render_physiological_metrics_form():
    """Render form for physiological sleep metrics"""
    ui = config.UI_TEXT
    
    with st.expander("Adv. Metrics", icon=":material/biotech:", expanded=False):
        st.caption("Wearable device data")
        
        hrv = st.number_input("HRV (ms)", min_value=0.0, max_value=200.0, 
                            value=st.session_state.shared_inputs.get('Heart_Rate_Variability', 70.0),
                            key="hrv_quality",
                            help=ui["help"]["hrv"])
        st.session_state.shared_inputs['Heart_Rate_Variability'] = hrv
        
        movement = st.number_input("Movement (0-5)", min_value=0.0, max_value=5.0, 
                                value=st.session_state.shared_inputs.get('Movement_During_Sleep', 1.5),
                                key="movement_quality")
        st.session_state.shared_inputs['Movement_During_Sleep'] = movement
        
        body_temp = st.number_input("Body Temp (°C)", min_value=35.0, max_value=40.0, 
                                value=st.session_state.shared_inputs.get('Body_Temperature', 36.8), 
                                format="%.1f",
                                key="body_temp_quality")
        st.session_state.shared_inputs['Body_Temperature'] = body_temp
        
        light_exposure = st.number_input("Light Exposure (hrs)", min_value=0.0, max_value=24.0, 
                                    value=st.session_state.shared_inputs.get('Light_Exposure_hours', 8.0),
                                    key="light_exposure_quality")
        st.session_state.shared_inputs['Light_Exposure_hours'] = light_exposure
        
        caffeine = st.number_input("Caffeine (mg)", min_value=0, max_value=1000, 
                                value=st.session_state.shared_inputs.get('Caffeine_Intake_mg', 100),
                                key="caffeine_quality")
        st.session_state.shared_inputs['Caffeine_Intake_mg'] = caffeine
        
        bedtime_consistency = st.slider("Consistency Score", 0.0, 1.0, 
                                    st.session_state.shared_inputs.get('Bedtime_Consistency', 0.7), 0.01,
                                    key="bedtime_consistency_quality")
        st.session_state.shared_inputs['Bedtime_Consistency'] = bedtime_consistency

def render_audio_upload():
    """Render file uploader to accept audio"""
    
    with st.expander("Audio Upload", icon=":material/mic:", expanded=True):
        # Clean file uploader area
        uploaded_file = st.file_uploader("Upload .wav/.mp3", type=["wav", "mp3"], key="audio_uploader")
        
        if uploaded_file is not None:
            st.success("Uploaded!")
            st.audio(uploaded_file, format="audio/wav")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name
            
            # Store path in session state
            st.session_state.temp_audio_path = temp_path

def render_inputs():
    """Orchestrate all input forms"""
    render_personal_data_form()
    render_physiological_metrics_form()
    render_audio_upload()
