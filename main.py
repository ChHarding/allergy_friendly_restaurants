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

from urllib import response

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
OVERPASS_URL = "https://overpass-api.de/api/interpreter" # Overpass API endpoint for querying OpenStreetMap data


def get_location(zip_code): # Function to convert user input location (ZIP code) into latitude and longitude coordinates using the Nominatim API
    NOMINATIMurl = "https://nominatim.openstreetmap.org/search" # Nominatim API endpoint for geocoding
    
    APIparams = {
        "q": zip_code,
        "format": "json",
        "countrycodes": "us",
        "limit": 1
    } # Parameters for Nominatim API request, including the query (ZIP code), response format (JSON), country code (US), and limit on the number of results (1)

    headers = {
        "User-Agent": "accessible-dining-app"  # reaquired by Nominatim API to identify the application making requests
    }

    APIresponse = requests.get(NOMINATIMurl, params=APIparams, headers=headers) # Send get request to Nominatim API with specified parameters and headers
    NOMINATIMdata = APIresponse.json() # Parse the JSON response from the API into a list of dictionaries

    if NOMINATIMdata: # Check if the response contains any results (i.e., if the list is not empty)
        return float(NOMINATIMdata[0]["lat"]), float(NOMINATIMdata[0]["lon"]) # Return the latitude and longitude of the first result from the Nominatim API response
    
    return None, None



def fetch_restaurants(lat, lon, radius, dietary): # Function to fetch nearby restaurants from the Overpass API based on latitude, longitude, and search radius
    # Convert miles to meters 
    radius_km = radius * 1609  # meters (Overpass uses meters)

    dietary_filter = ""  # filter results in Python instead of API

    # Construct the Overpass API query to retrieve nodes, ways, and relations that are tagged as restaurants and match the specified dietary filter within the given radius around the provided latitude and longitude.
    APIquery = f"""
    [out:json][timeout:60];
    (
    node["amenity"="restaurant"](around:{radius_km},{lat},{lon});
    way["amenity"="restaurant"](around:{radius_km},{lat},{lon});
    relation["amenity"="restaurant"](around:{radius_km},{lat},{lon});
    );
    out center;
    """
    # Send a post request to the Overpass API with the constructed query to retrieve restaurant data in JSON format
    # The response is stored in the variable 'response'
    response = requests.post(OVERPASS_URL, data={"data": APIquery}, headers={"User-Agent": "accessible-dining-app"})

    # Print the status code and the first 200 characters of the response text for debugging purposes. 
    # This helps to verify that the API request was successful and to inspect the raw response from the Overpass API
    print("Status:", response.status_code)
    print(response.text[:200])

    # Check if the API request was successful (status code 200)
    # If not, return an empty list to indicate that no restaurant data could be retrieved
    if response.status_code != 200:
        return []

    # Attempt to parse the JSON response from the Overpass API.
    # If there is an error during parsing (e.g., if the response is not valid JSON), catch the exception, print an error message, and return an empty list to indicate that no restaurant data could be processed.
    try:
        data = response.json()

    # Catch any exceptions that occur during the JSON parsing process, print an error message indicating that there was a JSON decode error along with the exception details, and return an empty list to indicate that no restaurant data could be processed due to the parsing error.
    except Exception as e:
        print("JSON decode error:", e)
        return []

    # Initialize an empty list called 'restaurants' to store the processed restaurant data that will be extracted from the API response. Each restaurant will be represented as a dictionary containing its name, latitude, longitude, and tags.
    restaurants = []

    # Iterate through each element in the "elements" list of the parsed JSON data from the Overpass API response. 
    # For each element, extract the relevant information such as the restaurant's name, latitude, longitude, and tags. 
    # Depending on whether the element is a node or a way/relation, the latitude and longitude are extracted differently (nodes have direct lat/lon, while ways/relations have a center with lat/lon).
    for i in data.get("elements", []):
        tags = i.get("tags", {})
        name = tags.get("name")

        if not name:
            continue

        if i["type"] == "node":
            lat = i.get("lat")
            lon = i.get("lon")
        else:
            center = i.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")

        if lat is not None and lon is not None:
            restaurants.append({
                "name": name,
                "lat": lat,
                "lon": lon,
                "tags": tags
            })

    return restaurants
   

# Function to compute a "safety score" for a restaurant based on the presence of specific dietary tags in the restaurant's metadata. 
# The safety score is calculated by checking for the presence of certain dietary options (e.g., gluten-free, vegan, dairy-free) in the restaurant's tags and incrementing the score accordingly. 
# The function returns an integer representing the computed safety score for the restaurant.
def compute_safety_score(restaurant): 

    tags = restaurant.get("tags", {}) 
    safety_score = 0 # Initialize the safety score to 0. This variable will be incremented based on the presence of dietary keywords in the restaurant's tags.

    # Check for the presence of specific dietary options in the restaurant's tags and increment the safety score accordingly. 
    # Each keyword corresponds to a particular dietary accommodation, and if the tag indicates that the restaurant offers that accommodation (e.g., "yes"), the safety score is increased by 1.
    if tags.get("diet:gluten_free") == "yes":
        safety_score += 1
    if tags.get("diet:vegan") == "yes":
        safety_score += 1
    if tags.get("diet:dairy_free") == "yes":
        safety_score += 1

    return safety_score # Return the computed safety score for the restaurant, which is an integer representing the number of dietary keywords found in the restaurant's tags


# Function to filter a list of restaurants based on user-selected criteria such as dietary needs. 
# The function takes in a list of restaurant dictionaries and a filters dictionary containing the user's selected filters. 
# It iterates through the list of restaurants and checks if each restaurant meets the specified criteria (e.g., if the restaurant has the required dietary tags). 
# If a restaurant meets all the criteria, it is added to the filtered list, which is returned at the end of the function.
def filter_restaurants(restaurants, filters):
    
    # Initialize an empty list called 'filtered' to store the restaurants that meet the specified filter criteria. 
    # This list will be populated with restaurant dictionaries that pass the filtering conditions based on the user's selected dietary needs and other criteria.
    filtered = []

    # Extract the dietary filter value from the filters dictionary. 
    # This value represents the user's selected dietary needs (e.g., "gluten_free", "vegan", "dairy_free").
    dietary = filters.get("dietary")
    #cuisine = filters.get("cuisine")

    # Iterate through each restaurant in the input list of restaurants. 
    # For each restaurant, extract its tags and check if it meets the specified dietary filter criteria.
    for r in restaurants:
        tags = r.get("tags", {})

        # dietary filter
        if dietary:
            tag_value = tags.get(f"diet:{dietary}")

            if tag_value not in ["yes", "only"]:
                continue
        
        """"
        # cuisine filter
        if cuisine:
            cuisine_tags = tags.get("cuisine", "")
            cuisine_list = cuisine_tags.lower().split(";")

            if cuisine.lower() not in cuisine_list:
                continue
        """
        #adds to filtered list if it passes all filters        
        filtered.append(r)

    return filtered


#TODO make sure map is showing pins for every location instead of weird graphics sometimes
def generate_map(data): # Function to create a Folium map with markers for each restaurant in the input data (list of restaurant dictionaries)
    if not data:
        return None  # prevent crash

    # Create a Folium map centered on the location of the first restaurant in the data list, with an initial zoom level of 13
    m = folium.Map(location=[data[0]["lat"], data[0]["lon"]], zoom_start=13)
    
    # Iterate through each restaurant in the input data list and add a marker to the Folium map for each restaurant
    # Each marker is placed at the restaurant's latitude and longitude coordinates, and includes a popup that displays the restaurant's name and its computed safety score when the marker is clicked
    for restaurant in data:
        folium.Marker(
            location=[restaurant["lat"], restaurant["lon"]],
            popup=f"{restaurant['name']} - Safety Score: {restaurant['safety_score']}"
        ).add_to(m)
    
    return m # Create a Folium map centered on the location of the first restaurant in the data list


#TODO make sure to let the user know the radius has to be between 5-50 mi
#TODO make this implementable on an app not just desktop
def main(): # Main function to run the Streamlit app, which handles user input, data fetching, processing, and displaying results on an interactive map
    
    # Check if the "results" key is not already present in the Streamlit session state. If it is not present, initialize it to None.
    if "results" not in st.session_state:
        st.session_state.results = None # Initialize a session state variable called "results" to store the list of restaurants fetched from the API. 
        #This allows the data to persist across user interactions within the Streamlit app.

    st.title("Accessible Dining Finder") # Set the title of the Streamlit app to "Accessible Dining Finder"
    
    location_input = st.text_input("Enter a location (e.g., ZIP code, city):") # Create a text input field for the user to enter a location (such as a ZIP code or city name) and store the input in the variable 'location_input'
    radius_input = st.number_input("Enter search radius (miles):", min_value=1, max_value=50, value=5) # Create a number input field for the user to specify the search radius in miles, with a minimum value of 1, a maximum value of 50, and a default value of 5. Store the input in the variable 'radius_input'
    dietary_filter = st.selectbox("Select dietary needs:", ["", "Gluten-free", "Vegan", "Dairy-free"]) # Create a dropdown select box for the user to choose a dietary filter (options include "Gluten-free", "Vegan", "Dairy-free", and an empty option for no filter). Store the selected option in the variable 'dietary_filter'
    #cuisine_filter = st.text_input("Enter cuisine type (optional):") # Create a text input field for the user to optionally enter a cuisine type as a filter and store the input in the variable 'cuisine_filter'
    
    #Convert dietary filter input to tag format
    dietary_filter = dietary_filter.lower().replace("-", "_").replace(" ", "_") # Convert the user's selected dietary filter into a format that matches the expected tag format used in the restaurant data (e.g., "Gluten-free" becomes "gluten_free"). If no dietary filter is selected, set 'dietary_tag' to an empty string.

    # The dietary filter is transformed to match the tag format used in the restaurant data.
    if st.button("Search"):
        lat, lon = get_location(location_input)
        #st.write(f"DEBUG location: lat={lat}, lon={lon}")

        # Fetch restaurants from the Overpass API based on the user's input location, search radius, and dietary filter. 
        # The fetched restaurant data is stored in the variable 'restaurants'.
        restaurants = fetch_restaurants(lat, lon, radius_input, dietary_filter)

        #parses through restaurant data and computes safety score for each restaurant, adding it as a new key-value pair in the restaurant dictionary
        for restaurant in restaurants:
            restaurant["safety_score"] = compute_safety_score(restaurant)

        #filters = {"dietary": dietary_filter, "cuisine": cuisine_filter}
        filters = {"dietary": dietary_filter}
        filtered_restaurants = filter_restaurants(restaurants, filters)

        # save results so it doesn't flicker on every interaction
        st.session_state.results = filtered_restaurants

    # Check if there are results stored in the session state. 
    # If there are results, display them on an interactive map using Folium. 
    results = st.session_state.results

    # If there are no results, prompt the user to enter a location and click Search.
    if results is None:
        st.write("Enter a location and click Search.")

    elif len(results) == 0:
        st.write("No restaurants found.")

    else:
        st.write(f"Showing {len(results)} restaurants")

        restaurant_map = generate_map(results)
        if restaurant_map:
            st_folium(restaurant_map, width=700, height=500)


#main function runs when entering this command in terminal in VScode: streamlit run "/Users/ctlott/Desktop/Master's Degree💅🏻/Python Application Development/allergy_friendly_restaurants/main.py"
if __name__ == "__main__":
    main()
