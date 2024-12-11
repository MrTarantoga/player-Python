import unittest
import json
from webserver_logic import app
from typing import Dict, Any

class TestWebServer(unittest.TestCase):
    def setUp(self):
        """Initialisiert den Testclient vor jedem Test"""
        self.app = app.test_client()
        self.app.testing = True
        
    def create_test_game(self) -> Dict[str, Any]:
        """Hilfsfunktion zum Erstellen eines Testspiels"""
        test_data = {
            "number_of_bases": 4,
            "max_base_level": 5,
            "coordinates": {
                "x": [0, 10],
                "y": [0, 10],
                "z": [0, 10]
            },
            "players": [1, 2]
        }
        
        response = self.app.post('/game/new',
                               data=json.dumps(test_data),
                               content_type='application/json')
        return json.loads(response.data)

    def test_create_new_game(self):
        """Testet die Erstellung eines neuen Spiels"""
        response_data = self.create_test_game()
        
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('game_state', response_data)
        self.assertIn('bases', response_data)
        
        # Überprüfe Spielzustand
        game_state = response_data['game_state']
        self.assertEqual(game_state['tick'], 0)
        self.assertEqual(game_state['player_count'], 2)
        self.assertEqual(game_state['remaining_players'], 2)
        
        # Überprüfe Basen
        bases = response_data['bases']
        self.assertEqual(len(bases), 4)
        
        # Überprüfe, dass jede Basis die erwarteten Felder hat
        expected_base_fields = {'uid', 'name', 'player', 'population', 
                              'level', 'units_until_upgrade', 'position'}
        for base in bases:
            self.assertTrue(all(field in base for field in expected_base_fields))
            self.assertLessEqual(base['level'], 5)  # max_base_level war 5

    def test_perform_action(self):
        """Testet die Ausführung einer Spielaktion"""
        # Erst ein Spiel erstellen
        game_data = self.create_test_game()
        bases = game_data['bases']
        
        # Finde eine Basis von Spieler 1 und eine andere Basis
        player1_base = next(b for b in bases if b['player'] == 1)
        other_base = next(b for b in bases if b['uid'] != player1_base['uid'])
        
        # Führe eine Aktion aus
        action_data = {
            "src_base": player1_base['uid'],
            "dest_base": other_base['uid'],
            "amount": 1  # Versuche, einen Trupp zu bewegen
        }
        
        response = self.app.post('/game/action',
                               data=json.dumps(action_data),
                               content_type='application/json')
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('result', response_data)

    def test_process_tick(self):
        """Testet die Verarbeitung eines Spielticks"""
        # Erst ein Spiel erstellen
        self.create_test_game()
        
        # Tick ausführen
        response = self.app.post('/game/tick')
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['game_state']['tick'], 1)
        self.assertIn('bases', response_data)
        self.assertIn('actions', response_data)

    def test_get_game_state(self):
        """Testet das Abrufen des Spielzustands"""
        # Erst ein Spiel erstellen
        original_data = self.create_test_game()
        
        # Spielzustand abrufen
        response = self.app.get('/game/state')
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('game_state', response_data)
        self.assertIn('bases', response_data)
        self.assertIn('actions', response_data)
        
        # Überprüfe, ob der zurückgegebene Zustand dem ursprünglichen entspricht
        self.assertEqual(
            response_data['game_state']['tick'],
            original_data['game_state']['tick']
        )
        self.assertEqual(
            len(response_data['bases']),
            len(original_data['bases'])
        )

    def test_error_handling(self):
        """Testet die Fehlerbehandlung"""
        # Teste Aktion ohne aktives Spiel
        action_data = {
            "src_base": 1,
            "dest_base": 2,
            "amount": 1
        }
        response = self.app.post('/game/action',
                               data=json.dumps(action_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Teste ungültige Spielerstellung
        invalid_game_data = {
            "number_of_bases": 1,  # Zu wenige Basen
            "max_base_level": 5,
            "coordinates": {
                "x": [0, 10],
                "y": [0, 10],
                "z": [0, 10]
            },
            "players": [1, 2]
        }
        response = self.app.post('/game/new',
                               data=json.dumps(invalid_game_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_action(self):
        """Testet ungültige Aktionen in einem laufenden Spiel"""
        # Erst ein Spiel erstellen
        self.create_test_game()
        
        # Versuche eine Aktion mit nicht existierenden Basen
        invalid_action = {
            "src_base": 9999,  # Nicht existierende Basis
            "dest_base": 9998,  # Nicht existierende Basis
            "amount": 1
        }
        response = self.app.post('/game/action',
                               data=json.dumps(invalid_action),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'error')

if __name__ == '__main__':
    unittest.main() 