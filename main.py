# Accessible Dining Finder for Dietary Needs: Project Spec
# General Description of the Project
# •	Traditional restaurant discovery tools focus on general ratings and reviews but do not reliably surface information about menu details.
# •	This application aims to fill that gap by extracting and analyzing relevant information to generate a “dietary safety score” for each restaurant.
# •	The application will allow users to input a location (such as a ZIP code or city) to discover nearby dining options. 
# •	Restaurants will be displayed on an interactive map with markers indicating their location. 
# •	Selecting a restaurant will reveal additional details, including extracted review snippets mentioning dietary accommodations (e.g., “gluten-free options,” “vegan options”) and a computed safety score based on keyword analysis.
# •	Users will be able to filter results based on criteria such as dietary needs (gluten-free, vegan), cuisine type, and distance from their location. 
# •	External:
# o	Overpass API for retrieving restaurant location and metadata
# o	Streamlit for building the user interface
# o	Folium for rendering interactive maps
# o	Basic keyword matching for review analysis
# •	GUI: Web app using Streamlit, but initial development may simulate interactions via a Jupyter Notebook or CLI.
# •	Possible Enhancements:
# o	More advanced NLP (sentiment detection, more thorough menu analysis)
# o	Users contribute their own notes or experiences, stored locally to enhance the dataset (SQLite or CSV for storing user-generated data)
# Task Vignettes (User Activity “Flow”)
# •	Task 1: Search for Restaurants by Location
# oUser configurable fields: Location, Dietary needs, Radius
# •	Task 1 User Activity:
# o	User opens app and is prompted to enter a location (Input: location string)
# o	User enters mile radius from selected location
# o	User clicks “Search,” and app displays an interactive map populated with restaurant markers (Query Overpass API for nearby restaurants, output: map markers, store results in a list/dictionary or pandas DataFrame)
# o	User can click into map pins to view restaurant names, approximate distance, and a safety score
# •	Task 2: Apply Filters
# o	After viewing initial results, user can apply filters
# o	User configurable fields: Dietary needs, Distance, Cuisine
# •	Task 2 User Activity:
# o	User applies dietary filter “Gluten-free” (Input: Dietary keyword filter)
# o	User adjusts distance within a certain mile radius (Numeric input, validation: distance must be positive)
# o	User specifies cuisine type (Dropdown or text filter)
# o	User clicks “Apply Filters,” and the map updates. Restaurants that do not meet the criteria are removed, and the list view updates accordingly. Filtering occurs on pre-fetched dataset (no new API call) 
# •	Task 3: View Restaurant Details and Safety Score
# o	Restaurant details display when the user clicks on a restaurant pin on the map. This helps the user quickly assess whether the restaurant is safe for their needs.
# •	Task 3 User Activity:
# o	User clicks on a restaurant pin
# o	User views restaurant name, location, computed “safety score” (safety score based on frequency of keyword matching (“gluten free”), output stored as part of restaurant object/dict)
# Technical “Flow”
# Data Structures: Restaurant dataset is a list of dictionaries OR pandas DataFrame with fields including name, latitude/longitude, cuisine (if available), raw tags/description, safety_score, and extracted_keywords. The user input config (dict) contains the location, radius, dietary_filter, and cuisine_filter.
# Core Functions:
# •	def get_location(user_input):
# o	Convert location string to lat/long (or use default)
# o	return lat, lon
# •	def fetch_restaurants(lat, lon, radius):
# o	Call Overpass API
# o	Parse JSON response
# o	return restaurant_list
# •	def compute_safety_score(restaurant):
# o	Keyword matching on tags/menus
# o	Assign score based on presence of keywords
# o	return score
# •	def filter_restaurants(data, filters):
# o	Apply dietary, distance, cuisine filters
# o	return filtered_data
# •	def generate_map(data):
# o	Create Folium map
# o	Add markers with popups
# o	return folium_map
# Program Flow:
# •	User launches Streamlit app
# •	App collects location input
# •	get_location() resolves coordinates
# •	fetch_restaurants() retrieves data from Overpass API
# •	For each restaurant, compute_safety_score() is applied
# •	Data stored in DataFrame
# •	User applies filters with filter_restaurants()
# •	generate_map() renders results
# •	User interacts with markers and then details are displayed
# •	API fetch, then parsing, then keyword analysis, then scoring, then filtering
# •	Output: Map (Folium), detail panel (details and score)

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
def get_location(user_input):
    # Placeholder for geocoding logic
    return 40.7128, -74.0060  # Example: New York City coordinates
def fetch_restaurants(lat, lon, radius):
    # Placeholder for Overpass API call
    # Example response structure
    return [
        {"name": "Gluten-Free Bistro", "lat": 40.7138, "lon": -74.0065, "tags": "gluten-free options available"},
        {"name": "Vegan Delight", "lat": 40.7120, "lon": -74.0050, "tags": "vegan menu items"},
        {"name": "Regular Diner", "lat": 40.7140, "lon": -74.0070, "tags": "no specific dietary accommodations"}
    ]
def compute_safety_score(restaurant):
    keywords = ["gluten-free", "vegan", "dairy-free"]
    score = sum(1 for keyword in keywords if keyword in restaurant["tags"].lower())
    return score
def filter_restaurants(data, filters):
    filtered = []
    for restaurant in data:
        if filters["dietary"] and filters["dietary"] not in restaurant["tags"].lower():
            continue
        if filters["cuisine"] and filters["cuisine"].lower() not in restaurant["tags"].lower():
            continue
        filtered.append(restaurant)
    return filtered
def generate_map(data):
    m = folium.Map(location=[data[0]["lat"], data[0]["lon"]], zoom_start=13)
    for restaurant in data:
        folium.Marker(
            location=[restaurant["lat"], restaurant["lon"]],
            popup=f"{restaurant['name']} - Safety Score: {restaurant['safety_score']}"
        ).add_to(m)
    return m
def main():
    st.title("Accessible Dining Finder")
    location_input = st.text_input("Enter a location (e.g., ZIP code, city):")
    radius_input = st.number_input("Enter search radius (miles):", min_value=1, max_value=50, value=5)
    dietary_filter = st.selectbox("Select dietary needs:", ["", "Gluten-free", "Vegan", "Dairy-free"])
    cuisine_filter = st.text_input("Enter cuisine type (optional):")
    if st.button("Search"):
        lat, lon = get_location(location_input)
        restaurants = fetch_restaurants(lat, lon, radius_input)
        for restaurant in restaurants:
            restaurant["safety_score"] = compute_safety_score(restaurant)
        filters = {"dietary": dietary_filter, "cuisine": cuisine_filter}
        filtered_restaurants = filter_restaurants(restaurants, filters)
        if filtered_restaurants:
            restaurant_map = generate_map(filtered_restaurants)
            st_folium(restaurant_map, width=700, height=500)
        else:
            st.write("No restaurants found matching the criteria.")
if __name__ == "__main__":
    main()
