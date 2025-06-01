from flask import Flask, render_template, request, redirect, url_for,jsonify,flash,session
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import pickle
import joblib
import numpy as np
import mysql.connector
import re
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
import plotly.express as px
import cv2
import tensorflow as tf
import os
import requests
from werkzeug.utils import secure_filename
matplotlib.use('Agg')  # Use non-GUI backend


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key
BLYNK_AUTH_TOKEN = '8VDegcvSkywp6--o9uGILoEMy1MXmGbx'

def get_blynk_value(vpin):
    url = f'https://blynk.cloud/external/api/get?token={BLYNK_AUTH_TOKEN}&{vpin}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return "N/A"
    except Exception as e:
        return "Error"


@app.route('/sensor-data')
def sensor_data():
    temperature = get_blynk_value('v0')
    humidity = get_blynk_value('v1')
    moisture = get_blynk_value('v3')

    return jsonify({
        'temperature': float(temperature),
        'humidity': int(humidity),
        'moisture': int(moisture)
    })


def set_blynk_value(vpin, value):
    url = f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH_TOKEN}&{vpin}={value}"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        return False

@app.route('/toggle-pump/<state>')
def toggle_pump(state):
    if state == "on":
        success = set_blynk_value('v5', 1)
    else:
        success = set_blynk_value('v5', 0)
    
    if success:
        return "Pump turned " + state
    else:
        return "Failed to change pump state"
# MySQL Configuration

# MySQL Configuration using mysql-connector
mysql = mysql.connector.connect(
    host='localhost',
    user='root',
    password='narutoop11',
    database='user_login'
)
cursor = mysql.cursor(dictionary=True)  # Use dictionary=True for fetching rows as dicts
model_leaf_disease = tf.keras.models.load_model('trained_model.h5')

# Load the trained model for fertilizer recommend
model = joblib.load('fertilizer_app.pkl')

# Load the dataset to fit LabelEncoders
data = pd.read_csv("./data/fertilizer_recommendation.csv")

# Initialize LabelEncoders and fit them with the dataset
le_soil = LabelEncoder()
le_crop = LabelEncoder()
le_fertilizer = LabelEncoder()  # For decoding the prediction
data['Soil Type'] = le_soil.fit_transform(data['Soil Type'])
data['Crop Type'] = le_crop.fit_transform(data['Crop Type'])
data['Fertilizer Name'] = le_fertilizer.fit_transform(data['Fertilizer Name'])


#loading models for yeild prediction
dtr = pickle.load(open('dtr.pkl','rb'))
preprocessor = pickle.load(open('preprocesser.pkl','rb'))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live-details')
def live_details():
    return render_template('live_details.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user_details WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login',form='login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['first-name']
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user_details WHERE username = %s', (username,))
        account = cursor.fetchone()

        # Validation logic
        if account:
            flash('Account already exists!', 'error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
        elif not username or not password or not email:
            flash('Please fill out the form!', 'error')
        else:
            cursor.execute('INSERT INTO user_details (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            mysql.commit()
            flash('Signup successful! Now login.', 'success')
            return redirect(url_for('login',form='login'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/live-sensor-dashboard')
def live_sensor_dashboard():
    return render_template('live_dashboard.html')




@app.route('/crop-recommend', methods=['GET', 'POST'])
def crop_recommend():
    if request.method == 'POST':
        # Extract form data
        try:
            nitrogen = float(request.form['nitrogen'])
            phosphorus = float(request.form['phosphorus'])
            potassium = float(request.form['potassium'])
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            ph_value = float(request.form['phValue'])
            rainfall = float(request.form['rainfall'])
        except ValueError:
            return "Please enter valid numeric values."

        # Input validation
        if not (0 <= nitrogen <= 300):
            return "Nitrogen value must be between 0 and 300 kg/ha."
        if not (0 <= phosphorus <= 150):
            return "Phosphorus value must be between 0 and 150 kg/ha."
        if not (0 <= potassium <= 250):
            return "Potassium value must be between 0 and 250 kg/ha."
        if not (0 <= temperature <= 45):
            return "Temperature must be between 0 and 45 °C."
        if not (0 <= humidity <= 100):
            return "Humidity must be between 0 and 100%."
        if not (4 <= ph_value <= 14):
            return "The pH value must be between 4 and 14."
        if not (0 <= rainfall <= 2000):
            return "Rainfall value must be between 0 and 2000 mm."

        # Create a feature array in the same order as the training data
        values = [nitrogen, phosphorus, potassium, temperature, humidity, ph_value, rainfall]
        
        try:
            # Load the model
            model = joblib.load('crop_app.pkl')
            arr = [values]

            # Get probabilities for each class
            probabilities = model.predict_proba(arr)[0]
            # Get the indices of the top 3 crops with the highest probabilities
            top_indices = probabilities.argsort()[-3:][::-1]

            # Assuming you have a list of crop labels corresponding to your model
            crop_labels = model.classes_  # Get the classes from the model
            recommended_crops = crop_labels[top_indices]  # Get the top crop names
            
            # Render the result
            return render_template('crop-recommend.html', prediction=recommended_crops.tolist())
        except Exception as e:
            return f"An error occurred: {e}"
    
    return render_template('crop-recommend.html')

@app.route("/schemes")
def government_schemes():
    return render_template("government_schemes.html")




@app.route('/weather-forecast')
def weather_forecast():
    return render_template('weather-forecast.html')

@app.route('/fertilizer-recommend', methods=['GET', 'POST'])
def fertilizer_recommend():
    if request.method == 'POST':
        try:
            # Extract form data
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            soil_moisture = float(request.form['soilMoisture'])
            soil_type = request.form['soilType']
            crop_type = request.form['cropType']
            nitrogen = float(request.form['nitrogen'])
            potassium = float(request.form['potassium'])
            phosphorous = float(request.form['phosphorous'])

            # Encode categorical features
            soil_type_encoded = le_soil.transform([soil_type])[0]
            crop_type_encoded = le_crop.transform([crop_type])[0]

            # Create a feature array
            features = [[temperature, humidity, soil_moisture, soil_type_encoded, crop_type_encoded, nitrogen, potassium, phosphorous]]

            # Try predicting class directly
            prediction = model.predict(features)
            print("Prediction:", prediction)

            # Decode the prediction back to the original fertilizer name
            recommended_fertilizer = le_fertilizer.inverse_transform(prediction)
            print("Recommended fertilizer:", recommended_fertilizer)

            # Render the result in the template
            return render_template('fertilizer-recommend.html', recommendations=recommended_fertilizer)

        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('fertilizer-recommend.html')



# Load your dataset
df = pd.read_csv('./data/analysis1_data.csv')

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    states = df['state'].unique()  # Get unique states from the dataset
    
    if request.method == 'POST':
        state = request.form['state']
        year = request.form['year']
        
        # Filter the data by selected year (for comparison across all crops)
        year_data = df[(df['state'] == state) & (df['year'] == int(year))]

        if year_data.empty:
            return render_template('analysis.html', states=states, error='No data available for the selected year.')

        # Create the first plot: Bar chart for cost of production
        plt.figure(figsize=(10, 6))  # Increased size for better visibility
        plt.bar(year_data['crop_type'], year_data['cost_of_production_per_hectare'], color='blue')
        plt.title(f'Cost of Production for Different Crops in {state} in {year}')
        plt.xlabel('Crop Type')
        plt.ylabel('Cost of Production (per hectare)')
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Create the second plot: Pie chart for cultivation area
        # Group by crop_type and sum the cultivation area
        grouped_data = year_data.groupby('crop_type', as_index=False)['cultivation_area_hectares'].sum()

        # Create the second plot: Pie chart for cultivation area
        plt.figure(figsize=(8, 8))  # Increased size for better visibility
        plt.pie(grouped_data['cultivation_area_hectares'], labels=grouped_data['crop_type'], autopct='%1.1f%%', startangle=90)
        plt.title(f'Cultivation Area Distribution in {state} in {year}')
        img2 = io.BytesIO()
        plt.savefig(img2, format='png')
        img2.seek(0)
        pie_chart_url = base64.b64encode(img2.getvalue()).decode()
        plt.close()

        # Rainfall effect on crops (filtered by state and year)
        plt.figure(figsize=(10, 6))  # Increased size for better visibility
        plt.bar(year_data['crop_type'], year_data['rainfall_mm'], color='teal')
        plt.title(f'Rainfall Impact on Different Crops in {state} in {year}')
        plt.xlabel('Crop Type')
        plt.ylabel('Rainfall (mm)')
        plt.xticks(rotation=45)
        img3 = io.BytesIO()
        plt.savefig(img3, format='png')
        img3.seek(0)

        # Convert the image to a base64 string
        rainfall_chart_url = base64.b64encode(img3.getvalue()).decode()

        plt.close()

        return render_template('analysis.html', 
                               states=states,
                               graph_url=graph_url, 
                               pie_chart_url=pie_chart_url, 
                               rainfall_chart_url=rainfall_chart_url, 
                               selected_state=state,
                               selected_year=year)

    return render_template('analysis.html', states=states)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username, password, email, phone, location FROM user_details WHERE id=%s", (user_id,))
        account = cursor.fetchone()
        
        if request.method == 'POST':
            # Update profile details in the database
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['phone']
            location = request.form['location']
            
            cursor.execute("""
                UPDATE user_details 
                SET username=%s, password=%s, email=%s, phone=%s, location=%s 
                WHERE id=%s
            """, (username, password, email, phone, location, user_id))
            mysql.commit()
            flash('Profile saved successfully', 'success')
            return redirect(url_for('profile'))
        
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Here we would normally clear the session or any user-specific data
    return redirect(url_for('index'))


@app.route('/help')
def help_us():
    return render_template('help.html')  # The help/contact page

class_name = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]

@app.route('/predict-leaf-disease', methods=['POST'])
def predict_leaf_disease():
    # Setup upload folder locally inside the function
    upload_folder = 'static/uploads'
    os.makedirs(upload_folder, exist_ok=True)

    if 'image' not in request.files:
        return "No image part in request", 400

    file = request.files['image']
    if file.filename == '':
        return "No selected image", 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Load and preprocess image
        image = tf.keras.preprocessing.image.load_img(filepath, target_size=(128, 128))
        input_arr = tf.keras.preprocessing.image.img_to_array(image)
        input_arr = np.expand_dims(input_arr, axis=0) / 255.0

        prediction = model_leaf_disease.predict(input_arr)
        result_index = np.argmax(prediction)
        result_label = class_name[result_index]

        return render_template('live_dashboard.html',
                               image_path=filepath,
                               prediction=result_label)

    return "Something went wrong", 500

if __name__ == '__main__':
    app.run(debug=True)
