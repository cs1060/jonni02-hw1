from flask import Flask, render_template, request, jsonify
import os
import logging
from dotenv import load_dotenv
import chess
from stockfish import Stockfish
import subprocess

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
stockfish = None  # Initialize as global variable

# Find Stockfish path
def find_stockfish():
    try:
        # First try environment variable
        env_path = os.getenv('STOCKFISH_PATH')
        if env_path:
            try:
                result = subprocess.run([env_path], capture_output=True, timeout=1)
                logging.info(f"Found Stockfish at env path: {env_path}")
                return env_path
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                logging.debug(f"Failed to find Stockfish at env path {env_path}: {str(e)}")
        
        # Try common paths as fallback
        paths = [
            '/opt/stockfish/stockfish',  # Our custom location
            '/usr/games/stockfish',
            '/usr/bin/stockfish',
            '/usr/local/bin/stockfish',
            'stockfish'  # Try PATH
        ]
        
        for path in paths:
            try:
                result = subprocess.run([path], capture_output=True, timeout=1)
                logging.info(f"Found Stockfish at: {path}")
                return path
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                logging.debug(f"Failed to find Stockfish at {path}: {str(e)}")
                continue
                
        raise FileNotFoundError("Stockfish not found in any location")
    except Exception as e:
        logging.error(f"Error finding Stockfish: {str(e)}")
        raise

def init_stockfish():
    global stockfish
    try:
        stockfish_path = find_stockfish()
        stockfish = Stockfish(path=stockfish_path)
        # Test that it works
        stockfish.get_parameters()
        logging.info("Stockfish initialized successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Stockfish: {str(e)}")
        stockfish = None
        return False

# Try to initialize Stockfish at startup
init_stockfish()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_move', methods=['POST'])
def get_move():
    global stockfish
    try:
        if stockfish is None:
            # Try to initialize again if it failed before
            if not init_stockfish():
                return jsonify({'error': 'Stockfish not available'}), 503
            
        fen = request.json.get('fen')
        if not fen:
            return jsonify({'error': 'FEN position required'}), 400
            
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
    app.run(host='0.0.0.0', port=port)
