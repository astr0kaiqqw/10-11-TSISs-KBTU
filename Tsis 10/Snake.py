import pygame
import random
import time
import psycopg2
from datetime import datetime

# --- Настройки базы данных ---
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="TaikpanovRus12",
    host="localhost",
    port="1501"
)
cur = conn.cursor()

# --- Таблицы ---
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        level INTEGER DEFAULT 1
    );
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS user_scores (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        score INTEGER,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()

# --- Получение или создание пользователя ---
def get_or_create_user(username):
    cur.execute("SELECT id, level FROM users WHERE username = %s;", (username,))
    result = cur.fetchone()
    if result:
        return result  # (id, level)
    else:
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id, level;", (username,))
        conn.commit()
        return cur.fetchone()

# --- Сохранение результата ---
def save_score(user_id, score):
    cur.execute("INSERT INTO user_scores (user_id, score) VALUES (%s, %s);", (user_id, score))
    conn.commit()

# --- Запрос имени пользователя ---
username = input("Введите имя пользователя: ")
user_id, level = get_or_create_user(username)
print(f"Добро пожаловать, {username}! Ваш текущий уровень: {level}")

# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 400, 400
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
font = pygame.font.Font(None, 30)

# --- Игровые классы ---
class Snake:
    def __init__(self):
        self.body = [(100, 100), (80, 100), (60, 100)]
        self.direction = "RIGHT"
        self.grow = False

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == "UP":
            head_y -= CELL_SIZE
        elif self.direction == "DOWN":
            head_y += CELL_SIZE
        elif self.direction == "LEFT":
            head_x -= CELL_SIZE
        elif self.direction == "RIGHT":
            head_x += CELL_SIZE

        new_head = (head_x, head_y)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        self.body.insert(0, new_head)

    def check_collision(self):
        head_x, head_y = self.body[0]
        if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
            return True
        if (head_x, head_y) in self.body[1:]:
            return True
        return False

    def draw(self):
        for segment in self.body:
            pygame.draw.rect(screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))

class Food:
    def __init__(self, snake_body):
        self.position = self.generate_food(snake_body)
        self.spawn_time = time.time()
        self.weight = random.randint(1, 3)

    def generate_food(self, snake_body):
        while True:
            x = random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE
            y = random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
            if (x, y) not in snake_body:
                return (x, y)

    def draw(self):
        pygame.draw.rect(screen, RED, (*self.position, CELL_SIZE, CELL_SIZE))

    def is_expired(self):
        return time.time() - self.spawn_time > 5

# --- Игровой цикл ---
snake = Snake()
food = Food(snake.body)
score = 0
clock = pygame.time.Clock()
running = True
paused = False

while running:
    if not paused:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and snake.direction != "DOWN":
            snake.direction = "UP"
        if keys[pygame.K_DOWN] and snake.direction != "UP":
            snake.direction = "DOWN"
        if keys[pygame.K_LEFT] and snake.direction != "RIGHT":
            snake.direction = "LEFT"
        if keys[pygame.K_RIGHT] and snake.direction != "LEFT":
            snake.direction = "RIGHT"
        if keys[pygame.K_p]:  # клавиша для паузы и сохранения
            paused = True
            save_score(user_id, score)
            print(f"Игра приостановлена. Счёт {score} сохранён.")

        snake.move()

        if snake.check_collision():
            print("Столкновение! Игра окончена.")
            save_score(user_id, score)
            break

        if snake.body[0] == food.position:
            snake.grow = True
            score += food.weight
            food = Food(snake.body)

        if food.is_expired():
            food = Food(snake.body)

        snake.draw()
        food.draw()

        score_text = font.render(f"Score: {score}", True, BLUE)
        screen.blit(score_text, (10, 10))
        pygame.display.update()

        # Уровень влияет на скорость
        clock.tick(7 + level * 2)

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            print("Продолжение игры...")
            paused = False

pygame.quit()
cur.close()
conn.close()
