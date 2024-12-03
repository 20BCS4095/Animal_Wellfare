from flask import Flask, render_template, request, redirect, url_for,Response
import pandas as pd
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

# Initialize Twilio client (you need to get these from Twilio account)
TWILIO_PHONE_NUMBER = '+17752629661'
TWILIO_ACCOUNT_SID = 'AC749485ba42d2b47677f7a93905f99c16'
TWILIO_AUTH_TOKEN = '7c57e2f53643e4783e07bc8a803bdfc7'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Load the Excel sheet (this should be placed in the same directory or provide path)
df = pd.read_excel('dog_data.xlsx')

# Route to show the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        animal_name = request.form['animal_name']  # animal name field
        animal_type = request.form['animal_type']  # animal type field
        species = request.form['species']  # species field

        # Find matching record in the Excel sheet
        matching_record = df[
            (df['animal_name'].str.lower() == animal_name.lower()) &
            (df['animal_type'].str.lower() == animal_type.lower()) &
            (df['species'].str.lower() == species.lower())  # Matching species
        ]
        
        if not matching_record.empty:
            owner_name = matching_record.iloc[0]['owner_name']
            phone_number = "+91" + str(matching_record.iloc[0]['phone_number'])
            ngo ="Animal Welfare"
            ngo_number="+917358933435"
            # Send a message to the owner's phone number
            message = client.messages.create(
                body=f"Hello {owner_name}, we have matched your {animal_name} ({animal_type}, {species}).",
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            message = client.messages.create(
                body=f"Hello {ngo}, we have matched your {animal_name} ({animal_type}, {species}).",
                from_=TWILIO_PHONE_NUMBER,
                to=ngo_number
            )
            call = client.calls.create(
                to=phone_number,  # Recipient's phone number
                from_=TWILIO_PHONE_NUMBER,  # Your Twilio number
                url='https://animal-wellfare1.onrender.com/voice'  # This URL will provide the TwiML instructions
            )
            
            return render_template('index.html', message=f"Message sent to {owner_name} at {phone_number}. And also for NGO {ngo}.")
        else:
            ngo ="Animal Welfare"
            ngo_number="+917358933435"
            message = client.messages.create(
                body=f"Hello {ngo}, we have matched your {animal_name} ({animal_type}, {species}).",
                from_=TWILIO_PHONE_NUMBER,
                to=ngo_number
            )
            return render_template('index.html', message=f"No matching owner found in the database. So calling only NGO {ngo}.")
        
@app.route('/voice', methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    response.say("Hello! This is a call regarding your animal match. Please check your messages.", voice='alice')
    return Response(str(response), content_type='application/xml')

if __name__ == '__main__':
    # Read the dynamic port number from the environment
    app.run(host='0.0.0.0', port='5000', debug=False)
