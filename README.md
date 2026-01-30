# Sleep-Pattern-Analysis

## Overview

Sleep-Pattern-Analysis is a comprehensive tool designed to analyze sleep patterns, detect snoring, assess sleep quality, and identify possible sleep anomalies using both audio and physiological data. The project combines deep learning models for audio analysis, machine learning models for data classification, and an interactive Streamlit frontend for user input and results visualization.

## Features

- **Snoring Detection from Audio Files:** Uses CNN and LSTM deep learning models trained on publicly available snoring datasets to detect snoring episodes from uploaded audio recordings.
- **Sleep Anomaly & Quality Detection from CSV Data:** Employs Random Forest models to classify numerical sleep data for anomaly detection and quality assessment.
- **Personalized Recommendations:** Provides actionable sleep hygiene tips and personalized suggestions based on the analysis results.
- **Interactive Web App:** Built with Streamlit, allowing users to input data, upload audio, and view results and recommendations in a user-friendly interface.

## Project Structure

```text
Sleep-Pattern-Analysis/
├── dataset/                # Dataset for training
├── models/                 # Trained models (.h5, .pkl, .joblib)
├── sleep_analysis/         # Core analysis package
│   ├── analyzer.py         # Main analysis logic
│   ├── config.py           # Configuration settings
│   └── ui/                 # UI components
├── LSTM+CNN+MFCC.py        # Audio model training script
├── streamlit_app.py        # Main Streamlit application entry point
└── requirements.txt        # Python dependencies
```

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.7+ installed. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Models Setup

#### Audio Model (Snoring Detection)
The audio detection model needs to be trained or placed in the `models/` directory.
- **Train your own:**
    1. Download the snoring dataset from [Kaggle](https://www.kaggle.com/datasets/tareqkhanemu/snoring/data) and place it in `dataset/`.
    2. Run the training script:
       ```bash
       python LSTM+CNN+MFCC.py
       ```
    3. This will save `sleep_audio_model.h5` in the `models/` folder.

#### Tabular Models (Disorder & Quality)
The application expects pre-trained models for sleep disorder and quality assessment.
- Ensure the following files are present in the `models/` directory:
    - `sleep_disorder_model.pkl`
    - `sleep_quality_model.pkl`

### 3. Running the Application

Run the Streamlit app from the project root:

```bash
streamlit run streamlit_app.py
```

## Usage

1. **Configure Profile**: Use the sidebar to enter physiological and lifestyle data (age, gender, sleep duration, heart rate, etc.).
2. **Upload Audio**: Upload a sleep recording (WAV or MP3) in the "Audio Analysis" section for snoring detection.
3. **Analyze**: Click the **Analyze Sleep Patterns** button in the sidebar.
4. **View Results**: The application will display:
   - Sleep Disorder Predictions
   - Sleep Quality Assessment
   - Snoring Detection analysis (if audio provided)
   - Personalized Recommendations

## Dataset

The snoring detection model uses the dataset created by Tareq Khan, available on Kaggle. The dataset consists of 500 snoring and 500 non-snoring 1-second audio clips.

If you use the dataset, please cite:
> T. H. Khan, "A deep learning model for snoring detection and vibration notification using a smart wearable gadget," Electronics, vol. 8, no. 9, article. 987, ISSN 2079-9292, 2019.

## Requirements

- `streamlit>=1.20.0`
- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `librosa>=0.9.0`
- `matplotlib>=3.5.0`
- `scikit-learn>=1.5.1`
- `tensorflow>=2.8.0`
- `seaborn>=0.11.0`
- `plotly>=5.0.0`
- `shap>=0.40.0`

## Key Files

- `streamlit_app.py`: Entry point for the Streamlit application.
- `sleep_analysis/`: Python package containing the core logic and UI components.
- `LSTM+CNN+MFCC.py`: Script to train the snoring detection model.
- `models/`: Directory where trained models are stored.

## Acknowledgements

- Audio dataset courtesy of Tareq Khan, [Kaggle](https://www.kaggle.com/datasets/tareqkhanemu/snoring/data)
