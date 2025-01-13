import pygame
import sys

pygame.init()

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SOBOL: Assault")

# Шрифты
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Музыка
pygame.mixer.init()
music_playing = False


def toggle_music():
    """
    Включает или выключает музыку.
    """
    global music_playing
    if music_playing:
        pygame.mixer.music.stop()
        music_playing = False
    else:
        pygame.mixer.music.load("data/main.mp3")
        pygame.mixer.music.play(-1)
        music_playing = True


def show_start_screen():
    """
    Отображает начальный экран с инструкциями и позволяет выбрать уровень или включить/выключить музыку.
    Возвращает выбранный уровень.
    """

    background_image = pygame.image.load("data/background.png")
    background_image = pygame.transform.scale(
        background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    screen.blit(background_image, (0, 0))

    title_text = font.render("SOBOL: Assault", True, BLACK)
    instruction_text = small_font.render("Press 1-5 to select level", True, BLACK)
    music_text = small_font.render("Press M to toggle music", True, BLACK)

    title_rect = title_text.get_rect(topleft=(10, 10))
    instruction_rect = instruction_text.get_rect(topleft=(10, title_rect.bottom + 10))
    music_rect = music_text.get_rect(topleft=(10, instruction_rect.bottom + 10))

    screen.blit(title_text, title_rect)
    screen.blit(instruction_text, instruction_rect)
    screen.blit(music_text, music_rect)
    pygame.display.flip()

    waiting = True
    level_selected = None
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    level_selected = 1
                    waiting = False
                elif event.key == pygame.K_2:
                    level_selected = 2
                    waiting = False
                elif event.key == pygame.K_3:
                    level_selected = 3
                    waiting = False
                elif event.key == pygame.K_4:
                    level_selected = 4
                    waiting = False
                elif event.key == pygame.K_5:
                    level_selected = 5
                    waiting = False
                elif event.key == pygame.K_m:
                    toggle_music()

    return level_selected


def main_game(level):
    """
    Основной игровой цикл для выбранного уровня.
    """
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Отрисовка уровня
        screen.fill(WHITE)
        level_text = font.render(f"Level {level}", True, BLACK)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(level_text, level_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


def main():
    """
    Главная функция, которая запускает игровой цикл и возвращается на начальный экран после завершения уровня.
    """
    while True:
        selected_level = show_start_screen()
        main_game(selected_level)


if __name__ == "__main__":
    main()
