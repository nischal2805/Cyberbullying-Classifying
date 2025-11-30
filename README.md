# CyberGuard: AI-Powered Cyberbullying Detection Platform

A modern social media platform with dual-AI cyberbullying detection using local ML models and Google Gemini API.

![CyberGuard](https://img.shields.io/badge/CyberGuard-AI%20Powered-6366f1)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

## 🚀 Features

- **Dual AI Classification**: Combines local HuggingFace DistilBERT model with Google Gemini 2.0 Flash
- **Real-time Detection**: Instant classification of text content with explanations
- **Multi-Category Detection**: Identifies race, gender, religion-based bullying and general harassment
- **Reputation System**: User reputation scores based on behavior
- **Modern UI**: Beautiful dark-themed React/Next.js interface
- **REST API**: FastAPI backend for flexible integrations

## 📁 Project Structure

```
Cyberbullying-Classifying/
├── api/
│   └── main.py          # FastAPI backend
├── frontend/
│   ├── src/
│   │   └── app/         # Next.js pages
│   ├── package.json
│   └── tailwind.config.js
├── detector.py          # ML model & detection logic
├── api_client.py        # Gemini API integration
├── auth.py              # Firebase authentication
├── database.py          # Firebase database operations
├── app.py               # Legacy Streamlit app
├── requirements.txt
└── .env.example
```

## 🛠️ Setup

### 1. Clone and Install Python Dependencies

```bash
cd Cyberbullying-Classifying
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `FIREBASE_*` - Get from [Firebase Console](https://console.firebase.google.com)
- `JWT_SECRET` - Any secure random string

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Start the Backend

```bash
# From project root
python -m uvicorn api.main:app --reload --port 8000
```

### 5. Start the Frontend

```bash
# From frontend directory
npm run dev
```

Visit `http://localhost:3000` for the UI and `http://localhost:8000/docs` for API docs.

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/classify` | POST | Dual AI classification |
| `/api/classify/local` | POST | Local model only |
| `/api/classify/gemini` | POST | Gemini API only |
| `/api/auth/login` | POST | User login |
| `/api/auth/signup` | POST | User registration |
| `/api/posts` | GET/POST | Posts CRUD |
| `/api/posts/{id}/comments` | GET/POST | Comments with detection |

## 🧠 Classification Categories

| Category | Description |
|----------|-------------|
| Not Cyberbullying | Safe, neutral, or positive content |
| Ethnicity/Race | Bullying based on race or nationality |
| Gender/Sexual | Bullying based on gender or orientation |
| Religion | Bullying based on religious beliefs |
| Other | General insults and harassment |

## 📱 Screenshots

The UI features:
- Dark theme with gradient accents
- Real-time text analysis
- Side-by-side model comparison
- Social feed with flagged content warnings
- User reputation tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

## 📄 License

MIT License - feel free to use for any project!
