import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import os
import sys
import base64
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from auth import login, signup, get_user_data, update_profile
from database import create_post, get_all_posts, create_comment, get_post_comments
from detector import detect_cyberbullying
from api_client import get_detailed_classification, classify_with_gemini

# Page configuration
st.set_page_config(
    page_title="CyberGuard Social",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if os.path.exists("styles.css"):
    load_css("styles.css")

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# This function should be in app.py
def decrease_reputation(user_id):
    """Decrease user reputation after bullying comments."""
    user_data = get_user_data(user_id)
    if not user_data:
        st.error("Could not retrieve user data")
        return
        
    current_score = user_data.get('reputation_score', 10)
    bad_comments_count = user_data.get('bad_comments_count', 0) + 1
    
    # For debugging
    print(f"User {user_id}: current score={current_score}, bad comments={bad_comments_count}")
    
    # For every 2 bad comments, decrease score by 1
    if bad_comments_count % 2 == 0:  # Only decrease on even counts (2, 4, 6...)
        new_score = max(0, current_score - 1)
        
        # Update user data in Firebase
        from auth import db
        db.child("users").child(user_id).update({
            "reputation_score": new_score,
            "bad_comments_count": bad_comments_count
        })
        
        st.warning(f"⚠️ Your reputation score decreased to {new_score}/10")
        
        # Check if user needs to be banned
        if new_score < 5:
            db.child("users").child(user_id).update({"is_banned": True})
            st.error("Your account has been banned due to low reputation score.")
    else:
        # Just update the bad comments count
        from auth import db
        db.child("users").child(user_id).update({"bad_comments_count": bad_comments_count})

# Login page
def show_login_page():
    st.title("🛡️ CyberGuard Social")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            user = login(email, password)
            if user:
                st.session_state.user = user
                user_data = get_user_data(user['localId'])
                
                # Add this check and initialization
                if user_data is None:
                    # User exists in auth but not in database - create basic profile
                    from auth import db
                    user_data = {
                        "username": email.split('@')[0],  # Simple username from email
                        "email": email,
                        "reputation_score": 10,
                        "profile_complete": False,
                        "is_banned": False
                    }
                    db.child("users").child(user['localId']).set(user_data)
                    # Get the user data again
                    user_data = get_user_data(user['localId'])
                
                if user_data.get('is_banned', False):
                    st.error("Your account has been banned. Please contact support.")
                    st.session_state.user = None
                elif not user_data.get('profile_complete', False):
                    st.session_state.page = 'complete_profile'
                    st.experimental_rerun()
                else:
                    st.session_state.page = 'home'
                    st.experimental_rerun()
            else:
                st.error("Invalid email or password")
    
    with tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Sign Up"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                user = signup(new_email, new_password, new_username)
                if user:
                    st.success("Account created! Please complete your profile")
                    st.session_state.user = user
                    st.session_state.page = 'complete_profile'
                    st.experimental_rerun()

# Complete profile page
def show_complete_profile():
    st.title("Complete Your Profile")
    
    with st.form("profile_form"):
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=13, max_value=100, value=18)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
        bio = st.text_area("Bio", height=100)
        
        submitted = st.form_submit_button("Save Profile")
        if submitted:
            profile_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "bio": bio,
            }
            update_profile(st.session_state.user['localId'], profile_data)
            st.success("Profile updated!")
            st.session_state.page = 'home'
            st.experimental_rerun()

# Home page
def show_home():
    st.title("Home Feed")
    
    # Sidebar with user profile
    user_data = get_user_data(st.session_state.user['localId'])
    with st.sidebar:
        st.write(f"Welcome, {user_data.get('username', 'User')}")
        st.write(f"Reputation Score: {user_data.get('reputation_score', 10)}/10")
        
        # Navigation menu
        selected = option_menu(
            "Navigation",
            ["Home", "Create Post", "Profile", "Logout"],
            icons=['house', 'pencil-square', 'person', 'box-arrow-right'],
            menu_icon="cast",
            default_index=0
        )
        
        if selected == "Create Post":
            st.session_state.page = 'create_post'
            st.experimental_rerun()
        elif selected == "Profile":
            st.session_state.page = 'profile'
            st.experimental_rerun()
        elif selected == "Logout":
            st.session_state.user = None
            st.session_state.page = 'login'
            st.experimental_rerun()
    
    # For testing cyberbullying detection
    with st.expander("Test Cyberbullying Detection"):
        test_text = st.text_input("Enter text to test")
        if st.button("Test Detection"):
            is_bullying, bullying_type = detect_cyberbullying(test_text)
            if is_bullying:
                st.error(f"This text contains {bullying_type} bullying content")
            else:
                st.success("This text does not contain bullying content")
    
    # Display posts
    posts = get_all_posts()
    
    if not posts:
        st.info("No posts yet! Be the first to post something.")
        return
    
    for post in sorted(posts, key=lambda x: x.get('timestamp', ''), reverse=True):
        with st.container():
            post_author = get_user_data(post.get('user_id', ''))
            
            # Display post header
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write("👤")  # Avatar placeholder
            with col2:
                st.write(f"**{post_author.get('username', 'Unknown User')}**")
                st.caption(post.get('timestamp', ''))
            
            # Display post content
            st.write(post.get('content', ''))
            
            # Display post image if available
            if post.get('image_url'):
                st.image(post.get('image_url'), use_column_width=True)
            
            # Comment section
            with st.expander(f"💬 Comments"):
                comments = get_post_comments(post.get('id', ''))
                
                for comment in comments:
                    comment_author = get_user_data(comment.get('user_id', ''))
                    st.write(f"**{comment_author.get('username', 'Unknown')}**: {comment.get('content', '')}")
                    if comment.get('is_bullying'):
                        st.warning(f"⚠️ This comment has been flagged as {comment.get('bullying_type')} content")
                
                # Add comment
                new_comment = st.text_input("Add a comment", key=f"comment_{post.get('id')}")
                if st.button("Post Comment", key=f"post_comment_{post.get('id')}"):
                    if new_comment.strip():
                        # Check for cyberbullying
                        is_bullying, bullying_type = detect_cyberbullying(new_comment)
                        print(f"Detection result for '{new_comment}': is_bullying={is_bullying}, type={bullying_type}")
                        
                        # Create the comment
                        comment_id = create_comment(st.session_state.user['localId'], 
                                                 post.get('id'), 
                                                 new_comment, 
                                                 is_bullying, 
                                                 bullying_type)
                        
                        if is_bullying:
                            # Show a warning
                            st.warning(f"⚠️ Your comment has been flagged as {bullying_type} content.")
                            # Update user's reputation
                            decrease_reputation(st.session_state.user['localId'])
                        
                        # Force a rerun to refresh comments
                        st.experimental_rerun()
        
        st.markdown("---")

# Create post page
def show_create_post():
    st.title("Create Post")
    
    content = st.text_area("What's on your mind?", height=150)
    uploaded_file = st.file_uploader("Add an image (optional)", type=["jpg", "jpeg", "png"])
    
    if st.button("Post"):
        if content.strip() or uploaded_file:
            create_post(st.session_state.user['localId'], content, uploaded_file)
            st.success("Post created successfully!")
            st.session_state.page = 'home'
            st.experimental_rerun()
        else:
            st.error("Please add some content to your post")
    
    if st.button("Cancel"):
        st.session_state.page = 'home'
        st.experimental_rerun()

# Profile page
def show_profile():
    user_data = get_user_data(st.session_state.user['localId'])
    st.title(f"{user_data.get('username', 'User')}'s Profile")
    
    # Display reputation score prominently
    st.markdown(f"""
    <div style='background-color:#f0f2f6; padding:10px; border-radius:10px;'>
        <h2 style='text-align:center;'>Reputation Score: {user_data.get('reputation_score', 10)}/10</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # User details
    st.subheader("User Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {user_data.get('name', 'Not provided')}")
        st.write(f"**Username:** {user_data.get('username', 'Not provided')}")
        st.write(f"**Email:** {user_data.get('email', 'Not provided')}")
    
    with col2:
        st.write(f"**Age:** {user_data.get('age', 'Not provided')}")
        st.write(f"**Gender:** {user_data.get('gender', 'Not provided')}")
    
    st.write(f"**Bio:** {user_data.get('bio', 'No bio provided')}")
    
    if st.button("Edit Profile"):
        st.session_state.page = 'complete_profile'
        st.experimental_rerun()
    
    if st.button("Back to Home"):
        st.session_state.page = 'home'
        st.experimental_rerun()

# Main app routing
def main():
    if st.session_state.page == 'login':
        show_login_page()
    elif st.session_state.page == 'complete_profile':
        show_complete_profile()
    elif st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'create_post':
        show_create_post()
    elif st.session_state.page == 'profile':
        show_profile()

if __name__ == "__main__":
    main()