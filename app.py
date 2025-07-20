from flask import Flask, request, jsonify, render_template
from services.gcp_services import call_vision_api, call_gemini_api
import os
import pandas as pd 
import json
import uuid
from datetime import datetime

app = Flask(__name__)

# Le nom de notre fichier de base de données local
EXCEL_FILE = 'cv_database.xlsx'

@app.route('/')
def index():
    """Affiche la page d'accueil."""
    return render_template('index.html')

@app.route('/api/process-document', methods=['POST'])
def process_document():
    """
    Reçoit un document, l'envoie à l'API Vision pour l'OCR,
    puis à l'API Gemini pour l'extraction des données du CV.
    """
    if 'document' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if file:
        file_content = file.read()
        
        # Étape 1: Appel à l'API Vision (OCR)
        text_from_ocr = call_vision_api(file_content)
        if "Erreur" in str(text_from_ocr):
            return jsonify({'error': text_from_ocr}), 500
        
        # Étape 2: Appel à l'API Gemini (Extraction)
        extracted_data = call_gemini_api(text_from_ocr)
        return jsonify(extracted_data)

    return jsonify({'error': 'Erreur lors du traitement du fichier'}), 500

@app.route('/api/submit-corrections', methods=['POST'])
def submit_corrections():
    """
    Reçoit les données validées du formulaire et les injecte dans le fichier Excel local.
    """
    try:
        data = request.json
        
        # Prépare la nouvelle ligne de données pour le fichier Excel
        new_row = {
            'ID': str(uuid.uuid4())[:8],
            'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Name': data.get('Name'),
            'Title': data.get('Title'),
            'Bio': data.get('Bio'),
            'Skills': json.dumps(data.get('Skills'), ensure_ascii=False),
            'Soft Skills': json.dumps(data.get('Soft_Skills'), ensure_ascii=False),
            'Experience': data.get('Experience'), # Le résumé textuel est déjà une chaîne
            'Projects': data.get('Projects'),     # Le résumé textuel est déjà une chaîne
            'Location': data.get('Location'),
            'Certifications': data.get('Certifications') # Le résumé textuel est déjà une chaîne
        }

        # Lit le fichier Excel existant ou en crée un nouveau
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
        else:
            df = pd.DataFrame(columns=list(new_row.keys()))

        # Ajoute la nouvelle ligne au DataFrame
        new_df_row = pd.DataFrame([new_row])
        df = pd.concat([df, new_df_row], ignore_index=True)
        
        # Sauvegarde le DataFrame dans le fichier Excel
        df.to_excel(EXCEL_FILE, index=False)
        
        return jsonify({'status': 'success', 'message': 'Données sauvegardées avec succès dans le fichier Excel local !'})

    except Exception as e:
        print(f"Erreur lors de la sauvegarde dans Excel : {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)