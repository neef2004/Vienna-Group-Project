# Itinerary App

A full-stack itinerary planning app with a React frontend and a Flask backend.

## Project Structure

```text
itinerary-app/
  frontend/   React + TypeScript + Vite app
  backend/    Flask API
```

## Tech Stack

- Frontend: React, TypeScript, Vite
- Backend: Flask
- Linting: Oxlint for the frontend

## Getting Started

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd itinerary-app
```

Replace `YOUR-USERNAME` and `YOUR-REPO-NAME` with the actual GitHub repository path.

## Frontend Setup

Go into the frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will usually run at:

```text
http://localhost:5173
```

If that port is already in use, Vite may choose another one.

### Frontend Scripts

```bash
npm run dev
```

Starts the frontend development server.

```bash
npm run build
```

Builds the frontend for production.

```bash
npm run lint
```

Runs the frontend linter.

```bash
npm run preview
```

Previews the production build locally.

## Backend Setup

Go into the backend folder:

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask server:

```bash
python run.py
```

The backend will usually run at:

```text
http://localhost:5000
```

## Running the Full App

Use two terminal windows.

Terminal 1:

```bash
cd backend
source venv/bin/activate
python run.py
```

Terminal 2:

```bash
cd frontend
npm run dev
```

## API Routes

Backend API routes should be placed in the Flask backend under:

```text
backend/app/routes/
```

Recommended route prefix:

```text
/api
```

Example health check route:

```text
GET /api/health
```

## Notes for Contributors

- Keep frontend code inside `frontend/`.
- Keep backend code inside `backend/`.
- Do not commit `node_modules/`, virtual environments, cache folders, or `.env` files.
- Add environment variable examples to `.env.example` instead of committing real secrets.

