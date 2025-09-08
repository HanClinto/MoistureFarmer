"""Centralized pydantic model rebuilds to resolve forward references.
Call rebuild_models() early (e.g., in simulation.__init__) so importing simulation ensures models are fully defined.
"""
from typing import List, Callable

# Import model classes lazily inside function to avoid circulars at module import time.

def rebuild_models(verbose: bool = False) -> List[str]:
    rebuilt: List[str] = []
    def try_rebuild(name: str, fn: Callable[[], None]):
        try:
            fn()
            rebuilt.append(name)
        except Exception as e:
            if verbose:
                print(f"[rebuild_models] Skipped {name}: {e}")
    # Core base/graph dependent ordering: Entity -> Component -> Chassis -> Storage -> World
    from simulation.core.entity.Entity import Entity
    try_rebuild('Entity', Entity.model_rebuild)
    
    try:
        from simulation.core.entity.ComponentSlot import ComponentSlot
        try_rebuild('ComponentSlot', ComponentSlot.model_rebuild)
    except Exception as e:
        if verbose:
            print(f"[rebuild_models] ComponentSlot import failed: {e}")
    
    try:
        from simulation.core.entity.component.Component import Component
        try_rebuild('Component', Component.model_rebuild)
    except Exception as e:
        if verbose:
            print(f"[rebuild_models] Component import failed: {e}")
    
    try:
        from simulation.core.entity.Chassis import Chassis
        try_rebuild('Chassis', Chassis.model_rebuild)
    except Exception as e:
        if verbose:
            print(f"[rebuild_models] Chassis import failed: {e}")
    
    try:
        from simulation.core.entity.component.Storage import Storage
        try_rebuild('Storage', Storage.model_rebuild)
    except Exception as e:
        if verbose:
            print(f"[rebuild_models] Storage import failed: {e}")
    
    try:
        from simulation.core.entity.component.Gripper import Gripper
        try_rebuild('Gripper', Gripper.model_rebuild)
    except Exception as e:
        if verbose:
            print(f"[rebuild_models] Gripper import failed: {e}")
    
    try:
        from simulation.core.World import World
        try_rebuild('World', World.model_rebuild)
    except Exception as e:
        if verbose:
            print(f"[rebuild_models] World import failed: {e}")
    return rebuilt

# Allow direct execution for diagnostics
if __name__ == '__main__':
    done = rebuild_models(verbose=True)
    print("Rebuilt:", done)
