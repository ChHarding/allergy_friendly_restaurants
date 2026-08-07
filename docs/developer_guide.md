# Developer Documentation – Restaurant Finder App

## Overview

This is a Streamlit-based web application that allows users to search for restaurants based on location and radius. It integrates with an external API to fetch restaurant data and displays results dynamically.

---

## Project Structure

```bash
project/
│
├── main.py                # Entry point (run this)
├── requirements.txt
└── docs/
    └── developer_guide.md

Setup Notes (Developer-Specific)
Streamlit runs in a reactive model (important for debugging UI updates)

User Flow → Code Flow
1. App Launch
main.py initializes the Streamlit UI

2. User Input
location_input = st.text_input(...)

3. Search Trigger
When the user submits:
restaurants = fetch_restaurants(lat, lon, radius_input, bbox)

4. Data Processing
API response is parsed into a usable format (list/dict)

5. Display
Results rendered using:
st.write
st.map
tables

Key Functions
fetch_restaurants(lat, lon, radius, bbox)

Purpose:
Fetch restaurant data from API

Returns:
List of restaurant objects

Notes:
Depends on API response format
Handles request and parsing


Debug Logging
st.write(f"DEBUG: Raw restaurants fetched = {len(restaurants)}")
Used to verify API response size.


UI Styling
Custom CSS is injected via:
st.markdown("<style>...</style>", unsafe_allow_html=True)


Important Note
Streamlit components share selectors like:
div[data-testid="stTextInput"]
This can unintentionally style all inputs.
Fix: Use custom wrappers like:
<div class="green-search">


Known Issues
Minor:
CSS sometimes affects unintended elements
UI inconsistencies across browsers
Major:
API failures are not always gracefully handled
Invalid locations may break coordinate conversion


Potential Inefficiencies
API calls are synchronous which may slow UI
No caching (st.cache_data) implemented yet
Large radius → slower responses


TODO/ Improvements
# TODO: Add caching for API calls
# TODO: Add error handling for invalid API responses
# TODO: Improve CSS targeting specificity


Future Work
Add filters (rating, cuisine)
Integrate advanced map visualization (Leaflet/Mapbox)


Extending the Project
To Add Features:
Add new UI inputs in main.py
Extend fetch_restaurants() to support filters
Modify display logic accordingly


To Swap API:
Replace logic inside fetch_restaurants()
Keep the same return format to avoid breaking the UI


Misc Design Notes:
Streamlit reruns the script on every interaction
State must be handled carefully using st.session_state
UI and logic are tightly coupled


Final Advice for Developers
If you're taking over this project:
Start with main.py
Trace data flow from input → API → display
Be careful when modifying CSS (it has global impact)
Add logging early when debugging


Optional Enhancement:
Deploy via Streamlit Cloud
