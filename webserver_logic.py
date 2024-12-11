from flask import Flask, request, jsonify
import generator_logic as gl
import generator_state as gs
from typing import Dict, List, Union, Any

app = Flask(__name__)

# Globaler Spielzustand
game_bases: List[gs.Base] = []
game_actions: List[gs.Action] = []
current_game_state: Union[gs.GameState, None] = None

@app.route('/game/new', methods=['POST'])
def create_new_game() -> Dict[str, Any]:
    """
    Erstellt ein neues Spiel mit den angegebenen Parametern
    
    Erwartet JSON:
    {
        "number_of_bases": int,
        "max_base_level": int,
        "coordinates": {
            "x": [min, max],
            "y": [min, max],
            "z": [min, max]
        },
        "players": [player_ids]
    }
    """
    global game_bases, current_game_state
    
    try:
        data = request.get_json()
        
        # Karte generieren
        bases = list(gl.generate_random_map(
            number_of_bases=data['number_of_bases'],
            max_base_level=data['max_base_level'],
            x=tuple(data['coordinates']['x']),
            y=tuple(data['coordinates']['y']),
            z=tuple(data['coordinates']['z'])
        ))
        
        # Spieler zuweisen
        game_bases = gl.assert_player_to_bases(bases, data['players'])
        
        # Spielzustand initialisieren
        current_game_state = gs.GameState(
            uid=1,  # Vereinfacht - sollte in Produktion eindeutig sein
            tick=0,
            player_count=len(data['players']),
            remaining_players=len(data['players']),
            player=data['players'][0]
        )
        
        return jsonify({
            "status": "success",
            "game_state": current_game_state.to_dict(),
            "bases": [base.to_dict() for base in game_bases]
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@app.route('/game/action', methods=['POST'])
def perform_action() -> Dict[str, Any]:
    """
    Führt eine Spieleraktion aus
    
    Erwartet JSON:
    {
        "src_base": int,
        "dest_base": int,
        "amount": int
    }
    """
    global game_bases, game_actions, current_game_state
    
    if not current_game_state:
        return jsonify({
            "status": "error",
            "message": "No active game"
        }), 400
    
    try:
        data = request.get_json()
        
        # Finde Quell- und Zielbasis
        src_base = next((b for b in game_bases if b.uid == data['src_base']), None)
        dest_base = next((b for b in game_bases if b.uid == data['dest_base']), None)
        
        if not src_base or not dest_base:
            return jsonify({
                "status": "error",
                "message": "Base not found"
            }), 400
            
        # Erstelle Benutzeraktion
        user_action = gs.UserAction(src_base, dest_base, data['amount'])
        
        # Berechne Aktion
        result = gl.compute_user_action(game_bases, user_action, current_game_state)
        
        # Verarbeite Ergebnis
        if isinstance(result, gs.Action):
            game_actions.append(result)
            response_data = result.to_dict()
        else:  # Liste von aktualisierten Basen
            game_bases = result
            response_data = [base.to_dict() for base in game_bases]
            
        return jsonify({
            "status": "success",
            "result": response_data
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@app.route('/game/tick', methods=['POST'])
def process_tick() -> Dict[str, Any]:
    """Verarbeitet einen Spieltick und aktualisiert alle laufenden Aktionen"""
    global game_bases, game_actions, current_game_state
    
    if not current_game_state:
        return jsonify({
            "status": "error",
            "message": "No active game"
        }), 400
        
    try:
        # Verarbeite alle aktiven Aktionen
        updated_actions = []
        for action in game_actions:
            result = gl.compute_action(game_bases, action)
            
            if isinstance(result, gs.Action):
                updated_actions.append(result)
            elif isinstance(result, gs.Base):
                # Basis wurde aktualisiert, keine weitere Aktion nötig
                pass
                
        game_actions = updated_actions
        current_game_state.tick += 1
        
        return jsonify({
            "status": "success",
            "game_state": current_game_state.to_dict(),
            "bases": [base.to_dict() for base in game_bases],
            "actions": [action.to_dict() for action in game_actions]
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@app.route('/game/state', methods=['GET'])
def get_game_state() -> Dict[str, Any]:
    """Gibt den aktuellen Spielzustand zur��ck"""
    if not current_game_state:
        return jsonify({
            "status": "error",
            "message": "No active game"
        }), 400
        
    return jsonify({
        "status": "success",
        "game_state": current_game_state.to_dict(),
        "bases": [base.to_dict() for base in game_bases],
        "actions": [action.to_dict() for action in game_actions]
    })

if __name__ == '__main__':
    app.run(debug=True)
