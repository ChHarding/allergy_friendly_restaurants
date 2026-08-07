
````markdown
# Allergy Friendly Restaurants  
## EZ Dietary Dining App: User Guide

This app helps you find restaurants near a location you enter (ZIP, city, or county). Users can search within a radius between 5–50 miles and optionally filter by dietary needs such as gluten-free, vegan, or dairy-free.

The app uses a map-based search to display nearby results based on your input.

---

## Installation Requirements

- Python 3.10+
- pip (Python package manager)

---

## Clone the Repository

```bash
gh repo clone ctlott00/allergy_friendly_restaurants
````

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

OR install manually:

```bash
pip install streamlit requests pandas
```

---

## Running the App

### Option 1: Use the Hosted App

Access on mobile or desktop:
[https://ez-dietary-dining.onrender.com](https://ez-dietary-dining.onrender.com)

### Option 2: Run Locally

```bash
streamlit run app.py
```

---

## How to Use the App

1. **Enter Location**
   Type a ZIP code, city, or county into the location box.

2. **Adjust Search Radius**
   Choose how far out to search (5–50 miles).

3. **Select Dietary Needs** *(optional)*
   Choose filters: gluten-free, vegan, and/or dairy-free.

4. **Click Search**
   Results will load below.

5. **View Results**
   Restaurants will appear on an interactive map.

---

## Common Problems + Solutions

**Problem:** No results found
**Solution:** Try increasing the search radius

**Problem:** Invalid location
**Solution:** Enter a more specific location (ZIP code works best)

---

## Known Limitations

* Some locations may return limited data
* API rate limits may restrict usage
* UI styling may vary slightly across devices

---

## Screenshots

![Screenshot 1](https://github.com/user-attachments/assets/5887bed3-dfe8-49e7-a6bd-3b390d51f6fa)

![Screenshot 2](https://github.com/user-attachments/assets/4edf2936-d88e-460c-b99d-cd192163c034)

![Screenshot 3](https://github.com/user-attachments/assets/29c24f5b-c2ba-4092-b737-8b1653c3f142)

---

## Future Ideas to Improve

* More advanced filters (price, rating, cuisine)
* Improved map visualization
* Ability to save favorite restaurants

