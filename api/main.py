"""
CyberGuard API - FastAPI Backend
Provides REST endpoints for the React/Next.js frontend
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
import sys
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from detector import detect_cyberbullying, _predict_local_label, CLASS_LABELS
from api_client import classify_with_gemini, get_detailed_classification

# Initialize FastAPI
app = FastAPI(
    title="CyberGuard API",
    description="Cyberbullying Detection & Social Platform API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# ============================================
# Pydantic Models
# ============================================

class TextInput(BaseModel):
    text: str

class ClassificationResult(BaseModel):
    text: str
    local_model_label: Optional[str]
    gemini_label: Optional[str]
    gemini_explanation: Optional[str]
    final_label: str
    is_bullying: bool
    bullying_type: Optional[str]
    confidence: Optional[float] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    reputation_score: int
    is_banned: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PostCreate(BaseModel):
    content: str
    image_url: Optional[str] = None

class CommentCreate(BaseModel):
    content: str

class PostResponse(BaseModel):
    id: str
    user_id: str
    username: str
    content: str
    image_url: Optional[str]
    timestamp: str
    likes: int
    comments_count: int

class CommentResponse(BaseModel):
    id: str
    user_id: str
    username: str
    content: str
    timestamp: str
    is_bullying: bool
    bullying_type: Optional[str]

# ============================================
# Helper Functions
# ============================================

def create_token(user_id: str, email: str) -> str:
    """Create JWT token for user"""
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """API Health Check"""
    return {
        "status": "online",
        "service": "CyberGuard API",
        "version": "2.0.0",
        "endpoints": {
            "docs": "/docs",
            "classify": "/api/classify",
            "auth": "/api/auth/*"
        }
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    firebase_configured = bool(os.getenv("FIREBASE_API_KEY"))
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "local_model": "available",
            "gemini_api": "configured" if gemini_configured else "not_configured",
            "firebase": "configured" if firebase_configured else "not_configured"
        }
    }

# ============================================
# Classification Endpoints
# ============================================

@app.post("/api/classify", response_model=ClassificationResult)
async def classify_text(input_data: TextInput):
    """
    Classify text for cyberbullying content.
    
    Uses both local HuggingFace model and Gemini API for dual classification.
    The Gemini result is used as the final authoritative label.
    """
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
    
    # Get detailed classification
    result = get_detailed_classification(text)
    
    return ClassificationResult(
        text=text,
        local_model_label=result.get("local_label"),
        gemini_label=result.get("api_label"),
        gemini_explanation=result.get("api_explanation"),
        final_label=result.get("final_label", "Not Cyberbullying"),
        is_bullying=result.get("is_bullying", False),
        bullying_type=result.get("bullying_type")
    )

@app.post("/api/classify/local")
async def classify_local_only(input_data: TextInput):
    """Classify using only the local HuggingFace model"""
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        label = _predict_local_label(text)
        is_bullying = label != "Not Cyberbullying"
        
        return {
            "text": text,
            "label": label,
            "is_bullying": is_bullying,
            "bullying_type": label.lower() if is_bullying else None,
            "model": "boss2805/cyberbully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")

@app.post("/api/classify/gemini")
async def classify_gemini_only(input_data: TextInput):
    """Classify using only the Gemini API"""
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="Gemini API not configured")
    
    category, explanation = classify_with_gemini(text)
    
    if category is None:
        raise HTTPException(status_code=500, detail="Gemini API failed to respond")
    
    is_bullying = category != "Not Cyberbullying"
    
    return {
        "text": text,
        "label": category,
        "explanation": explanation,
        "is_bullying": is_bullying,
        "bullying_type": category.lower() if is_bullying else None,
        "model": "gemini-2.0-flash"
    }

@app.get("/api/categories")
async def get_categories():
    """Get all available classification categories"""
    return {
        "categories": CLASS_LABELS,
        "descriptions": {
            "Not Cyberbullying": "Safe, neutral, or positive content",
            "Ethnicity/Race": "Bullying based on race, ethnicity, or nationality",
            "Gender/Sexual": "Bullying based on gender or sexual orientation",
            "Religion": "Bullying based on religious beliefs",
            "Other": "General insults, harassment, or bullying"
        }
    }

# ============================================
# Auth Endpoints (Firebase-backed)
# ============================================

@app.post("/api/auth/login")
async def login_user(request: LoginRequest):
    """Authenticate user and return JWT token"""
    try:
        from auth import login as firebase_login, get_user_data
        
        user = firebase_login(request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_data = get_user_data(user['localId'])
        if not user_data:
            raise HTTPException(status_code=404, detail="User data not found")
        
        if user_data.get('is_banned', False):
            raise HTTPException(status_code=403, detail="Account is banned")
        
        token = create_token(user['localId'], request.email)
        reputation_score = user_data.get('reputation_score', 10)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user['localId'],
                "uid": user['localId'],
                "email": request.email,
                "username": user_data.get('username', 'User'),
                "displayName": user_data.get('username', 'User'),
                "reputation_score": reputation_score,
                "reputation": reputation_score * 10,  # Feed expects 0-100 scale
                "is_banned": user_data.get('is_banned', False)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/signup")
async def signup_user(request: SignupRequest):
    """Create new user account"""
    try:
        from auth import signup as firebase_signup, get_user_data
        
        user = firebase_signup(request.email, request.password, request.username)
        if not user:
            raise HTTPException(status_code=400, detail="Failed to create account")
        
        token = create_token(user['localId'], request.email)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user['localId'],
                "uid": user['localId'],
                "email": request.email,
                "username": request.username,
                "displayName": request.username,
                "reputation_score": 10,
                "reputation": 100,  # 10 * 10 for feed 0-100 scale
                "is_banned": False
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me")
async def get_current_user(token_data: dict = Depends(verify_token)):
    """Get current authenticated user"""
    try:
        from auth import get_user_data
        
        user_data = get_user_data(token_data['sub'])
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        reputation_score = user_data.get('reputation_score', 10)
        
        # Return both snake_case and camelCase for compatibility with different frontend pages
        return {
            "id": token_data['sub'],
            "uid": token_data['sub'],
            "email": token_data['email'],
            "username": user_data.get('username', 'User'),
            "displayName": user_data.get('username', 'User'),
            "reputation_score": reputation_score,
            "reputation": reputation_score * 10,  # Feed expects 0-100 scale
            "is_banned": user_data.get('is_banned', False)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Posts Endpoints
# ============================================

@app.get("/api/posts")
async def get_posts():
    """Get all posts"""
    try:
        from database import get_all_posts, get_post_comments
        from auth import get_user_data
        
        posts = get_all_posts()
        result = []
        
        for post in sorted(posts, key=lambda x: x.get('timestamp', ''), reverse=True):
            user_data = get_user_data(post.get('user_id', ''))
            comments = get_post_comments(post.get('id', ''))
            likes_list = post.get('likes', [])
            if isinstance(likes_list, int):
                likes_list = []
            
            result.append({
                "id": post.get('id', ''),
                "userId": post.get('user_id', ''),
                "userName": user_data.get('username', 'Unknown') if user_data else 'Unknown',
                "content": post.get('content', ''),
                "imageUrl": post.get('image_url'),
                "timestamp": post.get('timestamp', ''),
                "likes": likes_list,
                "commentCount": len(comments),
                "isBullying": post.get('is_bullying', False),
                "bullyingType": post.get('bullying_type')
            })
        
        return {"posts": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts")
async def create_new_post(post: PostCreate, token_data: dict = Depends(verify_token)):
    """Create a new post"""
    try:
        from database import create_post
        from auth import get_user_data
        
        post_id = create_post(token_data['sub'], post.content, None)
        user_data = get_user_data(token_data['sub'])
        
        return {
            "id": post_id,
            "userId": token_data['sub'],
            "userName": user_data.get('username', 'User') if user_data else 'User',
            "content": post.content,
            "imageUrl": post.image_url,
            "timestamp": datetime.utcnow().isoformat(),
            "likes": [],
            "commentCount": 0,
            "isBullying": False,
            "bullyingType": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts/{post_id}/comments")
async def get_comments(post_id: str):
    """Get comments for a post"""
    try:
        from database import get_post_comments
        from auth import get_user_data
        
        comments = get_post_comments(post_id)
        result = []
        
        for comment in comments:
            user_data = get_user_data(comment.get('user_id', ''))
            result.append({
                "id": comment.get('id', ''),
                "userId": comment.get('user_id', ''),
                "userName": user_data.get('username', 'Unknown') if user_data else 'Unknown',
                "content": comment.get('content', ''),
                "timestamp": comment.get('timestamp', ''),
                "isBullying": comment.get('is_bullying', False),
                "bullyingType": comment.get('bullying_type')
            })
        
        return {"comments": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts/{post_id}/comments")
async def add_comment(post_id: str, comment: CommentCreate, token_data: dict = Depends(verify_token)):
    """Add a comment to a post (with cyberbullying detection)"""
    try:
        from database import create_comment
        from auth import get_user_data
        
        # Detect cyberbullying in comment
        is_bullying, bullying_type = detect_cyberbullying(comment.content)
        
        # Create comment
        comment_id = create_comment(
            token_data['sub'],
            post_id,
            comment.content,
            is_bullying,
            bullying_type
        )
        
        user_data = get_user_data(token_data['sub'])
        
        # If bullying detected, decrease reputation
        if is_bullying:
            from reputation import decrease_reputation
            decrease_reputation(token_data['sub'])
        
        return {
            "id": comment_id,
            "userId": token_data['sub'],
            "userName": user_data.get('username', 'User') if user_data else 'User',
            "content": comment.content,
            "timestamp": datetime.utcnow().isoformat(),
            "isBullying": is_bullying,
            "bullyingType": bullying_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/posts/{post_id}/comments/{comment_id}")
async def delete_comment(post_id: str, comment_id: str, token_data: dict = Depends(verify_token)):
    """Delete a comment (only the comment owner can delete)"""
    try:
        from database import get_post_comments, delete_comment as db_delete_comment
        
        # Get the comment to verify ownership
        comments = get_post_comments(post_id)
        comment = next((c for c in comments if c.get('id') == comment_id), None)
        
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Check if user owns the comment
        if comment.get('user_id') != token_data['sub']:
            raise HTTPException(status_code=403, detail="You can only delete your own comments")
        
        # Delete the comment
        db_delete_comment(post_id, comment_id)
        
        return {"message": "Comment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/posts/{post_id}/like")
async def toggle_like_post(post_id: str, token_data: dict = Depends(verify_token)):
    """Toggle like on a post"""
    try:
        from database import toggle_like, get_post
        
        post = get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        likes = toggle_like(post_id, token_data['sub'])
        
        return {"likes": likes, "liked": token_data['sub'] in likes}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# User Search Endpoints
# ============================================

@app.get("/api/users/search")
async def search_users(q: str, token_data: dict = Depends(verify_token)):
    """Search for users by username or email"""
    try:
        from database import search_users as db_search_users
        
        if not q or len(q) < 2:
            return {"users": []}
        
        users = db_search_users(q)
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
