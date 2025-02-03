# Chess Game with AI Integration

A web-based chess game that allows players to get move suggestions from the Lichess Cloud Evaluation API.

Live Demo: [https://jonni02-hw1.onrender.com](https://jonni02-hw1.onrender.com)

## Features

- Playable chess game with a modern interface
- Move validation and game state tracking
- AI assistance powered by Lichess Cloud Evaluation
- Simple and intuitive controls
- Dark/Light theme toggle
- Comprehensive test suite

## Contributors

- **Jon Syla**
  - Worked on: Complete application development including:
    - Frontend UI with dark/light theme support
    - Backend integration with Lichess Cloud Evaluation API
    - Comprehensive test suite implementation
    - Security vulnerability fixes
    - Deployment to Render.com
  - Time spent: 5.5 hours
  - Challenges encountered:
    - AI assistance precision: Ensuring the AI followed instructions accurately
    - Result verification: Need for thorough testing to confirm AI-implemented changes worked as intended

## Local Development

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

## Running Tests

Run the test suite:
```bash
python -m pytest tests/test_app.py -v
```

## How to Play

1. The game starts with white to move
2. Drag and drop pieces to make moves
3. Click the "Get AI Advice" button to get move suggestions from Lichess
4. Use the "New Game" button to start a new game

## Technologies Used

- Flask (Python web framework)
- chess.js (Chess logic)
- chessboard.js (Chess board UI)
- Lichess Cloud Evaluation API (Chess engine integration)
- pytest (Testing framework)
