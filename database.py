import pyrebase
from datetime import datetime
import uuid
import ssl
from auth import config

# SSL workaround for Firebase connections
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

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
        "likes": [],  # Changed to array to track who liked
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


def toggle_like(post_id, user_id):
    """Toggle like on a post. Returns the updated likes array."""
    post = db.child("posts").child(post_id).get()
    if not post.val():
        return None
    
    post_data = post.val()
    likes = post_data.get('likes', [])
    
    # Handle legacy int format
    if isinstance(likes, int):
        likes = []
    
    if user_id in likes:
        likes.remove(user_id)
    else:
        likes.append(user_id)
    
    db.child("posts").child(post_id).update({"likes": likes})
    return likes


def get_post(post_id):
    """Get a single post by ID"""
    post = db.child("posts").child(post_id).get()
    if post.val():
        return {**post.val(), "id": post_id}
    return None