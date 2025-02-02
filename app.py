from flask import Flask, render_template, request, jsonify
import os
import logging
from dotenv import load_dotenv
import chess  # Import the chess library
from stockfish import Stockfish

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Initialize Stockfish
stockfish = Stockfish(path="/usr/games/stockfish")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_move', methods=['POST'])
def get_move():
    try:
        fen = request.json.get('fen')
        board = chess.Board(fen)
        
        # Set up Stockfish with the current position
        stockfish.set_position([])  # Clear any previous position
        stockfish.set_fen_position(fen)
        
        # Get the best move
        best_move = stockfish.get_best_move()
        
        if best_move:
            return jsonify({
                'move': best_move,
                'score': stockfish.get_evaluation()
            })
        else:
            return jsonify({'error': 'No valid moves found'}), 400
            
    except Exception as e:
        logging.error(f"Error in get_move: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
