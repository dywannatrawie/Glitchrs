import pygame
import random
import sys

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Level 2 - Alion Invasion")


pygame.mixer.init()
pygame.mixer.music.load("glitch_three.mp3")
pygame.mixer.music.play(-1)  # -1 oznacza zapętlone odtwarzanie



WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)

font = pygame.font.SysFont("Courier", 24)

clock = pygame.time.Clock()

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
alien_fire_chance = 0.002
alien_bullet_speed = 4

block_size = 6
bunker_shape = [
    "  xxxxxxx",
    "xxxxxxxxxxx",
    "  xxxxxxx"
]

bunker_positions = [100 + i * 130 for i in range(5)]
bunker_blocks = pygame.sprite.Group()

class Block(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

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

def spawn_aliens():
    global player_index, invincible_index
    aliens.clear()  # ← dodaj to na wszelki wypadek
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
                "dy": random.choice([-1, 1]) * alien_speed
            })

    player_index = 0
    invincible_index = random.randint(0, len(aliens) - 1)


def init_game():
    global spaceship, bullets, bullet_count, can_shoot, last_shot_time, aliens
    global alien_bullets, player_index, invincible_index, game_over, spaceship_health, win

    spaceship = spaceship_img.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
    bullets = []
    bullet_count = 0
    can_shoot = True
    last_shot_time = 0
    aliens = []
    alien_bullets = []
    game_over = False
    spaceship_health = 5
    win = False
    spawn_aliens()

init_game()
create_bunkers()

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
    if not game_over:
        player = aliens[player_index]
        if keys[pygame.K_LEFT]:
            player["rect"].x -= 5
        if keys[pygame.K_RIGHT]:
            player["rect"].x += 5
        if keys[pygame.K_UP]:
            player["rect"].y -= 5
        if keys[pygame.K_DOWN]:
            player["rect"].y += 5
        player["rect"].clamp_ip(screen.get_rect())

        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and can_shoot and len(bullets) < 5:
            bullets.append({"rect": pygame.Rect(player["rect"].centerx - 2, player["rect"].bottom, 4, 10), "color": RED})
            bullet_count += 1
            last_shot_time = current_time
            can_shoot = False

        if not can_shoot and current_time - last_shot_time >= 300:
            can_shoot = True

        danger_zone = [b for b in bullets if spaceship.left - 50 < b["rect"].centerx < spaceship.right + 50 and b["rect"].y < spaceship.bottom]
        if danger_zone:
            avg_x = sum(b["rect"].centerx for b in danger_zone) / len(danger_zone)
            if avg_x > spaceship.centerx:
                spaceship.x -= 4
            else:
                spaceship.x += 4
        else:
            spaceship.x += random.choice([-1, 1]) * 2

        spaceship.clamp_ip(screen.get_rect())

        if random.random() < 0.03 and len(bullets) < 5:
            bullets.append({"rect": pygame.Rect(spaceship.centerx - 2, spaceship.y - 10, 4, 10), "color": WHITE})

        for i, alien in enumerate(aliens[:]):
            if i == player_index:
                continue
            rect = alien["rect"]
            rect.x += alien["dx"]
            rect.y += alien["dy"]
            if rect.left <= 0 or rect.right >= WIDTH:
                alien["dx"] *= -1
            if rect.top <= 0 or rect.bottom >= HEIGHT // 2:
                alien["dy"] *= -1
            if random.random() < alien_fire_chance:
                alien_bullets.append(pygame.Rect(rect.centerx - 2, rect.bottom, 4, 10))

    for bullet in alien_bullets[:]:
        bullet.y += alien_bullet_speed
        if bullet.top > HEIGHT:
            alien_bullets.remove(bullet)
            continue
        for block in bunker_blocks:
            if bullet.colliderect(block.rect):
                alien_bullets.remove(bullet)
                bunker_blocks.remove(block)
                break

    for bullet in bullets[:]:
        bullet["rect"].y += 6 if bullet["color"] == RED else -6
        if bullet["rect"].bottom < 0 or bullet["rect"].top > HEIGHT:
            bullets.remove(bullet)
            continue
        collided_blocks = [block for block in bunker_blocks if bullet["rect"].colliderect(block.rect)]
        if collided_blocks:
            top_y = min(block.rect.y for block in collided_blocks)
            top_row_blocks = [b for b in collided_blocks if b.rect.y == top_y]
            top_block = min(top_row_blocks, key=lambda b: abs(b.rect.centerx - bullet["rect"].centerx))
            bullets.remove(bullet)
            bunker_blocks.remove(top_block)
        else:
            for i, alien_data in enumerate(aliens[:]):
                if i == player_index:
                    continue
                if bullet["rect"].colliderect(alien_data["rect"]):
                    if bullet["color"] == WHITE:
                        aliens.remove(alien_data)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

            # Sprawdzamy trafienie gracza
            if bullet["rect"].colliderect(aliens[player_index]["rect"]):
                if bullet["color"] == WHITE:
                    game_over = True
                if bullet in bullets:
                    bullets.remove(bullet)

            # Sprawdzamy trafienie statku
            if bullet["rect"].colliderect(spaceship):
                if bullet["color"] == RED:  # Trafienie czerwonym pociskiem
                    spaceship_health -= 1
                    bullets.remove(bullet)

    if spaceship_health <= 0:
        win = True
        game_over = True

    # Rysowanie serduszek życia gracza
    for i in range(spaceship_health):
        pygame.draw.rect(screen, RED, (10 + i * 30, 10, 20, 20))

    if not game_over:
        screen.blit(spaceship_img, spaceship)

        for i, alien_data in enumerate(aliens):
            screen.blit(alien_data["image"], alien_data["rect"])

        for bullet in bullets:
            pygame.draw.rect(screen, bullet["color"], bullet["rect"])
        for bullet in alien_bullets:
            pygame.draw.rect(screen, RED, bullet)

        bunker_blocks.draw(screen)

    if game_over:
        if win:
            screen.fill(BLACK)
            message1 = font.render("Dobrze ci idzie...", True, CYAN)
            screen.blit(message1, (WIDTH // 2 - message1.get_width() // 2, HEIGHT // 2 - 20))
            pygame.display.flip()

            pygame.time.delay(2000)  # wyświetl tylko pierwszy tekst przez 2 sekundy

            waiting_for_enter = True
            while waiting_for_enter:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        waiting_for_enter = False

                screen.fill(BLACK)
                # wyświetl oba teksty jednocześnie
                screen.blit(message1, (WIDTH // 2 - message1.get_width() // 2, HEIGHT // 2 - 30))
                message2 = font.render("Naciśnij ENTER, aby kontynuować", True, WHITE)
                screen.blit(message2, (WIDTH // 2 - message2.get_width() // 2, HEIGHT // 2 + 10))

                pygame.display.flip()

            pygame.quit()
            import subprocess
            subprocess.run([sys.executable, "level_3.py"])
            sys.exit()


        else:
            screen.fill(BLACK)
            end_text = font.render("GAME OVER", True, RED)
            restart_text = font.render("Naciśnij SPACJĘ, aby kontynuować", True, WHITE)
            screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 30))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))


    pygame.display.flip()

pygame.quit()
sys.exit()
