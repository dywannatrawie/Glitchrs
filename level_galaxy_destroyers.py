import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Level 1")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

font = pygame.font.SysFont("Courier", 24)

clock = pygame.time.Clock()

def init_game():
    global player, bullets, bullet_count, can_shoot, last_shot_time, aliens
    global alien_bullets, invincible_index, glitching, glitch_started, glitch_timer
    global show_lore, game_over

    player = spaceship_img.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
    bullets = []
    bullet_count = 0
    can_shoot = True
    last_shot_time = 0
    aliens = []
    alien_bullets = []
    invincible_index = None
    glitching = False
    glitch_started = False
    glitch_timer = 0
    show_lore = False
    game_over = False
    spawn_aliens()

alien_images = [
    pygame.transform.scale(pygame.image.load("Graphics/alien_1.png").convert_alpha(), (36, 36)),
    pygame.transform.scale(pygame.image.load("Graphics/alien_2.png").convert_alpha(), (40, 28)),
    pygame.transform.scale(pygame.image.load("Graphics/alien_3.png").convert_alpha(), (56, 36)),
    pygame.transform.scale(pygame.image.load("Graphics/alien_4.png").convert_alpha(), (36, 40))
]

spaceship_img = pygame.transform.scale(pygame.image.load("Graphics/spaceship.png").convert_alpha(), (50, 40))


alien_speed = 2.5
alien_rows = 3
alien_cols = 6
alien_fire_chance = 0.009
alien_bullet_speed = 4

block_size = 6
bunker_shape = [
    "  xxxxxxx",
    "xxxxxxxxxxx",
    "  xxxxxxx"
]

bunker_positions = [100 + i * 130 for i in range(5)]
bunker_blocks = pygame.sprite.Group()
def create_bunkers():
    bunker_blocks.empty()
    for bx in bunker_positions:
        by = HEIGHT - 150
        for row_idx, row in enumerate(bunker_shape):
            for col_idx, char in enumerate(row):
                if char == "x":
                    x = bx + col_idx * block_size
                    y = by + row_idx * block_size
                    bunker_blocks.add(Block(block_size, GREEN, x, y))

class Block(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

def spawn_aliens():
    global invincible_index
    for row in range(alien_rows):
        for col in range(alien_cols):
            alien_image = random.choice(alien_images)
            width, height = alien_image.get_size()
            x = random.randint(50, WIDTH - width - 50)
            y = random.randint(50, HEIGHT // 2 - 100)

            aliens.append({
                "rect": pygame.Rect(x, y, width, height),
                "image": alien_image,
                "dx": random.choice([-1, 1]) * alien_speed,
                "dy": random.choice([-1, 1]) * alien_speed,
                "base_image": alien_image,
                "scale": 1.0
            })
    invincible_index = random.randint(0, len(aliens) - 1)

init_game()
create_bunkers()

lore_text = [
    "LOREM IPSUM DOLOR SIT AMET...",
    "EXTRATERRESTRIAL ERROR DETECTED...",
    "THE SYSTEM HAS BEEN COMPROMISED...",
    "NOW YOU WILL UNDERSTAND...",
    "...THE TRUTH."
]

running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            init_game()
            create_bunkers()

    keys = pygame.key.get_pressed()
    if not game_over and not show_lore:
        if keys[pygame.K_LEFT]:
            player.move_ip(-6, 0)
        if keys[pygame.K_RIGHT]:
            player.move_ip(6, 0)
        player.clamp_ip(screen.get_rect())


    current_time = pygame.time.get_ticks()
    if keys[pygame.K_SPACE] and not game_over and not show_lore and can_shoot and len(bullets) < 5:
        bullets.append(pygame.Rect(player.centerx - 2, player.y, 4, 10))
        bullet_count += 1
        last_shot_time = current_time
        can_shoot = False

    if bullet_count > 10 and not glitch_started:
        glitch_started = True
        glitching = True

    if glitching and invincible_index is not None and invincible_index < len(aliens):
        target = aliens[invincible_index]
        target_rect = target["rect"]
        center_x = WIDTH // 2 - target_rect.width // 2
        center_y = HEIGHT // 4 - target_rect.height // 2
        dx = (center_x - target_rect.x) * 0.05
        dy = (center_y - target_rect.y) * 0.05
        target_rect.x += int(dx)
        target_rect.y += int(dy)

        glitch_timer += 10
        if glitch_timer % 5 == 0:
            alien = aliens[invincible_index]
            factor = random.uniform(1.0, 1.5)
            new_size = (int(alien["base_image"].get_width() * factor * alien["scale"]),
                        int(alien["base_image"].get_height() * factor * alien["scale"]))
            alien["image"] = pygame.transform.scale(alien["base_image"], new_size)
            alien["rect"].width, alien["rect"].height = new_size
            alien["rect"].center = (target_rect.centerx + random.randint(-5,5), target_rect.centery + random.randint(-5,5))

        if aliens[invincible_index]["rect"].width > WIDTH * 0.75:
            alien = aliens[invincible_index]
            if alien["scale"] < 1.5:
                alien["scale"] = 1.5
                new_size = (int(alien["base_image"].get_width() * alien["scale"]),
                            int(alien["base_image"].get_height() * alien["scale"]))
                alien["image"] = pygame.transform.scale(alien["base_image"], new_size)
                alien["rect"].width, alien["rect"].height = new_size
                alien["rect"].center = (WIDTH // 2, HEIGHT // 4)
            else:
                show_lore = True
                glitching = False

    if not can_shoot and current_time - last_shot_time >= 300:
        can_shoot = True

    if not game_over and not show_lore:
        for alien_data in aliens:
            rect = alien_data["rect"]
            rect.x += alien_data["dx"]
            rect.y += alien_data["dy"]

            if rect.left <= 0 or rect.right >= WIDTH:
                alien_data["dx"] *= -1
            if rect.top <= 0 or rect.bottom >= HEIGHT // 2:
                alien_data["dy"] *= -1

            if random.random() < alien_fire_chance:
                alien_bullets.append(pygame.Rect(rect.centerx - 2, rect.bottom, 4, 10))

    for bullet in alien_bullets[:]:
        bullet.y += alien_bullet_speed
        if bullet.top > HEIGHT:
            alien_bullets.remove(bullet)
            continue
        if bullet.colliderect(player):
            if not show_lore:
                game_over = True
            alien_bullets.clear()
            bullets.clear()
            continue
        for block in bunker_blocks:
            if bullet.colliderect(block.rect):
                alien_bullets.remove(bullet)
                bunker_blocks.remove(block)
                break

    for bullet in bullets[:]:
        bullet.y -= 6
        if bullet.bottom < 0:
            bullets.remove(bullet)
            continue
        collided_blocks = [block for block in bunker_blocks if bullet.colliderect(block.rect)]
        if collided_blocks:
            top_y = min(block.rect.y for block in collided_blocks)
            top_row_blocks = [b for b in collided_blocks if b.rect.y == top_y]
            top_block = min(top_row_blocks, key=lambda b: abs(b.rect.centerx - bullet.centerx))
            if bullet in bullets:
                bullets.remove(bullet)
            bunker_blocks.remove(top_block)
        else:
            for i, alien_data in enumerate(aliens):
                rect = alien_data["rect"]
                if bullet.colliderect(rect):
                    if glitching and i == invincible_index:
                        alien_data["scale"] *= 1.2
                        bullets.remove(bullet)
                        break
                    else:
                        if bullet in bullets:
                            bullets.remove(bullet)
                        aliens.remove(alien_data)
                        if invincible_index is not None and i < invincible_index:
                            invincible_index -= 1
                        break

    if not show_lore and not game_over:
        screen.blit(spaceship_img, player)

        for i, alien_data in enumerate(aliens):
            if i != invincible_index:
                screen.blit(alien_data["image"], alien_data["rect"])

        if invincible_index is not None and invincible_index < len(aliens):
            alien_data = aliens[invincible_index]
            screen.blit(alien_data["image"], alien_data["rect"])

        for bullet in bullets:
            pygame.draw.rect(screen, WHITE, bullet)
        for bullet in alien_bullets:
            pygame.draw.rect(screen, RED, bullet)

        bunker_blocks.draw(screen)

    if show_lore:
        screen.fill(BLACK)
        for i, line in enumerate(lore_text):
            text = font.render(line, True, GREEN)
            screen.blit(text, (40, 100 + i * 40))

    if game_over:
        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press SPACE to restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
