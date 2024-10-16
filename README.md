# Hart-AI--Your-Experience-Chatbot
HART - Your Experience Planning Chatbot
Setup Instructions


Make Sure that Python is Installed on your system Golbally.

Make sure you have a file named full_experience_list.json in your project directory. This file should contain a list of experiences in the following format:

json

[
  {
    "Experience": "Skydiving",
    "Description": "Jump out of a plane and experience freefall.",
    "Experience_Type": "Adventure"
  },
  ...
]

1. Clone the Repository



2. Create a Virtual Environment


python -m venv venv


Activate the virtual environment:
Windows:
bash
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate



3. Install Dependencies


pip install streamlit googlemaps sendgrid python-dotenv openai



4. Add Your API Keys

Create a `.env` file in the root directory of the project and add your Google Maps,OpenAI and SendGrid API keys:

GOOGLE_MAPS_API_KEY=your-google-maps-api-key
SENDGRID_API_KEY=your-sendgrid-api-key
OPENAI_API_KEY=your-openai-api-key


5. Run the App


streamlit run your_script_name.py

This will launch the app in your browser, allowing you to interact with it.


