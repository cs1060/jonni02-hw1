from flask import Flask, render_template, request, jsonify
import os
import logging
from dotenv import load_dotenv
import chess
import requests

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

STOCKFISH_API_URL = "https://stockfish.online/api/v2/stockfish.php"

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
        
        # Call Stockfish API v2
        data = {
            'fen': fen,
            'depth': 15,
            'time': 1000,  # 1 second think time
            'mode': 'bestmove'
        }
        
        response = requests.post(STOCKFISH_API_URL, json=data)
        logging.debug(f"API Response: {response.text}")
        
        if response.status_code != 200:
            logging.error(f"Stockfish API error: {response.text}")
            return jsonify({'error': 'Failed to get move from Stockfish API'}), 503
            
        data = response.json()
        if not data.get('success'):
            return jsonify({'error': data.get('data', 'Unknown error')}), 400
            
        move_data = data.get('data', {})
        best_move = move_data.get('bestmove')
        score = move_data.get('score', 0)
        
        if best_move:
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
