import random
import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_SQUARE_SIZE = 8
MAX_SQUARE_SIZE = 24
MAX_SPEED = 5
SQUARE_COUNT = 100
BACKGROUND_COLOR = (20, 20, 30)
FPS = 60


def random_non_zero_velocity(max_speed: float) -> float:
	velocity = 0
	while velocity == 0:
		velocity = random.randint(-int(max_speed), int(max_speed))
	return velocity


class MovingSquare:
	def __init__(self) -> None:
		self.size = random.randint(MIN_SQUARE_SIZE, MAX_SQUARE_SIZE)
		# Bigger squares move slower: max_speed inversely proportional to size
		self.max_speed = MAX_SPEED * (MIN_SQUARE_SIZE / self.size)
		self.x = random.randint(0, WINDOW_WIDTH - self.size)
		self.y = random.randint(0, WINDOW_HEIGHT - self.size)
		self.vx = random_non_zero_velocity(self.max_speed)
		self.vy = random_non_zero_velocity(self.max_speed)
		self.color = (
			random.randint(60, 255),
			random.randint(60, 255),
			random.randint(60, 255),
		)

	def update(self) -> None:
		# Add slight random jitter so movement feels less uniform.
		if random.random() < 0.05:
			self.vx += random.choice([-1, 1])
			self.vy += random.choice([-1, 1])

		self.vx = max(-self.max_speed, min(self.max_speed, self.vx))
		self.vy = max(-self.max_speed, min(self.max_speed, self.vy))

		self.x += self.vx
		self.y += self.vy

		if self.x <= 0 or self.x >= WINDOW_WIDTH - self.size:
			self.vx *= -1
			self.x = max(0, min(self.x, WINDOW_WIDTH - self.size))

		if self.y <= 0 or self.y >= WINDOW_HEIGHT - self.size:
			self.vy *= -1
			self.y = max(0, min(self.y, WINDOW_HEIGHT - self.size))

	def draw(self, surface: pygame.Surface) -> None:
		pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))


def main() -> None:
	pygame.init()
	screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
	pygame.display.set_caption("Random Moving Squares")
	clock = pygame.time.Clock()

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

		pygame.display.flip()
		clock.tick(FPS)

	pygame.quit()


if __name__ == "__main__":
	main()
