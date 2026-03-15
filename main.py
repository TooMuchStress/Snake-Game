
import pygame
import sys
from settings import *
from entities import Snake, Food
from states import MenuState

class Game:
    """
    The main controller class. Initializes Pygame, manages the core game loop,
    holds global variables, and delegates logic to the active State.
    """
    def __init__(self):
        # Initialize all required Pygame modules
        pygame.init()
        
        # Set up the main display window using dimensions from settings
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        
        # Create a clock object to enforce the frame rate (FPS)
        self.clock = pygame.time.Clock()
        
        # Initialize fonts used for UI and messages
        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.score_font = pygame.font.SysFont("Arial", 20)
        
        # Boolean to keep the main application loop running
        self.running = True
        
        # Set up game entities, score, and counters
        self.reset_game()
        
        # State machine initialization
        self.current_state = None
        # Boot the game directly into the Menu State
        self.change_state(MenuState(self))

    def reset_game(self):
        """
        Reinitializes the game entities and variables for a fresh playthrough.
        """
        # Create fresh instances of the Snake and Food
        self.snake = Snake()
        self.food = Food()
        
        # Sprite group used purely for easy rendering of Pygame Sprites
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.food)
        
        # Place the food on the board for the first time
        self.food.respawn(self.snake.body)
        
        # Reset gameplay tracking variables
        self.score = 0
        self.frames_played = 0

    def change_state(self, new_state):
        """
        Handles transitioning from one game state to another.
        """
        self.current_state = new_state
        self.current_state.enter() # Trigger any setup logic in the new state

    def draw_base_ui(self):
        """
        Renders the static visual elements: the background grid, the playable area border,
        and the top navigation bar containing score and time.
        """
        # Render the checkered green background grid
        for y in range(TOP_BAR_HEIGHT, HEIGHT, CELL_SIZE):
            for x in range(0, WIDTH, CELL_SIZE):
                # Use a mathematical check to alternate colors for adjacent cells
                color = GREEN if ((x // CELL_SIZE) + (y // CELL_SIZE)) % 2 == 0 else DARK_GREEN
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))

        # Render a white perimeter border around the playable area
        field_rect = pygame.Rect(0, TOP_BAR_HEIGHT, WIDTH, HEIGHT - TOP_BAR_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, field_rect, 2)

        # Render the background for the top UI bar
        pygame.draw.rect(self.screen, (40, 40, 40), (0, 0, WIDTH, TOP_BAR_HEIGHT))
        # Render a thick separator line right under the top UI bar
        pygame.draw.line(self.screen, WHITE, (0, TOP_BAR_HEIGHT), (WIDTH, TOP_BAR_HEIGHT), 2)
        
        # Render the current score text and position it on the left side
        score_text = self.score_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, TOP_BAR_HEIGHT // 2 - score_text.get_height() // 2))
        
        # Calculate the elapsed time in minutes and seconds
        total_seconds = self.frames_played // FPS
        minutes, seconds = divmod(total_seconds, 60)
        
        # Render the formatted time string and anchor it to the right side
        time_text = self.score_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        self.screen.blit(time_text, (WIDTH - time_text.get_width() - 20, TOP_BAR_HEIGHT // 2 - time_text.get_height() // 2))

    def draw_game_objects(self):
        """
        Helper method to quickly draw the snake and the food sprite group.
        """
        self.snake.draw(self.screen)
        self.all_sprites.draw(self.screen)

    def show_message(self, text):
        """
        Draws a large, prominent message across the center of the screen,
        backed by a dark semi-transparent banner for readability.
        """
        # Create and draw the dark translucent banner
        banner = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        banner.fill(BLACK_ALPHA)
        self.screen.blit(banner, (0, HEIGHT // 2 - 50))
        
        # Render the text surface and position its center directly in the middle of the screen
        text_surface = self.font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)

    def run(self):
        """
        The main application loop. Continuously handles events, updates game logic, 
        and redraws the screen until the user closes the window.
        """
        while self.running:
            # Enforce the game's strict frame rate
            self.clock.tick(FPS)
            
            # Retrieve all queued user input events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Break the loop if the 'X' button on the window is clicked
                    self.running = False
                else:
                    # Pass unhandled events down to the current active state
                    self.current_state.handle_event(event)
            
            # Execute the frame-by-frame logic for the active state
            self.current_state.update()
            
            # Clear the entire screen to black to prevent visual tearing
            self.screen.fill((0, 0, 0))
            
            # Tell the active state to draw its specific graphics
            self.current_state.draw(self.screen)
            
            # Swap the double buffers to push the drawn frame to the monitor
            pygame.display.flip()

        # Safely shut down Pygame and terminate the script
        pygame.quit()
        sys.exit()

# Program entry point
if __name__ == "__main__":
    game = Game()
    game.run()