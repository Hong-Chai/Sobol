import pygame
import sys
import os

pygame.init()

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 64

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SOBOL: Assault")

# Шрифты
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Музыка
pygame.mixer.init()
music_playing = False


def load_image(name, colorkey=None, scale=(TILE_SIZE, TILE_SIZE)):
    fullname = os.path.join("data", name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return pygame.transform.scale(image, scale)


all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
floor_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = load_image("player.png")
        self.rect = self.image.get_rect().move(
            TILE_SIZE * pos_x + 15, TILE_SIZE * pos_y + 5
        )


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(walls_group, all_sprites)
        self.image = load_image("wall.png")
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)


class Door(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(doors_group, all_sprites)
        self.image = load_image("door.png")
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)


class Floor(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, color):
        super().__init__(floor_group, all_sprites)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)


class Room:
    def __init__(self, pos_x, pos_y, enemies):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.enemies = enemies


def generate_level(level_num):
    """
    Генерирует уровень на основе номера уровня

    Returns:
        Кортеж (level, rooms), где:
        level - двумерный массив, представляющий карту уровня.
        rooms - список объектов Room, представляющих комнаты на уровне.
    """
    if level_num == 1:
        level = [
            "#####################",
            "#bbbbbbbbpbbbbbbbbb#",
            "#b##d########d####b#",
            "#b#...#..........#b#",
            "#b#...#..........#b#",
            "#b#...############b#",
            "#b#####...#......#b#",
            "#b#.......#......#b#",
            "#b#.......#......db#",
            "#b#.......#......#b#",
            "#bd.......#......###",
            "####################",
        ]
        rooms = [
            # TODO
        ]

    else:
        # возвращаем пустой уровень
        return [], []

    return level, rooms


def draw_level(level):
    """
    Отрисовывает уровень на экране.
    """
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            if cell == "#":
                Wall(x, y)
            elif cell == ".":
                Floor(x, y, BLACK)
            elif cell == "b":
                Floor(x, y, WHITE)
            elif cell == "d":
                Door(x, y)
            elif cell == "p":
                Player(x, y)


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


def main_game(level_num):
    """
    Основной игровой цикл для выбранного уровня.
    """
    clock = pygame.time.Clock()
    running = True

    level_map, rooms = generate_level(level_num)
    if not level_map:
        print(f"Уровень {level_num} не найден.")
        return

    player = Player(1, 1)
    draw_level(level_map)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        floor_group.draw(screen)
        all_sprites.draw(screen)
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
