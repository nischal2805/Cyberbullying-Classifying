# CyberGuard - AI-Powered Cyberbullying Detection Platform

A social media platform with dual-AI cyberbullying detection using local ML models and Google Gemini API.

---

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Project Structure](#project-structure)
4. [Step-by-Step Setup Guide](#step-by-step-setup-guide)
   - [Step 1: Clone the Repository](#step-1-clone-the-repository)
   - [Step 2: Install Python](#step-2-install-python)
   - [Step 3: Install Node.js](#step-3-install-nodejs)
   - [Step 4: Set Up Python Environment](#step-4-set-up-python-environment)
   - [Step 5: Configure Environment Variables](#step-5-configure-environment-variables)
   - [Step 6: Set Up Firebase](#step-6-set-up-firebase)
   - [Step 7: Get Gemini API Key](#step-7-get-gemini-api-key)
   - [Step 8: Set Up Frontend](#step-8-set-up-frontend)
5. [Running the Application](#running-the-application)
6. [API Documentation](#api-documentation)
7. [Troubleshooting](#troubleshooting)

---

## Overview

CyberGuard uses two AI systems to detect cyberbullying:

1. **Local Model**: A DistilBERT model from HuggingFace (`boss2805/cyberbully`) that runs on your machine
2. **Gemini API**: Google's Gemini 2.0 Flash model for additional verification

The platform includes:
- User authentication (Firebase)
- Social feed with posts and comments
- Real-time content moderation
- User reputation system
- Modern Next.js frontend

---

## Requirements

### Software Versions (IMPORTANT - Use these exact versions)

| Software | Version | Download Link |
|----------|---------|---------------|
| Python | 3.9 - 3.11 | https://www.python.org/downloads/ |
| Node.js | 18.x or 20.x (LTS) | https://nodejs.org/ |
| npm | 9.x or 10.x (comes with Node.js) | Included with Node.js |
| Git | Latest | https://git-scm.com/downloads |

### Hardware Requirements

- **RAM**: Minimum 8GB (16GB recommended for running the ML model)
- **Storage**: At least 5GB free space
- **Internet**: Required for Firebase and Gemini API

---

## Project Structure

```
Cyberbullying-Classifying/
|
|-- api/                    # FastAPI backend
|   |-- main.py             # API endpoints
|
|-- frontend/               # Next.js frontend
|   |-- src/
|   |   |-- app/
|   |       |-- page.tsx           # Home page
|   |       |-- login/page.tsx     # Login/Signup
|   |       |-- feed/page.tsx      # Social feed
|   |       |-- detector/page.tsx  # Text analyzer
|   |       |-- profile/page.tsx   # User profile
|   |-- package.json
|   |-- tailwind.config.js
|
|-- api_client.py           # Gemini API integration
|-- app.py                  # Legacy Streamlit app
|-- auth.py                 # Firebase authentication
|-- database.py             # Firebase database operations
|-- detector.py             # ML model and detection logic
|-- reputation.py           # User reputation management
|-- requirements.txt        # Python dependencies
|-- .env.example            # Environment variables template
|-- .env                    # Your environment variables (create this)
```

---

## Step-by-Step Setup Guide

### Step 1: Clone the Repository

Open your terminal (Command Prompt, PowerShell, or Terminal) and run:

```bash
git clone https://github.com/nischal2805/Cyberbullying-Classifying.git
```

Then navigate into the folder:

```bash
cd Cyberbullying-Classifying
```

---

### Step 2: Install Python

1. Go to https://www.python.org/downloads/
2. Download Python **3.10.x** (recommended) or any version between 3.9 and 3.11
3. **IMPORTANT**: During installation, check the box that says **"Add Python to PATH"**
4. Verify installation by opening a new terminal and running:

```bash
python --version
```

You should see something like `Python 3.10.11`

If you see an error, restart your computer and try again.

---

### Step 3: Install Node.js

1. Go to https://nodejs.org/
2. Download the **LTS version** (should be 18.x or 20.x)
3. Run the installer and follow the prompts (default options are fine)
4. Verify installation:

```bash
node --version
```

Should show `v18.x.x` or `v20.x.x`

```bash
npm --version
```

Should show `9.x.x` or `10.x.x`

---

### Step 4: Set Up Python Environment

#### Option A: Using pip directly (Simpler)

Open terminal in the project folder and run:

**Windows:**
```bash
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

#### Option B: Using Virtual Environment (Recommended)

This keeps your project dependencies isolated.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

The installation will download about 2-3GB of data (including the ML model). This may take 5-15 minutes depending on your internet speed.

---

### Step 5: Configure Environment Variables

1. In the project folder, find the file named `.env.example`
2. Create a copy of this file and name it `.env`

**Windows (Command Prompt):**
```bash
copy .env.example .env
```

**Windows (PowerShell):**
```bash
Copy-Item .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

3. Open the `.env` file in any text editor (Notepad, VS Code, etc.)

---

### Step 6: Set Up Firebase

Firebase is used for user authentication and database.

#### 6.1 Create a Firebase Project

1. Go to https://console.firebase.google.com/
2. Click **"Create a project"** (or "Add project")
3. Enter a project name (e.g., "cyberguard-app")
4. Disable Google Analytics (optional, not needed)
5. Click **"Create project"**
6. Wait for it to finish, then click **"Continue"**

#### 6.2 Enable Authentication

1. In your Firebase project, click **"Authentication"** in the left sidebar
2. Click **"Get started"**
3. Click on **"Email/Password"**
4. Enable the first toggle **"Email/Password"**
5. Click **"Save"**

#### 6.3 Create Realtime Database

1. Click **"Realtime Database"** in the left sidebar
2. Click **"Create Database"**
3. Choose a location (pick the one closest to you)
4. Select **"Start in test mode"** (for development)
5. Click **"Enable"**

#### 6.4 Get Firebase Configuration

1. Click the **gear icon** next to "Project Overview" and select **"Project settings"**
2. Scroll down to **"Your apps"** section
3. Click the **web icon** (`</>`) to add a web app
4. Enter a nickname (e.g., "cyberguard-web")
5. Click **"Register app"**
6. You will see a code block with your Firebase configuration. It looks like this:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "your-project.firebaseapp.com",
  databaseURL: "https://your-project-default-rtdb.firebaseio.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

7. Copy these values into your `.env` file:

```
FIREBASE_API_KEY=AIzaSy...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
FIREBASE_PROJECT_ID=your-project
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abc123
```

**IMPORTANT**: Make sure `FIREBASE_DATABASE_URL` ends with a `/`

---

### Step 7: Get Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Select your project (or create a new one)
5. Copy the API key
6. Paste it in your `.env` file:

```
GEMINI_API_KEY=AIzaSy...your-api-key...
```

---

### Step 8: Set Up Frontend

1. Open a new terminal window
2. Navigate to the frontend folder:

```bash
cd frontend
```

3. Install dependencies:

```bash
npm install
```

This will take 1-2 minutes and download about 200MB of packages.

---

## Running the Application

You need to run TWO terminals - one for the backend and one for the frontend.

### Terminal 1: Start the Backend API

Open a terminal in the project root folder:

```bash
python -m uvicorn api.main:app --reload --port 8000
```

**What you should see:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

If you see a model download progress bar, wait for it to complete (first run only).

**Keep this terminal open!**

### Terminal 2: Start the Frontend

Open a NEW terminal window:

```bash
cd Cyberbullying-Classifying/frontend
npm run dev
```

**What you should see:**

```
> cyberguard-frontend@1.0.0 dev
> next dev

  - ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

### Access the Application

Open your web browser and go to:

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

---

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/classify` | Analyze text for cyberbullying (dual AI) |
| POST | `/api/classify/local` | Analyze using local model only |
| POST | `/api/classify/gemini` | Analyze using Gemini API only |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/signup` | User registration |
| GET | `/api/auth/me` | Get current user info |
| GET | `/api/posts` | Get all posts |
| POST | `/api/posts` | Create a new post |
| GET | `/api/posts/{id}/comments` | Get comments for a post |
| POST | `/api/posts/{id}/comments` | Add a comment (with auto-detection) |

### Classification Categories

| Category | Description |
|----------|-------------|
| Not Cyberbullying | Safe, neutral, or positive content |
| Ethnicity/Race | Bullying based on race or nationality |
| Gender/Sexual | Bullying based on gender or orientation |
| Religion | Bullying based on religious beliefs |
| Other | General insults and harassment |

---

## Troubleshooting

### "Python is not recognized as a command"

- You didn't add Python to PATH during installation
- Solution: Reinstall Python and check "Add Python to PATH"
- Alternative: Use `python3` instead of `python`

### "npm is not recognized as a command"

- Node.js is not installed or not in PATH
- Solution: Reinstall Node.js and restart your terminal

### "Module not found" errors in Python

- Dependencies not installed properly
- Solution: Run `pip install -r requirements.txt` again

### "ENOENT: no such file or directory" in npm

- You're not in the correct folder
- Solution: Make sure you're in the `frontend` folder before running `npm install`

### Backend starts but shows Firebase errors

- Environment variables not set correctly
- Solution: Double-check your `.env` file matches the Firebase console values

### "GEMINI_API_KEY not set" warning

- Gemini API key missing or incorrect
- Solution: Get a new API key from https://aistudio.google.com/app/apikey

### Frontend shows "Failed to fetch" or network errors

- Backend is not running
- Solution: Make sure the backend is running on port 8000 in another terminal

### Port already in use

- Another application is using the port
- Solution: Kill the process or use a different port:
  - Backend: `python -m uvicorn api.main:app --reload --port 8001`
  - Frontend: `npm run dev -- -p 3001`

### Model download is stuck

- Slow internet or HuggingFace servers are busy
- Solution: Wait, or try again later. First download is around 500MB

### Virtual environment not activating (Windows)

- PowerShell execution policy blocking scripts
- Solution: Run PowerShell as Administrator and execute:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

---

## Need Help?

If you're still stuck:

1. Make sure you followed EVERY step exactly as written
2. Check that all version numbers match the requirements
3. Read the error message carefully - it usually tells you what's wrong
4. Google the exact error message
5. Open an issue on GitHub with:
   - Your operating system
   - Python version (`python --version`)
   - Node version (`node --version`)
   - The complete error message

---

## License

MIT License - feel free to use for any project!
