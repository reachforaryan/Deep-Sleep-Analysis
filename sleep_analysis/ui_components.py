import streamlit as st
import matplotlib.pyplot as plt
import librosa
import librosa.display
import pandas as pd
import numpy as np

def create_visualization(audio_path, results, sr=8000):
    """Create visualization of audio analysis results"""
    try:
        # Load audio for visualization
        y, _ = librosa.load(audio_path, sr=sr)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot waveform
        librosa.display.waveshow(y, sr=sr, ax=ax1, alpha=0.6)
        ax1.set_title('Audio Waveform with Snoring Segments Highlighted')
        ax1.set_xlabel('Time (s)')
        
        # Highlight snoring segments on waveform
        for start, end in results['snoring_segments']:
            ax1.axvspan(start, end, color='red', alpha=0.3)
        
        # Create snoring timeline
        x_timeline = []
        y_timeline = []
        
        # Create timeline data
        max_time = len(y) / sr
        timeline_resolution = max(1, int(max_time / 300))  # One point per timeline_resolution seconds
        
        for i in range(0, int(max_time), timeline_resolution):
            x_timeline.append(i)
            
            # Check if this time point is in a snoring segment
            in_snoring_segment = False
            for start, end in results['snoring_segments']:
                if start <= i <= end:
                    in_snoring_segment = True
                    break
            
            y_timeline.append(1 if in_snoring_segment else 0)
        
        # Plot timeline
        ax2.plot(x_timeline, y_timeline, 'b-', linewidth=2)
        ax2.set_title('Snoring Timeline (1 = Snoring, 0 = No Snoring)')
        ax2.set_xlabel('Time (s)')
        ax2.set_yticks([0, 1])
        ax2.set_yticklabels(['No Snoring', 'Snoring'])
        ax2.grid(True)
        
        # Add summary statistics as text annotation
        summary_text = (
            f"Total Duration: {results['total_duration_minutes']:.2f} minutes\n"
            f"Snoring Duration: {results['total_snoring_duration'] / 60:.2f} minutes\n"
            f"Snoring Percentage: {results['snoring_percentage']:.2f}%\n"
            f"Snoring Episodes: {results['snoring_segments_count']}\n"
            f"Snoring Frequency: {results['snoring_frequency']:.2f} episodes/hour"
        )
        
        # Add text box for summary
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.02, 0.3, summary_text, transform=ax2.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        return None

def render_disorder_results(disorder_results, shared_inputs):
    """Render sleep disorder analysis results"""
    if disorder_results:
        disorder = disorder_results['prediction']
        
        # Display disorder prediction prominently
        if disorder == "None":
            st.success("### No Sleep Disorder Detected")
        elif disorder == "Insomnia":
            st.warning("### Insomnia Detected")
        elif disorder == "Sleep Apnea":
            st.error("### Sleep Apnea Detected")
        else:
            st.info(f"### Predicted: {disorder}")
        
        # Display probabilities if available
        if 'probabilities' in disorder_results and disorder_results['probabilities'] is not None:
            # Get class probabilities
            probs_dict = disorder_results['probabilities']
            
            # Convert the dict to a DataFrame directly
            prob_data = pd.DataFrame(list(probs_dict.items()), columns=['Disorder', 'Probability'])
            
            st.write("#### Disorder Probabilities")
            st.bar_chart(prob_data.set_index('Disorder'))
        
        # Show input summary
        st.write("#### Key Risk Factors")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sleep Duration", f"{shared_inputs.get('Sleep Duration', 0):.1f} hrs")
            st.metric("BMI Category", shared_inputs.get('BMI Category', 'Unknown'))
        with col2:
            st.metric("Physical Activity", f"{shared_inputs.get('Physical Activity Level', 0)} min/day")
        with col3:
            st.metric("Stress Level", f"{shared_inputs.get('Stress Level', 0)}/10")
            st.metric("Heart Rate", f"{shared_inputs.get('Heart Rate', 0)} bpm")
    else:
        st.info("Sleep disorder analysis not completed.")

def render_quality_results(quality_results, shared_inputs):
    """Render sleep quality analysis results"""
    if quality_results:
        quality_score = quality_results['score']
        
        # Display result prominently
        if quality_score <= 3:
            st.error(f"### Poor Sleep Quality: {quality_score:.2f}/10")
        elif quality_score <= 7:
            st.warning(f"### Moderate Sleep Quality: {quality_score:.2f}/10")
        else:
            st.success(f"### Good Sleep Quality: {quality_score:.2f}/10")
        
        # Display quality score
        st.slider("Sleep Quality Score", 1, 10, int(quality_score) if int(quality_score) >= 1 else 1, disabled=True, key="result_quality_score")
        
        # Show key metrics
        st.write("#### Key Physiological Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Heart Rate Variability", f"{shared_inputs.get('Heart_Rate_Variability', 0):.1f} ms")
        with col2:
            st.metric("Body Temperature", f"{shared_inputs.get('Body_Temperature', 0):.1f} °C")
        with col3:
            st.metric("Movement", f"{shared_inputs.get('Movement_During_Sleep', 0):.2f} index")
        with col4:
            st.metric("Sleep Duration", f"{shared_inputs.get('Sleep Duration', 0):.1f} hrs")
    else:
        st.info("Sleep quality analysis not completed.")

def render_snoring_results(audio_results, audio_fig=None):
    """Render snoring analysis results"""
    if audio_results:
        results = audio_results
        
        # Display snoring severity prominently
        if results['snoring_percentage'] < 10:
            st.success(f"### Minimal Snoring: {results['snoring_percentage']:.1f}%")
        elif results['snoring_percentage'] < 30:
            st.info(f"### Mild Snoring: {results['snoring_percentage']:.1f}%")
        elif results['snoring_percentage'] < 50:
            st.warning(f"### Moderate Snoring: {results['snoring_percentage']:.1f}%")
        else:
            st.error(f"### Severe Snoring: {results['snoring_percentage']:.1f}%")
        
        # Show key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Recording Duration", f"{results['total_duration_minutes']:.1f} min")
        with col2:
            st.metric("Snoring Duration", f"{results['total_snoring_duration'] / 60:.1f} min")
        with col3:
            st.metric("Snoring Episodes", f"{results['snoring_segments_count']}")
        
        # Display visualization if available
        if audio_fig is not None:
            st.write("#### Snoring Pattern Visualization")
            st.pyplot(audio_fig)
    else:
        st.info("Audio analysis not completed.")

def render_recommendations(combined_suggestions):
    """Render comprehensive recommendations"""
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
