import random
import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SQUARE_SIZE = 30
SQUARE_COUNT = 10
BACKGROUND_COLOR = (20, 20, 30)
FPS = 60


class MovingSquare:
	def __init__(self) -> None:
		self.x = random.randint(0, WINDOW_WIDTH - SQUARE_SIZE)
		self.y = random.randint(0, WINDOW_HEIGHT - SQUARE_SIZE)
		self.vx = random.choice([-3, -2, -1, 1, 2, 3])
		self.vy = random.choice([-3, -2, -1, 1, 2, 3])
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

		self.vx = max(-4, min(4, self.vx))
		self.vy = max(-4, min(4, self.vy))

		self.x += self.vx
		self.y += self.vy

		if self.x <= 0 or self.x >= WINDOW_WIDTH - SQUARE_SIZE:
			self.vx *= -1
			self.x = max(0, min(self.x, WINDOW_WIDTH - SQUARE_SIZE))

		if self.y <= 0 or self.y >= WINDOW_HEIGHT - SQUARE_SIZE:
			self.vy *= -1
			self.y = max(0, min(self.y, WINDOW_HEIGHT - SQUARE_SIZE))

	def draw(self, surface: pygame.Surface) -> None:
		pygame.draw.rect(surface, self.color, (self.x, self.y, SQUARE_SIZE, SQUARE_SIZE))


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
