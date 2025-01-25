import pygame
import os
from dotenv import load_dotenv
import requests
from client.config import SERVER_BASE_URL

def main():
    load_dotenv()
    API_KEY = os.environ.get("API_KEY", "")
    response = requests.get(SERVER_BASE_URL + "/games", headers={"x-api-key": API_KEY})
    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Create a game window (800x600)
    pygame.display.set_caption("My Game")  # Set the window title

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check if the quit event is triggered
                running = False
    pygame.quit()
    
