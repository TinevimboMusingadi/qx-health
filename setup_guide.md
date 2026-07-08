# AIRS Sprint 1 Web Application Setup & Deployment Guide

This guide covers how to run the project locally and deploy it to production using Vercel (Frontend) and Render (Backend).

## 1. Local Development Setup

### Backend (FastAPI)
The backend requires Python 3.9+.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`.

### Frontend (React + Vite)
The frontend requires Node.js.

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`. By default, it communicates with the local backend.

---

## 2. Deployment Guide

### Deploying the Backend on Render
Render is perfect for deploying Python microservices.

1. Create a GitHub repository and push your code (`backend` and `frontend` folders).
2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New > Web Service**.
3. Connect your GitHub repository.
4. Fill in the following settings:
   - **Name**: `airs-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Click **Create Web Service**.
6. Once deployed, Render will give you a URL (e.g., `https://airs-backend.onrender.com`). Copy this URL.

### Deploying the Frontend on Vercel
Vercel is optimized for React/Vite applications.

1. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New > Project**.
2. Import your GitHub repository.
3. In the Configuration screen:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
4. **Environment Variables**:
   Add the following environment variable to tell the frontend where the backend is hosted:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://airs-backend.onrender.com` *(Replace with your actual Render URL)*
5. Click **Deploy**.

## 3. Environment Variables Summary

### Frontend (`frontend/.env`)
For local testing against a production backend, you can create a `.env` file in the `frontend` directory:
```env
VITE_API_URL=https://airs-backend.onrender.com
```

### Backend (`backend/.env`)
The backend **requires** Hugging Face Hub authentication to dynamically download the private AIRS models. You must create a `.env` file locally and add this token in Render:
```env
HF_TOKEN=your_hugging_face_read_token
```
**Important for Render:** You MUST add this token in your Render Dashboard under **Environment > Environment Variables** for the deployment to succeed.
