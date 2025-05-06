import pygame
import sys
import random
import subprocess
import os


pygame.init()

# Ustawienia okna
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GL!TCHTRS")

# Kolory
CYAN = (0, 255, 255)
PINK = (255, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Czcionka retro
font = pygame.font.Font(pygame.font.match_font('courier', bold=True), 32)
big_font = pygame.font.Font(pygame.font.match_font('courier', bold=True), 64)
small_font = pygame.font.Font(pygame.font.match_font('courier', bold=True), 20)

# Pozycje menu
menu_items = ["START", "WYJDŹ"]
selected = 0

clock = pygame.time.Clock()

def draw_glitch_text(text, font, x, y):
    # Efekt glitch: nakładające się cienie
    for dx, dy, color in [(-2, 0, PINK), (2, 0, GREEN), (0, 0, CYAN)]:
        rendered = font.render(text, True, color)
        screen.blit(rendered, (x + dx, y + dy))

def draw_menu():
    screen.fill(BLACK)

    # Tytuł
    title_text = "GL!TCHTRS"
    title_surface = big_font.render(title_text, True, CYAN)
    title_rect = title_surface.get_rect(center=(WIDTH//2, 100))
    draw_glitch_text(title_text, big_font, title_rect.x, title_rect.y)

    # Pozycje menu z > < dla wybranej
    for i, item in enumerate(menu_items):
        if i == selected:
            display_text = f"> {item} <"
            color = WHITE
        else:
            display_text = f"  {item}  "
            color = CYAN

        text_surface = font.render(display_text, True, color)
        rect = text_surface.get_rect(center=(WIDTH//2, 250 + i * 60))
        screen.blit(text_surface, rect)

    # Instrukcje na dole
    instruct1 = ">> poruszaj się strzałkami <<"
    instruct2 = ">> wciśnij ENTER aby wybrać <<"
    ins1 = small_font.render(instruct1, True, CYAN)
    ins2 = small_font.render(instruct2, True, CYAN)
    screen.blit(ins1, ins1.get_rect(center=(WIDTH//2, HEIGHT - 60)))
    screen.blit(ins2, ins2.get_rect(center=(WIDTH//2, HEIGHT - 30)))


def main():
    global selected
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        running = False  # wyjdź z pętli menu
                        pygame.quit()    # opcjonalne: zamknij okno pygame
                        subprocess.run([sys.executable, os.path.join("level_1.py")])
                    elif selected == 1:
                        pygame.quit()
                        sys.exit()

        draw_menu()
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
