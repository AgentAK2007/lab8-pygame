# 'random' lets us pick random numbers (like for colors or spawning positions).
import random
# 'pygame' is the library that actually draws the graphics and opens the game window.
import pygame
# 'math' gives us advanced math tools, specifically for calculating distances between points.
import math

# --- WINDOW AND SIMULATION CONFIGURATION ---
# (Variables in ALL CAPS are "constants" - settings we don't plan to change while the game runs).
WINDOW_WIDTH = 800  # The screen will be 800 pixels wide.
WINDOW_HEIGHT = 600 # The screen will be 600 pixels tall.
MIN_SQUARE_SIZE = 15 # The smallest a square can possibly be.
MAX_SQUARE_SIZE = 50 # The largest a square can possibly be.
# BASE_SPEED is a massive number because it's divided by the square's size later to calculate real speed.
BASE_SPEED = 7200 
SQUARE_COUNT = 30 # We will spawn exactly 30 squares at the start.
BACKGROUND_COLOR = (20, 20, 30) # A dark blue/grey background color (Red=20, Green=20, Blue=30).
FPS = 60 # We want the game to try and run at 60 Frames Per Second.

# --- THE BLUEPRINT FOR A SQUARE ---
class MovingSquare:
    # __init__ is the "setup" function. It runs once exactly when a new square is born.
    #Add 'size: int None = None' to for specific sizes
    def __init__(self, size: int | None = None) -> None:
        
        #1. Use provided size, or choose a random one if none is provided.
        if size is not None:
            self.size = size
        else:
            self.size = random.randint(MIN_SQUARE_SIZE, MAX_SQUARE_SIZE)
        
        # 2. Calculate speed. 
        speed_magnitude = BASE_SPEED / self.size 
        
        # 3. Pick a random starting X and Y position on the screen.
        # We use 'float' (decimals) because time-based movement moves in tiny decimal fractions.
        # We subtract self.size so it doesn't spawn halfway off the right or bottom edge.
        self.x = float(random.randint(0, WINDOW_WIDTH - self.size))
        self.y = float(random.randint(0, WINDOW_HEIGHT - self.size))
        
        # 4. Set the starting velocity (vx = speed on X axis, vy = speed on Y axis).
        # random.choice([-1, 1]) randomly makes the speed positive (right/down) or negative (left/up).
        self.vx = random.choice([-1, 1]) * speed_magnitude
        self.vy = random.choice([-1, 1]) * speed_magnitude
        
        # 5. Pick a random color. (Red, Green, Blue). 
        # We start at 60 instead of 0 so the colors aren't too dark to see against the background.
        self.color = (
            random.randint(60, 255),
            random.randint(60, 255),
            random.randint(60, 255),
        )
        
        # 6. Lifecycle setup. Age starts at 0 seconds.
        self.age = 0.0
        # Pick a random expiration date between 30 and 180 seconds.
        self.lifespan = random.uniform(30.0, 180.0) 
        # It is born alive, so is_dead starts as False.
        self.is_dead = False
        
        # 7. Setup the spinning visual effect. Angle starts at 0.
        self.angle = 0.0
        self.rotation_speed = 0.0
        
        # 8. Create a blank Pygame image (Surface) just big enough to hold this square.
        # SRCALPHA allows it to have a transparent background when it spins.
        self.base_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        # Paint that blank image with the random color we chose in step 5.
        self.base_image.fill(self.color)

    # --- HELPER: GET CENTER ---
    def get_center(self) -> tuple[float, float]:
        """Return the exact middle pixel of the square."""
        # Pygame x and y are the TOP-LEFT corner. 
        # To find the middle, we add half of the width to x, and half of the height to y.
        return (self.x + self.size / 2, self.y + self.size / 2)

    # --- HELPER: CALCULATE DISTANCE ---
    def distance_between_centers(self, other: 'MovingSquare') -> float:
        """Find how many pixels are between this square and another square."""
        # Get my center (cx1, cy1)
        cx1, cy1 = self.get_center()
        # Get the other square's center (cx2, cy2)
        cx2, cy2 = other.get_center()
        # math.hypot does the Pythagorean theorem (a^2 + b^2 = c^2) to find the direct line distance.
        return math.hypot(cx1 - cx2, cy1 - cy2)
    
    #EXERCISE 4
    def check_collision(self, other: 'MovingSquare') -> bool:
        #Returns True if this square is colliding with the other square.
        #Create an invisible Pygame rectangle for this square
        my_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
        #Creates an invisible Pygame rectangle for the other square
        other_rect = pygame.Rect(other.x, other.y, other.size, other.size)
        
        #Pygame's collision 
        return my_rect.colliderect(other_rect)

    # --- HELPER: FIND THREAT ---
    def find_nearest_larger_square(self, squares: list['MovingSquare']) -> 'MovingSquare | None':
        """Look at all squares and find the closest one that is bigger than me."""
        closest_square = None
        # Start the minimum distance at "infinity" so the first square we check is guaranteed to be closer.
        min_distance = float('inf')

        # Loop through every square in the game
        for other in squares:
            # If the 'other' square is actually ME, or if it's dead, ignore it and skip to the next loop.
            if other is self or other.is_dead:
                continue
            
            # If the other square is bigger than me...
            if other.size > self.size:
                # Calculate how far away it is.
                dist = self.distance_between_centers(other)
                # If it's the closest one we've seen so far...
                if dist < min_distance:
                    # Update our record of the shortest distance.
                    min_distance = dist
                    # Save this square as the current biggest threat.
                    closest_square = other
                    
        # Return the threat we found (or None if no bigger squares exist).
        return closest_square

    # --- HELPER: FIND PREY ---
    def find_nearest_smaller_square(self, squares: list['MovingSquare']) -> 'MovingSquare | None':
        """Look at all squares and find the closest one that is smaller than me."""
        closest_square = None
        min_distance = float('inf')

        for other in squares:
            # Skip myself and dead squares.
            if other is self or other.is_dead:
                continue
            
            # Exactly the same as above, but we only care if the other square is SMALLER.
            if other.size < self.size:
                dist = self.distance_between_centers(other)
                if dist < min_distance:
                    min_distance = dist
                    closest_square = other
                    
        return closest_square

    # --- HELPER: MATH TO RUN AWAY ---
    def compute_flee_vector(self, threat: 'MovingSquare') -> tuple[float, float]:
        """Calculate the exact direction pointing directly away from a threat."""
        cx_self, cy_self = self.get_center()
        cx_threat, cy_threat = threat.get_center()

        # To point AWAY from the threat, we subtract the Threat's position FROM Our position.
        dx = cx_self - cx_threat
        dy = cy_self - cy_threat
        
        # Find the total distance between us.
        distance = math.hypot(dx, dy)
        # CRASH PREVENTION: If we are exactly on top of each other, distance is 0. 
        # Dividing by 0 crashes the program, so we return a random direction instead.
        if distance == 0:
            return (random.choice([-1, 1]), random.choice([-1, 1]))
            
        # "Normalize" the vector: divide x and y by the total distance.
        # This shrinks the arrow to a length of exactly 1. We do this so we only have the DIRECTION,
        # and we can multiply it by our own speed later.
        return (dx / distance, dy / distance)

    # --- HELPER: MATH TO CHASE ---
    def compute_chase_vector(self, prey: 'MovingSquare') -> tuple[float, float]:
        """Calculate the exact direction pointing directly toward a smaller square."""
        cx_self, cy_self = self.get_center()
        cx_prey, cy_prey = prey.get_center()

        # To point TOWARD the prey, we subtract Our position FROM the Prey's position. (Reverse of fleeing).
        dx = cx_prey - cx_self
        dy = cy_prey - cy_self
        
        distance = math.hypot(dx, dy)
        if distance == 0:
            return (random.choice([-1, 1]), random.choice([-1, 1]))
            
        return (dx / distance, dy / distance)

    # --- MAIN BRAIN: MAKE DECISIONS ---
    def apply_steering_and_jitter(self, squares: list['MovingSquare']) -> None:
        """Decide where to move based on threats, prey, walls, and randomness."""
        # Find the nearest threat and the nearest prey.
        threat = self.find_nearest_larger_square(squares)
        prey = self.find_nearest_smaller_square(squares)
        
        # Recalculate my natural speed based on my size.
        speed = BASE_SPEED / self.size

        # PRIORITY 1: RUN FOR YOUR LIFE
        # If there is a threat AND it is closer than 150 pixels...
        if threat and self.distance_between_centers(threat) < 150:
            # Get the direction to run away (length of 1).
            flee_vx, flee_vy = self.compute_flee_vector(threat)
            # Multiply that direction by our speed to set our new velocity.
            self.vx = flee_vx * speed
            self.vy = flee_vy * speed
            
        # PRIORITY 2: HUNT FOR FOOD
        # Only happens if Priority 1 didn't trigger. If prey is closer than 200 pixels...
        elif prey and self.distance_between_centers(prey) < 200:
            # Get the direction pointing at the prey.
            chase_vx, chase_vy = self.compute_chase_vector(prey)
            # Multiply direction by speed.
            self.vx = chase_vx * speed
            self.vy = chase_vy * speed

        # --- RANDOM WIGGLES (JITTER) ---
        # 5% chance every single frame to wiggle slightly off path.
        if random.random() < 0.05:
            # Add or subtract 30 to our velocity randomly.
            self.vx += random.choice([-30.0, 30.0])
            self.vy += random.choice([-30.0, 30.0])
            
            # Cap the speed so wiggles don't stack up and make us move at super-speed.
            max_speed = speed * 1.2
            self.vx = max(-max_speed, min(max_speed, self.vx))
            self.vy = max(-max_speed, min(max_speed, self.vy))

        # 10% chance to randomly change how fast we are visually spinning.
        if random.random() < 0.10: 
            self.rotation_speed += random.choice([-120.0, 120.0])
            
        # Don't spin faster than 360 degrees per second.
        self.rotation_speed = max(-360.0, min(360.0, self.rotation_speed))

    # --- APPLY THE MOVEMENT ---
    def update(self, squares: list['MovingSquare'], dt: float) -> None:
        """Apply age, call the brain, and actually change the X/Y coordinates."""
        
        # AGING: Add the tiny fraction of a second (dt) that passed to our age.
        self.age += dt
        # If our age is higher than our randomly chosen death date...
        if self.age >= self.lifespan:
            # Mark as dead and STOP doing anything else in this function.
            self.is_dead = True
            return 
            
        # Call the "Brain" function above to figure out our self.vx and self.vy.
        self.apply_steering_and_jitter(squares)

        # TIME-BASED INTEGRATION: The most important math!
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle = (self.angle + self.rotation_speed * dt) % 360

        #EXERCISE 3
        #modulo operator so i get the remainder after the division by the screen width/height 
        #If x goes to 805, 805 % 800 = 5. So its on the left side
        #If x goes to -5, -5 % 800 = 795. So its on the right side
        self.x = self.x % WINDOW_WIDTH
        self.y = self.y % WINDOW_HEIGHT


    # --- DRAW IT TO THE SCREEN ---
    def draw(self, surface: pygame.Surface) -> None:
        """Stamp the square's image onto the main game window."""
        # Create a new version of the image that is rotated by 'self.angle'.
        rotated_image = pygame.transform.rotate(self.base_image, self.angle)
        # Find the center of where the square SHOULD be.
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        # Wrap an invisible box (rect) around the rotated image, and pin it to the exact center.
        # This stops the square from wobbling off-center when it spins.
        new_rect = rotated_image.get_rect(center=(center_x, center_y))
        # 'Blit' is Pygame's word for 'stamp'. Stamp the image onto the screen at the calculated position.
        surface.blit(rotated_image, new_rect.topleft)

# --- MAIN GAME LOOP ---
def main() -> None:
    # Turn on the Pygame engine.
    pygame.init()
    # Open the game window to our width and height.
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # Name the window.
    pygame.display.set_caption("Random Moving Squares with Lifecycle and Chase")
    # Create a clock to keep track of Time and Frames Per Second.
    clock = pygame.time.Clock()
    # Create a font so we can write the FPS on the screen.
    fps_font = pygame.font.SysFont(None, 28)

    #empty list to hold squares
    squares = []
    
    #Spawn 5 squares of size 25
    for _ in range(5):
        squares.append(MovingSquare(size=25))
        
    #Spawn 10 squares of size 10
    for _ in range(10):
        squares.append(MovingSquare(size=10))
        
    #pawn 30 squares of size 4
    for _ in range(30):
        squares.append(MovingSquare(size=4))

    # The game runs as long as this is True.
    running = True
    while running:
        # Tick the clock. This forces the game to run at 60 FPS maximum.
        # It returns milliseconds. We divide by 1000 to get 'dt' (Delta Time in seconds).
        dt = clock.tick(FPS) / 1000.0

        # Look for events (like the user clicking the red X on the window).
        for event in pygame.event.get():
            # If they clicked the red X...
            if event.type == pygame.QUIT:
                # Break the while loop to close the game.
                running = False

        # 1. UPDATE ALL SQUARES
        for square in squares:
            # Tell every square to do its math, update its age, and move.
            square.update(squares, dt)

        # 2. REBIRTH LOGIC
        # Loop through the list of squares by their index number (0, 1, 2, etc.)
        for i in range(len(squares)):
            #IF the square at this spot says it's dead
            if squares[i].is_dead:
                #Save its size before it gets overwritten
                old_size = squares[i].size
                
                #Overwrite it completely with a brand new MovingSquare, 
                #passing in the size that was saved
                squares[i] = MovingSquare(size=old_size)

        # 3. DRAWING
        # Wipe the screen clean with the background color (hides the old frames).
        screen.fill(BACKGROUND_COLOR)
        # Tell every square to draw itself on the clean screen.
        for square in squares:
            square.draw(screen)

        # Create an image of the text showing the current Frames Per Second.
        fps_surface = fps_font.render(f"FPS: {clock.get_fps():.1f}", True, (240, 240, 240))
        # Stamp the FPS text into the top-left corner (x=10, y=10).
        screen.blit(fps_surface, (10, 10))

        # Pygame draws everything on a hidden screen first to prevent flickering.
        # display.flip() swaps the hidden screen to the visible monitor.
        pygame.display.flip()

    # If the while loop breaks, safely shut down the Pygame engine.
    pygame.quit()

# This is a Python rule. It just means "If I run this file directly, start the main() function".
if __name__ == "__main__":
    main()