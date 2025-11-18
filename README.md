# Medicinal Plant AI Identifier & Crowdsourcing Platform

This is a full-stack web application that uses a deep learning pipeline to identify medicinal plants from user-uploaded images. It provides a rich profile of the plant, including medicinal uses, an interactive location heatmap, and a crowdsourcing feature for users to contribute new sightings.

This project fulfills all objectives outlined in the original research document, including image segmentation, classification, and crowdsourced geotagging.

---

## Features

* **AI-Powered Identification**: Upload a leaf image and the AI pipeline (U-Net + ResNet/Random Forest) will identify the species.
* **Rich Data Profiles**: View detailed information, including local/English names, plant descriptions from Wikipedia, and medicinal uses.
* **Safety & Habitat Info**: See potential toxicity warnings, habitat type, and flowering season for known plants.
* **Interactive Heatmap**: Displays a density map of all known sightings (from GBIF and user contributions) for an identified plant.
* **Crowdsourcing Platform**: Users can contribute new sightings by uploading a photo, which is first verified by the AI and then added to the map with a user-placed pin.

---

## Project Structure

This project is a monorepo containing the backend, frontend, and all AI models.

    plant_project/
    ├── frontend/             # React Frontend (UI)
    ├── uploads/              # Stores user-contributed images
    │
    ├── app.py                # Main Flask Backend Server (API)
    │
    ├── leaf_segmenter.h5     # Trained U-Net Segmentation Model
    ├── leaf_classifier.pkl   # Trained Random Forest Classifier Model
    │
    ├── medicinal_plants.db   # Populated SQLite Database
    │
    ├── requirements.txt      # Python library requirements
    ├── README.md             # This instruction file
    │
    └── (Data Scripts)        # .py scripts used to build the database
        ├── create_database.py
        ├── load_invasive_data.py
        ├── populate_rich_data.py
        └── ...

---

## Prerequisites

Before you begin, you must have the following software installed on your machine:
1.  **Anaconda (or Miniconda):** [https://www.anaconda.com/download](https://www.anaconda.com/download)
2.  **Node.js (LTS version):** [https://nodejs.org/](https://nodejs.org/)

---

## How to Run This Project

You must run two separate servers in two separate terminals.

### Part 1: Start the Backend Server (Terminal 1)

This server runs the AI models and the database.

1.  **Open Anaconda Prompt.**
2.  **Navigate to the Project Folder:**
    ```bash
    D:
    cd plant_project
    ```
3.  **Create the Conda Environment:**
    * Create a new environment named `plant_env`:
        ```bash
        conda create -n plant_env python=3.10
        ```
    * Activate the new environment:
        ```bash
        conda activate plant_env
        ```
4.  **Install All Python Libraries:**
    * Use the `requirements.txt` file to install everything:
        ```bash
        pip install -r requirements.txt
        ```
5.  **Run the Backend Server:**
    * Once all libraries are installed, run the `app.py` script:
        ```bash
        python app.py
        ```
    * **Wait 1-3 minutes.** The server needs time to load the large AI models.
    * The server is running when you see: `* Running on http://127.0.0.1:5000`
    * **Leave this terminal running.**

### Part 2: Start the Frontend Server (Terminal 2)

This server runs the React website.

1.  **Open a second, new Anaconda Prompt.**
2.  **Navigate to the `frontend` Folder:**
    ```bash
    D:
    cd plant_project\frontend
    ```
3.  **Activate the Conda Environment:**
    ```bash
    conda activate plant_env
    ```
4.  **Install All Node.js Libraries:**
    * This reads the `package.json` file and installs all React dependencies.
        ```bash
        npm install
        ```
5.  **Run the Frontend Server:**
    * Once installed, run the start script:
        ```bash
        npm start
        ```
    * This will automatically open the application in your web browser at: `http://localhost:3000`
