"""
Helper functions for testing game logic
"""

def find_player_base(bases, player_id):
    """
    Find the first base belonging to a player
    
    Args:
        bases: List of bases to search
        player_id: ID of the player to find base for
        
    Returns:
        Base: First base found belonging to the player
        
    Raises:
        ValueError: If no base is found for the player
    """
    for base in bases:
        if base.player == player_id:
            return base
    raise ValueError(f"No base found for player {player_id}")

def find_player_bases(bases, player_id):
    """
    Find all bases belonging to a player
    
    Args:
        bases: List of bases to search
        player_id: ID of the player to find bases for
        
    Returns:
        list[Base]: All bases belonging to the player
        
    Raises:
        ValueError: If no bases are found for the player
    """
    player_bases = [base for base in bases if base.player == player_id]
    if not player_bases:
        raise ValueError(f"No bases found for player {player_id}")
    return player_bases 

def find_base_by_uid(bases, uid):
    """
    Find a base with a specific UID
    
    Args:
        bases: List of bases to search
        uid: UID of the base to find
        
    Returns:
        Base: The base with the specified UID
        
    Raises:
        ValueError: If no base with the given UID is found
    """
    for base in bases:
        if base.uid == uid:
            return base
    raise ValueError(f"No base found with uid {uid}")