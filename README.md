# Hart-AI--Your-Experience-Chatbot
HART - Your Experience Planning Chatbot
Setup Instructions
1. Clone the Repository


git clone https://github.com/yourusername/your-repository-name.git
cd your-repository-name



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


