import pyrebase
import streamlit as st
from firebase_admin import credentials, auth, initialize_app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firebase Configuration from environment variables
config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
auth_firebase = firebase.auth()
db = firebase.database()
storage = firebase.storage()

def login(email, password):
    try:
        user = auth_firebase.sign_in_with_email_and_password(email, password)
        return user
    except:
        return None

def signup(email, password, username):
    try:
        # Create user
        user = auth_firebase.create_user_with_email_and_password(email, password)
        # Initialize user data
        user_data = {
            "username": username,
            "email": email,
            "reputation_score": 10,
            "profile_complete": False,
            "is_banned": False
        }
        db.child("users").child(user['localId']).set(user_data)
        return user
    except Exception as e:
        st.error(f"Error: {e}")
        return None  # Make sure we return None on error

def get_user_data(user_id):
    return db.child("users").child(user_id).get().val()

def update_profile(user_id, profile_data):
    current_data = get_user_data(user_id)
    updated_data = {**current_data, **profile_data, "profile_complete": True}
    db.child("users").child(user_id).update(updated_data)

def update_reputation_score(user_id, new_score):
    """Update user's reputation score in the database."""
    try:
        db.child("users").child(user_id).update({"reputation_score": new_score})
        return True
    except Exception as e:
        print(f"Error updating reputation score: {e}")
        return False