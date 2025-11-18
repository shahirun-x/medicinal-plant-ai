import os
import time
import sqlite3
import pickle
import numpy as np
import tensorflow as tf
import cv2  # This is opencv-python
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input

# --- 1. GLOBAL SETUP ---

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Define file paths
DATABASE_FILE = 'medicinal_plants.db'
SEGMENTER_MODEL_FILE = 'leaf_segmenter.h5'
CLASSIFIER_MODEL_FILE = 'leaf_classifier.pkl'

# Define image dimensions
SEG_IMG_HEIGHT, SEG_IMG_WIDTH = 256, 256
CLASS_IMG_HEIGHT, CLASS_IMG_WIDTH = 224, 224

# --- 2. LOAD MODELS INTO MEMORY ---

print("Loading AI models. This may take a moment...")

try:
    # Load the Segmentation U-Net model
    segmentation_model = tf.keras.models.load_model(
        SEGMENTER_MODEL_FILE,
        custom_objects={'MeanIoU': tf.keras.metrics.MeanIoU(num_classes=2)}
    )
    print(f"Successfully loaded segmentation model: {SEGMENTER_MODEL_FILE}")

    # Load the ResNet50 base model (for feature extraction)
    resnet_model = tf.keras.applications.ResNet50(
        weights='imagenet',
        include_top=False,
        pooling='avg',
        input_shape=(CLASS_IMG_HEIGHT, CLASS_IMG_WIDTH, 3)
    )
    print("Successfully loaded ResNet50 feature extractor.")

    # Load the trained Random Forest Classifier
    with open(CLASSIFIER_MODEL_FILE, 'rb') as f:
        classification_model = pickle.load(f)
    print(f"Successfully loaded classification model: {CLASSIFIER_MODEL_FILE}")

except Exception as e:
    print(f"FATAL ERROR: Could not load models. {e}")
    segmentation_model = None
    classification_model = None
    resnet_model = None

# --- 3. CREATE FLASK APP ---

app = Flask(__name__)
CORS(app)

print("\nFlask app created. Ready to serve requests.")

# --- NEW MAPPING DICTIONARY ---
NAME_MAPPER = {
    'Alstonia Scholaris diseased (P2a)': 'Alstonia scholaris',
    'Alstonia Scholaris healthy (P2b)': 'Alstonia scholaris',
    'Arjun diseased (P1a)': 'Terminalia arjuna',
    'Arjun healthy (P1b)': 'Terminalia arjuna',
    'Bael diseased (P4b)': 'Aegle marmelos',
    'Basil healthy (P8)': 'Ocimum tenuiflorum',
    'Chinar diseased (P11b)': 'Platanus orientalis',
    'Chinar healthy (P11a)': 'Platanus orientalis',
    'Gauva diseased (P3b)': 'Psidium guajava',
    'Gauva healthy (P3a)': 'Psidium guajava',
    'Jamun diseased (P5b)': 'Syzygium cumini',
    'Jamun healthy (P5a)': 'Syzygium cumini',
    'Jatropha diseased (P6b)': 'Jatropha curcas',
    'Jatropha healthy (P6a)': 'Jatropha curcas',
    'Lemon diseased (P10b)': 'Citrus limon',
    'Lemon healthy (P10a)': 'Citrus limon',
    'Mango diseased (P0b)': 'Mangifera indica',
    'Mango healthy (P0a)': 'Mangifera indica',
    'Pomegranate diseased (P9b)': 'Punica granatum',
    'Pomegranate healthy (P9a)': 'Punica granatum',
    'Pongamia Pinnata diseased (P7b)': 'Millettia pinnata',
    'Pongamia Pinnata healthy (P7a)': 'Millettia pinnata'
}
# --- END OF NEW SECTION ---

# --- 4. HELPER FUNCTIONS (DATABASE) ---

def get_db_connection():
    """Connects to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def get_plant_profile(scientific_name):
    """Queries the database for a full plant profile."""
    profile = {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Get Species info (names)
        # --- UPDATED: Now selects all the new columns ---
        cursor.execute(
            """
            SELECT * FROM Species 
            WHERE scientific_name = ?
            """, 
            (scientific_name,)
        )
        species_data = cursor.fetchone()
        
        if not species_data:
            conn.close()
            return {"error": "Plant not found in database", "scientific_name": scientific_name}
        
        species_id = species_data['species_id']
        profile['scientific_name'] = species_data['scientific_name']
        profile['english_name'] = species_data['english_name']
        profile['local_name'] = species_data['local_name']
        
        # --- NEW: Add the rich data to our response ---
        profile['plant_description'] = species_data['plant_description']
        profile['habitat_type'] = species_data['habitat_type']
        profile['flowering_season'] = species_data['flowering_season']
        profile['general_warnings'] = species_data['general_warnings']
        # --- END OF NEW SECTION ---

        # 2. Get Medicinal Uses
        cursor.execute("SELECT part_used, usage_description FROM MedicinalUses WHERE species_id = ?", (species_id,))
        uses_data = cursor.fetchall()
        profile['medicinal_uses'] = [{'part': row['part_used'], 'use': row['usage_description']} for row in uses_data]

        # 3. Get Invasive Status
        cursor.execute("SELECT is_invasive FROM InvasiveStatus WHERE species_id = ?", (species_id,))
        status_data = cursor.fetchone()
        profile['is_invasive'] = bool(status_data['is_invasive']) if status_data else False

        # 4. Get Map Coordinates
        cursor.execute("SELECT latitude, longitude FROM Observations WHERE species_id = ?", (species_id,))
        obs_data = cursor.fetchall()
        profile['locations'] = [{'lat': row['latitude'], 'lon': row['longitude']} for row in obs_data]

        conn.close()
        return profile

    except Exception as e:
        print(f"Database error: {e}")
        if conn:
            conn.close()
        return {"error": str(e)}

# --- 5. HELPER FUNCTIONS (AI PIPELINE) ---

def run_segmentation(image_bytes):
    """Takes raw image bytes, runs U-Net, and returns a binary mask."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img_resized = cv2.resize(img, (SEG_IMG_HEIGHT, SEG_IMG_WIDTH))
    img_resized = img_resized / 255.0
    img_batch = np.expand_dims(img_resized, axis=0)

    pred_mask = segmentation_model.predict(img_batch)[0]
    pred_mask = (pred_mask > 0.5).astype(np.uint8)

    return img, pred_mask


def segment_and_crop(original_image, mask):
    """Applies the mask to the original image to cut out the leaf."""
    mask_resized = cv2.resize(mask, (original_image.shape[1], original_image.shape[0]))
    contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return original_image

    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    cropped_leaf = original_image[y:y + h, x:x + w]

    return cropped_leaf


def run_classification(leaf_image):
    """Takes the cropped leaf, runs ResNet+RF, and returns the species name."""
    img_resized = cv2.resize(leaf_image, (CLASS_IMG_HEIGHT, CLASS_IMG_WIDTH))
    img_array = img_to_array(img_resized)
    img_batch = np.expand_dims(img_array, axis=0)
    img_preprocessed = preprocess_input(img_batch)

    features = resnet_model.predict(img_preprocessed)
    features_flat = features.flatten()
    prediction = classification_model.predict([features_flat])

    return prediction[0]

# --- 6. FLASK API ROUTES ---

@app.route('/', methods=['GET'])
def index():
    """A simple test route to see if the server is alive."""
    return "Hello! The Plant API server is running."


@app.route('/predict', methods=['POST'])
def predict():
    """Main endpoint: receives an image and returns a full JSON profile."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and segmentation_model and classification_model:
        try:
            image_bytes = file.read()

            original_image, mask = run_segmentation(image_bytes)
            cropped_leaf = segment_and_crop(original_image, mask)
            predicted_label = run_classification(cropped_leaf)

            scientific_name_to_find = NAME_MAPPER.get(predicted_label, None)

            if not scientific_name_to_find:
                return jsonify({
                    "error": "Plant identified, but not in our medicinal database.",
                    "scientific_name": predicted_label
                })

            plant_profile = get_plant_profile(scientific_name_to_find)
            return jsonify(plant_profile)

        except Exception as e:
            print(f"Error during prediction: {e}")
            return jsonify({"error": f"An error occurred: {e}"}), 500

    return jsonify({"error": "Server is not ready or models not loaded"}), 503
# --- 6.5. FLASK API ROUTE (FOR CROWDSOURCING) ---

@app.route('/contribute', methods=['POST'])
def contribute():
    """Receives a new plant observation from a user."""
    
    # 1. Get all the data from the form
    if 'file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
        
    file = request.files['file']
    scientific_name = request.form.get('scientific_name')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    health_condition = request.form.get('health_condition', 'Unknown') # Default value

    if not all([file, scientific_name, latitude, longitude]):
        return jsonify({"error": "Missing required data (file, name, lat, or lon)"}), 400

    # 2. Find the species_id in our database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT species_id FROM Species WHERE scientific_name = ?", (scientific_name,))
        species_data = cursor.fetchone()
        
        if not species_data:
            conn.close()
            return jsonify({"error": f"Species '{scientific_name}' not found in our database."}), 404
            
        species_id = species_data['species_id']

        # 3. Save the image to the 'uploads' folder
        # We create a unique filename to avoid overwrites
        filename = f"{species_id}_{int(time.time())}_{file.filename}"
        image_path = os.path.join('uploads', filename)
        file.save(image_path)
        
        # 4. Insert the new observation into the database
        cursor.execute(
            """
            INSERT INTO Observations 
            (species_id, latitude, longitude, data_source, timestamp, health_condition, image_url, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                species_id,
                float(latitude),
                float(longitude),
                'Crowdsourced',
                time.strftime('%Y-%m-%dT%H:%M:%SZ'), # ISO 8601 format
                health_condition,
                image_path,
                True # We'll assume True since our AI will verify it first
            )
        )
        
        conn.commit()
        conn.close()
        
        print(f"--- CROWDSOURCE: New observation for '{scientific_name}' added! ---")
        return jsonify({"success": True, "message": "Contribution received. Thank you!"})

    except Exception as e:
        print(f"Error during contribution: {e}")
        if conn:
            conn.close()
        return jsonify({"error": f"An error occurred: {e}"}), 500

# --- 7. START THE SERVER ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
