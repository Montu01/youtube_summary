# YouTube Video Summarizer

A modern web application that generates summaries of YouTube videos and shorts, supporting both Hindi and English languages.

## Features

- Extract content from YouTube videos and shorts via URL
- Generate concise summaries in both Hindi and English
- Modern, responsive UI built with React
- Backend API powered by Python
- High-quality thumbnails with 2x, 4K, and 8K upscaling options

## Project Structure

- `frontend/` - React application
- `backend/` - Python Flask API

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Start the backend server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Open your browser to http://localhost:3000

## Deployment on Render

This application can be easily deployed on Render's free tier. Follow these steps to deploy your own instance:

### Prerequisites

1. Create a [Render](https://render.com) account if you don't have one
2. Push your code to a GitHub repository
3. Make sure your `.env.production` file is properly configured

### Deploy Backend (Web Service)

1. From the Render dashboard, click "New" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - Name: `youtube-summarizer-backend` (or your preferred name)
   - Environment: `Python 3`
   - Region: Choose the region closest to your users
   - Branch: `main` (or your default branch)
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: Free (or select a paid plan for better performance)
4. Add these environment variables:
   - `FLASK_ENV`: `production`
   - `RENDER`: `true`
   - `FRONTEND_URL`: URL of your frontend (after it's deployed)
5. Click "Create Web Service"

### Deploy Frontend (Static Site)

1. From the Render dashboard, click "New" and select "Static Site"
2. Connect the same GitHub repository
3. Configure the service:
   - Name: `youtube-summarizer-frontend` (or your preferred name)
   - Branch: `main` (or your default branch)
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `build`
4. Add this environment variable:
   - `REACT_APP_API_URL`: URL of your backend service (from the previous step)
5. Click "Create Static Site"

### Connect Frontend and Backend

After both services are deployed:

1. Update the backend environment variable:
   - Go to the backend service dashboard
   - Add/update `FRONTEND_URL` with your frontend URL (e.g., `https://youtube-summarizer-frontend.onrender.com`)

2. Update the frontend environment variable:
   - Go to the frontend service dashboard
   - Add/update `REACT_APP_API_URL` with your backend URL (e.g., `https://youtube-summarizer-backend.onrender.com`)
   - Trigger a new deploy for changes to take effect

Your YouTube Video Summarizer should now be fully deployed and accessible online!
