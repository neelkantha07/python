import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
width = 640
height = 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Set up the game clock
clock = pygame.time.Clock()

# Set up the snake
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_dir = "RIGHT"

# Set up the food
food_pos = [random.randrange(1, width // 10) * 10, random.randrange(1, height // 10) * 10]

# Set up the score
score = 0

# Main game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_dir != "DOWN":
                snake_dir = "UP"
            elif event.key == pygame.K_DOWN and snake_dir != "UP":
                snake_dir = "DOWN"
            elif event.key == pygame.K_LEFT and snake_dir != "RIGHT":
                snake_dir = "LEFT"
            elif event.key == pygame.K_RIGHT and snake_dir != "LEFT":
                snake_dir = "RIGHT"

    # Move the snake
    if snake_dir == "UP":
        snake_pos[1] -= 10
    elif snake_dir == "DOWN":
        snake_pos[1] += 10
    elif snake_dir == "LEFT":
        snake_pos[0] -= 10
    elif snake_dir == "RIGHT":
        snake_pos[0] += 10
    snake_body.insert(0, list(snake_pos))

    # Check if the snake has collided with the food
    if snake_pos == food_pos:
        food_pos = [random.randrange(1, width // 10) * 10, random.randrange(1, height // 10) * 10]
        score += 1
    else:
        snake_body.pop()

    # Check if the snake has collided with itself or the wall
    if snake_pos[0] < 0 or snake_pos[0] > width - 10 or snake_pos[1] < 0 or snake_pos[1] > height - 10:
        pygame.quit()
        quit()
    for block in snake_body[1:]:
        if snake_pos == block:
            pygame.quit()
            quit()

    # Draw the game objects
    screen.fill((0, 0, 0))
    for block in snake_body:
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(block[0], block[1], 10, 10))
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(food_pos[0], food_pos[1], 10, 10))
    pygame.display.update()

    # Set the game clock tick rate
    clock.tick(15)
