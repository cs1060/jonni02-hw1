# Chess Game with Stockfish Integration

A web-based chess game that allows players to get move suggestions from the Stockfish chess engine.

## Features

- Playable chess game with a modern interface
- Move validation and game state tracking
- Stockfish integration for move suggestions
- Simple and intuitive controls

## Deployment Instructions

### Deploy to Render.com

1. Create a Render account at https://render.com
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Fill in the following settings:
   - Name: chess-game (or your preferred name)
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Python Version: 3.9

5. Click "Create Web Service"

The app will be automatically deployed and available at your Render URL.

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Visit `http://localhost:5000` in your browser

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example` and add your Stockfish API key:
```bash
cp .env.example .env
```

3. Edit the `.env` file and replace `your_api_key_here` with your actual Stockfish API key.

## Running the Application

Run the Flask application:
```bash
python app.py
```

The game will be available at `http://localhost:5000`

## How to Play

1. The game starts with white to move
2. Drag and drop pieces to make moves
3. Click the "Get Stockfish Advice" button to get move suggestions
4. Use the "Reset Board" button to start a new game

## Technologies Used

- Flask (Python web framework)
- chess.js (Chess logic)
- chessboard.js (Chess board UI)
- Stockfish API (Chess engine integration)
