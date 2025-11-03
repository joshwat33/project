from flask import Flask, request, jsonify, render_template,make_response # type: ignore
from werkzeug.utils import secure_filename # type: ignore
import requests # type: ignore
from flask_cors import CORS # type: ignore
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__,template_folder="/templates",static_folder="/static")
CORS(app)

ACCESS_TOKEN = os.getenv('your_access_token') #add your access token
EXTRACTOR_ID = os.getenv('your_extractor_id') #add your extractor id

@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    # Relax the Content-Security-Policy header to allow inline scripts and resources
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; img-src 'self' data: https://*; style-src 'self' 'unsafe-inline';"
    return response

@app.route('/students')
def students():
    # Same header for the students route
    response = make_response(render_template('students.html'))
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; img-src 'self' data: https://*; style-src 'self' 'unsafe-inline';"
    return response

@app.route('/questions', methods=['GET', 'POST'])
def questions():
    # Handle GET request
    if request.method == 'GET':
        exam = request.args.get('exam')
        student = request.args.get('student')
        return render_template('questions.html', exam=exam, student=student)

    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file attached'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file:
            filename = secure_filename(file.filename)
            file.save(filename)  # Save the uploaded file

            # Prepare the data to send to the external API
            url = "https://worker.formextractorai.com/v2/extract"
            files = open(filename, 'rb')
            headers = {
                'X-WORKER-TOKEN': ACCESS_TOKEN,
                'X-WORKER-EXTRACTOR-ID': EXTRACTOR_ID,
                'Content-Type': 'image/*'
            }
            temp = {}
            dataa = []
            newdata = []
            newdata2 = []
            newdata3 = []

            # Make a POST request to the external API
            response = requests.request("POST",url, headers=headers, data=files)
            temp=response.json()
            dataa = temp['documents'][0]['data']['marklist']
            newdata = dataa[0].values()
            newdata2 = dataa[1].values()
            newdata3 = dataa[2].values()
            dataa = list(newdata)
            dataa.extend(list(newdata2))
            dataa.extend(list(newdata3))
            #dataa=jsonify(dataa)
            # Process the response from the external API
            if response.status_code == 200:
                return jsonify(dataa)
                #return render_template('questions.html', response=response)
            else:
                return jsonify({'error': 'Failed to process the image'}), 500
    return render_template('questions.html')

if __name__ == '__main__':
    app.run(debug=True)
