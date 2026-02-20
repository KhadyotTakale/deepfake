# bherr — AI-Powered Misinformation Detection

A full-stack web application that detects **deepfake videos**, **AI-generated images**, and **fake news articles** using deep learning and LLM-based analysis.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Video Deepfake Detection** — EfficientNet-B4 + LSTM model analyzes spatial features (frame artifacts) and temporal features (movement/flicker) across video frames
- **AI Image Detection** — LLM-powered vision analysis checks for skin anomalies, hand/finger errors, background coherence, lighting inconsistencies, and other AI-generation tells
- **Fake News Detection** — NLP analysis of text articles for sensationalist language, missing sources, logical inconsistencies, and known misinformation patterns
- **Detection History** — All past analyses stored in Supabase and viewable in-app

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19 · Vite · Tailwind CSS · Lucide Icons |
| **Backend** | FastAPI · Python 3.10+ · Uvicorn |
| **Video Model** | PyTorch · EfficientNet-B4 + LSTM |
| **Image & News** | GPT-4o-mini via FastRouter API (OpenRouter-compatible) |
| **Database** | Supabase (PostgreSQL) |

## Project Structure

```
deepfake_detection/
├── backend/
│   ├── main.py              # FastAPI server, routes, LLM calls
│   ├── model.py             # EfficientNet-B4 + LSTM architecture
│   ├── utils.py             # Frame extraction & preprocessing
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app shell, routing, layout
│   │   ├── api.js           # API client (Axios)
│   │   ├── components/
│   │   │   ├── VideoDetector.jsx
│   │   │   ├── ImageDetector.jsx
│   │   │   ├── NewsDetector.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   └── HistoryPage.jsx
│   │   └── index.css        # Global styles & design tokens
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── LICENSE
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### 1. Clone the repo

```bash
git clone https://github.com/KhadyotTakale/deepfake.git
cd deepfake
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys:
#   OPENROUTER_API_KEY=your_fastrouter_api_key
#   SUPABASE_URL=your_supabase_url
#   SUPABASE_KEY=your_supabase_anon_key

# Start the backend server
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`.

### 3. Frontend Setup

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be live at `http://localhost:5173`.

## Environment Variables

Create a `backend/.env` file using `backend/.env.example` as reference:

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | API key for FastRouter/OpenRouter (used for image & news detection) |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anonymous/public key |
| `MODEL_WEIGHTS_PATH` | *(Optional)* Path to trained deepfake model weights (`.pth`) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/detect/video` | Upload video for deepfake analysis |
| `POST` | `/detect/image` | Upload image for AI-generation detection |
| `POST` | `/detect/news` | Submit text for fake news analysis |
| `GET` | `/history` | Retrieve past detection results |

## How It Works

### Video Detection
Frames are extracted from the uploaded video, preprocessed, and fed through an **EfficientNet-B4** backbone (spatial features) connected to an **LSTM** layer (temporal features). The model outputs a probability score indicating the likelihood of deepfake manipulation.

### Image Detection
The uploaded image is base64-encoded and sent to **GPT-4o-mini** with a detailed forensic analysis prompt that evaluates 8 categories: skin/face anomalies, hand/finger errors, text rendering, background coherence, edge transitions, lighting, clothing, and overall AI-generation indicators.

### News Detection
The article text is sent to the LLM with a prompt checking for sensationalism, missing sources, logical inconsistencies, bias, and known misinformation patterns.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

Built by [Khadyot Takale](https://github.com/KhadyotTakale)
