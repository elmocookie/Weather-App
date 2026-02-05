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


def get_weather_condition(precip_prob, wind_speed):
    """
    Determine weather condition based on precipitation probability and wind speed.
    Returns (icon, condition_name) tuple.

    Args:
        precip_prob: Precipitation probability (0-100) or None
        wind_speed: Wind speed in km/h or None
    """
    # Default values if data is missing
    if precip_prob is None:
        precip_prob = 0
    if wind_speed is None:
        wind_speed = 0

    # Determine condition based on precipitation and wind
    if precip_prob > 70:
        return "🌧️💙", "Rainy"
    elif precip_prob > 40:
        return "☁️💤", "Cloudy"
    elif precip_prob > 20:
        if wind_speed > 20:
            return "🌤️🌸", "Partly Cloudy & Windy"
        else:
            return "⛅💭", "Partly Cloudy"
    else:
        if wind_speed > 25:
            return "🌤️💫", "Sunny & Windy"
        else:
            return "☀️✨", "Sunny"


def get_location_from_ip():
    """
    Get approximate location from IP address using ip-api.com.
    Returns (latitude, longitude, display_name) or None on error.

    Note: This provides city-level accuracy based on IP address.
    It may be less accurate with VPNs or proxies.
    """
    try:
        url = "http://ip-api.com/json/"
        params = {"fields": "status,message,country,regionName,city,lat,lon"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            lat = data.get("lat")
            lon = data.get("lon")
            city = data.get("city", "Unknown")
            region = data.get("regionName", "")
            country = data.get("country", "")

            display_name = f"{city}, {region}, {country}" if region else f"{city}, {country}"
            return lat, lon, display_name
        else:
            st.error(f"Location detection failed: {data.get('message', 'Unknown error')}")
            return None
    except requests.RequestException as e:
        st.error(f"Network error detecting location: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error detecting location: {e}")
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
col1, col2, col3 = st.columns([2.5, 1, 1.2])
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
with col3:
    st.write("")  # Spacing
    st.write("")  # Spacing
    location_button = st.button("📍 Use My Location")

# Determine which action to take
geocode_result = None
location_source = None

if location_button:
    with st.spinner("Detecting your location..."):
        geocode_result = get_location_from_ip()
    location_source = "auto"

    if geocode_result is None:
        st.error("❌ Could not detect your location. Please try entering a city manually.")

elif search_button:
    if not city_input or city_input.strip() == "":
        st.warning("⚠️ Please enter a city name")
    else:
        with st.spinner("Searching for location..."):
            geocode_result = geocode_city(city_input.strip())
        location_source = "manual"

        if geocode_result is None:
            st.error("❌ City not found. Try adding country/state for better results.")

# Display weather if we have valid coordinates
if geocode_result is not None:
    lat, lon, display_name = geocode_result

    if location_source == "auto":
        st.info(f"📍 **Your Location (approximate): {display_name}**")
    else:
        st.success(f"📍 **{display_name}**")

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

        # Get current weather condition (use first hour forecast for precip prob)
        current_precip = None
        if forecast_24h and len(forecast_24h) > 0:
            current_precip = forecast_24h[0].get("precipitation_probability")

        condition_icon, condition_name = get_weather_condition(current_precip, current_wind)

        # Display current weather
        st.subheader("🌡️ Current Weather")
        st.markdown(f"### {condition_icon} {condition_name}")

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

                # Get condition icon for this hour
                hour_icon, _ = get_weather_condition(hour['precipitation_probability'], hour['wind_speed'])

                temp = f"{hour['temperature']:.1f}°C" if hour['temperature'] is not None else "N/A"
                precip = f"{hour['precipitation_probability']}%" if hour['precipitation_probability'] is not None else "N/A"
                wind = f"{hour['wind_speed']:.1f} km/h" if hour['wind_speed'] is not None else "N/A"

                st.text(f"{hour_icon} {display_time} | Temp: {temp} | Precip: {precip} | Wind: {wind}")

# Footer
st.divider()
st.caption("Data provided by Open-Meteo.com • No API key required")
