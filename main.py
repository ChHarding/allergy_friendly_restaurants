# Accessible Dining Finder for Dietary Needs

#imports
from urllib import response
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd

# Overpass API endpoint for querying OpenStreetMap data
OVERPASS_URL = "https://overpass-api.de/api/interpreter" 


#converts input location into lat and lon using Nominatim API endpoint for geocoding 
#Parameters for Nominatim API request include the location/zip/county, json response format,
# country code (US), and limit on the number of results (1)
# headers are required by Nominatim API to identify the application making requests
# APIresponse gets request to Nominatim API with specified parameters and headers
# NOMINATIMdata parses JSON response from API into list of dictionaries
def get_location(location): 
    NOMINATIMurl = "https://nominatim.openstreetmap.org/search"
    
    APIparams = {
        "q": location,
        "format": "json",
        "countrycodes": "us",
        "limit": 1,
        "addressdetails": 1,
        "polygon_geojson": 0
    } 
    
    headers = {
        "User-Agent": "accessible-dining-app"  
    }

    APIresponse = requests.get(NOMINATIMurl, params=APIparams, headers=headers)
    NOMINATIMdata = APIresponse.json() 
    
    # checks json response
    if not NOMINATIMdata:
        return None, None, None
    
    # gets response from API
    result = NOMINATIMdata[0] 

    # assigns values to lat and lon from API call
    lat = float(result["lat"])
    lon = float(result["lon"])

    # creates bounding box to align lat/lon with vague city/county names
    bbox = result.get("boundingbox", None)

    return lat, lon, bbox

#fetches nearby restaurants from the Overpass API based on latitude, longitude, and search radius
#adds a bounding box parameter optionally
# Convert miles to meters since overpass uses meters
# dietary_filter filters results in Python instead of API
#determines API query based on if the user entered a city/county and needs a bounding box
# Sends post request to Overpass API with query to retrieve restaurant data in JSON format
# post request response is stored in the variable 'response'
def fetch_restaurants(lat, lon, radius, bbox=None): 

    radius_km = radius * 1609 

    dietary_filter = ""  

    
    if bbox:
        lat1, lat2, lon1, lon2 = bbox

        APIquery = f"""
        [out:json][timeout:60];
        (
        node["amenity"="restaurant"]({lat1},{lon1},{lat2},{lon2});
        way["amenity"="restaurant"]({lat1},{lon1},{lat2},{lon2});
        relation["amenity"="restaurant"]({lat1},{lon1},{lat2},{lon2});
        );
        out center;
        """
    else:
        APIquery = f"""
        [out:json][timeout:60];
        (
        node["amenity"="restaurant"](around:{radius_km},{lat},{lon});
        way["amenity"="restaurant"](around:{radius_km},{lat},{lon});
        relation["amenity"="restaurant"](around:{radius_km},{lat},{lon});
        );
        out center;
        """

    response = requests.post(OVERPASS_URL, data={"data": APIquery}, headers={"User-Agent": "accessible-dining-app"})


    # Check if API request was successful (status code 200)
    # If not, return empty list to show no restaurant data could be retrieved
    if response.status_code != 200:
        return []

    # Attempt to parse the JSON response from the Overpass API.
    # If error during parsing (e.g., if the response is not valid JSON), catch exception, 
    # print error message, return empty list to show that there's no restaurant data
    try:
        data = response.json()

    except Exception as e:
        print("JSON decode error:", e)
        return []

    # Initialize empty list to store restaurant data extracted from API response. 
    # Each restaurant is represented as a dict containing name, lat, lon, and tags.
    restaurants = []

    # Iterate through each element in the "elements" list of the parsed JSON data from API response. 
    # extract  relevant info such as restaurant's name, latitude, longitude, and tags. 
    # whether the element is a node or a way/relation, the latitude and longitude are extracted differently 
    # (nodes have direct lat/lon, ways/relations have a center with lat/lon)
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
   

# compute "safety score" for a restaurant based on how many preferred dietary tags are in its metadata. 
#ie, if someone selects "gluten free" and "vegan" and a restaurant has both, it will receive a score of 2
#returns an integer representing the computed safety score for the restaurant.
# safety score initialized to 0. incremented based on the dietary keywords in tags.
def compute_safety_score(restaurant): 

    tags = restaurant.get("tags", {}) 
    safety_score = 0 

    if tags.get("diet:gluten_free") == "yes":
        safety_score += 1
    if tags.get("diet:vegan") == "yes":
        safety_score += 1
    if tags.get("diet:dairy_free") == "yes":
        safety_score += 1

    return safety_score 


# Filters list of restaurants based on user-selected criteria (location, dietary needs, radius)
# takes in a list of restaurant dicts and a filters dict of users' filters. 
# Initializes empty list 'filtered' to store restaurants that meet specified filter criteria. 
# Extract the dietary filter value from the filters dictionary. 
# iterates through list of restaurants to check if any meet the specified dietary tags
# If a restaurant meets all criteria, it's added to filtered list
# filtered list is returned at the end of the function.
def filter_restaurants(restaurants, filters):
    
    filtered = []

    dietary = filters.get("dietary")
    #cuisine = filters.get("cuisine")

    for r in restaurants:
        tags = r.get("tags", {})

        # dietary filter
        if dietary:
            all_match = True

            # parses through the dietary tags to find which ones have been selected, if any
            for d in dietary:
                tag_value = tags.get(f"diet:{d}")

                if tag_value not in ["yes", "only"]:
                    all_match = False
                    break
                
            # if no dietary tags have been selected, then continue
            if not all_match:
                continue
        
        #adds to filtered list if it passes all filters        
        filtered.append(r)

    return filtered


# creates a Folium map with markers for each restaurant in input data (list of restaurant dictionaries)
# Create Folium map centered on  location of first restaurant in data list, with initial zoom of 13
# Iterate through each restaurant in input data list and add marker to Folium map for each
# Each marker is at the restaurant's lat and lon coordinates
# Each marker has a popup displaying restaurant's name and safety score when the marker is clicked
# Returns Folium map centered on the location of the first restaurant in the data list
def generate_map(data):

    # prevent crash
    if not data:
        return None  

    m = folium.Map(location=[data[0]["lat"], data[0]["lon"]], zoom_start=13)
    
    
    for restaurant in data:
        folium.Marker(
            location=[restaurant["lat"], restaurant["lon"]],
            popup=f"{restaurant['name']} - Safety Score: {restaurant['safety_score']}"
        ).add_to(m)
    
    return m 

#TODO move the instructions above the text entry fields
#TODO make this implementable on an app not just desktop
# runs Streamlit, handles user input, data fetching, processing, displaying results on interactive map
# check if "results" key is present in the Streamlit session state, if it is not present, initialize it to None.
# Initialize session state variable "results" to store list of restaurants fetched from API. 
# Create text input field for user to enter a location and store input in variable 'location_input'
# Create select box for user to multi select dietary needs ("Gluten-free", "Vegan", "Dairy-free", or none)
# Store the selected dietary option in 'dietary_filter'
def main(): 
    
    #This allows the data to persist across user interactions within the Streamlit app.
    if "results" not in st.session_state:
        st.session_state.results = None 
    
    #prevent the map from re-rendering too often
    if "map" not in st.session_state:
        st.session_state.map = None

    # Set the title of the Streamlit app to "Accessible Dining Finder"
    st.title("Accessible Dining Finder") 
    

    location_input = st.text_input("Enter a location (ZIP, city, or county):") 
    radius_input = st.number_input("Enter search radius (5-50 miles):", min_value=1, max_value=50, value=5)
    dietary_options = st.multiselect(
        "Select dietary needs:",
        ["Gluten-free", "Vegan", "Dairy-free"]
    ) 
    #cuisine_filter = st.text_input("Enter cuisine type (optional):") 
    

    #Convert dietary filter input to tag format
    dietary_filters = [
        d.lower().replace("-", "_").replace(" ", "_")
        for d in dietary_options
    ] 


    # The dietary filter is transformed to match the tag format used in the restaurant data.
    if st.button("Search"):
        lat, lon, bbox = get_location(location_input)

        if lat is None or lon is None:
            st.error("Could not find that location. Try a different city, ZIP, or county.")
            return
        #st.write(f"DEBUG location: lat={lat}, lon={lon}")

        # Fetch restaurants from API based on the user input location, radius, and dietary filters. 
        restaurants = fetch_restaurants(lat, lon, radius_input, bbox)

        #parses restaurant data, computes safety score, adds it as a key-value pair in restaurant dict
        for restaurant in restaurants:
            restaurant["safety_score"] = compute_safety_score(restaurant)

        #filters = {"dietary": dietary_filter, "cuisine": cuisine_filter}
        filters = {"dietary": dietary_filters}
        filtered_restaurants = filter_restaurants(restaurants, filters)

        # save results so it doesn't flicker on every interaction
        st.session_state.results = filtered_restaurants
        st.session_state.map = generate_map(filtered_restaurants)  # store map

    # Check if there are results stored in the session state, if so, show on Folium map
    results = st.session_state.results

    # If no results, prompt user to enter a location and click Search.
    if results is None:
        st.write("Enter a location and click Search.")

    elif len(results) == 0:
        st.write("No restaurants found.")

    else:
        st.write(f"Showing {len(results)} restaurants")

        #builds folium map with 700 width and 500 height
        if st.session_state.map:
            st_folium(st.session_state.map, width=700, height=500)


#main
if __name__ == "__main__":
    main()
