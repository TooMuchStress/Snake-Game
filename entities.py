
import pygame
import random
from settings import *

class Food(pygame.sprite.Sprite):
    """
    Represents the food that the snake eats to grow and increase the score.
    """
    def __init__(self):
        super().__init__()
        # Create a transparent surface for the food entity
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        # Draw a red circle as the base of the food
        pygame.draw.circle(self.image, RED, (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2)
        
        # Draw a white outline around the food to make it pop visually
        pygame.draw.circle(self.image, WHITE, (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2, 2)
        
        # Get the bounding rectangle used for positioning and collision detection
        self.rect = self.image.get_rect()
        
        # Initialize position off-screen before the first respawn is called
        self.x = -1
        self.y = -1

    def respawn(self, snake_body):
        """
        Moves the food to a new random location on the grid.
        Ensures the food does not spawn inside the snake's body.
        """
        while True:
            # Calculate random X coordinate aligned to the grid cells
            self.rect.x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            
            # Calculate random Y coordinate, ensuring it spawns below the top UI bar
            self.rect.y = random.randint(TOP_BAR_HEIGHT // CELL_SIZE, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            
            # Check if the generated position overlaps with any part of the snake
            collision = any(segment.x == self.rect.x and segment.y == self.rect.y for segment in snake_body)
            
            # If the spot is free (no collision), break out of the loop
            if not collision:
                break


class Snake:
    """
    Represents the player-controlled snake entity.
    """
    def __init__(self):
        # The snake's body is a list of pygame.Rect objects. Starts with a single segment.
        self.body = [pygame.Rect(100, 100, CELL_SIZE, CELL_SIZE)]
        
        # Current movement direction
        self.direction = ""
        
        # Next queued movement direction (prevents reversing into itself instantly)
        self.new_direction = ""
        
        # Flag indicating whether the snake should grow on the next frame
        self.grow_pending = False

    def change_direction(self, dir_string):
        """
        Updates the intended direction of the snake.
        Includes logic to prevent the snake from making an impossible 180-degree turn.
        """
        if dir_string == "up" and self.direction != "down": 
            self.new_direction = "up"
        elif dir_string == "down" and self.direction != "up": 
            self.new_direction = "down"
        elif dir_string == "left" and self.direction != "right": 
            self.new_direction = "left"
        elif dir_string == "right" and self.direction != "left": 
            self.new_direction = "right"

    def update(self):
        """
        Handles the snake's movement, checks for collisions with walls or itself,
        and manages the growing mechanism.
        Returns False if the snake dies, True if it survives this frame.
        """
        # If no direction is set (e.g., game just started), do not move
        if self.new_direction == "":
            return True
            
        # Apply the queued direction
        self.direction = self.new_direction
        
        # Create a copy of the head segment to project its next position
        head = self.body[0].copy()
        
        # Move the projected head based on the current direction
        if self.direction == "up": head.y -= CELL_SIZE
        elif self.direction == "down": head.y += CELL_SIZE
        elif self.direction == "left": head.x -= CELL_SIZE
        elif self.direction == "right": head.x += CELL_SIZE
        
        # Death Condition 1: Check for collision with the screen borders and top UI bar
        if head.left < 0 or head.right > WIDTH or head.top < TOP_BAR_HEIGHT or head.bottom > HEIGHT:
            return False
            
        # Death Condition 2: Check for collision with its own body segments
        for segment in self.body:
            if head.colliderect(segment):
                return False
                
        # Move forward by inserting the newly positioned head at the start of the list
        self.body.insert(0, head)
        
        # If the snake just ate food, leave the tail intact so it grows by 1 block
        if self.grow_pending:
            self.grow_pending = False
        else:
            # If not growing, remove the last segment (the tail) to maintain current length
            self.body.pop()
            
        return True

    def draw(self, surface):
        """
        Draws all segments of the snake's body onto the screen.
        """
        for segment in self.body:
            # Fill the segment area with a gray color
            pygame.draw.rect(surface, GRAY, segment)
            
            # Draw a white outline around the segment for visual distinction
            pygame.draw.rect(surface, WHITE, segment, 2)