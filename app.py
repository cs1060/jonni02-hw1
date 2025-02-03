from flask import Flask, render_template, request, jsonify
import os
import logging
from dotenv import load_dotenv
import chess
import requests

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

LICHESS_API_URL = "https://lichess.org/api/cloud-eval"

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
        
        # Handle game-over positions
        if board.is_game_over():
            if board.is_checkmate():
                return jsonify({'move': '', 'score': -10000 if board.turn else 10000, 'status': 'checkmate'}), 200
            elif board.is_stalemate():
                return jsonify({'move': '', 'score': 0, 'status': 'stalemate'}), 200
            else:
                return jsonify({'move': '', 'score': 0, 'status': 'draw'}), 200
        
        # Call Lichess API with timeout
        response = requests.get(
            LICHESS_API_URL,
            params={'fen': fen},
            headers={'Accept': 'application/json'},
            timeout=3  # 3 second timeout
        )
        
        if response.status_code != 200:
            logging.error(f"Lichess API error: {response.text}")
            return jsonify({'error': 'Failed to get move from Lichess API'}), 503
            
        data = response.json()
        pvs = data.get('pvs', [])
        if not pvs:
            return jsonify({'error': 'No analysis available'}), 400
            
        best_move = pvs[0].get('moves', '').split()[0]  # Get first move from PV
        score = pvs[0].get('cp', 0)  # Centipawns score
        
        if best_move:
            # Validate the move is legal
            try:
                move = chess.Move.from_uci(best_move)
                if move not in board.legal_moves:
                    return jsonify({'error': 'Invalid move returned by API'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid move format returned by API'}), 400
                
            return jsonify({
                'move': best_move,
                'score': score
            })
        else:
            return jsonify({'error': 'No valid moves found'}), 400
            
    except requests.Timeout:
        logging.error("Lichess API timeout")
        return jsonify({'error': 'API request timed out'}), 503
    except requests.RequestException as e:
        logging.error(f"Request error: {str(e)}")
        return jsonify({'error': 'Failed to connect to Lichess API'}), 503
    except Exception as e:
        logging.error(f"Error in get_move: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)
