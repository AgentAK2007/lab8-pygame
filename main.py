import random
import pygame
import math

# Window and simulation configuration.
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_SQUARE_SIZE = 15
MAX_SQUARE_SIZE = 50
# BASE_SPEED increased from 120 to 7200 because pixels-per-second Time-Based is used
BASE_SPEED = 7200 
SQUARE_COUNT = 20
BACKGROUND_COLOR = (20, 20, 30)
FPS = 60


class MovingSquare:
    def __init__(self) -> None:
        # Randomize size so smaller squares naturally move faster.
        self.size = random.randint(MIN_SQUARE_SIZE, MAX_SQUARE_SIZE)
        speed_magnitude = BASE_SPEED / self.size 
        
        # Store position as float to support smooth time-based updates.
        self.x = float(random.randint(0, WINDOW_WIDTH - self.size))
        self.y = float(random.randint(0, WINDOW_HEIGHT - self.size))
        
        # Start with a random velocity direction.
        self.vx = random.choice([-1, 1]) * speed_magnitude
        self.vy = random.choice([-1, 1]) * speed_magnitude
        
        self.color = (
            random.randint(60, 255),
            random.randint(60, 255),
            random.randint(60, 255),
        )
        
        # Lifecycle Properties
        self.age = 0.0
        self.lifespan = random.uniform(30.0, 180.0) 
        self.is_dead = False
        
        # Rotation state is independent of movement state.
        self.angle = 0.0
        self.rotation_speed = 0.0
        self.base_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.base_image.fill(self.color)

    def get_center(self) -> tuple[float, float]:
        """Return the center point used for interaction math between squares."""
        # Center is the top-left x,y plus half the width/height.
        return (self.x + self.size / 2, self.y + self.size / 2)

    def distance_between_centers(self, other: 'MovingSquare') -> float:
        """Compute Euclidean distance from this square's center to another's."""
        cx1, cy1 = self.get_center()
        cx2, cy2 = other.get_center()
        # math.hypot calculates Euclidean distance.
        return math.hypot(cx1 - cx2, cy1 - cy2)

    def find_nearest_larger_square(self, squares: list['MovingSquare']) -> 'MovingSquare | None':
        """Return the closest square that is strictly larger than this one."""
        closest_square = None
        min_distance = float('inf')

        for other in squares:
            # Skip self and dead squares that haven't been cleaned up yet
            if other is self or other.is_dead:
                continue
            
            # Only care about strictly larger squares.
            if other.size > self.size:
                dist = self.distance_between_centers(other)
                if dist < min_distance:
                    min_distance = dist
                    closest_square = other
                    
        return closest_square

    def compute_flee_vector(self, threat: 'MovingSquare') -> tuple[float, float]:
        """Return a normalized direction vector that points away from a threat."""
        cx_self, cy_self = self.get_center()
        cx_threat, cy_threat = threat.get_center()

        # Vector pointing FROM threat TO self.
        dx = cx_self - cx_threat
        dy = cy_self - cy_threat
        
        distance = math.hypot(dx, dy)
        
        # Zero-distance guard to prevent division by zero.
        if distance == 0:
            return (random.choice([-1, 1]), random.choice([-1, 1]))
            
        # Normalize so only direction remains.
        return (dx / distance, dy / distance)

    def apply_flee_and_jitter(self, squares: list['MovingSquare']) -> None:
        """Steer away from nearby larger squares while keeping random motion jitter."""
        threat = self.find_nearest_larger_square(squares)
        
        # If a larger square is close enough, switch to flee steering.
        if threat and self.distance_between_centers(threat) < 150:
            flee_vx, flee_vy = self.compute_flee_vector(threat)
            
            # Escape speed is size-dependent: smaller means faster.
            escape_speed = BASE_SPEED / self.size
            self.vx = flee_vx * escape_speed
            self.vy = flee_vy * escape_speed

        # Blend steering with small random changes to avoid rigid movement.
        if random.random() < 0.05:
            # Scaled for per-second velocity units.
            self.vx += random.choice([-30.0, 30.0])
            self.vy += random.choice([-30.0, 30.0])
            
            # Cap speed to prevent runaway acceleration.
            max_speed = BASE_SPEED / self.size
            self.vx = max(-max_speed, min(max_speed, self.vx))
            self.vy = max(-max_speed, min(max_speed, self.vy))

        # Apply random angular acceleration for visual variety.
        if random.random() < 0.10: 
            # Scaled for per-second rotation units.
            self.rotation_speed += random.choice([-120.0, 120.0])
            
        self.rotation_speed = max(-360.0, min(360.0, self.rotation_speed))

    def update(self, squares: list['MovingSquare'], dt: float) -> None:
        """Update steering and position using time-based motion."""
        # NEW: Aging Logic
        self.age += dt
        if self.age >= self.lifespan:
            self.is_dead = True
            return  # Stop moving if dead
            
        # Update steering state before applying movement.
        self.apply_flee_and_jitter(squares)

        # Time-based integration keeps behavior stable across frame rates.
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle = (self.angle + self.rotation_speed * dt) % 360

        # Bounce off the simulation bounds.
        if self.x <= 0 or self.x >= WINDOW_WIDTH - self.size:
            self.vx *= -1
            self.x = max(0, min(self.x, float(WINDOW_WIDTH - self.size)))

        if self.y <= 0 or self.y >= WINDOW_HEIGHT - self.size:
            self.vy *= -1
            self.y = max(0, min(self.y, float(WINDOW_HEIGHT - self.size)))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the square as a rotated sprite centered on its current position."""
        rotated_image = pygame.transform.rotate(self.base_image, self.angle)
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        new_rect = rotated_image.get_rect(center=(center_x, center_y))
        surface.blit(rotated_image, new_rect.topleft)


def main() -> None:
    """Initialize pygame, run the main loop, and render simulation + FPS overlay."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Random Moving Squares with Lifecycle")
    clock = pygame.time.Clock()
    fps_font = pygame.font.SysFont(None, 28)

    squares = [MovingSquare() for _ in range(SQUARE_COUNT)]

    running = True
    while running:
        # Delta time in seconds for frame-rate independent motion.
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for square in squares:
            # Each square needs full group context for flee behavior.
            square.update(squares, dt)

        # Rebirth Logic (Check for dead squares and replace them)
        for i in range(len(squares)):
            if squares[i].is_dead:
                squares[i] = MovingSquare()

        screen.fill(BACKGROUND_COLOR)
        for square in squares:
            square.draw(screen)

        fps_surface = fps_font.render(f"FPS: {clock.get_fps():.1f}", True, (240, 240, 240))
        screen.blit(fps_surface, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()