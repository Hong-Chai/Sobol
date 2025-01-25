import pygame
import sys
import os

pygame.init()

from levels import generate_level
from assault_settings import get_assault_settings


global player

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


"""TODO
Функциональные требования:
a. Общие функции:
    i. Возможность свободно перемещать группу Соболь по нейтральным и зачищенным локациям
    ii. Иметь систему коллизий
    iii. Иметь систему анимации движения спецназовцев
    iv. Окно настройки каждого отдельного штурма комнаты
    v. Поэтапное открытие новых функций (см пункт б)
    vi. Реалистичное звуковое сопровождение
    vii. Обучение
b. Функции с поэтапным открытием
    i. Уровень 0 – обучение (только перемещение и слепой штурм)
    ii. Уровень 1 – улучшения отряда
    iii. Уровень 2 – возможность разведки противников в комнате (кол-во ограничено)
    iv. Уровень 3 – режим нелетального штурма (больше очков)
    v. Уровень 4 – гранаты и прочие примочки
С. Главное меню
    Возможность сбросить прогресс
    Возможность отключить фоновую музыку
"""


def load_image(name, colorkey=None, scale=(TILE_SIZE, TILE_SIZE)):
    """
    Загружает изображение из директории data.

    --Взята с учебника ЯЛ--

    Args:
        name (str): Имя файла изображения.
        colorkey (tuple, optional): Цветовой ключ для прозрачности.
        scale (tuple, optional): Размер для масштабирования изображения.

    Returns:
        pygame.Surface: Загруженное и масштабированное изображение.
    """
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
        """
        Инициализирует спрайт игрока.

        Args:
            pos_x (int): Координата x начальной позиции игрока.
            pos_y (int): Координата y начальной позиции игрока.
        """
        super().__init__(player_group, all_sprites)
        self.frames = [
            load_image(f"player{i}.png", scale=(50, 50))
            for i in range(1, 7)  # Load player1.png to player6.png
        ]
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(
            TILE_SIZE * pos_x + 15, TILE_SIZE * pos_y + 5
        )
        self.speed = 5
        self.target_pos = None
        self.animation_delay = 100
        self.is_moving = False
        self.last_update = pygame.time.get_ticks()
        self.facing_right = True

    def animate(self):
        """Обновляет кадр анимации"""
        now = pygame.time.get_ticks()
        if self.is_moving:
            if now - self.last_update > self.animation_delay:
                self.last_update = now
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                current_frame = self.frames[self.cur_frame]
                if not self.facing_right:
                    self.image = pygame.transform.flip(current_frame, True, False)
                else:
                    self.image = current_frame
        else:
            self.cur_frame = 0
            current_frame = self.frames[self.cur_frame]
            if not self.facing_right:
                self.image = pygame.transform.flip(current_frame, True, False)
            else:
                self.image = current_frame

    def update(self):
        """
        Обновляет позицию игрока на основе целевой позиции.

        --Логика частично позаимствована с документации pygame--
        """
        # Anti-bug
        if (
            self.rect.x < 0 + TILE_SIZE
            or self.rect.x > SCREEN_WIDTH - TILE_SIZE
            or self.rect.y < 0 + TILE_SIZE
            or self.rect.y > SCREEN_HEIGHT - TILE_SIZE
        ):
            self.rect.x = 64
            self.rect.y = 64

        if self.target_pos:
            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            distance = (dx**2 + dy**2) ** 0.5

            if dx != 0:
                self.facing_right = dx > 0

            if distance > self.speed:
                self.is_moving = True
                move_x = dx / distance * self.speed
                move_y = dy / distance * self.speed

                intended_move_x = move_x
                intended_move_y = move_y

                self.rect.x += move_x
                self.resolve_collisions(intended_move_x, 0)

                self.rect.y += move_y
                self.resolve_collisions(0, intended_move_y)

                if move_x == 0 and move_y != 0:
                    # Horizontal sliding
                    self.rect.x += intended_move_x
                    if self.check_collisions():
                        self.rect.x -= intended_move_x
                elif move_y == 0 and move_x != 0:
                    # Vertical sliding
                    self.rect.y += intended_move_y
                    if self.check_collisions():
                        self.rect.y -= intended_move_y
            else:
                self.rect.x = self.target_pos[0]
                self.rect.y = self.target_pos[1]
                self.target_pos = None
                self.is_moving = False

        self.animate()

    def check_collisions(self):
        """
        Проверяет столкновения со стенами и дверями.

        Returns:
            bool: True, если есть столкновение, False в противном случае.
        """
        return pygame.sprite.spritecollideany(
            self, walls_group
        ) or pygame.sprite.spritecollideany(self, doors_group)

    def resolve_collisions(self, dx, dy):
        """
        Решает столкновения, выталкивая игрока из перекрывающих объектов.

        --Логика частично позаимствована с документации pygame--

        Args:
            dx (int): Изменение координаты x.
            dy (int): Изменение координаты y.
        """
        while True:
            wall_collision = pygame.sprite.spritecollideany(self, walls_group)
            door_collision = pygame.sprite.spritecollideany(self, doors_group)
            collision_object = wall_collision or door_collision

            if not collision_object:
                break  # Больше нет столкновений

            if dx > 0:  # Движение вправо
                self.rect.right = collision_object.rect.left
            elif dx < 0:  # Движение влево
                self.rect.left = collision_object.rect.right
            elif dy > 0:  # Движение вниз
                self.rect.bottom = collision_object.rect.top
            elif dy < 0:  # Движение вверх
                self.rect.top = collision_object.rect.bottom


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        """
        Инициализирует спрайт стены.

        Args:
            pos_x (int): Координата x позиции стены.
            pos_y (int): Координата y позиции стены.
        """
        super().__init__(walls_group, all_sprites)
        self.image = load_image("wall.png")
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)


class Door(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, rotated=False):
        """
        Инициализирует спрайт двери.

        Args:
            pos_x (int): Координата x позиции двери.
            pos_y (int): Координата y позиции двери.
            rotated (bool, optional): Ориентация двери (по умолчанию False - горизонтальная).

        """
        super().__init__(doors_group, all_sprites)
        if rotated:
            self.image = pygame.transform.rotate(load_image("door.png"), 90)
        else:
            self.image = load_image("door.png")
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)


class Floor(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, color):
        """
        Инициализирует спрайт пола.

        Args:
            pos_x (int): Координата x позиции пола.
            pos_y (int): Координата y позиции пола.
            color (tuple): Цвет пола.
        """
        super().__init__(floor_group, all_sprites)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)


class Room:
    def __init__(self, pos_x, pos_y, enemies):
        """
        Инициализирует комнату.

        Args:
            pos_x (int): Координата x позиции комнаты.
            pos_y (int): Координата y позиции комнаты.
            enemies (list): Список врагов в комнате.
        """
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.enemies = enemies


def draw_level(level):
    """
    Отрисовывает уровень на экране.

    Args:
        level (list): Карта уровня.
    """
    global player
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
            elif cell == "f":
                Door(x, y, rotated=True)
            elif cell == "p":
                coords = (x, y)
    player = Player(coords[0], coords[1])


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
    Отображает начальный экран с инструкциями и позволяет пользователю выбрать уровень или включить/выключить музыку.


    Returns:
        int: Номер выбранного уровня.
    """
    background_image = pygame.image.load("data/background.png")
    background_image = pygame.transform.scale(
        background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    screen.blit(background_image, (0, 0))

    title_text = font.render("SOBOL: Assault", True, BLACK)
    instruction_text = small_font.render("Нажмите 1-5 для выбора уровня", True, BLACK)
    music_text = small_font.render(
        "Нажмите M для включения/выключения музыки", True, BLACK
    )

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

    Args:
        level_num (int): Номер уровня.
    """
    clock = pygame.time.Clock()
    running = True

    level_map, rooms = generate_level(level_num)
    if not level_map:
        print(f"Уровень {level_num} не найден.")
        return

    draw_level(level_map)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for door in doors_group:
                    if door.rect.collidepoint(mouse_pos):
                        dx = mouse_pos[0] - player.rect.x
                        dy = mouse_pos[1] - player.rect.y
                        distance = (dx**2 + dy**2) ** 0.5
                        if distance > 90:
                            player.target_pos = mouse_pos
                        else:
                            lethal_mode, use_flashbang = get_assault_settings(level_num)
                            if lethal_mode:
                                print("Starting lethal assault!")
                            else:
                                print("Starting non-lethal assault!")
                            if use_flashbang:
                                print("Using flashbang!")
                        break
                else:
                    if player:
                        player.target_pos = mouse_pos

        player_group.update()

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
