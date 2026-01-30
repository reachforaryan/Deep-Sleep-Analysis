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

def render_gauge_chart(score, max_score=10):
    """Render a gauge chart for Sleep Quality Score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Sleep Score", 'font': {'size': 24, 'color': '#ccc'}},
        gauge = {
            'axis': {'range': [None, max_score], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "rgba(0,0,0,0)"}, # invisible bar, using steps
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [0, 3], 'color': '#ff4b4b'},
                {'range': [3, 7], 'color': '#ffa421'},
                {'range': [7, 10], 'color': '#21c354'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=220, 
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "white"}
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

def create_unified_dashboard(audio_path, results, input_data, sr=8000, view_mode="Waveform"):
    """
    Create a synchronized dashboard combining Audio, Heart Rate, and Snoring Probability.
    
    Args:
        audio_path: Path to audio file
        results: Dictionary containing audio analysis results
        input_data: Dictionary containing user inputs (specifically Heart Rate)
        sr: Sampling rate for audio loading
        view_mode: "Waveform" or "Spectrogram"
    """
    try:
        # --- 1. Load and Process Audio (The Master Time Axis) ---
        y, _ = librosa.load(audio_path, sr=sr)
        duration = len(y) / sr
        
        # Downsample for faster plotting if array is too large (only for waveform)
        max_points = 10000
        hop = max(1, len(y) // max_points)
        y_plot = y[::hop]
        x_plot = np.arange(len(y))[::hop] / sr
        
        # --- 2. Generate Synthetic Heart Rate Data ---
        # We only have a scalar 'Heart Rate', so we simulate a trace centered around it
        base_hr = input_data.get('Heart Rate', 70)
        
        # Create a time vector for HR matching the plotting resolution
        # Add some random variability (noise)
        noise = np.random.normal(0, 2, len(x_plot)) 
        
        # Add some slow-moving trend (respiration sinus arrhythmia simulation)
        trend = 5 * np.sin(2 * np.pi * 0.1 * x_plot)
        
        hr_trace = base_hr + trend + noise
        
        # Add reactive spikes if snoring is detected
        # Check snoring segments and add BPM spikes during those times
        if 'snoring_segments' in results:
            for start, end in results['snoring_segments']:
                # Find indices corresponding to this time range
                mask = (x_plot >= start) & (x_plot <= end)
                if np.any(mask):
                     # Add a spike of 10-15 BPM
                     hr_trace[mask] += np.random.uniform(5, 15, size=np.sum(mask))

        # Smoothen the HR trace slightly for visual appeal using pandas rolling
        hr_series = pd.Series(hr_trace).rolling(window=50, center=True, min_periods=1).mean().values

        # --- 3. Construct Snoring Heatmap Data ---
        # Create a binary or probability array aligned with time
        snoring_prob = np.zeros_like(x_plot)
        if 'snoring_segments' in results:
            for start, end in results['snoring_segments']:
                mask = (x_plot >= start) & (x_plot <= end)
                snoring_prob[mask] = 1.0 # High confidence of snoring
                
                # Add transition/falloff logic if desired, keeping binary 0/1 for now

        # --- 4. Build Plotly Subplots ---
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.3, 0.4, 0.3],
            subplot_titles=("Audio Signal Analysis", "Heart Rate (BPM)", "Snoring Detection")
        )

        # Row 1: Audio Visualization (Swappable)
        if view_mode == "Spectrogram":
            # Compute Mel Spectrogram
            S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, fmax=sr/2)
            S_dB = librosa.power_to_db(S, ref=np.max)
            
            # Spectrogram is Matrix [Freq, Time]
            # Time axis needs to match strictly
            # S_dB.shape[1] is number of time frames
            # We need to map this to x axes
            time_frames = np.linspace(0, duration, S_dB.shape[1])
            
            fig.add_trace(
                go.Heatmap(
                    z=S_dB,
                    x=time_frames,
                    y=np.linspace(0, sr/2, S_dB.shape[0]),
                    colorscale='Magma',
                    showscale=False,
                    name='Spectrogram'
                ),
                row=1, col=1
            )
            fig.update_yaxes(title_text="Hz", row=1, col=1)
            
        else:
            # Standard Waveform
            fig.add_trace(
                go.Scatter(
                    x=x_plot, y=y_plot, 
                    mode='lines', 
                    name='Audio',
                    line=dict(color='#4facfe', width=1),
                    hoverinfo='skip' 
                ),
                row=1, col=1
            )
            fig.update_yaxes(title_text="Amp", row=1, col=1, showticklabels=False)

        # Row 2: Heart Rate with Trendline logic
        fig.add_trace(
            go.Scatter(
                x=x_plot, y=hr_series,
                mode='lines',
                name='Heart Rate',
                line=dict(color='#ff5e62', width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 94, 98, 0.1)'
            ),
            row=2, col=1
        )
        
        # Add baseline reference line
        fig.add_hline(y=base_hr, line_dash="dot", line_color="gray", annotation_text="Baseline", row=2, col=1)

        # Row 3: Snoring Heatmap
        # Construct 2D array for Heatmap [1, TimeSteps]
        z_data = [snoring_prob]
        
        fig.add_trace(
            go.Heatmap(
                z=z_data,
                x=x_plot,
                y=[0], # Dummy y
                colorscale=[[0, '#1e1e1e'], [1, '#ff2b2b']],
                showscale=False,
                name='Snore Prob'
            ),
            row=3, col=1
        )
        
        # Event Markers (Apnea Simulation logic)
        # If we have long silence > 5s followed by snoring spike, might be Apnea
        # Simple heuristic for "Event Markers" from user request
        if 'snoring_segments' in results and len(results['snoring_segments']) > 0:
            for start, end in results['snoring_segments']:
                if (end - start) > 2.0: # Only mark significant events > 2s
                    fig.add_vline(x=start, line_width=1, line_dash="dot", line_color="#ff2b2b", row='all')

        # --- 5. Styling & Interaction ---
        fig.update_layout(
            height=600,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            font=dict(color="#a0a0a0")
        )
        
        # Enable Spikelines
        fig.update_xaxes(
            showspikes=True, 
            spikemode='across', 
            spikesnap='cursor', 
            showline=False, 
            showgrid=False
        )
        fig.update_yaxes(showgrid=True, gridcolor='#333')
        
        # Axis Labels
        fig.update_yaxes(title_text="BPM", row=2, col=1)
        fig.update_yaxes(title_text="Prob", row=3, col=1, showticklabels=False)
        fig.update_xaxes(title_text="Time (s)", row=3, col=1)

        return fig

    except Exception as e:
        st.error(f"Error creating unified dashboard: {str(e)}")
        # import traceback
        # st.error(traceback.format_exc())
        return None
