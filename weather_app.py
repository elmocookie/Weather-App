import streamlit as st
import requests
from datetime import datetime
import random

# Page configuration
st.set_page_config(page_title="Let's Check the Weather!", page_icon="🌤️")

st.title("🌈✨ Let's Check the Weather! ✨🌈")
st.write("Discover today's weather vibes and plan your perfect day! 🌤️")
st.write("---")

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


def get_weather_condition(precip_prob, wind_speed, temperature=None):
    """
    Determine weather condition based on precipitation probability, wind speed, and temperature.
    Returns (icon, condition_name, description, tip) tuple.

    Args:
        precip_prob: Precipitation probability (0-100) or None
        wind_speed: Wind speed in km/h or None
        temperature: Temperature in Celsius or None
    """
    # Default values if data is missing
    if precip_prob is None:
        precip_prob = 0
    if wind_speed is None:
        wind_speed = 0

    # Determine temperature category
    temp_cold = temperature is not None and temperature < 10
    temp_cool = temperature is not None and 10 <= temperature < 20
    temp_warm = temperature is not None and 20 <= temperature < 30
    temp_hot = temperature is not None and temperature >= 30

    # Determine condition based on precipitation and wind
    if precip_prob > 70:
        if temp_cold:
            tip = "☔ Bundle up! It's cold and rainy - perfect for cozy indoor activities with hot drinks! ☕❄️"
        else:
            tip = "☔ Grab your cutest umbrella and rain boots! Puddle jumping optional but recommended! 💧"
        return ("🌧️💙", "Rainy",
                "Perfect day for cozy indoor vibes! 🏠💕", tip)

    elif precip_prob > 40:
        if temp_cold:
            tip = "🧣 Chilly and cloudy! Perfect for hot chocolate and warm blankets! Stay cozy! ☕🛋️"
        else:
            tip = "📚 Perfect for reading, napping, or enjoying hot chocolate! Blanket forts highly encouraged! 🛋️"
        return ("☁️💤", "Cloudy",
                "Dreamy cloud-watching weather! ☁️✨", tip)

    elif precip_prob > 20:
        if wind_speed > 20:
            if temp_cold:
                tip = "🧥 Breezy and chilly! Layer up for outdoor adventures - the fresh air is invigorating! 🌬️❄️"
            else:
                tip = "🎐 Perfect for flying kites or feeling the wind in your hair! Hold onto your hat! 🎩"
            return ("🌤️🌸", "Partly Cloudy & Windy",
                    "Nature's gentle breeze is here! 🌸💨", tip)
        else:
            if temp_cold:
                tip = "📸 Great lighting for photos! Dress warm and enjoy the crisp air! 🧣✨"
            else:
                tip = "📸 Great for photos! The lighting is *chef's kiss* perfect! ✨"
            return ("⛅💭", "Partly Cloudy",
                    "Soft clouds making art in the sky! 🎨", tip)

    else:  # Sunny conditions
        if wind_speed > 25:
            if temp_cold:
                tip = "🌞 Sunny but cold! Bundle up for winter walks - the sunshine makes it feel warmer! ❄️☀️"
            elif temp_hot:
                tip = "🌞 Hot and breezy! Stay hydrated and seek shade when needed! 💦🌴"
            else:
                tip = "🌞 Sun's out, fun's out! Don't forget sunscreen - SPF is your BFF! 🧴"
            return ("🌤️💫", "Sunny & Windy",
                    "Sparkly sunshine with a fun breeze! ✨💨", tip)
        else:
            if temp_cold:
                tip = "☀️ Sunny but chilly! Perfect for winter walks with warm layers and hot cocoa after! ☕❄️"
            elif temp_hot:
                tip = "☀️ It's sizzling! Stay cool, hydrate often, and enjoy ice cream in the shade! 🍦💦"
            elif temp_warm:
                tip = "☀️ Perfect weather! Ideal for outdoor fun - parks, picnics, or just vibing in the sunshine! 🧺"
            else:
                tip = "☀️ Beautiful day for outdoor activities! Enjoy the sunshine! 🌟"
            return ("☀️✨", "Sunny",
                    "Perfect day for adventures! 🌟", tip)


def get_weather_joke():
    """Returns a random weather-related joke or pun."""
    jokes = [
        "What's a tornado's favorite game? Twister! 🌪️",
        "Why did the sun go to school? To get brighter! ☀️📚",
        "What do you call dangerous precipitation? A rain of terror! 😱💧",
        "How do hurricanes see? With one eye! 👁️🌀",
        "What's a cloud's favorite type of music? Heavy metal... rain! 🎸☁️",
        "Why don't meteorologists ever win at poker? They always give away their tells about the weather! 🃏",
        "What did the thermometer say to the graduated cylinder? You may have graduated, but I have more degrees! 🌡️",
    ]
    return random.choice(jokes)


def get_mood_emoji(condition_name):
    """Returns mood emoji based on weather condition."""
    moods = {
        "Sunny": "😎 Feeling energized!",
        "Sunny & Windy": "🤗 Feeling playful!",
        "Partly Cloudy": "😌 Feeling peaceful!",
        "Partly Cloudy & Windy": "🥰 Feeling alive!",
        "Cloudy": "😴 Feeling cozy!",
        "Rainy": "🥺 Feeling contemplative!",
    }
    return moods.get(condition_name, "😊 Feeling good!")


def get_weather_twin_city(temperature, condition_name):
    """
    Find a city with similar weather conditions.
    Returns a fun fact about a weather twin city.
    """
    # Determine temperature category
    if temperature is None:
        temp_category = "moderate"
    elif temperature < 5:
        temp_category = "freezing"
    elif temperature < 15:
        temp_category = "cold"
    elif temperature < 25:
        temp_category = "moderate"
    else:
        temp_category = "hot"

    # Simplify condition name
    if "Rainy" in condition_name:
        condition_type = "rainy"
    elif "Cloudy" in condition_name:
        condition_type = "cloudy"
    else:
        condition_type = "sunny"

    # Database of cities with typical weather patterns
    weather_twins = {
        ("freezing", "sunny"): [
            ("Reykjavik, Iceland", "Known for its geothermal pools and northern lights! 🇮🇸"),
            ("Yellowknife, Canada", "One of the best places to see the aurora borealis! 🇨🇦"),
        ],
        ("freezing", "cloudy"): [
            ("Moscow, Russia", "Home to the colorful St. Basil's Cathedral! 🇷🇺"),
            ("Helsinki, Finland", "The happiest country with cozy cafes everywhere! 🇫🇮"),
        ],
        ("freezing", "rainy"): [
            ("Bergen, Norway", "The gateway to Norway's famous fjords! 🇳🇴"),
            ("Anchorage, Alaska", "Where you can spot whales and glaciers! 🇺🇸"),
        ],
        ("cold", "sunny"): [
            ("Prague, Czech Republic", "Famous for its fairy-tale architecture! 🇨🇿"),
            ("Seoul, South Korea", "Amazing street food and K-pop culture! 🇰🇷"),
        ],
        ("cold", "cloudy"): [
            ("London, England", "Home to double-decker buses and afternoon tea! 🇬🇧"),
            ("Dublin, Ireland", "Friendly pubs and beautiful green landscapes! 🇮🇪"),
        ],
        ("cold", "rainy"): [
            ("Seattle, USA", "Coffee capital and home of grunge music! 🇺🇸☕"),
            ("Vancouver, Canada", "Surrounded by mountains and ocean! 🇨🇦"),
        ],
        ("moderate", "sunny"): [
            ("Barcelona, Spain", "Famous for Gaudí's architecture and beaches! 🇪🇸"),
            ("San Francisco, USA", "Home to the Golden Gate Bridge! 🇺🇸"),
        ],
        ("moderate", "cloudy"): [
            ("Paris, France", "The city of love, art, and croissants! 🇫🇷"),
            ("Amsterdam, Netherlands", "Known for bikes, canals, and tulips! 🇳🇱"),
        ],
        ("moderate", "rainy"): [
            ("Portland, Oregon", "Known for its quirky culture and food trucks! 🇺🇸"),
            ("Wellington, New Zealand", "The coolest little capital in the world! 🇳🇿"),
        ],
        ("hot", "sunny"): [
            ("Dubai, UAE", "Home to the world's tallest building! 🇦🇪"),
            ("Los Angeles, USA", "Hollywood, beaches, and sunshine! 🇺🇸🌴"),
        ],
        ("hot", "cloudy"): [
            ("Singapore", "A garden city with amazing food! 🇸🇬"),
            ("Miami, USA", "Beautiful beaches and vibrant nightlife! 🇺🇸"),
        ],
        ("hot", "rainy"): [
            ("Bangkok, Thailand", "Street food paradise and golden temples! 🇹🇭"),
            ("Mumbai, India", "Bollywood central and incredible culture! 🇮🇳"),
        ],
    }

    # Get matching cities
    key = (temp_category, condition_type)
    cities = weather_twins.get(key, [("Earth", "We're all weather buddies! 🌍")])

    # Pick a random city
    city, fact = random.choice(cities)

    return f"🌍 **Weather Twin Alert!** Right now, **{city}** likely has similar weather! {fact}"


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
            st.error(f"🌐 Oopsie! Location detection had a hiccup: {data.get('message', 'Unknown error')} 😅")
            return None
    except requests.RequestException as e:
        st.error(f"🌐 The internet hamster needs a break! Network error: {e} 🐹💤")
        return None
    except Exception as e:
        st.error(f"✨ Something magical (but unexpected) happened: {e} 🎩✨")
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
        st.error(f"🌈 The weather clouds are being shy! Network error: {e} ☁️")
        return None
    except Exception as e:
        st.error(f"🌟 The weather fairies got confused: {e} 🧚‍♀️")
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
    with st.spinner("📍 Playing hide and seek with your location... 🔍✨"):
        geocode_result = get_location_from_ip()
    location_source = "auto"

    if geocode_result is None:
        st.error("🗺️ Oops! Your location is playing hide and seek! Try entering a city manually! 😊")

elif search_button:
    if not city_input or city_input.strip() == "":
        st.warning("🌟 Psst! Don't forget to tell me which city you're curious about! 💭")
    else:
        with st.spinner("🔍 Finding your happy place... 🗺️✨"):
            geocode_result = geocode_city(city_input.strip())
        location_source = "manual"

        if geocode_result is None:
            st.error("🗺️ Hmm, that city is being shy! Try adding a country or state? Like 'Paris, France' or 'Portland, Oregon'! 🌍")

# Display weather if we have valid coordinates
if geocode_result is not None:
    lat, lon, display_name = geocode_result

    if location_source == "auto":
        st.info(f"📍 **Your magical location: {display_name}** ✨")
    else:
        st.success(f"🎉 **Found it! {display_name}** 🌟")

    with st.spinner("🌈 Asking the clouds about their mood... ☁️💭"):
        weather_data = fetch_weather(lat, lon)

    if weather_data is None:
        st.error("😅 Oopsie! The weather data got lost in the clouds! Try again? 🌥️")
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

        condition_icon, condition_name, condition_desc, condition_tip = get_weather_condition(current_precip, current_wind, current_temp)

        # Display current weather
        st.subheader("Current Weather Vibes")
        st.markdown(f"### {condition_icon} {condition_name}")
        st.info(f"💭 {condition_desc}")

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

        st.write("---")

        # Mood of the day
        mood = get_mood_emoji(condition_name)
        st.subheader("Today's Mood")
        st.info(f"**{mood}**")

        # Weather tip section
        st.subheader("Weather Tip")
        st.success(condition_tip)

        # Weather twin city fun fact
        st.subheader("Twin Alert")
        twin_city_fact = get_weather_twin_city(current_temp, condition_name)
        st.info(twin_city_fact)

        # Weather joke
        st.subheader("Joke of the Day")
        joke = get_weather_joke()
        st.write(f"🎭 {joke}")

        st.write("---")

        # Generate and display prediction
        st.subheader("Crystal Ball")
        if current_temp is not None and forecast_24h:
            prediction = predict_trend(current_temp, forecast_24h)
            st.info(prediction)
        else:
            st.warning("🔮 The crystal ball is a bit foggy right now! 🌫️")

        # Show detailed hourly data in expandable section
        with st.expander("📋✨ Peek at the Next 12 Hours"):
            for hour in forecast_24h[:12]:  # Show first 12 hours
                time_str = hour["time"]
                try:
                    dt = datetime.fromisoformat(time_str)
                    display_time = dt.strftime("%H:%M")
                except:
                    display_time = time_str

                # Get condition icon for this hour
                hour_icon, _, _, _ = get_weather_condition(hour['precipitation_probability'], hour['wind_speed'], hour['temperature'])

                temp = f"{hour['temperature']:.1f}°C" if hour['temperature'] is not None else "N/A"
                precip = f"{hour['precipitation_probability']}%" if hour['precipitation_probability'] is not None else "N/A"
                wind = f"{hour['wind_speed']:.1f} km/h" if hour['wind_speed'] is not None else "N/A"

                st.text(f"{hour_icon} {display_time} | 🌡️ {temp} | 💧 {precip} | 💨 {wind}")

# Playful Footer
st.divider()
footer_messages = [
    "🌈 Made with love and kawaii vibes! Data by Open-Meteo.com ✨",
    "☀️ Stay sunny, stay awesome! Powered by Open-Meteo.com 💕",
    "🌸 Weather data brought to you with extra sparkles! ✨",
    "💫 Spreading weather joy one forecast at a time! 🌤️",
    "🎨 Making weather cute since today! Data: Open-Meteo.com 💖",
]
st.caption(random.choice(footer_messages))
