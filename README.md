# RAG AI Assistant (Video-Based Q&A System)

This project is a **Retrieval-Augmented Generation (RAG) AI Assistant** that answers user questions **only from your own video content**, along with **exact timestamps** showing where the answer appears in the video.

The system is fully **cloud-based**, free to deploy, and works even when your local PC is turned off.

---

##  Key Features

-  Chat-style AI interface
-  Answers generated strictly from video transcripts
-  Shows exact video timestamps (start–end)
-  No hallucinated answers
-  Shareable public link
-  Fully cloud hosted (Vercel + Render)
-  Uses free tiers only
-  Secure API key handling

---

##  System Architecture

- User (Browser)
  ↓
- Frontend (Vercel)
- ↓ POST /ask
- Backend API (Flask on Render)
  ↓
- JSON Transcripts (from videos)
  ↓
- Groq LLM (Cloud)
  ↓
- Answer + Timestamp
 
 ## Hierarchy way direction
 RAG-app/
│
├── backend/
│ ├── app.py # Flask API
│ ├── process_incoming.py # RAG logic (retrieval + Groq)
│ ├── load_chunks.py # Optional embedding loader
│ ├── embeddings.joblib # (Optional) precomputed embeddings
│ ├── jsons/ # Video transcript JSON files
│ └── requirements.txt
│
├── frontend/
│ ├── index.html # UI
│ ├── style.css # Styling
│ └── script.js # API calls
│
└── README.md

##  How Video Data Is Used

1. Videos are converted to audio (`.mp3`)
2. Audio is transcribed into JSON
3. Each JSON contains:
   - Text
   - Start time
   - End time
   - (Optional) lecture number / title
4. These JSON files are uploaded to the backend (`backend/jsons/`)
5. AI retrieves answers **only from these JSONs**

 If a concept is not present in the videos, the AI responds:
 # Not covered in the video.

 ##  Example Questions

- `Where is greater than operator taught?`
- `Explain not equal operator with timestamp`
- `At what time assignment operator is explained?`
- `Is plus equal operator covered?`

---

##  Deployment Setup

### Frontend (Vercel)
- Type: Static site
- Always online
- Public shareable URL

### Backend (Render)
- Type: Python Web Service
- Framework: Flask
- Free tier supported
- Cold start: ~30–60 seconds

---

##  Groq API Setup

1. Create a Groq API key
2. In **Render → Environment Variables**, add:
3. GROQ_API_KEY=your_api_key_here
4. Save → Manual Deploy

# API keys are never exposed to the frontend.
