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