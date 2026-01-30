import streamlit as st
import librosa
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def create_visualization(audio_path, results, sr=8000):
    """Create interactive Plotly visualization of audio analysis results"""
    try:
        # Load audio for visualization
        y, _ = librosa.load(audio_path, sr=sr)
        
        # Downsample for faster plotting if array is too large
        # Keep max ~20k points for performance
        max_points = 20000
        if len(y) > max_points:
            hop = len(y) // max_points
            y_plot = y[::hop]
            x_plot = np.arange(len(y))[::hop] / sr
        else:
            y_plot = y
            x_plot = np.arange(len(y)) / sr

        # Create subplots: Row 1 = Waveform, Row 2 = Snoring Probability
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=("Audio Waveform", "Snoring Events"),
            row_heights=[0.7, 0.3]
        )
        
        # 1. Audio Waveform
        fig.add_trace(
            go.Scatter(x=x_plot, y=y_plot, mode='lines', name='Audio', 
                      line=dict(color='#4c78a8', width=1), opacity=0.8),
            row=1, col=1
        )
        
        # Highlight snoring segments on waveform (using shapes or filled area)
        # For better performance with many segments, we can create a mask overlay
        
        # 2. Snoring Timeline (Binary/Timeline)
        # Construct timeline for plotting
        x_timeline = []
        y_timeline = []
        
        duration = len(y) / sr
        resolution = 1.0 # 1 second resolution for timeline bar
        
        current_time = 0
        while current_time < duration:
            is_snoring = 0
            # Check if current second is within any snoring segment
            for start, end in results['snoring_segments']:
                # Simple overlap check
                if start <= current_time <= end or start <= current_time+resolution <= end:
                    is_snoring = 1
                    break
            
            x_timeline.append(current_time)
            y_timeline.append(is_snoring)
            current_time += resolution
            
        fig.add_trace(
            go.Bar(x=x_timeline, y=y_timeline, name='Snoring',
                  marker_color='#e45756', opacity=0.6),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified"
        )
        
        fig.update_yaxes(title_text="Amplitude", row=1, col=1)
        fig.update_yaxes(title_text="Event", row=2, col=1, tickvals=[0, 1], ticktext=["No", "Yes"])
        fig.update_xaxes(title_text="Time (s)", row=2, col=1)
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

def render_snoring_results(audio_results, audio_fig=None):
    """Render snoring analysis results"""
    if audio_results:
        results = audio_results
        
        # Display snoring severity prominently (Summary Text for the card)
        pct = results['snoring_percentage']
        
        # Show key metrics in columns (Optional, if not already shown in Hero card, but good for context above chart)
        # Keeping it minimal as per bento design, focusing on the chart
        
        # Display visualization if available
        if audio_fig is not None:
            # Interactive Plotly Chart
            st.plotly_chart(audio_fig, width="stretch", config={'displayModeBar': False})
            
            # Additional details below chart
            st.caption(f"Detected {results['snoring_segments_count']} snoring episodes over {results['total_duration_minutes']:.1f} minutes.")
            
    else:
        st.info("Audio analysis not completed.")

def render_disorder_chart(disorder_results):
    """Render chart for disorder probabilities using Plotly"""
    if 'probabilities' in disorder_results and disorder_results['probabilities'] is not None:
        # Get class probabilities
        probs_dict = disorder_results['probabilities']
        
        # Convert to DataFrame
        prob_data = pd.DataFrame(list(probs_dict.items()), columns=['Disorder', 'Probability'])
        prob_data['Probability'] = prob_data['Probability'] * 100 # Convert to percentage
        
        # Create Plotly Bar Chart
        fig = px.bar(
            prob_data, 
            x='Disorder', 
            y='Probability',
            color='Disorder',
            text='Probability',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}%', 
            textposition='outside'
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title='Probability (%)', range=[0, 110]),
            xaxis=dict(title=None)
        )
        
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
