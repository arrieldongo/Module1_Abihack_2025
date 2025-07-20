import os
import json
import google.generativeai as genai
from google.cloud import vision

# --- CONFIGURATION ---
# Collez ici votre clé API obtenue sur https://aistudio.google.com/app/apikey
AI_STUDIO_API_KEY = "ici"
genai.configure(api_key=AI_STUDIO_API_KEY)
# -------------------

def call_vision_api(image_content):
    """Appelle l'API Google Cloud Vision pour l'OCR."""
    print("[DEBUG-SVC-1] Entrée dans call_vision_api.")
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        CREDENTIALS_PATH = os.path.join(BASE_DIR, 'gcp-credentials.json')
        print(f"[DEBUG-SVC-2] Utilisation du fichier de credentials : {CREDENTIALS_PATH}")
        
        client = vision.ImageAnnotatorClient.from_service_account_file(CREDENTIALS_PATH)
        print("[DEBUG-SVC-3] Client Vision créé.")
        
        image = vision.Image(content=image_content)
        print("[DEBUG-SVC-4] Appel de l'API text_detection...")
        response = client.text_detection(image=image)
        print("[DEBUG-SVC-5] Réponse de l'API Vision reçue.")

        if response.error.message:
            raise Exception(f"{response.error.message}")
        if response.text_annotations:
            print("[DEBUG-SVC-6] Succès : Texte extrait par Vision.")
            return response.text_annotations[0].description
        else:
            print("[AVERTISSEMENT-SVC] Aucun texte détecté par Vision.")
            return "Aucun texte détecté."
    except Exception as e:
        print(f"[ERREUR-SVC] Erreur dans call_vision_api : {e}")
        return f"Erreur API Vision: {e}"

def call_gemini_api(text_from_ocr, user_corrections={}):
    """Appelle l'API Gemini via AI Studio pour analyser le texte d'un CV."""
    print("[DEBUG-SVC-7] Entrée dans call_gemini_api.")
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        print("[DEBUG-SVC-8] Modèle Gemini 'gemini-1.5-flash-latest' chargé.")

        # --- PROMPT MIS À JOUR POUR L'EXTRACTION COMPLÈTE DU CV ---
        prompt = f"""
        **Votre Rôle et Objectif :**
        Vous êtes un recruteur expert. Votre mission est d'analyser le texte d'un CV et de le transformer en un JSON structuré et lisible par un humain.

        **Règles de formatage :**
        1.  Retournez UNIQUEMENT le JSON, sans aucun autre texte ou commentaire.
        2.  **Règle cruciale : Si une section entière comme 'Projects' ou 'Certifications' est absente du CV, omettez complètement la clé correspondante du JSON final.** Ne retournez pas de liste vide `[]` ou une chaîne vide.
        3.  Pour les sections 'Experience', 'Projects', et 'Certifications', ne retournez pas une liste d'objets JSON. À la place, créez un **résumé textuel clair et bien formaté** pour chacune, en utilisant des retours à la ligne pour séparer les différentes entrées (postes, projets, etc.).

        **Structure JSON attendue :**
        - **Name** (string) : Le nom complet du candidat.
        - **Title** (string) : Le titre professionnel le plus marquant.
        - **Bio** (string) : Un résumé de 2-3 phrases du profil.
        - **Location** (string) : La ville et le pays.
        - **Skills** (list of strings) : La liste des compétences techniques clés.
        - **Soft_Skills** (list of strings) : La liste des compétences humaines clés.
        - **Experience** (string) : Un résumé textuel et formaté des expériences professionnelles.
        - **Projects** (string) : Un résumé textuel et formaté des projets.
        - **Certifications** (string) : Un résumé textuel et formaté des certifications.
        
        **Texte du CV à analyser :**
        ---
        {text_from_ocr}
        ---
        """
        
        print("[DEBUG-SVC-9] Envoi du prompt à Gemini...")
        response = model.generate_content(prompt)
        print("[DEBUG-SVC-10] Réponse de Gemini reçue.")
        
        json_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        print(f"[DEBUG-SVC-11] Réponse JSON brute de Gemini : {json_text}")
        
        extracted_data = json.loads(json_text)
        print("[DEBUG-SVC-12] Parsing JSON réussi.")
        
        return extracted_data
    except Exception as e:
        print(f"[ERREUR-SVC] Erreur dans call_gemini_api : {e}")
        return {'error': f"Erreur lors de l'analyse par Gemini: {e}"}
