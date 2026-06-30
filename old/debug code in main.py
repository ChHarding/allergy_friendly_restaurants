            """ 
        st.session_state.raw_restaurants = restaurants # Store the raw restaurant data in session state for debugging purposes
        examples = []

        for r in restaurants:
            tags = r.get("tags", {})
            if any(k.startswith("diet:") for k in tags):
                examples.append(tags)
            
            if len(examples) >= 5:
                break

        st.write("Sample dietary-tagged restaurants:", examples)
         """
        """
        total = len(restaurants)

        with_diet = sum(
            1 for r in restaurants
            if any(k.startswith("diet:") for k in r.get("tags", {}))
        )

        st.write(f"Total restaurants: {total}")
        st.write(f"Restaurants with ANY diet tags: {with_diet}")
        """



"""
    if "raw_restaurants" in st.session_state and st.session_state.raw_restaurants:

        restaurants = st.session_state.raw_restaurants

        examples = []

        for r in restaurants:
            tags = r.get("tags", {})
            if any(k.startswith("diet:") for k in tags):
                examples.append(tags)

            if len(examples) >= 5:
                break
    """

#old api query
# Construct the Overpass API query to retrieve nodes, ways, and relations that are tagged as restaurants and match the specified dietary filter within the given radius around the provided latitude and longitude.
    APIquery = f"""
#   [out:json][timeout:60];
#    (
#    node["amenity"="restaurant"](around:{radius_km},{lat},{lon});
#    way["amenity"="restaurant"](around:{radius_km},{lat},{lon});
#   relation["amenity"="restaurant"](around:{radius_km},{lat},{lon});
#    );
#    out center;
#    """


    # In fetch_restaurants
    # Print the status code and the first 200 characters of the response text for debugging purposes
    #verify that API request was successful and inspect raw response from Overpass API
    #print("Status:", response.status_code)
    #print(response.text[:200])