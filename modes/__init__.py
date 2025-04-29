"""
Operation modes for AnonCodexCli.
"""
from modes.interactive import InteractiveMode
from modes.autonomous import AutonomousMode
from modes.manual import ManualMode

def get_mode_class(mode_name: str):
    """
    Get the mode class for the given mode name.
    
    Args:
        mode_name: Mode name ('interactive', 'autonomous', or 'manual')
        
    Returns:
        Mode class
    """
    mode_map = {
        "interactive": InteractiveMode,
        "autonomous": AutonomousMode,
        "manual": ManualMode
    }
    
    return mode_map.get(mode_name.lower(), InteractiveMode) 