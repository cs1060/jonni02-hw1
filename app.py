from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv
import chess  # Import the chess library
import logging

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

STOCKFISH_API_URL = "https://chess-api.com/v1"  # Updated API URL

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_move', methods=['POST'])
def get_move():
    fen = request.json.get('fen')
    board = chess.Board(fen)  # Initialize the board with the given FEN
    
    # Call Chess API
    headers = {'Content-Type': 'application/json'}  # Use JSON content type
    data = {
        'fen': board.fen(),
        'depth': 12,  # Set desired depth
        'maxThinkingTime': 50  # Set max thinking time in ms
    }

    try:
        response = requests.post(STOCKFISH_API_URL, headers=headers, json=data)  # Send JSON data
        response.raise_for_status()  # Raise an error for bad responses
        logging.debug(f"API Response Status Code: {response.status_code}")  # Log status code
        logging.debug(f"API Response Content: {response.content}")  # Log raw response content
        
        try:
            data = response.json()
            logging.debug(f"Parsed API Response: {data}")  # Log parsed JSON
            return jsonify(data)
        except ValueError as e:
            logging.error(f"JSON parsing error: {e}")
            return jsonify({'error': 'Invalid JSON response from API'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
