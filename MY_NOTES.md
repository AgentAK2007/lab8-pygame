Chasing / Fleeing Behavior
Analysis/Strategy:
To make smaller squares flee from bigger ones, I think I have to use vector math.
Since the smaller and larger sqaures interact, I think they need to be aware/look at each other on the screen.
So eg. IF a square detects another square that is LARGER than itself, it needs to check the distance between them.
IF the distance is within a certain range I will set that is too close to each other, the smaller square must move away.
I think I will use a vector that should point away or in the opposite direction from the larger square.
But I also need to maintain the random jitter.
After seeing the teacher's visualization and explanations, the smaller square needs to check not just the distance between it and the larger square, but the distance between their centers.

Edge Cases
Division by Zero Case, if two squares spawn exactly on top of each other, their distance will be 0. Dividing by 0 to on the vector will crash the game.

Progressive TODO
1. Give each square a center point helper.
2. Add a neighbor-check helper that finds the closest bigger square.
3. Add a distance helper that uses the centers, not the top-left corners.
4. Add a steering helper that returns a direction away from the bigger square.
5. Blend that steering with the existing random jitter.
6. Add a zero-distance guard before normalizing any vector.

Function Stubs
These are not the full solution yet. They are the pieces you would fill in one by one.

```python
def get_center(square):
	# Return the square's center as a vector or (x, y) tuple.
	pass


def find_nearest_larger_square(current_square, squares):
	# Look through the other squares and return the closest one that is larger.
	pass


def distance_between_centers(square_a, square_b):
	# Use the two centers to measure distance.
	pass


def compute_flee_vector(current_square, threat_square):
	# Return a vector that points away from the threat.
	# If the distance is zero, return a safe fallback vector.
	pass


def apply_flee_and_jitter(current_square, squares):
	# Combine fleeing behavior with your existing random jitter.
	pass
```

How the stubs depend on each other
- `get_center()` is the foundation: both distance and fleeing need the center, not the corner.
- `distance_between_centers()` uses `get_center()` so the math stays consistent.
- `find_nearest_larger_square()` decides which bigger square matters most right now.
- `compute_flee_vector()` uses the chosen threat and the center distance to produce movement away from it.
- `apply_flee_and_jitter()` is the final step in the update loop, where you mix the flee vector with the random movement you already like.

Implementation order
1. Implement `get_center()` first and print the values to confirm they look right.
2. Implement `distance_between_centers()` and test it with two fixed squares.
3. Implement `find_nearest_larger_square()` and verify it picks the expected square.
4. Implement `compute_flee_vector()` with a zero-distance guard.
5. Only then wire everything into the square update method.

Learning check
- If you can explain why the zero-distance case is dangerous, you understand the hardest edge case.
- If you can explain why centers are better than top-left corners, you understand the geometry.
- If you can describe where jitter is added relative to fleeing, you understand the control flow.
