from flask import Flask, render_template, request, jsonify
import os
import logging
from dotenv import load_dotenv
import chess
import requests

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

STOCKFISH_API_URL = "https://stockfish.online/api/stockfish.php"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_move', methods=['POST'])
def get_move():
    try:
        fen = request.json.get('fen')
        if not fen:
            return jsonify({'error': 'FEN position required'}), 400
            
        board = chess.Board(fen)
        
        # Call Stockfish API
        params = {
            'fen': fen,
            'depth': '10',
            'mode': 'bestmove'
        }
        
        response = requests.get(STOCKFISH_API_URL, params=params)
        logging.debug(f"API Response: {response.text}")
        
        if response.status_code != 200:
            logging.error(f"Stockfish API error: {response.text}")
            return jsonify({'error': 'Failed to get move from Stockfish API'}), 503
            
        data = response.json()
        best_move = data.get('bestmove')
        
        if best_move:
            # Convert score from centipawns to a more readable format
            score = data.get('evaluation', 0) / 100.0  # Convert centipawns to pawns
            return jsonify({
                'move': best_move,
                'score': score
            })
        else:
            return jsonify({'error': 'No valid moves found'}), 400
            
    except Exception as e:
        logging.error(f"Error in get_move: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)
