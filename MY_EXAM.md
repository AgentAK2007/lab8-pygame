Exercise1
Exercise2
Exercise 3: I have to remove the all the wall bounce feature, and other features the make the sqaures stay in the window.
Exercise 4: I will use Pygame Rectangle Collision Detection
Exercise 5: reuse check_collision from exercise 4, and exercise 2 automatically completes Eaten squares die and get respawn with their original size. I have to update flee and chase as due to the sqaures going through the boarders, no collisions occur.
Exercise 6:
I made the chasing square grow by adding other.size * 0.5. But when I multiply by a decimal (float) like 0.5, the result becomes a float. So, self.size turned from a whole integer like 25 into a float like 27.0.
Due to exercise 2 rebirth logic, the square respawns with that float size.
When the new square tries to pick a random starting X position, it runs random.randint(0, WINDOW_WIDTH - self.size). Because self.size is now a float, the math results in a float. I get a type error as the randint() function only accepts whole numbers and crashes my pygame.
So I need to force self.size back into being a whole integer when the square is born.
Exercise 7:
