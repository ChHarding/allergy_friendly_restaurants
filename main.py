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
OVERPASS_URL = "https://overpass-api.de/api/interpreter" # Overpass API endpoint for querying OpenStreetMap data


def get_location(zip_code): # Function to convert user input location (ZIP code) into latitude and longitude coordinates using the Nominatim API
    NOMINATIMurl = "https://nominatim.openstreetmap.org/search" # Nominatim API endpoint for geocoding
    
    APIparams = { # Parameters for Nominatim API request
        "postalcode": zip_code,
        "country": "USA",
        "format": "json"
    }

    headers = {
        "User-Agent": "accessible-dining-app"  # REQUIRED by Nominatim API usage policy to identify the application making requests
    }

    APIresponse = requests.get(NOMINATIMurl, params=APIparams, headers=headers) # Send GET request to Nominatim API with specified parameters and headers
    NOMINATIMdata = APIresponse.json() # Parse the JSON response from the API into a list of dictionaries

    if NOMINATIMdata: # Check if the response contains any results (i.e., if the list is not empty)
        return float(NOMINATIMdata[0]["lat"]), float(NOMINATIMdata[0]["lon"]) # Return the latitude and longitude of the first result from the Nominatim API response
    
    return None, None



def fetch_restaurants(lat, lon, radius, dietary): # Function to fetch nearby restaurants from the Overpass API based on latitude, longitude, and search radius
    # Convert miles to meters 
    radius_km = radius * 1609  # meters (Overpass uses meters)

    # Create the dietary filter string for the Overpass API query based on the user's selected dietary filter. 
    # If a dietary filter is selected, it constructs a filter string that checks for the presence of the corresponding tag (e.g., "diet:gluten_free") with a value of "yes". 
    # If no dietary filter is selected, the filter string is set to an empty string, meaning that no additional filtering will be applied to the API query based on dietary needs.
    if dietary:
        dietary_filter = f'["diet:{dietary}"="yes"]'
    else:
        dietary_filter = ""

    # Construct the Overpass API query to retrieve nodes, ways, and relations that are tagged as restaurants and match the specified dietary filter within the given radius around the provided latitude and longitude.
    APIquery = f"""
    [out:json][timeout:60];
    (
      node
      ["amenity"="restaurant"]
      {dietary_filter}(around:{radius_km},{lat},{lon});
      
      way
      ["amenity"="restaurant"]
      {dietary_filter}(around:{radius_km},{lat},{lon});

      relation
      ["amenity"="restaurant"]
      {dietary_filter}(around:{radius_km},{lat},{lon});

    );
    out center tags;
    """
    # Send a POST request to the Overpass API with the constructed query to retrieve restaurant data in JSON format. 
    # The response is stored in the variable 'response'.
    response = requests.post(OVERPASS_URL, data=APIquery)

    # Print the status code and the first 300 characters of the response text for debugging purposes. 
    # This helps verify that the API request was successful and to inspect the raw response data.
    print("Status:", response.status_code)
    print(response.text[:300])

    # Check if the API request was successful (status code 200). 
    # If not, return an empty list to indicate that no restaurant data could be retrieved.
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

        if lat and lon:
            restaurants.append({
                "name": name,
                "lat": lat,
                "lon": lon,
                "tags": tags
            })

    return restaurants
   

# Function to compute a "safety score" for a restaurant based on the presence of dietary keywords in its tags. 
# The score is calculated by checking for specific dietary options (gluten-free, vegan, dairy-free) and incrementing the score for each option found.
# Extract the "tags" dictionary from the restaurant dictionary, which contains metadata about the restaurant. 
# If the "tags" key is not present, an empty dictionary is returned by default to avoid errors when accessing keys later in the function.
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



def filter_restaurants(data, filters): # Function to filter the list of restaurants based on user-selected criteria (dietary needs and cuisine type)
    filtered = [] # Initialize an empty list to store restaurants that meet the filter criteria

    for restaurant in data: # Iterate through each restaurant in the input data (list of restaurant dictionaries)
        # Extract the "tags" dictionary from the restaurant dictionary, which contains metadata about the restaurant.
        #If the "tags" key is not present, an empty dictionary is returned by default to avoid errors when accessing keys later in the function.
        tags = restaurant.get("tags", {})  
        # Check if the dietary filter is set and if the restaurant's tags do not contain the dietary keyword (case-insensitive). 
        # If so, skip this restaurant and move to the next iteration of the loop.
        tags_str = str(tags).lower()

        if filters["dietary"] and filters["dietary"] not in tags_str:
            continue

        # Check if the cuisine filter is set and if the restaurant's tags do not contain the cuisine keyword (case-insensitive). 
        # If so, skip this restaurant and move to the next iteration of the loop.
        if filters["cuisine"] and filters["cuisine"] not in tags_str:
            continue
        
        # Dietary filter checks: If the user has selected a specific dietary filter (e.g., "Gluten-free", "Vegan", "Dairy-free"), check if the corresponding tag in the restaurant's tags indicates that the restaurant offers that dietary accommodation.
        # If the restaurant does not offer the selected dietary accommodation (i.e., the tag value is not "yes"), skip this restaurant and move to the next iteration of the loop.
        if filters["dietary"] == "Gluten-free" and tags_str.get("diet:gluten_free") != "yes":
            continue
        if filters["dietary"] == "Vegan" and tags_str.get("diet:vegan") != "yes":
            continue
        if filters["dietary"] == "Dairy-free" and tags_str.get("diet:dairy_free") != "yes":
            continue

        filtered.append(restaurant) # If the restaurant passes both filter checks, add it to the filtered list
    
    return filtered



def generate_map(data): # Function to create a Folium map with markers for each restaurant in the input data (list of restaurant dictionaries)
    m = folium.Map(location=[data[0]["lat"], data[0]["lon"]], zoom_start=13) # Create a Folium map centered on the location of the first restaurant in the data list, with an initial zoom level of 13
    
    for restaurant in data: #  Iterate through each restaurant in the input data
        folium.Marker( # Add a marker to the map for each restaurant, with the following properties:
            location=[restaurant["lat"], restaurant["lon"]],
            popup=f"{restaurant['name']} - Safety Score: {restaurant['safety_score']}"
        ).add_to(m) # Add the marker to the Folium map object 'm'
    
    return m # Return the generated Folium map object with all restaurant markers added



def main(): # Main function to run the Streamlit app, which handles user input, data fetching, processing, and displaying results on an interactive map
    st.title("Accessible Dining Finder") # Set the title of the Streamlit app to "Accessible Dining Finder"
    
    location_input = st.text_input("Enter a location (e.g., ZIP code, city):") # Create a text input field for the user to enter a location (such as a ZIP code or city name) and store the input in the variable 'location_input'
    radius_input = st.number_input("Enter search radius (miles):", min_value=1, max_value=50, value=5) # Create a number input field for the user to specify the search radius in miles, with a minimum value of 1, a maximum value of 50, and a default value of 5. Store the input in the variable 'radius_input'
    dietary_filter = st.selectbox("Select dietary needs:", ["", "Gluten-free", "Vegan", "Dairy-free"]) # Create a dropdown select box for the user to choose a dietary filter (options include "Gluten-free", "Vegan", "Dairy-free", and an empty option for no filter). Store the selected option in the variable 'dietary_filter'
    cuisine_filter = st.text_input("Enter cuisine type (optional):") # Create a text input field for the user to optionally enter a cuisine type as a filter and store the input in the variable 'cuisine_filter'
    
    #Convert dietary filter input to tag format
    dietary_filter = dietary_filter.lower().replace(" ", "_") if dietary_filter else "" # Convert the user's selected dietary filter into a format that matches the expected tag format used in the restaurant data (e.g., "Gluten-free" becomes "gluten_free"). If no dietary filter is selected, set 'dietary_tag' to an empty string.

    if st.button("Search"): # Create a button labeled "Search" that the user can click to initiate the search process. When the button is clicked, the following code block will be executed:
        lat, lon = get_location(location_input) # Call the 'get_location' function with the user's location input to retrieve the corresponding latitude and longitude coordinates, and store them in the variables 'lat' and 'lon'
        restaurants = fetch_restaurants(lat, lon, radius_input, dietary_filter) # Call the 'fetch_restaurants' function with the retrieved latitude, longitude, and user-specified search radius to fetch a list of nearby restaurants. Store the resulting list of restaurant dictionaries in the variable 'restaurants'
        
        for restaurant in restaurants: # Iterate through each restaurant in the fetched list of restaurants
            restaurant["safety_score"] = compute_safety_score(restaurant) # For each restaurant, call the 'compute_safety_score' function to calculate its safety score based on the presence of dietary keywords in its tags, and add this score as a new key-value pair in the restaurant's dictionary under the key "safety_score"
        
        filters = {"dietary": dietary_filter, "cuisine": cuisine_filter} # Create a dictionary called 'filters' to store the user's selected dietary and cuisine filters, with keys "dietary" and "cuisine" corresponding to the respective user inputs
        filtered_restaurants = filter_restaurants(restaurants, filters) # Call the 'filter_restaurants' function with the list of restaurants and the filters dictionary to obtain a new list of restaurants that meet the specified criteria. Store this filtered list in the variable 'filtered_restaurants'
        
        if filtered_restaurants: # Check if the filtered list of restaurants is not empty (i.e., if there are any restaurants that match the user's criteria)
            restaurant_map = generate_map(filtered_restaurants) # If there are matching restaurants, call the 'generate_map' function with the filtered list of restaurants to create a Folium map with markers for each restaurant. Store the resulting map object in the variable 'restaurant_map'
            st_folium(restaurant_map, width=700, height=500) # Use the 'st_folium' function from the 'streamlit_folium' library to display the generated Folium map in the Streamlit app, with specified width and height dimensions
        
        else: # If the filtered list of restaurants is empty (i.e., no restaurants match the user's criteria), display a message to the user indicating that no restaurants were found matching the criteria
            st.write("No restaurants found matching the criteria.") #  Display a message in the Streamlit app to inform the user that no restaurants were found that match the specified filters



if __name__ == "__main__":
    main()
