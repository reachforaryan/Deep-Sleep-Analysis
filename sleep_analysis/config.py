"""
Configuration file for Sleep Pattern Analysis application.
Contains profiles, UI text options, and mappings.
"""

# Sleep Profiles
SLEEP_PROFILES = {
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

# Key Mapping
WIDGET_KEY_MAPPING = {
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

# UI Options
GENDER_OPTIONS = ["Male", "Female"]

OCCUPATION_OPTIONS = [
    "Software Engineer", "Doctor", "Sales Representative", "Teacher",
    "Nurse", "Engineer", "Accountant", "Scientist", "Lawyer",
    "Salesperson", "Manager", "Athlete"
]

BMI_OPTIONS = ["Normal", "Overweight", "Obese", "Underweight"]

# UI Text & Labels
UI_TEXT = {
    "sections": {
        "personal": {
            "title": "Personal Profile",
            "icon": ":material/person:",
            "desc": "Tell us about yourself."
        },
        "habits": {
            "title": "Sleep Habits",
            "icon": ":material/bed:",
            "desc": "Your typical sleep routine."
        },
        "physiological": {
            "title": "Advanced Physiological Metrics",
            "icon": ":material/biotech:",
            "desc": "Data typically measured by wearables."
        },
        "audio": {
            "title": "Audio Analysis",
            "icon": ":material/mic:",
            "desc": "Upload sleep recording for snoring detection."
        }
    },
    "labels": {
        "age": "Age",
        "occupation": "Occupation",
        "sleep_duration": "Avg. Sleep Duration (hours)",
        "quality": "Perceived Quality (1-10)",
        "stress": "Stress Level (1-10)",
        "physical_activity": "Daily Physical Activity (mins)",
        "daily_steps": "Daily Steps",
        "hrv": "Heart Rate Variability (ms)",
        "movement": "Movement Index (0-5)",
        "light_exposure": "Daytime Light Exposure (hours)",
        "body_temp": "Avg Body Temp during Sleep (°C)",
        "caffeine": "Caffeine Intake (mg)",
        "bedtime_consistency": "Bedtime Consistency Score"
    },
    "help": {
        "age": "Age is a key factor in sleep patterns and ideal sleep duration.",
        "occupation": "Work stress and schedule often correlate with sleep quality.",
        "quality": "How refreshed do you feel?",
        "regular_exercise": "Regular exercise can improve sleep quality.",
        "systolic": "Upper number (mmHg)",
        "diastolic": "Lower number (mmHg)",
        "hrv": "Higher HRV generally indicates better recovery.",
        "movement": "0 = Still, 5 = Restless",
        "caffeine": "Approx 1 coffee = 95mg",
        "consistency": "1.0 means you go to bed at the exact same time every night.",
        "good_profile": "Load healthy sleep profile",
        "avg_profile": "Load average sleep profile",
        "poor_profile": "Load unhealthy sleep profile"
    }
}
