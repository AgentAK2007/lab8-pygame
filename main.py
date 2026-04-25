import random
import pygame
import math

# Window and simulation configuration.
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_SQUARE_SIZE = 15
MAX_SQUARE_SIZE = 50
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
        return (self.x + self.size / 2, self.y + self.size / 2)

    def distance_between_centers(self, other: 'MovingSquare') -> float:
        """Compute Euclidean distance from this square's center to another's."""
        cx1, cy1 = self.get_center()
        cx2, cy2 = other.get_center()
        return math.hypot(cx1 - cx2, cy1 - cy2)

    def find_nearest_larger_square(self, squares: list['MovingSquare']) -> 'MovingSquare | None':
        """Return the closest square that is strictly larger than this one."""
        closest_square = None
        min_distance = float('inf')

        for other in squares:
            if other is self or other.is_dead:
                continue
            
            if other.size > self.size:
                dist = self.distance_between_centers(other)
                if dist < min_distance:
                    min_distance = dist
                    closest_square = other
                    
        return closest_square

    def find_nearest_smaller_square(self, squares: list['MovingSquare']) -> 'MovingSquare | None':
        """Return the closest square that is strictly smaller than this one."""
        closest_square = None
        min_distance = float('inf')

        for other in squares:
            if other is self or other.is_dead:
                continue
            
            # Only care about strictly smaller squares for chasing
            if other.size < self.size:
                dist = self.distance_between_centers(other)
                if dist < min_distance:
                    min_distance = dist
                    closest_square = other
                    
        return closest_square

    def compute_flee_vector(self, threat: 'MovingSquare') -> tuple[float, float]:
        """Return a normalized direction vector that points away from a threat."""
        cx_self, cy_self = self.get_center()
        cx_threat, cy_threat = threat.get_center()

        # Vector pointing from chasing square to self.
        dx = cx_self - cx_threat
        dy = cy_self - cy_threat
        
        distance = math.hypot(dx, dy)
        if distance == 0:
            return (random.choice([-1, 1]), random.choice([-1, 1]))
            
        return (dx / distance, dy / distance)

    def compute_chase_vector(self, prey: 'MovingSquare') -> tuple[float, float]:
        """Return a normalized direction vector that points toward a prey."""
        cx_self, cy_self = self.get_center()
        cx_prey, cy_prey = prey.get_center()

        # Vector pointing from self TO prey so its inverse of flee.
        dx = cx_prey - cx_self
        dy = cy_prey - cy_self
        
        distance = math.hypot(dx, dy)
        if distance == 0:
            return (random.choice([-1, 1]), random.choice([-1, 1]))
            
        return (dx / distance, dy / distance)

    def apply_steering_and_jitter(self, squares: list['MovingSquare']) -> None:
        """Steer away from larger squares, chase smaller ones, and keep random motion jitter."""
        threat = self.find_nearest_larger_square(squares)
        prey = self.find_nearest_smaller_square(squares)
        
        # Flee if a chasing square is close
        if threat and self.distance_between_centers(threat) < 150:
            flee_vx, flee_vy = self.compute_flee_vector(threat)
            escape_speed = BASE_SPEED / self.size
            self.vx = flee_vx * escape_speed
            self.vy = flee_vy * escape_speed
            
        # Hunt feature  Chase if prey is in range and not being chased
        elif prey and self.distance_between_centers(prey) < 200:
            chase_vx, chase_vy = self.compute_chase_vector(prey)
            chase_speed = BASE_SPEED / self.size
            self.vx = chase_vx * chase_speed
            self.vy = chase_vy * chase_speed

        # Blend steering with small random changes to avoid straight rigid movement.
        if random.random() < 0.05:
            self.vx += random.choice([-30.0, 30.0])
            self.vy += random.choice([-30.0, 30.0])
            
            max_speed = BASE_SPEED / self.size
            self.vx = max(-max_speed, min(max_speed, self.vx))
            self.vy = max(-max_speed, min(max_speed, self.vy))

        # Apply random angular acceleration for visual variety and randomness.
        if random.random() < 0.10: 
            self.rotation_speed += random.choice([-120.0, 120.0])
            
        self.rotation_speed = max(-360.0, min(360.0, self.rotation_speed))

    def update(self, squares: list['MovingSquare'], dt: float) -> None:
        """Update steering and position using time-based motion."""
        # Aging Logic
        self.age += dt
        if self.age >= self.lifespan:
            self.is_dead = True
            return  # Stop moving if dead
            
        # Updates Steering state before applying movement.
        self.apply_steering_and_jitter(squares)

        # Time-based integration
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle = (self.angle + self.rotation_speed * dt) % 360

        # Bounce off the games boundarys.
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
    pygame.display.set_caption("Random Moving Squares with Lifecycle and Chase")
    clock = pygame.time.Clock()
    fps_font = pygame.font.SysFont(None, 28)

    squares = [MovingSquare() for _ in range(SQUARE_COUNT)]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for square in squares:
            square.update(squares, dt)

        # Rebirth Logic
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