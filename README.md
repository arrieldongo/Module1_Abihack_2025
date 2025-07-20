# Shaifai AI Docs

**Shaifai AI Docs** est un moteur d'extraction de données intelligent conçu pour être la première brique de la transformation digitale des entreprises. Il transforme les documents non structurés (images, PDF) en données JSON structurées et exploitables.

## 🚀 Ce que fait le projet

Le projet est un pipeline de bout en bout qui :
1.  **Ingère** un document (CV, facture, etc.).
2.  **Lit** le document avec une haute précision grâce à l'API **Google Cloud Vision**.
3.  **Comprend** le texte et extrait les informations clés grâce à l'API **Gemini** et à une ingénierie de prompts avancée.
4.  **Livre** des données JSON propres, prêtes à être utilisées dans n'importe quel autre système.

## 🛠️ Stack Technique

* **Backend :** Python 3.12, Flask
* **IA & Cloud :** Google Cloud Vision, Google Gemini API (via AI Studio)
* **Gestion de Données :** Pandas
* **Support PDF :** `pdf2image`, `poppler`

## ⚙️ Installation et Lancement

1.  **Cloner le dépôt :**
    ```bash
    git clone [URL_DE_VOTRE_DÉPÔT_GIT]
    cd shaifai-ai-docs
    ```
2.  **Créer et activer l'environnement virtuel :**
    ```bash
    python3.12 -m venv venv
    source venv/bin/activate
    ```
3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configurer les clés :**
    * Placez votre fichier de compte de service Google Cloud à la racine et nommez-le `gcp-credentials.json`.
    * Ouvrez `services/gcp_services.py` et insérez votre clé API de AI Studio dans la variable `AI_STUDIO_API_KEY`.

5.  **Lancer l'application :**
    ```bash
    python -m flask run
    ```
