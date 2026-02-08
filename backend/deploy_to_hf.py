"""
Deploy backend to Hugging Face Spaces
Run: python deploy_to_hf.py
"""
from huggingface_hub import HfApi, create_repo, upload_folder, login
import os

# Configuration
SPACE_NAME = "todo-backend-api"  # Change this if you want a different name

# Files and folders to upload
FILES_TO_UPLOAD = [
    "Dockerfile",
    "README.md",
    "requirements.txt",
    "main.py",
    "config.py",
    "database.py",
    "dependencies.py",
    "utils.py",
]

FOLDERS_TO_UPLOAD = [
    "models",
    "routes",
    "schemas",
]

def main():
    # Login - this will prompt for token if not logged in
    print("Checking Hugging Face authentication...")
    try:
        api = HfApi()
        user_info = api.whoami()
        username = user_info["name"]
        print(f"Logged in as: {username}")
    except Exception:
        print("Not logged in. Please enter your HuggingFace token.")
        print("Get it from: https://huggingface.co/settings/tokens")
        token = input("Enter your HF token (with write access): ").strip()
        login(token=token)
        api = HfApi()
        user_info = api.whoami()
        username = user_info["name"]
        print(f"Logged in as: {username}")

    repo_id = f"{username}/{SPACE_NAME}"

    # Create the Space
    print(f"\nCreating Space: {repo_id}")
    try:
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            exist_ok=True,
        )
        print(f"Space created/exists: https://huggingface.co/spaces/{repo_id}")
    except Exception as e:
        print(f"Error creating space: {e}")
        return

    # Get current directory (backend folder)
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    # Upload the entire backend folder
    print(f"\nUploading files from: {backend_dir}")

    try:
        upload_folder(
            folder_path=backend_dir,
            repo_id=repo_id,
            repo_type="space",
            ignore_patterns=[
                ".env",
                "*.pyc",
                "__pycache__",
                ".git",
                ".gitignore",
                "deploy_to_hf.py",
                "*.db",
                "*.sqlite",
                "venv",
                ".venv",
                "set",
                "uvicorn",
                "uvicorn.run*",
            ],
        )
        print("\nUpload complete!")
    except Exception as e:
        print(f"Error uploading: {e}")
        return

    # Remind about secrets
    print("\n" + "="*60)
    print("DEPLOYMENT SUCCESSFUL!")
    print("="*60)
    print(f"\nSpace URL: https://huggingface.co/spaces/{repo_id}")
    print(f"\nIMPORTANT: Add these secrets in Space Settings:")
    print("  1. Go to: https://huggingface.co/spaces/{}/settings".format(repo_id))
    print("  2. Scroll to 'Variables and secrets'")
    print("  3. Add these secrets:")
    print("     - DATABASE_URL = your Neon PostgreSQL connection string")
    print("     - SECRET_KEY = your JWT secret key")
    print("\nAfter adding secrets, the Space will rebuild automatically.")
    print(f"\nYour API will be available at:")
    print(f"  https://{username}-{SPACE_NAME}.hf.space/api/v1/docs")

if __name__ == "__main__":
    main()
