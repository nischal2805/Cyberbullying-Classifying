import pyrebase
import streamlit as st
from datetime import datetime
import uuid
from auth import config

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()

def create_post(user_id, content, image=None):
    post_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    post_data = {
        "user_id": user_id,
        "content": content,
        "timestamp": timestamp,
        "likes": 0,
        "image_url": None
    }
    
    if image is not None:
        # Upload image to Firebase Storage
        image_path = f"posts/{post_id}/{image.name}"
        storage.child(image_path).put(image)
        # Get image URL
        image_url = storage.child(image_path).get_url(None)
        post_data["image_url"] = image_url
    
    db.child("posts").child(post_id).set(post_data)
    return post_id

def get_all_posts():
    posts = db.child("posts").get()
    if posts.each():
        return [{**post.val(), "id": post.key()} for post in posts.each()]
    return []

def create_comment(user_id, post_id, content, is_bullying=False, bullying_type=None):
    comment_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    comment_data = {
        "user_id": user_id,
        "content": content,
        "timestamp": timestamp,
        "is_bullying": is_bullying,
        "bullying_type": bullying_type
    }
    
    db.child("comments").child(post_id).child(comment_id).set(comment_data)
    return comment_id

def get_post_comments(post_id):
    comments = db.child("comments").child(post_id).get()
    if comments.each():
        return [{**comment.val(), "id": comment.key()} for comment in comments.each()]
    return []

def delete_comment(post_id, comment_id):
    """Delete a comment from a post"""
    db.child("comments").child(post_id).child(comment_id).remove()
    return True

def search_users(query):
    """Search for users by username or email"""
    query = query.lower()
    users = db.child("users").get()
    results = []
    
    if users.each():
        for user in users.each():
            user_data = user.val()
            username = user_data.get('username', '').lower()
            email = user_data.get('email', '').lower()
            
            if query in username or query in email:
                results.append({
                    "uid": user.key(),
                    "email": user_data.get('email'),
                    "displayName": user_data.get('username'),
                    "reputation": user_data.get('reputation_score', 100)
                })
    
    return results[:10]  # Limit to 10 results