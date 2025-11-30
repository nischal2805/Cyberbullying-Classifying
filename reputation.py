"""
Reputation management functions for CyberGuard
"""

from auth import get_user_data, db


def decrease_reputation(user_id: str):
    """
    Decrease user reputation after bullying comments.
    
    For every 2 bad comments, decrease score by 1.
    Ban user if reputation drops below 5.
    """
    user_data = get_user_data(user_id)
    if not user_data:
        print(f"Could not retrieve user data for {user_id}")
        return
        
    current_score = user_data.get('reputation_score', 10)
    bad_comments_count = user_data.get('bad_comments_count', 0) + 1
    
    print(f"User {user_id}: current score={current_score}, bad comments={bad_comments_count}")
    
    # For every 2 bad comments, decrease score by 1
    if bad_comments_count % 2 == 0:
        new_score = max(0, current_score - 1)
        
        # Update user data in Firebase
        db.child("users").child(user_id).update({
            "reputation_score": new_score,
            "bad_comments_count": bad_comments_count
        })
        
        print(f"User {user_id} reputation decreased to {new_score}/10")
        
        # Check if user needs to be banned
        if new_score < 5:
            db.child("users").child(user_id).update({"is_banned": True})
            print(f"User {user_id} has been banned due to low reputation score.")
        
        return new_score
    else:
        # Just update the bad comments count
        db.child("users").child(user_id).update({"bad_comments_count": bad_comments_count})
        return current_score
