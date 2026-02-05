# Hello World Project

## Purpose

A simple weather forecasting application built with Python and Streamlit. This app fetches real-time weather data from the Open-Meteo API and provides:

- Current weather conditions (temperature, feels-like, wind speed)
- 24-hour temperature forecast with visualization
- Simple trend predictions (warming/cooling, rain likelihood)
- Clean, beginner-friendly interface

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or navigate to the repository**
```bash
cd "/Volumes/SAMSUNG/Macbook/Claude Code Project"
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Running the App

```bash
streamlit run weather_app.py
```

The app will open in your default web browser at `http://localhost:8501`

### Using the Weather Predictor

1. Enter a city name in the search box
   - For better accuracy, include country/state: "Portland, Oregon" or "Paris, France"
2. Click the "Search" button
3. View:
   - Current weather conditions
   - 24-hour temperature chart
   - Trend prediction (warming/cooling, rain likelihood)
   - Detailed hourly forecast (expandable)

### Features

- **Real-time Data**: Fetches current weather from Open-Meteo API (no API key needed)
- **24-Hour Forecast**: Temperature visualization over the next day
- **Smart Predictions**: Simple trend analysis for temperature changes and precipitation
- **Error Handling**: Graceful handling of network issues and invalid city names
- **Responsive UI**: Clean, intuitive Streamlit interface

## Technical Details

### APIs Used

1. **Open-Meteo Geocoding API**
   - Converts city names to coordinates
   - Endpoint: `https://geocoding-api.open-meteo.com/v1/search`

2. **Open-Meteo Weather API**
   - Fetches forecast data
   - Endpoint: `https://api.open-meteo.com/v1/forecast`
   - Parameters: hourly temperature, apparent temperature, precipitation probability, wind speed

### Project Structure

```
.
├── weather_app.py      # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore patterns
├── README.md          # This file
└── hello_world.txt    # Original demo file
```

### Dependencies

- **streamlit**: Web application framework
- **requests**: HTTP library for API calls
- Standard library only (no pandas/numpy required)

## Troubleshooting

**City not found?**
- Try adding country or state: "Springfield, Illinois"
- Check spelling
- Use common city names

**Network errors?**
- Check your internet connection
- Open-Meteo API might be temporarily unavailable
- Try again in a few moments

**App won't start?**
- Ensure Python 3.8+ is installed: `python --version`
- Verify dependencies are installed: `pip list`
- Try reinstalling: `pip install -r requirements.txt --force-reinstall`

## Next Steps

Potential directions to expand this project:

1. **Enhanced Features**
   - Add 7-day forecast
   - Include weather icons/conditions (sunny, cloudy, rainy)
   - Add UV index, humidity, pressure
   - Save favorite locations

2. **Advanced Predictions**
   - Use historical data for better trend analysis
   - Implement simple ML model for predictions
   - Add weather alerts/warnings

3. **UI Improvements**
   - Add map view with location pin
   - Dark/light theme toggle
   - Export data to CSV
   - Multiple city comparison

4. **Testing & Quality**
   - Add unit tests for API functions
   - Add integration tests
   - Implement caching to reduce API calls

## Contributing

Contributions welcome! This is a learning project designed to be beginner-friendly.

## License

This is an open starter project - use it however you'd like!

## Credits

Weather data provided by [Open-Meteo.com](https://open-meteo.com/) - Free weather API for non-commercial use.
