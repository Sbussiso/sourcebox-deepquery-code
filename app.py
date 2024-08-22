from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
import os
import logging
import requests
from dotenv import load_dotenv
from gpt_toolkit import generate_suggestions

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Secret key for session handling
app.config['UPLOAD_FOLDER'] = 'uploads'
API_URL = os.getenv('API_URL')
LLM_API_URL = os.getenv('LLM_API_URL')
disable_prompt_suggestions = False  # Toggle prompt suggestions

# Utility functions
def check_authentication():
    logger.debug("Checking authentication status...")
    access_token = session.get('access_token')
    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}
        try:
            response = requests.get(f"{API_URL}/user_history", headers=headers)
            logger.debug(f"Authentication check response status: {response.status_code}")
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                logger.error("Access token is invalid or expired.")
                session.pop('access_token', None)
                flash('Session expired, please login again', 'danger')
                return False
            else:
                logger.error(f"Authentication check failed: {response.text}")
                session.pop('access_token', None)
                flash('Authentication check failed, please login again.', 'danger')
                return False
        except requests.RequestException as e:
            logger.error(f"Error during authentication check: {e}")
            flash('Error during authentication check. Please login again.', 'danger')
            session.pop('access_token', None)
            return False
    else:
        logger.debug("No access token found. User not authenticated.")
        flash('You need to login first.', 'danger')
        return False

@app.before_request
def before_request():
    logger.debug(f"Before request: {request.endpoint}")
    if request.endpoint not in ('login', 'register', 'static'):
        if not check_authentication():
            return redirect(url_for('login'))

@app.route('/')
def hello():
    logger.debug("Serving the homepage...")
    codepacks = []
    if 'access_token' in session:
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        try:
            response = requests.get(f"{API_URL}/packman/code/list_code_packs", headers=headers)
            logger.debug(f"List code packs response status: {response.status_code}")
            if response.status_code == 200:
                codepacks = response.json()
            elif response.status_code == 401:
                logger.error("Token expired or invalid. Redirecting to login.")
                flash("Your session has expired. Please log in again.", "danger")
                session.pop('access_token', None)
                return redirect(url_for('login'))
            else:
                logger.error(f"Failed to fetch codepacks: {response.text}")
                flash('Failed to fetch packs', 'danger')
        except requests.RequestException as e:
            logger.error(f"Error fetching codepacks: {e}")
            flash('Error fetching codepacks', 'danger')

    suggestions = None if disable_prompt_suggestions else generate_suggestions(None)
    logger.debug(f"Returning homepage with {len(codepacks)} codepacks and suggestions enabled: {not disable_prompt_suggestions}")
    return render_template('index.html', suggestions=suggestions, codepacks=codepacks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        logger.debug(f"Login attempt with email: {email}")

        try:
            response = requests.post(f"{API_URL}/login", json={'email': email, 'password': password})
            logger.debug(f"Login response status: {response.status_code}")

            if response.status_code == 200:
                access_token = response.json().get('access_token')
                session['access_token'] = access_token
                flash('Logged in successfully!', 'success')
                logger.debug("Login successful, redirecting to homepage...")
                return redirect(url_for('hello'))
            else:
                message = response.json().get('message', 'Login failed')
                logger.error(f"Login failed: {message}")
                flash(message, 'danger')
        except requests.RequestException as e:
            logger.error(f"Error during login: {e}")
            flash('Error during login.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    logger.debug("Redirecting to external registration page...")
    return redirect('https://sourcebox-official-website-9f3f8ae82f0b.herokuapp.com/sign_up')


@app.route('/chatbot', methods=['POST'])
def chatbot_route():
    # Expecting a JSON payload
    data = request.json
    query = data.get("queryVector")
    history = data.get("history", "")
    pack_id = data.get("pack_id", None)

    logger.debug(f"Received chatbot request with query: {query}, history: {history}, pack_id: {pack_id}")

    try:
        payload = {"user_message": query, "history": history, "pack_id": pack_id}
        access_token = session.get('access_token')

        if not access_token:
            logger.error("No access token available. Redirecting to login.")
            return redirect(url_for('login'))

        # Ensure the token is present and well-formed
        logger.debug(f"Access token before request: {access_token}")

        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        logger.debug("Sending payload to LLM API...")

        response = requests.post(f"{LLM_API_URL}/deepquery-code", json=payload, headers=headers)
        logger.debug(f"LLM API response status: {response.status_code}")

        if response.status_code == 200:
            chat_results = response.json().get("message", "No response from LLM.")
            logger.debug(f"Chat results: {chat_results}")
            return jsonify({"results": chat_results}), 200
        elif response.status_code == 401:
            logger.error("Token expired or invalid. Redirecting to login.")
            session.pop('access_token', None)
            flash("Your session has expired. Please log in again.", "danger")
            return redirect(url_for('login'))
        else:
            logger.error(f"Error from LLM API: {response.status_code} - {response.text}")
            return jsonify({"error": "Error from LLM API"}), response.status_code

    except Exception as e:
        logger.error(f"Error during chat forwarding: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/raw-vector-query', methods=['POST'])
def raw_vector_query():
    data = request.json
    query = data.get("queryVector")
    pack_id = data.get("pack_id", None)

    logger.debug(f"Received raw vector query with query: {query}, pack_id: {pack_id}")

    try:
        payload = {"user_message": query, "pack_id": pack_id}
        access_token = session.get('access_token')

        if not access_token:
            logger.error("No access token available. Redirecting to login.")
            return redirect(url_for('login'))

        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        logger.debug("Sending payload to LLM API for raw vector query...")

        # Sending the payload to the LLM API, but only performing vector search
        response = requests.post(f"{LLM_API_URL}/deepquery-raw", json=payload, headers=headers)
        logger.debug(f"LLM API raw vector query response status: {response.status_code}")

        if response.status_code == 200:
            vector_results = response.json().get("vector_results", {})
            logger.debug(f"Vector results: {vector_results}")
            return jsonify({"results": vector_results}), 200
        elif response.status_code == 401:
            logger.error("Token expired or invalid. Redirecting to login.")
            session.pop('access_token', None)
            flash("Your session has expired. Please log in again.", "danger")
            return redirect(url_for('login'))
        else:
            logger.error(f"Error from LLM API: {response.status_code} - {response.text}")
            return jsonify({"error": "Error from LLM API"}), response.status_code

    except Exception as e:
        logger.error(f"Error during raw vector query: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
