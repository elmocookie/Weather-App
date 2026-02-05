import streamlit as st
import requests
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Weather Predictor", page_icon="🌤️")

st.title("🌤️ Weather Predictor")
st.write("Get current weather and 24-hour forecast with trend prediction")

# --- Helper Functions ---

def geocode_city(city_name):
    """
    Convert city name to coordinates using Open-Meteo Geocoding API.
    Returns (latitude, longitude, display_name) or None if not found.
    """
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            lat = result["latitude"]
            lon = result["longitude"]
            name = result["name"]
            country = result.get("country", "")
            admin1 = result.get("admin1", "")

            # Build display name
            display_parts = [name]
            if admin1:
                display_parts.append(admin1)
            if country:
                display_parts.append(country)
            display_name = ", ".join(display_parts)

            return lat, lon, display_name
        return None
    except requests.RequestException as e:
        st.error(f"Network error during geocoding: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error during geocoding: {e}")
        return None


def fetch_weather(latitude, longitude):
    """
    Fetch weather data from Open-Meteo API.
    Returns weather data dictionary or None on error.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,apparent_temperature,precipitation_probability,wind_speed_10m",
            "current": "temperature_2m,apparent_temperature,wind_speed_10m",
            "forecast_days": 2,
            "timezone": "auto"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Network error fetching weather: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error fetching weather: {e}")
        return None


def extract_24h_forecast(weather_data):
    """
    Extract next 24 hours of forecast data.
    Returns list of dicts with time, temp, apparent_temp, precip_prob, wind.
    """
    hourly = weather_data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    apparent_temps = hourly.get("apparent_temperature", [])
    precip_probs = hourly.get("precipitation_probability", [])
    wind_speeds = hourly.get("wind_speed_10m", [])

    # Get next 24 hours (indices 0-23)
    forecast = []
    for i in range(min(24, len(times))):
        forecast.append({
            "time": times[i],
            "temperature": temps[i] if i < len(temps) else None,
            "apparent_temperature": apparent_temps[i] if i < len(apparent_temps) else None,
            "precipitation_probability": precip_probs[i] if i < len(precip_probs) else None,
            "wind_speed": wind_speeds[i] if i < len(wind_speeds) else None
        })

    return forecast


def predict_trend(current_temp, forecast_24h):
    """
    Generate simple trend prediction based on temperature and precipitation.
    Returns a string with the prediction summary.
    """
    if not forecast_24h:
        return "Insufficient data for prediction"

    # Calculate average temperature for next 12-24 hours (second half of forecast)
    second_half = forecast_24h[12:24]
    valid_temps = [h["temperature"] for h in second_half if h["temperature"] is not None]

    if not valid_temps:
        return "Insufficient temperature data for trend"

    avg_future_temp = sum(valid_temps) / len(valid_temps)
    temp_diff = avg_future_temp - current_temp

    # Determine temperature trend
    if temp_diff > 2:
        temp_trend = "warming up"
    elif temp_diff < -2:
        temp_trend = "cooling down"
    else:
        temp_trend = "staying stable"

    # Check for rain likelihood
    precip_probs = [h["precipitation_probability"] for h in forecast_24h
                    if h["precipitation_probability"] is not None]

    rain_likely = False
    if precip_probs:
        max_precip = max(precip_probs)
        rain_likely = max_precip > 50

    # Build prediction text
    prediction = f"🔮 **Trend**: Temperatures will be **{temp_trend}** "
    prediction += f"(currently {current_temp:.1f}°C → averaging {avg_future_temp:.1f}°C later). "

    if rain_likely:
        prediction += "☔ **Rain is likely** in the next 24 hours."
    else:
        prediction += "🌤️ **Low chance of rain** in the next 24 hours."

    return prediction


# --- Main App UI ---

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    city_input = st.text_input(
        "Enter city name",
        placeholder="e.g., London, New York, Tokyo",
        help="You can add country/state for better results: 'Portland, Oregon' or 'Paris, France'"
    )
with col2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    search_button = st.button("🔍 Search", type="primary")

# Process search
if search_button:
    if not city_input or city_input.strip() == "":
        st.warning("⚠️ Please enter a city name")
    else:
        with st.spinner("Searching for location..."):
            geocode_result = geocode_city(city_input.strip())

        if geocode_result is None:
            st.error("❌ City not found. Try adding country/state for better results.")
        else:
            lat, lon, display_name = geocode_result
            st.success(f"📍 Found: **{display_name}**")

            with st.spinner("Fetching weather data..."):
                weather_data = fetch_weather(lat, lon)

            if weather_data is None:
                st.error("❌ Failed to fetch weather data. Please try again.")
            else:
                # Extract current weather
                current = weather_data.get("current", {})
                current_temp = current.get("temperature_2m")
                current_apparent = current.get("apparent_temperature")
                current_wind = current.get("wind_speed_10m")

                # Extract 24h forecast
                forecast_24h = extract_24h_forecast(weather_data)

                # Display current weather
                st.subheader("🌡️ Current Weather")
                col1, col2, col3 = st.columns(3)

                with col1:
                    if current_temp is not None:
                        st.metric("Temperature", f"{current_temp:.1f} °C")
                    else:
                        st.metric("Temperature", "N/A")

                with col2:
                    if current_apparent is not None:
                        st.metric("Feels Like", f"{current_apparent:.1f} °C")
                    else:
                        st.metric("Feels Like", "N/A")

                with col3:
                    if current_wind is not None:
                        st.metric("Wind Speed", f"{current_wind:.1f} km/h")
                    else:
                        st.metric("Wind Speed", "N/A")

                # Display 24-hour forecast chart
                st.subheader("📊 24-Hour Temperature Forecast")

                if forecast_24h:
                    # Prepare data for chart
                    chart_data = {}
                    labels = []
                    temps = []

                    for hour in forecast_24h:
                        if hour["temperature"] is not None:
                            # Format time for display (show hour only)
                            time_str = hour["time"]
                            try:
                                dt = datetime.fromisoformat(time_str)
                                hour_label = dt.strftime("%H:%M")
                            except:
                                hour_label = time_str[-5:]  # Last 5 chars (HH:MM)

                            labels.append(hour_label)
                            temps.append(hour["temperature"])

                    if temps:
                        # Create a simple dict for st.line_chart
                        import pandas as pd
                        chart_df = pd.DataFrame({
                            "Temperature (°C)": temps
                        }, index=labels)
                        st.line_chart(chart_df)
                    else:
                        st.info("No temperature data available for chart")
                else:
                    st.info("No forecast data available")

                # Generate and display prediction
                st.subheader("🔮 Prediction")
                if current_temp is not None and forecast_24h:
                    prediction = predict_trend(current_temp, forecast_24h)
                    st.info(prediction)
                else:
                    st.warning("Insufficient data for prediction")

                # Show detailed hourly data in expandable section
                with st.expander("📋 Detailed Hourly Forecast"):
                    for hour in forecast_24h[:12]:  # Show first 12 hours
                        time_str = hour["time"]
                        try:
                            dt = datetime.fromisoformat(time_str)
                            display_time = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            display_time = time_str

                        temp = f"{hour['temperature']:.1f}°C" if hour['temperature'] is not None else "N/A"
                        precip = f"{hour['precipitation_probability']}%" if hour['precipitation_probability'] is not None else "N/A"
                        wind = f"{hour['wind_speed']:.1f} km/h" if hour['wind_speed'] is not None else "N/A"

                        st.text(f"{display_time} | Temp: {temp} | Precip: {precip} | Wind: {wind}")

# Footer
st.divider()
st.caption("Data provided by Open-Meteo.com • No API key required")
