import streamlit as st
import googlemaps
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json
from dotenv import load_dotenv
import os
import ssl
import random

# Load environment variables from .env file
def load_environment_variables():
    load_dotenv()
    ssl._create_default_https_context = ssl._create_unverified_context

# Initialize clients
def initialize_clients():
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    return googlemaps.Client(key=google_maps_api_key), sendgrid_api_key

# Parsing JSON to extract experiences
def parse_json(file_path):
    with open(file_path, 'r') as file:
        experiences = json.load(file)
    return experiences

# Function to filter experiences by type
def filter_experiences_by_type(experiences, experience_type):
    return [exp for exp in experiences if exp["Experience_Type"] == experience_type]

# Function to find specific places related to the experience using a keyword
def find_places_nearby_experience(gmaps, location, experience_keyword):
    places_result = gmaps.places_nearby(location=location, radius=8047, keyword=experience_keyword)
    return places_result['results']  # Return all places

# Function to find restaurant recommendations based on experience type and location
def find_restaurants_nearby(gmaps, location, experience_keyword):
    places_result = gmaps.places_nearby(location=location, radius=16093, keyword=experience_keyword + " restaurant")  # 5-10 miles (16093 meters)
    restaurants = [place for place in places_result['results'] if place['rating'] >= 4.0][:3]  # Top 3 restaurants
    return restaurants

# Function to send email using SendGrid
def send_email(sendgrid_api_key, user_email, name, experience, description, location, places, restaurants=None):
    places_html = ''.join([f'<li>{place["name"]} - {place["vicinity"]}</li>' for place in places])
    restaurants_html = ''.join([f'<li>{restaurant["name"]} - {restaurant["vicinity"]} (Rating: {restaurant["rating"]})</li>' for restaurant in restaurants]) if restaurants else ''

    html_content = f"""
    Hi {name},<br><br>
    Here is your experience suggestion:<br>
    <strong>{experience}</strong><br>
    Description: {description}<br>
    Location: {location}<br>
    Recommended Places to Enjoy Your Experience:<br>
    <ul>{places_html}</ul>
    """
    
    if restaurants_html:
        html_content += f"<br>Here are some restaurant recommendations:<br><ul>{restaurants_html}</ul>"

    html_content += "<br>Thank you!"

    message = Mail(
        from_email='info@mydatejar.com',
        to_emails=user_email,
        subject='Your Experience Suggestion from Hart',
        html_content=html_content
    )

    sg = SendGridAPIClient(sendgrid_api_key)
    response = sg.send(message)
    return response

# Function to handle the Streamlit UI
def streamlit_ui():
    st.title("HART! Your Experience Planning Chatbot")

    user_name = st.text_input("Please enter your name")
    
    if not user_name:
        st.write("Please enter your name to begin.")
        return

    st.write(f"Hi {user_name}, let's plan your experience!")
    experiences = parse_json("full_experience_list.json")
    
    experience_types = list(set(exp["Experience_Type"] for exp in experiences))
    selected_experience_type = st.selectbox("Choose your Experience Type", [""] + experience_types)

    if not selected_experience_type:
        st.write("Please select an experience type to see suggestions.")
        return

    filtered_experiences = filter_experiences_by_type(experiences, selected_experience_type)
    if not filtered_experiences:
        st.write("No experiences found for this type.")
        return

    selected_experience = random.choice(filtered_experiences)
    experience = selected_experience["Experience"]
    description = selected_experience["Description"]

    st.write(f"Here’s your suggested experience: **{experience}**")
    st.write(f"Description: {description}")

    city = st.text_input("Enter your city")
    state = st.text_input("Enter your state")

    if not city or not state:
        st.write("Please enter both city and state to proceed.")
        return

    st.write(f"Great! You chose {experience} in {city}, {state}.")
    gmaps, sendgrid_api_key = initialize_clients()
    
    geocode_result = gmaps.geocode(f"{city}, {state}")
    if not geocode_result:
        st.write("Unable to find the location. Please enter a valid city and state.")
        return
    
    location = geocode_result[0]["geometry"]["location"]
    formatted_address = geocode_result[0]["formatted_address"]
    st.write(f"Suggested location: {formatted_address}")

    setup_session_state()
    manage_experience_suggestion(gmaps, location, experience, formatted_address, description, user_name, sendgrid_api_key, selected_experience_type)

# Function to set up session state variables
def setup_session_state():
    if 'liked' not in st.session_state:
        st.session_state.liked = False
    if 'retry_count' not in st.session_state:
        st.session_state.retry_count = 0
    if 'places_queue' not in st.session_state:
        st.session_state.places_queue = []
    if 'current_place' not in st.session_state:
        st.session_state.current_place = None

# Function to suggest places and handle user interaction
def manage_experience_suggestion(gmaps, location, experience, formatted_address, description, user_name, sendgrid_api_key, experience_type):
    retry_count = st.session_state.retry_count

    # Suggest new places if not liked or first time
    def suggest_places():
        if not st.session_state.places_queue:
            nearby_places = find_places_nearby_experience(gmaps, location, experience)
            random.shuffle(nearby_places)
            st.session_state.places_queue = nearby_places
        return st.session_state.places_queue.pop(0) if st.session_state.places_queue else None

    if not st.session_state.current_place:
        st.session_state.current_place = suggest_places()

    if st.session_state.current_place:
        place = st.session_state.current_place
        st.write(f"Here is a nearby place where you can enjoy the experience:")
        st.write(f"- {place['name']} - {place['vicinity']}")
    else:
        st.write("No more places available for this experience.")
        st.button("Proceed to restaurant suggestions and email", key="proceed")
        return

    # Ask user if they like the current suggestion
    if not st.session_state.liked:  # Only ask if user has not liked a suggestion
        like_suggestion = st.radio("Do you like this suggestion?", ("Yes", "No"), key=f"like_suggestion_{retry_count}")

        if st.button("Submit", key=f"submit_{retry_count}"):
            if like_suggestion == "Yes":
                st.session_state.liked = True
                st.write("You've accepted the suggestion. We will not suggest more locations.")
            elif like_suggestion == "No":
                st.session_state.retry_count += 1
                st.session_state.liked = False
                st.session_state.current_place = suggest_places()
                if not st.session_state.current_place:
                    st.write("No more places available for this experience.")
                    st.button("Proceed to restaurant suggestions and email", key="proceed_no_more")
                    return

                # Display the new place and reset the loop
                st.write(f"Here is another nearby place where you can enjoy the experience:")
                place = st.session_state.current_place
                st.write(f"- {place['name']} - {place['vicinity']}")
                st.button("Submit New Suggestion", key=f"submit_new_{retry_count}")

    # If a suggestion is liked, proceed to send email and restaurant recommendation
    if st.session_state.liked:
        nearby_places = [st.session_state.current_place]

        want_restaurant = st.radio("Would you like a restaurant recommendation?", ("No", "Yes"), key="want_restaurant")
        restaurants = None
        if want_restaurant == "Yes":
            st.write("Fetching top-rated restaurants...")
            restaurants = find_restaurants_nearby(gmaps, location, experience_type)  # Updated to include experience type in search
            if restaurants:
                for restaurant in restaurants:
                    st.write(f"- {restaurant['name']} - {restaurant['vicinity']} (Rating: {restaurant['rating']})")

        user_email = st.text_input("Enter your email to receive details")
        if st.button("Send Email", key="send_email"):
            response = send_email(sendgrid_api_key, user_email, user_name, experience, description, formatted_address, nearby_places, restaurants)
            if response.status_code == 202:
                st.success("Email sent successfully!")
            else:
                st.error("Failed to send the email.")

# Main function
def main():
    load_environment_variables()
    streamlit_ui()

if __name__ == "__main__":
    main()
