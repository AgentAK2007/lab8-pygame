import random
import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_SQUARE_SIZE = 15
MAX_SQUARE_SIZE = 50
BASE_SPEED = 120  #Used to calculate speed based on size
SQUARE_COUNT = 20
BACKGROUND_COLOR = (20, 20, 30)
FPS = 60


class MovingSquare:
    def __init__(self) -> None:
        #Random sizes for the square
        self.size = random.randint(MIN_SQUARE_SIZE, MAX_SQUARE_SIZE)
        
        #Speed as a function of size (the bigger the square, the slower the speed)
        speed_magnitude = BASE_SPEED / self.size 
        
        self.x = random.randint(0, WINDOW_WIDTH - self.size)
        self.y = random.randint(0, WINDOW_HEIGHT - self.size)
        
        #Give it a random starting direction using the calculated speed
        self.vx = random.choice([-1, 1]) * speed_magnitude
        self.vy = random.choice([-1, 1]) * speed_magnitude
        
        self.color = (
            random.randint(60, 255),
            random.randint(60, 255),
            random.randint(60, 255),
        )
        
        #Setup for the rotation jitter effect
        self.angle = 0
        self.rotation_speed = 0
        
        #Create a base surface for this square to handle the rotation graphics
        self.base_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.base_image.fill(self.color)

    def update(self) -> None:
        #The jitter effect: slight random changes to rotation speed instead of modifying x,y
        if random.random() < 0.10: 
            self.rotation_speed += random.choice([-2, 2])
            
        #Constrain the rotation speed so it doesn't spin out of control 
        self.rotation_speed = max(-6, min(6, self.rotation_speed))
        self.angle = (self.angle + self.rotation_speed) % 360

        #Standard movement
        self.x += self.vx
        self.y += self.vy

        #Bounce movement
        if self.x <= 0 or self.x >= WINDOW_WIDTH - self.size:
            self.vx *= -1
            self.x = max(0, min(self.x, WINDOW_WIDTH - self.size))

        if self.y <= 0 or self.y >= WINDOW_HEIGHT - self.size:
            self.vy *= -1
            self.y = max(0, min(self.y, WINDOW_HEIGHT - self.size))

    def draw(self, surface: pygame.Surface) -> None:
        #Rotate the original surface
        rotated_image = pygame.transform.rotate(self.base_image, self.angle)
        
        #Re-center the rotated image so it doesn't drift
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        new_rect = rotated_image.get_rect(center=(center_x, center_y))
        
        surface.blit(rotated_image, new_rect.topleft)

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Random Moving Squares with Rotation")
    clock = pygame.time.Clock()
    fps_font = pygame.font.SysFont(None, 28)

    squares = [MovingSquare() for _ in range(SQUARE_COUNT)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for square in squares:
            square.update()

        screen.fill(BACKGROUND_COLOR)
        for square in squares:
            square.draw(screen)

        fps_surface = fps_font.render(f"FPS: {clock.get_fps():.1f}", True, (240, 240, 240))
        screen.blit(fps_surface, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()