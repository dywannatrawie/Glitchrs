import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 640, 480
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TETRIS + Gracz")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
MAGENTA = (255, 0, 255)
LIME = (0, 255, 0)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)  # Złoty kolor dla paska zwycięstwa

FPS = 60
BLOCK_SIZE = 20
GROUND_Y = HEIGHT - 20
VICTORY_Y = 0  # Pasek zwycięstwa na samej górze
VICTORY_HEIGHT = 5  # Cieniutki pasek
clock = pygame.time.Clock()

# Siatka do przechowywania zablokowanych bloków
grid = [[0] * (WIDTH // BLOCK_SIZE) for _ in range(HEIGHT // BLOCK_SIZE)]

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
        self.color = (0, 255, 255)
        self.speed = 6
        self.jump_power = -20
        self.gravity = 1
        self.velocity_y = 0
        self.on_ground = False

    def handle_input(self, grid):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.move(-self.speed, 0, grid)
        if keys[pygame.K_RIGHT]:
            self.move(self.speed, 0, grid)
        if keys[pygame.K_UP] and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

    def move(self, dx, dy, grid):
        # Ruch poziomy
        self.rect.x += dx
        if self.collides_with_grid(grid):
            self.rect.x -= dx
    
        # Ruch pionowy (jeśli kiedykolwiek potrzebny)
        self.rect.y += dy
        if self.collides_with_grid(grid):
            self.rect.y -= dy


    def apply_gravity(self, grid):
        self.velocity_y += self.gravity
        if self.velocity_y > 10:
            self.velocity_y = 10
    
        dy = int(self.velocity_y)
        for step in range(abs(dy)):
            move_dir = 1 if dy > 0 else -1
            self.rect.y += move_dir
            if self.collides_with_grid(grid):
                self.rect.y -= move_dir
                self.velocity_y = 0
                self.on_ground = True
                break
        else:
            self.on_ground = False
    
        self.clamp_position()


    def clamp_position(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0
            self.on_ground = True

    def collides_with_grid(self, grid):
        # Sprawdza, czy jakikolwiek róg gracza koliduje z białym blokiem
        for corner in [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]:
            x, y = corner
            col = x // BLOCK_SIZE
            row = y // BLOCK_SIZE
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                if grid[row][col] == 1:
                    return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Tetrisowe bloki
SHAPES = [
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (1, 0), (2, 0), (1, 1)],
    [(0, 0), (0, 1), (0, 2), (1, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(0, 0), (0, 1), (1, 0), (1, 1)]
]
SHAPE_COLORS = [RED, MAGENTA, LIME, (0, 128, 255), (255, 165, 0)]
falling_blocks = []
block_speed = 5

def create_tetris_block():
    shape = random.choice(SHAPES)
    color = random.choice(SHAPE_COLORS)
    max_shape_width = max(x for x, y in shape) + 1
    max_x_cells = (WIDTH // BLOCK_SIZE) - max_shape_width
    x_cell = random.randint(0, max_x_cells)
    x_pos = x_cell * BLOCK_SIZE
    y_pos = 0
    return {"shape": shape, "color": color, "x": x_pos, "y": y_pos, "stuck": False}

def update(player):
    global falling_blocks
    new_falling_blocks = []

    for block in falling_blocks:
        if not block["stuck"]:
            can_move = True

            # PRZYGOTUJ POZYCJE PO RUCHU
            future_rects = [pygame.Rect(block["x"] + x * BLOCK_SIZE, block["y"] + y * BLOCK_SIZE + block_speed, BLOCK_SIZE, BLOCK_SIZE)
                            for x, y in block["shape"]]

            # SPRAWDŹ KOLIZJĘ Z GRACZEM ZANIM KLOCEK SPADNIE
            for rect in future_rects:
                if rect.colliderect(player.rect):
                    # SPRAWDŹ CZY TRAFIŁ OD GÓRY
                    if rect.top < player.rect.bottom and rect.bottom <= player.rect.bottom:
                        print("Zginąłeś! Klocek spadł Ci na głowę.")
                        pygame.quit()
                        sys.exit()

            # SPRAWDŹ KOLIZJĘ Z GRUNTEM LUB INNYMI KLOCKAMI
            for x in range(4):
                max_y = -1
                for dx, dy in block["shape"]:
                    if dx == x:
                        max_y = max(max_y, dy)
                if max_y != -1:
                    grid_x = (block["x"] + x * BLOCK_SIZE) // BLOCK_SIZE
                    grid_y = (block["y"] + max_y * BLOCK_SIZE + block_speed) // BLOCK_SIZE

                    if grid_y >= HEIGHT // BLOCK_SIZE or grid[grid_y][grid_x] == 1:
                        can_move = False
                        break

            if can_move:
                block["y"] += block_speed
                new_falling_blocks.append(block)
            else:
                for bx, by in block["shape"]:
                    grid_x = (block["x"] + bx * BLOCK_SIZE) // BLOCK_SIZE
                    grid_y = (block["y"] + by * BLOCK_SIZE) // BLOCK_SIZE
                    if 0 <= grid_y < HEIGHT // BLOCK_SIZE and 0 <= grid_x < WIDTH // BLOCK_SIZE:
                        grid[grid_y][grid_x] = 1
        else:
            new_falling_blocks.append(block)

    falling_blocks = new_falling_blocks

    if random.randint(0, 60) == 0:
        falling_blocks.append(create_tetris_block())


def draw(player):
    WIN.fill(BLACK)

    # Rysowanie paska zwycięstwa na samej górze
    pygame.draw.rect(WIN, GOLD, (0, VICTORY_Y, WIDTH, VICTORY_HEIGHT))

    for block in falling_blocks:
        block_rects = [pygame.Rect(block["x"] + x * BLOCK_SIZE, block["y"] + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                       for x, y in block["shape"]]
        for rect in block_rects:
            pygame.draw.rect(WIN, block["color"], rect)

    for row in range(HEIGHT // BLOCK_SIZE):
        for col in range(WIDTH // BLOCK_SIZE):
            if grid[row][col] == 1:
                pygame.draw.rect(WIN, WHITE, pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    player.draw(WIN)

    pygame.display.update()

def check_victory(player):
    # Sprawdzenie, czy gracz dotknął paska zwycięstwa
    if player.rect.top <= VICTORY_Y + VICTORY_HEIGHT:
        print("You Win!")
        pygame.quit()
        sys.exit()

def main():
    player = Player(100, HEIGHT - 60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        player.handle_input(grid)
        player.apply_gravity(grid)

        update(player)  # aktualizacja klocków
        check_victory(player)  # Sprawdzenie zwycięstwa
        draw(player)

        pygame.display.update()
        clock.tick(FPS)

main()
