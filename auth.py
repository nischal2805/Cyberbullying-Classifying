import pyrebase
import streamlit as st
from firebase_admin import credentials, auth, initialize_app
import os

# Firebase Configuration
config = {
    "apiKey": "AIzaSyBecL1qrxfdkfl1Lc-xya2iUrqpZFKYcDY",
    "authDomain": "cyberbullly-eb3a7.firebaseapp.com",
    "databaseURL": "https://cyberbullly-eb3a7-default-rtdb.firebaseio.com/",
    "projectId": "cyberbullly-eb3a7",
    "storageBucket": "cyberbullly-eb3a7.appspot.com",
    "messagingSenderId": "224084281352",
    "appId": "1:224084281352:web:979981aaf70ccd4187a9bd"
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