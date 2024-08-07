from flask import Flask, render_template, request
from git import Repo
import shutil
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG,  # Set the logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Log format


app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/fetch-repo', methods=['POST'])
def fetch_repo():
    # Define the path to the directory
    directory_path = 'repofetch'

    # Check if the directory exists
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        logging.debug(f"The directory '{directory_path}' already exists.")
    else:
        logging.debug(f"The directory '{directory_path}' does not exist.")
        # Path to the directory
        main_directory = os.getcwd()  # Use the current working directory as the main directory
        repo_fetch_dir = os.path.join(main_directory, 'repofetch')

        # Create the directory
        os.makedirs(repo_fetch_dir, exist_ok=True)
        logging.debug(f"Directory 'repofetch' created at: {repo_fetch_dir}")

        #user input
        repo_url = request.form.get('repoURL')
        logging.debug(f"REPO URL: {repo_url}")

        #fetch github repo
        # Fetch the GitHub repo
        try:
            repo = Repo.clone_from(repo_url, repo_fetch_dir)
            logging.debug("Pulled repo from GitHub")
        except Exception as e:
            logging.error(f"Failed to fetch repository: {e}")
            return "Failed to fetch repository", 500
        
        logging.debug("pulled repo from github")
        return "Repository successfully fetched", 200

        


@app.route('/clear-repo')
def clear_repo():
    # Define the path to the directory
    directory_path = 'repofetch'

    # Check if the directory exists
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        logging.debug(f"The directory '{directory_path}' exists. deleting folder")
        shutil.rmtree(directory_path)
        logging.debug(f"Directory 'repofetch' deleted")
    else:
        logging.debug(f"The directory '{directory_path}' does not exist. No folder to delete")
        


if __name__ == '__main__':
    app.run(debug=True)
