import pygame
import os
import sys
import pytmx
from camera import Camera
from typing import Optional
from CollisionManager import CollisionManager
from TMXViewer import TMXViewer

def main():
    """Entry point"""
    # Path to TMX file - adjust as needed
    tmx_path = os.path.join("..", "resources", "world.tmx")

    if not os.path.exists(tmx_path):
        print(f"TMX file not found at: {tmx_path}")
        print("Please check the path and try again.")
        sys.exit(1)

    viewer = TMXViewer(tmx_path)
    viewer.run()

if __name__ == "__main__":
    main()
