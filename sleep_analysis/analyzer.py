import numpy as np
import pandas as pd
import librosa
from sklearn.preprocessing import StandardScaler
import os
import pickle
from tensorflow.keras.models import load_model
import warnings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')

class SleepAnalyzer:
    def __init__(self, 
             audio_model_path='models/sleep_audio_model.h5',
             disorder_model_path='models/sleep_disorder_model.pkl',
             quality_model_path='models/sleep_quality_model.pkl'):
        """Initialize comprehensive sleep analyzer with pre-trained models"""
        # Load audio model
        try:
            self.audio_model = load_model(audio_model_path)
            self.audio_model_loaded = True
        except Exception as e:
            logger.warning(f"Could not load audio model: {e}")
            self.audio_model_loaded = False
        
        # Load disorder prediction model
        try:
            with open(disorder_model_path, 'rb') as f:
                self.disorder_model = pickle.load(f)
            self.disorder_model_loaded = True
        except Exception as e:
            logger.warning(f"Could not load sleep disorder model: {e}")
            self.disorder_model_loaded = False
        
        # Load quality prediction model
        try:
            with open(quality_model_path, 'rb') as f:
                self.quality_model = pickle.load(f)
            self.quality_model_loaded = True
        except Exception as e:
            logger.warning(f"Could not load sleep quality model: {e}")
            self.quality_model_loaded = False
        
        # Set audio parameters
        self.sr = 8000
        self.n_mfcc = 13
        
        # Initialize scalers for preprocessing
        self.disorder_scaler = StandardScaler()
        self.quality_scaler = StandardScaler()
    
    def extract_features(self, audio_data):
        """Extract MFCC features from audio segment"""
        try:
            # Ensure consistent length
            segment_samples = self.sr  # 1 second
            if len(audio_data) < segment_samples:
                audio_data = np.pad(audio_data, (0, segment_samples - len(audio_data)), 'constant')
            else:
                audio_data = audio_data[:segment_samples]
            
            # Extract MFCCs
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sr, n_mfcc=self.n_mfcc)
            
            return mfccs
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    def analyze_audio(self, audio_path, segment_duration=30, progress_callback=None):
        """
        Analyze a sleep audio recording
        
        Args:
            audio_path: Path to audio file
            segment_duration: Duration of segments to analyze in seconds
            progress_callback: Optional function that accepts a float (0.0 to 1.0) for progress
        """
        if not self.audio_model_loaded:
            logger.error("Audio model not loaded. Cannot analyze audio.")
            return None
        
        try:
            # Load audio
            y, _ = librosa.load(audio_path, sr=self.sr)
            
            # Calculate total duration
            total_duration_seconds = len(y) / self.sr
            total_duration_minutes = total_duration_seconds / 60
            
            logger.info(f"Analyzing audio: {total_duration_minutes:.2f} minutes duration")
            
            # For very short recordings, adjust segment duration
            if total_duration_seconds < segment_duration:
                segment_duration = max(1, total_duration_seconds)  # Use at least 1 second
                logger.info(f"Short recording detected. Adjusting segment duration to {segment_duration} seconds")
            
            # Split into segments
            segment_samples = int(self.sr * segment_duration)
            n_segments = max(1, int(np.ceil(len(y) / segment_samples)))
            
            # Initialize variables
            snoring_segments = []
            snoring_confidences = []
            
            # Process each segment
            for i in range(n_segments):
                # Extract segment
                start_sample = i * segment_samples
                end_sample = min(start_sample + segment_samples, len(y))
                segment = y[start_sample:end_sample]
                
                # Calculate segment times
                segment_start_time = start_sample / self.sr
                segment_end_time = end_sample / self.sr
                
                # Split into 1-second sub-segments
                sub_segment_length = self.sr  # 1 second of samples
                n_sub_segments = max(1, int(np.ceil(len(segment) / sub_segment_length)))
                
                # Count snoring in sub-segments
                sub_segment_snoring_count = 0
                sub_segment_confidences = []
                
                for j in range(n_sub_segments):
                    # Extract sub-segment
                    sub_start = j * sub_segment_length
                    sub_end = min(sub_start + sub_segment_length, len(segment))
                    sub_segment = segment[sub_start:sub_end]
                    
                    # Skip if too short - reduced threshold for short recordings
                    min_length = 0.3 * self.sr  # 300ms minimum
                    if len(sub_segment) < min_length:
                        continue
                    
                    try:
                        # Extract features
                        mfccs = self.extract_features(sub_segment)
                        
                        if mfccs is None or mfccs.size == 0:
                            continue
                        
                        # Prepare for model input
                        mfccs = mfccs[np.newaxis, ..., np.newaxis]
                        
                        # Make prediction
                        pred = self.audio_model.predict(mfccs, verbose=0)[0]
                        pred_class = np.argmax(pred)
                        confidence = pred[pred_class]
                        
                        # If snoring detected
                        if pred_class == 1:  # 1 = snoring
                            sub_segment_snoring_count += 1
                            sub_segment_confidences.append(float(confidence))
                    
                    except Exception as sub_error:
                        logger.warning(f"Error processing sub-segment {j}: {str(sub_error)}")
                        continue
                
                # If significant snoring detected in the segment
                # Adjust threshold based on number of valid sub-segments
                valid_sub_segments = min(n_sub_segments, 1)  # Avoid division by zero
                if sub_segment_snoring_count > 0:  # For short recordings, detect any snoring
                    avg_confidence = np.mean(sub_segment_confidences) if sub_segment_confidences else 0
                    snoring_segments.append((segment_start_time, segment_end_time))
                    snoring_confidences.append(avg_confidence)
                
                # Update progress
                if progress_callback:
                    progress_callback((i + 1) / n_segments)
            
            # Calculate results
            total_snoring_duration = sum(end - start for start, end in snoring_segments)
            snoring_percentage = (total_snoring_duration / total_duration_seconds) * 100 if total_duration_seconds > 0 else 0
            snoring_segments_count = len(snoring_segments)
            
            # Calculate snoring frequency (episodes per hour)
            hours_of_sleep = max(total_duration_seconds / 3600, 0.0001)  # Avoid division by zero
            snoring_frequency = snoring_segments_count / hours_of_sleep
            
            # Prepare results
            results = {
                'total_duration_seconds': total_duration_seconds,
                'total_duration_minutes': total_duration_minutes,
                'snoring_segments': snoring_segments,
                'snoring_confidences': snoring_confidences,
                'total_snoring_duration': total_snoring_duration,
                'snoring_percentage': snoring_percentage,
                'snoring_segments_count': snoring_segments_count,
                'snoring_frequency': snoring_frequency
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            import traceback
            logger.error(f"Full error details: {traceback.format_exc()}")
            return None
    
    def predict_sleep_disorder(self, input_data):
        """Predict sleep disorder from input data"""
        if not self.disorder_model_loaded:
            logger.error("Sleep disorder model not loaded.")
            return None
        
        try:
            # Get all required components from the loaded model data
            model = self.disorder_model['model']
            label_encoders = self.disorder_model['label_encoders']
            target_encoder = self.disorder_model['target_encoder']
            scaler = self.disorder_model['scaler']
            feature_list = self.disorder_model['feature_list']
            numerical_columns = self.disorder_model['numerical_columns']
            categorical_columns = self.disorder_model['categorical_columns']
            
            # Convert input_data to a more suitable format matching the sample implementation
            sample_dict = {
                'Gender': input_data['Gender'].iloc[0],
                'Age': input_data['Age'].iloc[0],
                'Occupation': input_data['Occupation'].iloc[0],
                'Sleep Duration': input_data['Sleep Duration'].iloc[0],
                'Quality of Sleep': input_data['Quality of Sleep'].iloc[0],
                'Physical Activity Level': input_data['Physical Activity Level'].iloc[0],
                'Stress Level': input_data['Stress Level'].iloc[0],
                'BMI Category': input_data['BMI Category'].iloc[0],
                'Systolic BP': input_data['Systolic BP'].iloc[0],
                'Diastolic BP': input_data['Diastolic BP'].iloc[0],
                'Heart Rate': input_data['Heart Rate'].iloc[0],
                'Daily Steps': input_data['Daily Steps'].iloc[0]
            }
            
            # Create a DataFrame with the sample
            sample_df = pd.DataFrame([sample_dict])
            
            # Feature Engineering
            sample_df['Sleep Efficiency'] = sample_df['Quality of Sleep'] / sample_df['Sleep Duration']
            sample_df['Stress Activity Ratio'] = sample_df['Stress Level'] / sample_df['Physical Activity Level']
            sample_df['BP Difference'] = sample_df['Systolic BP'] - sample_df['Diastolic BP']
            
            # BMI and Heart Rate Interaction - Note the BMI values are not yet encoded here
            sample_df['HR_BMI_Factor'] = 0
            if sample_df['BMI Category'].iloc[0] == 'Obese':
                sample_df['HR_BMI_Factor'] = sample_df['Heart Rate'] * 1.5
            elif sample_df['BMI Category'].iloc[0] == 'Overweight':
                sample_df['HR_BMI_Factor'] = sample_df['Heart Rate'] * 1.2
            elif sample_df['BMI Category'].iloc[0] == 'Normal':
                sample_df['HR_BMI_Factor'] = sample_df['Heart Rate'] * 1.0
            
            # Steps Adequacy
            sample_df['Steps Adequacy'] = sample_df['Daily Steps'] / 10000
            
            # Encode categorical features
            for col in categorical_columns:
                if col in sample_df.columns:
                    sample_df[col] = label_encoders[col].transform(sample_df[col])
            
            # Scale numerical features
            sample_df[numerical_columns] = scaler.transform(sample_df[numerical_columns])
            
            # Reorder columns to match the training data
            sample_df = sample_df[feature_list]
            
            # Make prediction
            pred_encoded = model.predict(sample_df)[0]
            prediction = target_encoder.inverse_transform([pred_encoded])[0]
            
            # Get probabilities for each class
            pred_proba = model.predict_proba(sample_df)[0]
            prob_dict = {target_encoder.inverse_transform([i])[0]: prob for i, prob in enumerate(pred_proba)}
            
            # Also check the maximum probability threshold
            max_prob_key = max(prob_dict, key=prob_dict.get)
            max_prob_value = prob_dict[max_prob_key]
            
            return {
                'prediction': prediction,
                'probabilities': prob_dict
            }
            
        except Exception as e:
            logger.error(f"Error predicting sleep disorder: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def predict_sleep_quality(self, input_data):
        """Predict sleep quality score from physiological metrics"""
        if not self.quality_model_loaded:
            logger.error("Sleep quality model not loaded.")
            return None
        
        try:
            # Access the model and preprocessing info
            model = self.quality_model['model'] if isinstance(self.quality_model, dict) else self.quality_model
            scaler = self.quality_model.get('scaler', None) if isinstance(self.quality_model, dict) else None
            feature_list = self.quality_model.get('feature_list', None) if isinstance(self.quality_model, dict) else None
            
            # Clone input data to avoid modifying original
            sample_df = input_data.copy()
            
            # Map variable names if needed
            if 'Sleep Duration' in sample_df.columns and 'Sleep_Duration' not in sample_df.columns:
                sample_df['Sleep_Duration'] = sample_df['Sleep Duration']
            
            if 'Stress Level' in sample_df.columns and 'Stress_Level' not in sample_df.columns:
                sample_df['Stress_Level'] = sample_df['Stress Level']
            
            # Define the expected columns based on your training data
            expected_columns = [
                'Heart_Rate_Variability', 
                'Body_Temperature', 
                'Movement_During_Sleep', 
                'Sleep_Duration', 
                'Caffeine_Intake_mg', 
                'Stress_Level', 
                'Bedtime_Consistency',
                'Light_Exposure_hours'
            ]
            
            # Create a new DataFrame with all required columns
            prediction_df = pd.DataFrame()
            
            # Copy existing columns or create with default values
            for col in expected_columns:
                if col in sample_df.columns:
                    prediction_df[col] = sample_df[col]
                else:
                    logger.warning(f"Missing required feature: {col}. Using default value 0.")
                    prediction_df[col] = 0
            
            # If we have a scaler, use it
            if scaler is not None:
                try:
                    # Scale using all the expected columns
                    prediction_df = pd.DataFrame(
                        scaler.transform(prediction_df),
                        columns=prediction_df.columns,
                        index=prediction_df.index
                    )
                except ValueError as scale_error:
                    logger.error(f"Error during scaling: {scale_error}")
                    # If there's an error with the scaler, let's try using the raw features
                    logger.warning("Proceeding with unscaled features.")
            
            # Ensure features are in the correct order if we have the feature list
            if feature_list:
                # Check if all required features exist
                missing_features = [f for f in feature_list if f not in prediction_df.columns]
                if missing_features:
                    logger.warning(f"Missing features from model's feature list: {missing_features}")
                    for feat in missing_features:
                        prediction_df[feat] = 0
                
                # Reorder columns to match the feature list
                prediction_df = prediction_df[feature_list]
            
            # Make prediction with the model
            raw_prediction = model.predict(prediction_df)
            
            # Convert prediction to a scalar if it's an array
            if hasattr(raw_prediction, '__iter__'):
                raw_prediction = raw_prediction[0]
            
            quality_score = raw_prediction
            
            return {
                'score': float(quality_score),
                'raw_prediction': float(raw_prediction)
            }
            
        except Exception as e:
            logger.error(f"Error predicting sleep quality: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def generate_suggestions(self, audio_results=None, disorder_results=None, quality_results=None):
        """Generate comprehensive suggestions based on all analysis results"""
        suggestions = []
        severity = "Unknown"
        general_suggestions = []
        
        # Process audio results if available
        if audio_results:
            snoring_percentage = audio_results['snoring_percentage']
            
            # Determine snoring severity
            if snoring_percentage < 10:
                severity = "Minimal"
                suggestions.append("Your snoring is minimal and likely not affecting your sleep quality.")
                suggestions.append("Continue practicing good sleep hygiene.")
            elif snoring_percentage < 30:
                severity = "Mild"
                suggestions.append("You have mild snoring that might occasionally disturb your sleep.")
                suggestions.append("Try sleeping on your side instead of your back.")
                suggestions.append("Consider using nasal strips to improve airflow.")
            elif snoring_percentage < 50:
                severity = "Moderate"
                suggestions.append("Your moderate snoring could be impacting your sleep quality significantly.")
                suggestions.append("Use a specially designed anti-snoring pillow.")
                suggestions.append("Try mouth exercises to strengthen throat muscles.")
                suggestions.append("Consider a humidifier if your environment is dry.")
            else:
                severity = "Severe"
                suggestions.append("Your snoring is severe and may indicate sleep apnea.")
                suggestions.append("Consult with a sleep specialist as soon as possible.")
                suggestions.append("Consider getting tested for sleep apnea.")
        
        # Process disorder prediction if available
        if disorder_results:
            disorder = disorder_results['prediction']

            if disorder == "None":
                suggestions.append("No specific sleep disorder detected from your physiological data.")
            elif disorder == "Insomnia":
                suggestions.append("Your data suggests potential insomnia patterns.")
                suggestions.append("Establish a regular sleep schedule and bedtime routine.")
                suggestions.append("Avoid screens at least 1 hour before bedtime.")
                suggestions.append("Create a comfortable, dark, and quiet sleep environment.")
                suggestions.append("Consider relaxation techniques like meditation before sleep.")
            elif disorder == "Sleep Apnea":
                suggestions.append("Your data indicates patterns consistent with sleep apnea.")
                suggestions.append("Consult with a healthcare provider for proper diagnosis.")
                suggestions.append("Consider weight management strategies if appropriate.")
                suggestions.append("Avoid alcohol and sedatives before sleep.")
                suggestions.append("Sleep on your side rather than your back.")
        
        # Process quality prediction if available
        if quality_results:
            quality_score = quality_results['score']
            
            if quality_score <= 3:
                suggestions.append("Your sleep quality appears to be poor based on physiological markers.")
                suggestions.append("Focus on improving your sleep environment.")
                suggestions.append("Consider stress reduction techniques like meditation or deep breathing.")
            elif quality_score <= 7:
                suggestions.append("Your sleep quality is moderate based on physiological markers.")
                suggestions.append("Small improvements to your bedtime routine could help.")
                suggestions.append("Maintain consistent sleep and wake times.")
            else:
                suggestions.append("Your sleep quality appears to be good based on physiological markers.")
                suggestions.append("Continue your healthy sleep habits.")
        
        # Add general recommendations
        general_suggestions = [
            "Maintain a healthy weight through diet and exercise.",
            "Avoid caffeine and heavy meals at least 4 hours before bedtime.",
            "Exercise regularly, but not within 2 hours of bedtime.",
            "Ensure your bedroom is at a comfortable temperature (around 65°F/18°C).",
            "Use your bed only for sleep and intimacy to strengthen the mental association."
        ]
        
        # Return all suggestions
        return {
            'severity': severity,
            'specific_suggestions': suggestions,
            'general_suggestions': general_suggestions
        }
