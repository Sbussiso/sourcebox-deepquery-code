from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from git import Repo
import shutil
import os
import logging
from vector import project_to_vector
from dotenv import load_dotenv
from prompt_suggestions import generate_suggestions
from query import perform_query

load_dotenv()

logging.basicConfig(level=logging.DEBUG,  # Set the logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Log format

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

disable_prompt_suggestions = False  # toggle prompt suggestions

@app.route('/')
def hello():
    if disable_prompt_suggestions:
        suggestions = None
    else:
        prompt = None  # using default response
        suggestions = generate_suggestions(prompt)
    return render_template('index.html', suggestions=suggestions)

@app.route('/fetch-repo', methods=['POST'])
def fetch_repo():
    try:
        # Define the path to the directory
        directory_path = 'repofetch'
        logging.debug('Entered fetch_repo function')

        # Check if the directory exists
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            logging.debug(f"The directory '{directory_path}' already exists.")
            return jsonify({"error": "Directory already exists"}), 400

        logging.debug(f"The directory '{directory_path}' does not exist.")
        # Path to the directory
        main_directory = os.getcwd()  # Use the current working directory as the main directory
        repo_fetch_dir = os.path.join(main_directory, 'repofetch')

        # Create the directory
        os.makedirs(repo_fetch_dir, exist_ok=True)
        logging.debug(f"Directory 'repofetch' created at: {repo_fetch_dir}")

        # User input
        repo_url = request.form.get('repoURL')
        logging.debug(f"REPO URL: {repo_url}")

        if not repo_url:
            return jsonify({"error": "No repository URL provided"}), 400

        # Fetch the GitHub repo
        try:
            repo = Repo.clone_from(repo_url, repo_fetch_dir)
            logging.debug("Pulled repo from GitHub")
        except Exception as e:
            logging.error(f"Failed to fetch repository: {e}")
            return jsonify({"error": str(e)}), 500

        logging.debug("Pulled repo from GitHub")

        # Vectorize the repo in repofetch and send to DeepLake
        db = project_to_vector()
        if not db:
            return jsonify({"error": "Failed to process repository"}), 500

        return jsonify({"message": "Repository successfully fetched and data laked"}), 200
    except Exception as e:
        logging.error(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear-repo', methods=['POST'])
def clear_repo():
    try:
        # Define the path to the directory
        repo_directory_path = 'repofetch'
        deeplake_directory_path = 'my_deeplake'

        # Check if the repo directory exists
        if os.path.exists(repo_directory_path) and os.path.isdir(repo_directory_path):
            logging.debug(f"The directory '{repo_directory_path}' exists. deleting folder")
            shutil.rmtree(repo_directory_path)
            logging.debug(f"Directory 'repofetch' deleted")
        else:
            logging.debug(f"The directory '{repo_directory_path}' does not exist. No folder to delete")

        # Check if the my_deeplake directory exists
        if os.path.exists(deeplake_directory_path) and os.path.isdir(deeplake_directory_path):
            logging.debug(f"The directory '{deeplake_directory_path}' exists. deleting folder")
            shutil.rmtree(deeplake_directory_path)
            logging.debug(f"Directory 'my_deeplake' deleted")
        else:
            logging.debug(f"The directory '{deeplake_directory_path}' does not exist. No folder to delete")

        # delete processed files metadata
        main_directory = os.getcwd()
        file = os.path.join(main_directory, 'processed_files_metadata.json')
        if os.path.exists(file):
            os.remove(file)

        return jsonify({"message": "Directory cleared"}), 200
    except Exception as e:
        logging.error(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/query-vector', methods=['POST'])
def query_vector():
    try:
        query = request.form.get("queryVector")
        logging.debug(f"Query Vector: {query}")

        results = perform_query(query)
        return jsonify({"results": results}), 200
    
    except Exception as e:
        logging.error(f"Error during similarity search: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
