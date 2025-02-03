import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import requests
import chess

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

class TestChessApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.starting_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.checkmate_fen = 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4'  # Scholar's mate
        self.stalemate_fen = '5k2/5P2/5K2/8/8/8/8/8 b - - 0 1'  # Basic stalemate position

    def test_index_route(self):
        """Test the main page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Play chess with AI assistance', response.data)
        self.assertIn(b'AI assistance is powered by Lichess Cloud Evaluation', response.data)

    def test_get_move_missing_fen(self):
        """Test /get_move endpoint with missing FEN"""
        response = self.app.post('/get_move', 
                               data=json.dumps({}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'FEN position required')

    def test_get_move_invalid_fen(self):
        """Test /get_move endpoint with invalid FEN"""
        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': 'invalid_fen'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 500)

    def test_get_move_empty_fen(self):
        """Test /get_move endpoint with empty FEN string"""
        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': ''}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'FEN position required')

    def test_get_move_checkmate_position(self):
        """Test /get_move endpoint with a checkmate position"""
        board = chess.Board(self.checkmate_fen)
        self.assertTrue(board.is_checkmate())
        
        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': self.checkmate_fen}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['move'], '')
        self.assertEqual(data['score'], 10000)  # Black is checkmated (positive score means White is winning)
        self.assertEqual(data['status'], 'checkmate')

    def test_get_move_stalemate_position(self):
        """Test /get_move endpoint with a stalemate position"""
        board = chess.Board(self.stalemate_fen)
        self.assertTrue(board.is_stalemate())
        
        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': self.stalemate_fen}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['move'], '')
        self.assertEqual(data['score'], 0)
        self.assertEqual(data['status'], 'stalemate')

    @patch('requests.get')
    def test_get_move_successful(self, mock_get):
        """Test /get_move endpoint with valid FEN and successful API response"""
        # Mock successful Lichess API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'pvs': [{
                'moves': 'e2e4',
                'cp': 35
            }]
        }
        mock_get.return_value = mock_response

        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': self.starting_fen}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('move', data)
        self.assertIn('score', data)
        self.assertEqual(data['move'], 'e2e4')
        self.assertEqual(data['score'], 35)

    @patch('requests.get')
    def test_get_move_no_pvs(self, mock_get):
        """Test /get_move endpoint when API response has no PVs"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'pvs': []}
        mock_get.return_value = mock_response

        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': self.starting_fen}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No analysis available')

    @patch('requests.get')
    def test_get_move_invalid_move_format(self, mock_get):
        """Test /get_move endpoint when API returns invalid move format"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'pvs': [{
                'moves': 'invalid',
                'cp': 0
            }]
        }
        mock_get.return_value = mock_response

        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': self.starting_fen}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid move format returned by API')

    @patch('requests.get')
    def test_get_move_api_error(self, mock_get):
        """Test /get_move endpoint when Lichess API fails"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': self.starting_fen}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Failed to get move from Lichess API')

    @patch('requests.get')
    def test_get_move_timeout(self, mock_get):
        """Test /get_move endpoint when Lichess API times out"""
        mock_get.side_effect = requests.Timeout()

        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': self.starting_fen}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'API request timed out')

    @patch('requests.get')
    def test_get_move_connection_error(self, mock_get):
        """Test /get_move endpoint when connection fails"""
        mock_get.side_effect = requests.ConnectionError()

        response = self.app.post('/get_move', 
                               data=json.dumps({'fen': self.starting_fen}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Failed to connect to Lichess API')

if __name__ == '__main__':
    unittest.main()
