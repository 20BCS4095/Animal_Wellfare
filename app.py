from flask import Flask, render_template, request, redirect, url_for, Response
import pandas as pd
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from twilio.base.exceptions import TwilioRestException

app = Flask(__name__)

# Initialize Twilio client (you need to get these from Twilio account)
TWILIO_PHONE_NUMBER = '+17752629661'
TWILIO_ACCOUNT_SID = 'AC749485ba42d2b47677f7a93905f99c16'
TWILIO_AUTH_TOKEN = '06b3a378f74553b33f113001e48c698d'

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
        place = request.form['accident_location']

        try:
            # Find matching record in the Excel sheet
            matching_record = df[
                (df['animal_name'].str.lower() == animal_name.lower()) &
                (df['animal_type'].str.lower() == animal_type.lower()) &
                (df['species'].str.lower() == species.lower())  # Matching species
            ]

            if not matching_record.empty:
                owner_name = matching_record.iloc[0]['owner_name']
                phone_number = "+91" + str(matching_record.iloc[0]['phone_number'])
                ngo = "Animal Welfare"
                ngo_number = "+917358933435"
                # Send a message to the owner's phone number
                try:
                    message_owner = client.messages.create(
                        body=f"Hello {owner_name}, we have matched your {animal_name} ({animal_type}, {species}) and location is {place}.",
                        from_=TWILIO_PHONE_NUMBER,
                        to=phone_number
                    )
                except TwilioRestException as e:
                    return render_template('index.html', message=f"Error sending message to {owner_name}: {str(e)}")
                
                try:
                    # Send a message to the NGO
                    message_ngo = client.messages.create(
                        body=f"Hello {ngo}, we have matched your {animal_name} ({animal_type}, {species}) and location is {place}.",
                        from_=TWILIO_PHONE_NUMBER,
                        to=ngo_number
                    )
                except TwilioRestException as e:
                    return render_template('index.html', message=f"Error sending message to NGO: {str(e)}")

                try:
                    # Make a call to the owner's number
                    call = client.calls.create(
                        to=phone_number,  # Recipient's phone number
                        from_=TWILIO_PHONE_NUMBER,  # Your Twilio number
                        url='https://animal-wellfare1.onrender.com/voice'  # This URL will provide the TwiML instructions
                    )
                except TwilioRestException as e:
                    return render_template('index.html', message=f"Error making a call to {phone_number}: {str(e)}")

                return render_template('index.html', message=f"Message sent to {owner_name} at {phone_number}. And also for NGO {ngo} and location is {place}.")
            else:
                ngo = "Animal Welfare"
                ngo_number = "+917358933435"
                
                try:
                    # Send a message to the NGO (only if no match found)
                    message_ngo = client.messages.create(
                        body=f"Hello {ngo}, we have matched your {animal_name} ({animal_type}, {species}) and location is {place}.",
                        from_=TWILIO_PHONE_NUMBER,
                        to=ngo_number
                    )
                except TwilioRestException as e:
                    return render_template('index.html', message=f"Error sending message to NGO: {str(e)}")
                try:
                    # Make a call to the owner's number
                    call = client.calls.create(
                        to=ngo_number,  # Recipient's phone number
                        from_=TWILIO_PHONE_NUMBER,  # Your Twilio number
                        url='https://animal-wellfare1.onrender.com/voice'  # This URL will provide the TwiML instructions
                    )
                except TwilioRestException as e:
                    return render_template('index.html', message=f"Error making a call to {phone_number}: {str(e)}")
                
                return render_template('index.html', message=f"No matching owner found in the database. So calling only NGO {ngo} number {ngo_number} and location is {place}.")
        except Exception as e:
            # Catch all exceptions related to form submission and processing
            return render_template('index.html', message=f"An unexpected error occurred: {str(e)}")

@app.route('/voice', methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    response.say("Hello! This is a call regarding your animal match. Please check your messages.", voice='alice')
    return Response(str(response), content_type='application/xml')

if __name__ == '__main__':
    # Read the dynamic port number from the environment
    app.run(host='0.0.0.0', port=5000, debug=False)
