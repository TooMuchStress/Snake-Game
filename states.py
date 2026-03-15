
import pygame
from settings import *

class State:
    """
    Base class for all game states.
    Provides an interface that specific states will override.
    """
    def __init__(self, game):
        # Store a reference to the main Game object to access UI and entities
        self.game = game

    def enter(self): 
        """Called exactly once when the state becomes active."""
        pass
    
    def handle_event(self, event): 
        """Processes Pygame events (like keyboard inputs) specific to this state."""
        pass
    
    def update(self): 
        """Runs the game logic specific to this state every frame."""
        pass
    
    def draw(self, surface): 
        """Renders the visuals for this state onto the main surface."""
        pass


class MenuState(State):
    """
    State representing the initial main menu screen.
    """
    def handle_event(self, event):
        # Start the game and transition to PlayingState if ENTER is pressed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.game.change_state(PlayingState(self.game))

    def draw(self, surface):
        # Draw the standard background, grid, and initial entity positions
        self.game.draw_base_ui()
        self.game.draw_game_objects()
        
        # Create and apply a dark semi-transparent overlay over the game field
        overlay = pygame.Surface((WIDTH, HEIGHT - TOP_BAR_HEIGHT), pygame.SRCALPHA)
        overlay.fill(BLACK_ALPHA)
        surface.blit(overlay, (0, TOP_BAR_HEIGHT))
        
        # Render the text surfaces for title, controls, and instructions
        title_surf = self.game.font.render("SNAKE GAME", True, GREEN)
        controls_surf = self.game.score_font.render("Controls: WASD to move | SPACE to pause", True, WHITE)
        start_surf = self.game.font.render("Press ENTER to start playing", True, WHITE)
        
        # Calculate the vertical center of the playable area
        center_y = TOP_BAR_HEIGHT + (HEIGHT - TOP_BAR_HEIGHT) // 2
        
        # Blit (draw) the text surfaces onto the screen using their rect centers for alignment
        surface.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, center_y - 60)))
        surface.blit(controls_surf, controls_surf.get_rect(center=(WIDTH // 2, center_y - 10)))
        surface.blit(start_surf, start_surf.get_rect(center=(WIDTH // 2, center_y + 40)))


class PlayingState(State):
    """
    State representing the active gameplay phase.
    """
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Transition to PauseState if SPACEBAR is pressed
            if event.key == pygame.K_SPACE:
                self.game.change_state(PauseState(self.game))
            # Handle directional inputs using WASD keys
            elif event.key == pygame.K_w: self.game.snake.change_direction("up")
            elif event.key == pygame.K_s: self.game.snake.change_direction("down")
            elif event.key == pygame.K_a: self.game.snake.change_direction("left")
            elif event.key == pygame.K_d: self.game.snake.change_direction("right")

    def update(self):
        # Increment the frame counter used to track elapsed time
        self.game.frames_played += 1
        
        # Move the snake and determine if it survived the movement
        alive = self.game.snake.update()
        
        # If the snake collided with a wall or itself, end the game
        if not alive:
            self.game.change_state(GameOverState(self.game))
            return
            
        # Check if the snake's head overlaps with the food's rectangle
        if self.game.snake.body[0].colliderect(self.game.food.rect):
            self.game.score += 1                 # Increase the player's score
            self.game.snake.grow_pending = True  # Signal the snake to grow on the next update
            self.game.food.respawn(self.game.snake.body) # Relocate the food

    def draw(self, surface):
        # Draw the active game without any dark overlays
        self.game.draw_base_ui()
        self.game.draw_game_objects()


class PauseState(State):
    """
    State representing a paused game session.
    """
    def handle_event(self, event):
        # Resume gameplay if SPACEBAR is pressed again
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.change_state(PlayingState(self.game))

    def draw(self, surface):
        # Draw the current frozen state of the game
        self.game.draw_base_ui()
        self.game.draw_game_objects()
        
        # Display an unmissable pause message over the screen
        self.game.show_message("Game Paused")


class GameOverState(State):
    """
    State representing the end screen (win or lose conditions).
    """
    def enter(self):
        # Record the exact moment the Game Over state started
        self.timer_start = pygame.time.get_ticks()

    def update(self):
        # Automatically reset and go back to Menu after 3000 milliseconds (3 seconds)
        if pygame.time.get_ticks() - self.timer_start >= 3000:
            self.game.reset_game()
            self.game.change_state(MenuState(self.game))

    def draw(self, surface):
        # Keep displaying the final board configuration
        self.game.draw_base_ui()
        self.game.draw_game_objects()
        
        # 863 is roughly the maximum score (all cells filled) for 900x600 board with 25px cells
        if self.game.score >= 863:
            self.game.show_message("You Won!")
        else:
            self.game.show_message(f"You Lost! Score: {self.game.score}")