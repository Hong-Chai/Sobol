import pygame
import sys
import os

from random import randint

import saves

pygame.init()

from levels import generate_level, rooms_per_level
from assault_settings import get_assault_settings


global player

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 64

# Цвета
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("SOBOL: Assault")

# Шрифты
pygame.font.init()

# main menu font
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# game over font
font_large = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 45)

# Музыка
pygame.mixer.init()
music_playing = False


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
act_doors_group = pygame.sprite.Group()
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
            for i in range(1, 7)  # Загрузка player1.png до player6.png
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
            # Сброс анимации на первый кадр, когда игрок стоит
            self.cur_frame = 0
            current_frame = self.frames[self.cur_frame]
            if not self.facing_right:
                self.image = pygame.transform.flip(current_frame, True, False)
            else:
                self.image = current_frame

    def update(self):
        """
        Обновляет позицию игрока на основе целевой позиции.
        """
        if self.target_pos:
            old_x, old_y = self.rect.x, self.rect.y  # старая позиция

            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            distance = (dx**2 + dy**2) ** 0.5

            if dx != 0:
                self.facing_right = dx > 0

            if distance > self.speed:
                self.is_moving = True
                move_x = dx / distance * self.speed
                move_y = dy / distance * self.speed
                # Попытка сдвинуть игрока по X
                self.rect.x += move_x
                if self.check_collisions():
                    self.rect.x -= move_x  # Откат, если столкновение
                    move_x = 0  # Не удалось двигаться по X

                # Попытка сдвинуть игрока по Y
                self.rect.y += move_y
                if self.check_collisions():
                    self.rect.y -= move_y  # Откат, если столкновение
                    move_y = 0  # Не удалось двигаться по Y
            else:
                self.rect.x = self.target_pos[0]
                self.rect.y = self.target_pos[1]
                self.target_pos = None
                self.is_moving = False

            # Проверяем, произошло ли какое-либо движение
            if self.rect.x == old_x and self.rect.y == old_y:
                # Если позиция не изменилась, сбрасываем движение
                self.target_pos = None
                self.is_moving = False

        else:
            self.is_moving = False  # Нет цели для движения

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

    def move_to(self, x, y):
        """
        Устанавливает целевую позицию для движения игрока.

        Args:
            x (int): Целевая координата x (в пикселях).
            y (int): Целевая координата y (в пикселях).
        """
        # Проверяем, находится ли целевая позиция в пределах карты
        if 0 <= x <= SCREEN_WIDTH and 0 <= y <= SCREEN_HEIGHT:
            self.target_pos = (x, y)


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
    img = "door.png"
    rotated = None
    enemies = None

    def __init__(self, pos_x, pos_y, enem, rotated=False):
        """
        Инициализирует спрайт двери.

        Args:
            pos_x (int): Координата x позиции двери.
            pos_y (int): Координата y позиции двери.
            rotated (bool, optional): Ориентация двери (по умолчанию False - горизонтальная).

        """
        self.rotated = rotated
        self.enemies = enem

        super().__init__(act_doors_group, all_sprites, doors_group)
        if rotated:
            self.image = pygame.transform.rotate(load_image(self.img), 90)
        else:
            self.image = load_image(self.img)
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)

    def change_img(self, img):
        """
        Изменяет изображение двери.

        Args:
            img (str): Новое изображение двери.
        """
        act_doors_group.remove(self)
        self.img = img
        if self.rotated:
            self.image = pygame.transform.rotate(load_image(self.img), 90)
        else:
            self.image = load_image(self.img)


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


def draw_level(level, rooms):
    """
    Отрисовывает уровень на экране.

    Args:
        level (list): Карта уровня.
        rooms (list): Противники в комнате
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
                Door(x, y, rooms.pop())
            elif cell == "f":
                Door(x, y, rooms.pop(), rotated=True)
            elif cell == "p":
                coords = (x, y)
    player = Player(coords[0], coords[1])


def toggle_music(file=-1, stop=False, loop=-1):
    """
    Включает или выключает музыку.
    """
    if stop:
        pygame.mixer.music.stop()
    else:
        pygame.mixer.music.load(f"data/{file}.mp3")
        pygame.mixer.music.play(loop)


def show_start_screen():
    """
    Отображает начальный экран с инструкциями и позволяет пользователю выбрать уровень или включить/выключить музыку.


    Returns:
        int: Номер выбранного уровня.
    """
    user_level = saves.get_save()

    background_image = pygame.image.load("data/background.png")
    background_image = pygame.transform.scale(
        background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    screen.blit(background_image, (0, 0))

    title_text = font.render("SOBOL: Assault", True, BLACK)
    instruction_text = small_font.render(f"Ваш уровень: {user_level}", True, BLACK)
    instruction_text1 = small_font.render("Нажмите Р для начала игры", True, BLACK)
    instruction_text2 = small_font.render("Нажмите R для сброса прогресса", True, BLACK)
    music_text = small_font.render("Нажмите M для выключения музыки", True, BLACK)

    title_rect = title_text.get_rect(topleft=(10, 10))
    instruction_rect = instruction_text.get_rect(topleft=(10, title_rect.bottom + 10))
    instruction1_rect = instruction_text1.get_rect(
        topleft=(10, instruction_rect.bottom + 20)
    )
    instruction2_rect = instruction_text2.get_rect(
        topleft=(10, instruction1_rect.bottom + 20)
    )
    music_rect = music_text.get_rect(topleft=(10, instruction2_rect.bottom + 20))

    screen.blit(title_text, title_rect)
    screen.blit(instruction_text, instruction_rect)
    screen.blit(instruction_text1, instruction1_rect)
    screen.blit(instruction_text2, instruction2_rect)

    screen.blit(music_text, music_rect)
    pygame.display.flip()

    toggle_music("main")

    waiting = True
    level_selected = None
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    level_selected = user_level
                    waiting = False
                elif event.key == pygame.K_r:
                    saves.save(1)
                    user_level = 1
                elif event.key == pygame.K_m:
                    toggle_music(stop=1)

    return level_selected


def clear_groups():
    """
    Очищает все группы спрайтов.
    """
    all_sprites.empty()
    player_group.empty()
    walls_group.empty()
    doors_group.empty()
    floor_group.empty()


def to_black():
    """
    Переход к черному экрану
    """
    transition_duration = 2
    transition_frames = transition_duration * FPS
    transition_step = 255 / transition_frames
    current_alpha = 0
    for i in range(120):
        current_alpha += transition_step
        if current_alpha >= 255:
            current_alpha = 255

        screen.fill(WHITE)
        all_sprites.draw(screen)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(current_alpha)
        screen.blit(overlay, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)


def to_white():
    """
    Переход к белому экрану
    """
    transition_duration = 2
    transition_frames = transition_duration * FPS
    transition_step = 255 / transition_frames
    current_alpha = 255
    for i in range(120):
        current_alpha -= transition_step
        if current_alpha <= 0:
            current_alpha = 0

        screen.fill(WHITE)
        all_sprites.draw(screen)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(current_alpha)
        screen.blit(overlay, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen(text, color):
    """
    Вывод надписи о завершении уровня
    """
    screen.fill(BLACK)

    text_large = font_large.render(text, True, color)
    text_rect_large = text_large.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10)
    )
    screen.blit(text_large, text_rect_large)

    text_small = font_small.render("нажми ESC для главного меню", True, color)
    text_rect_small = text_small.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
    )
    screen.blit(text_small, text_rect_small)

    pygame.display.flip()


def main_game(level_num):
    """
    Основной игровой цикл для выбранного уровня.

    Args:
        level_num (int): Номер уровня.
    """
    toggle_music(f"intro{level_num}", loop=1)

    FRAG = 2
    SCOUT = 2
    ROOMS_OK = 0
    BONUS_IN_LEVEL = 0

    global player

    running = True

    level_map, rooms = generate_level(level_num)
    if not level_map:
        print(f"Уровень {level_num} не найден.")
        return

    draw_level(level_map, rooms)

    running = True
    waiting = False  # Add this flag to control update/draw
    wait_start = 0
    wait_time = 16000

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    clear_groups()
                    return
            elif (
                event.type == pygame.MOUSEBUTTONDOWN and not waiting
            ):  # Only process clicks if not waiting
                mouse_pos = pygame.mouse.get_pos()
                for door in act_doors_group:
                    if door.rect.collidepoint(mouse_pos):
                        dx = mouse_pos[0] - player.rect.x
                        dy = mouse_pos[1] - player.rect.y
                        distance = (dx**2 + dy**2) ** 0.5
                        if distance > 90:
                            player.target_pos = mouse_pos
                        else:
                            enemies = door.enemies
                            start, bonus, FRAG, SCOUT = get_assault_settings(
                                level_num, FRAG, SCOUT, ROOMS_OK, enemies
                            )
                            BONUS_IN_LEVEL += bonus
                            print(start)

                            if start:
                                toggle_music("assualt", loop=1)
                                to_black()
                                waiting = True
                                wait_start = current_time
                        break
                else:
                    if player:
                        player.target_pos = mouse_pos

        if waiting:
            if current_time - wait_start >= wait_time:
                if start <= randint(1, 100):
                    print("You died!")
                    toggle_music("fail", loop=1)
                    pygame.time.wait(4000)
                    game_over_screen("YOU DIED", RED)
                    wait_time = 1000000000000000000

                else:
                    ROOMS_OK += 1
                    door.change_img("line.png")
                    pygame.time.wait(1000)
                    toggle_music("ok", loop=1)
                    to_white()
                    if ROOMS_OK == rooms_per_level(level_num):
                        saves.save(level_num + 1)
                        toggle_music("complete", loop=1)
                        pygame.time.wait(2000)
                        game_over_screen(
                            f"LEVEL COMPLETE |ОЧКИ {ROOMS_OK * 200 + BONUS_IN_LEVEL}/{ROOMS_OK * 200 + ROOMS_OK * 100}|",
                            WHITE,
                        )
                        wait_time = 1000000000000000000
                    else:
                        waiting = False

        else:
            player_group.update()
            screen.fill(WHITE)
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
