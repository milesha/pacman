import os
import sys
import pygame
from random import randint, choice

pygame.init()
pygame.display.set_caption('Pacman')

FPS = 40
WIDTH = 1200
HEIGHT = 750

# Таймеры
CHANGE = 30
CONTINUEMOVE = 31

GHOSTS = [('Inky.png', 'INKY', (26, 175, 230)),
          ('Blinky.png', 'Blinky', (231, 0, 10)),
          ('Pinky.png', 'Pinky', (242, 159, 183)),
          ('Clyde.png', 'Clyde', (231, 141, 0))]
GHOSTSGAME = [('blinky_up.png', 'blinky_down.png',
               'blinky_left.png', 'blinky_right.png'),
              ('pinky_up.png', 'pinky_down.png',
               'pinky_left.png', 'pinky_right.png'),
              ('clyde_up.png', 'clyde_down.png',
               'clyde_left.png', 'clyde_right.png'),
              ('inky_up.png', 'inky_down.png',
               'inky_left.png', 'inky_right.png')]
INTRO = [["Начать игру", 0],
         ["Управление", 0],
         ["Об игре", 0],
         ["Таблица рекордов", 0],
         ["Выход", 0]]

# Шрифт надписей в игре
FULLNAME = os.path.join('data', 'Firenight-Regular.otf')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(pygame.Color("black"))

# Группы спрайтов для стартового экрана
all_sprites = pygame.sprite.Group()
all_ghosts = pygame.sprite.Group()

# Группы спрайтов интерфейса карты
all_maps = pygame.sprite.Group()
all_points = pygame.sprite.Group()
all_rects = pygame.sprite.Group()

# Группы спрайтов-персонажей
ghost_sprites = pygame.sprite.Group()
pacman_kill = pygame.sprite.Group()
pacman_sprite = pygame.sprite.Group()

pygame.mouse.set_visible(False)
clock = pygame.time.Clock()


def load_image(name):
    """
    Загрузка картинки из файла в программу
    :param name: имя файла с картинкой
    :return: изображение, готовое для работы
    """
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        return image
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)


class StartScreen:
    """
    Класс, отвечающий за вывод на экран стартового интерфейса
    """

    def __init__(self):
        global all_sprites, INTRO
        # Скорость передвижения призрака
        self.v = 6
        # Загрузка изображения названия игры и расположение на экране
        image = load_image('start_screen.png')
        sprite = pygame.sprite.Sprite()
        sprite.image = image
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = WIDTH // 2 - image.get_width() // 2
        sprite.rect.y = 0
        all_sprites.add(sprite)

    def print_text(self):
        """
        Вывод текста стартового окна
        :return:
        """
        for i in range(len(INTRO)):
            if INTRO[i][1] == 0:
                color = pygame.Color("white")
            else:
                color = pygame.Color("yellow")
            font = pygame.font.Font(FULLNAME, 50)
            text = font.render(INTRO[i][0], 1, (color))
            start_x = WIDTH // 2 - text.get_width() // 2
            start_y = HEIGHT // 2 - text.get_height() // 2 - 50
            text_x = start_x
            text_y = start_y + i * 60
            screen.blit(text, (text_x, text_y))


class Ghost(pygame.sprite.Sprite):
    """
    Класс привидений для стартового меню
    """

    def __init__(self, group, ghost_name):
        super().__init__(group)
        file_name = ghost_name[0]
        text = ghost_name[1]
        self.group = group
        image = load_image(file_name)
        # Скорость призрака
        self.v = 5
        self.moving = True
        self.show_name = False
        self.is_moving = True
        self.made_stop = False
        self.size = image.get_width()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = - 600
        self.rect.y = HEIGHT // 2 - 180

        # Вывод имен призраков
        font = pygame.font.Font(FULLNAME, 30)
        self.text = font.render(text, 1, (ghost_name[2]))
        self.start_x = WIDTH // 2 - self.text.get_width() // 2
        self.start_y = HEIGHT // 2 - 180

    def move(self):
        """
        Движение призрака по экрану
        :return: Перемещение призрака, его остановка в центре экрана,
        установка таймера для изображения имени призрака
        """
        if self.is_moving and self.moving:
            self.rect.x += self.v
        if not self.made_stop:
            if self.rect.x >= WIDTH // 2 + self.text.get_width() // 2 + 10:
                self.show_name = True
                self.is_moving = False
                self.made_stop = True
                pygame.time.set_timer(CONTINUEMOVE, 1000)
        if self.rect.x >= WIDTH + self.size:
            self.is_moving = False
            self.stop(1)

    def stop(self, pos=0):
        """
        Остановка привидений
        :param pos: отвечает за удаление спрайта призрака
        после выхода за пределы экрана
        :return: Остановка прдыдущего призрака и создание нового
        """
        global ghost_on_screen
        if pos == 1 and self.moving:
            self.moving = False
            self.kill()
            ghost_on_screen += 1
            if ghost_on_screen == 4:
                ghost_on_screen = 0
            Ghost(all_ghosts, GHOSTS[ghost_on_screen])
            Ghost.moving = True
            Ghost.is_moving = True
            Ghost.made_stop = False

    def continue_moving(self):
        """
        Продолжение движения
        :return:
        """
        if self.moving:
            self.show_name = False
            self.is_moving = True


class Map(pygame.sprite.Sprite):
    """
    Класс карты игры
    """

    def __init__(self, name):
        super().__init__(all_maps)
        image = load_image(name)
        size_w = image.get_width()
        size_h = image.get_height()
        self.image = image
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2 - size_w // 2
        self.rect.y = HEIGHT // 2 - size_h // 2


class GhostPlay(pygame.sprite.Sprite):
    """
    Класс призраков в игровом процессе
    """

    def __init__(self, num):
        super().__init__(ghost_sprites)
        image = load_image(GHOSTSGAME[num % 4][0])
        size_h = image.get_height()
        self.num = num % 4
        # скорость призрака
        self.v = 3
        self.way = 1
        self.p = 1
        self.image = image
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        if num % 2 == 0:
            self.rect.x = WIDTH // 2 + 235
            self.rect.y = HEIGHT // 2 - size_h // 2 - 20
        else:
            self.rect.x = WIDTH // 2 - 272
            self.rect.y = HEIGHT // 2 - size_h // 2 - 20

    def move(self):
        """
        Движение призрака по карте
        :return:
        """
        global stop_game
        if self.way == 1:
            self.image = load_image(GHOSTSGAME[self.num][0])
            self.rect.y -= self.v
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.y += 2 * self.v
                self.way = choice([2, 4])

        elif self.way == 2:
            self.image = load_image(GHOSTSGAME[self.num][3])
            self.rect.x += self.v
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.x -= 2 * self.v
                self.way = choice([1, 3])

        elif self.way == 3:
            self.image = load_image(GHOSTSGAME[self.num][1])
            self.rect.y += self.v
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.y -= 2 * self.v
                self.way = choice([2, 4])

        elif self.way == 4:
            self.image = load_image(GHOSTSGAME[self.num][2])
            self.rect.x -= self.v
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.x += 2 * self.v
                self.way = choice([1, 3])

        if self.way > 4:
            self.way = 1

        for pacman in pacman_sprite:
            if pygame.sprite.collide_mask(self, pacman):
                stop_game = True

    def change(self):
        """
        Изменение направления движения призрака
        :return:
        """
        last = self.way
        while self.way == 4 - last:
            self.way = randint(1, 4)


class Pacman(pygame.sprite.Sprite):
    def __init__(self, group, sheet, columns, rows, x, y, start_x=None, start_y=None):
        super().__init__(group)
        self.sheet_right = sheet
        self.columns, self.rows = columns, rows
        self.frames = []
        self.cut_sheet(self.sheet_right, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        if map_on_screen_num != 3:
            self.rect.x = WIDTH // 2 - 13
            self.rect.y = HEIGHT // 2 - 35
        else:
            self.rect.x = WIDTH // 2 - 7
            self.rect.y = HEIGHT // 2 - 15
        self.x1, self.y1 = self.rect.x, self.rect.y
        if start_x and start_y:
            self.rect.x = start_x
            self.rect.y = start_y
        self.speed = 3
        self.last_pos = "right"

        self.sheet_left = pygame.transform.flip(sheet, True, False)
        self.sheet_up = pygame.transform.rotate(sheet, 90)
        self.sheet_down = pygame.transform.rotate(sheet, -90)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def move(self, pos=0):
        global stop_game, score
        if pos == 0:
            pos = self.last_pos
        f1 = False
        if pos == "right":
            if self.last_pos:
                if self.last_pos == "up" or self.last_pos == "down":
                    self.rows, self.columns = self.columns, self.rows
                    f1 = True

            self.frames = []
            self.cut_sheet(self.sheet_right, self.columns, self.rows)

            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x1, self.y1)

            self.rect.x += self.speed
            self.x1 = self.rect.x
            self.last_pos = "right"

            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.x -= self.speed
                self.x1 = self.rect.x

                if f1:
                    if pygame.sprite.collide_mask(self, map_on_screen):
                        if pygame.sprite.collide_mask(self, map_on_screen):
                            if self.last_pos == "up":

                                self.rect.y += self.speed
                                self.y1 = self.rect.y
                            else:
                                self.rect.y -= self.speed
                                self.y1 = self.rect.y

        if pos == "left":
            if self.last_pos:
                if self.last_pos == "up" or self.last_pos == "down":
                    self.rows, self.columns = self.columns, self.rows
                    f1 = True

            self.frames = []
            self.cut_sheet(self.sheet_left, self.columns, self.rows)

            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x1, self.y1)

            self.rect.x -= self.speed
            self.x1 = self.rect.x
            self.last_pos = "left"
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.x += self.speed
                self.x1 = self.rect.x

                if f1:
                    if pygame.sprite.collide_mask(self, map_on_screen):
                        if self.last_pos == "up":
                            self.rect.y += self.speed
                            self.y1 = self.rect.y
                        else:
                            self.rect.y -= self.speed
                            self.y1 = self.rect.y

        if pos == "up":
            if self.last_pos:
                if self.last_pos != "up" and self.last_pos != "down":
                    self.rows, self.columns = self.columns, self.rows
                    f1 = True

            self.frames = []
            self.cut_sheet(self.sheet_up, self.columns, self.rows)

            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x1, self.y1)

            self.rect.y -= self.speed
            self.y1 = self.rect.y
            self.last_pos = "up"

            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.y += self.speed
                self.y1 = self.rect.y

                if f1:
                    if pygame.sprite.collide_mask(self, map_on_screen):
                        if self.last_pos == "left":
                            self.rect.x += self.speed
                            self.x1 = self.rect.x
                        else:
                            self.rect.x -= self.speed
                            self.x1 = self.rect.x

        if pos == "down":
            if self.last_pos:
                if self.last_pos != "up" and self.last_pos != "down":
                    self.rows, self.columns = self.columns, self.rows
                    f1 = True

            self.frames = []
            self.cut_sheet(self.sheet_down, self.columns, self.rows)

            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x1, self.y1)

            self.rect.y += self.speed
            self.y1 = self.rect.y
            self.last_pos = "down"

            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.y -= self.speed
                self.y1 = self.rect.y
                if f1:
                    if pygame.sprite.collide_mask(self, map_on_screen):

                        if self.last_pos == "left":
                            self.rect.x += self.speed
                            self.x1 = self.rect.x
                        else:
                            self.rect.x -= self.speed
                            self.x1 = self.rect.x

        for ghost in ghost_sprites:
            if pygame.sprite.collide_mask(self, ghost):
                if self.last_pos == "down":
                    self.rect.y -= self.speed
                if self.last_pos == "up":
                    self.rect.y += self.speed
                if self.last_pos == "left":
                    self.rect.x += self.speed
                if self.last_pos == "right":
                    self.rect.x -= self.speed
                stop_game = True

        for point in all_points:
            if pygame.sprite.collide_mask(self, point):
                f = True
                for rect in all_rects:
                    if pygame.sprite.collide_mask(self, rect):
                        f = False
                if f:
                    score += 10
                    Rects(self.rect, self.last_pos)


class Rects(pygame.sprite.Sprite):
    """
    Прямоугольники, закрывающие баллы
    """

    def __init__(self, pos, way):
        super().__init__(all_rects)
        image = load_image('rect.png')
        self.image = image
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1]

        if way == "left":
            self.image = pygame.transform.rotate(image, 90)
            self.rect.x -= 5

        if way == "right":
            self.rect.x += 5
            self.image = pygame.transform.rotate(image, 90)
        if way == "up":
            self.rect.y -= 5
        if way == "down":
            self.rect.y += 5


class Points(pygame.sprite.Sprite):
    """
    Загрузка и расстановка баллов на карте
    """

    def __init__(self):
        super().__init__(all_points)
        if map_on_screen_num == 3:
            image = load_image('points_level3.png')
        else:
            image = load_image('points.png')
        size_w = image.get_width()
        size_h = image.get_height()
        self.image = image
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2 - size_w // 2
        self.rect.y = HEIGHT // 2 - size_h // 2


def change_place(pos):
    """
    Изменение положения курсора
    :param pos: позиция курсора в данный момент
    :return:
    """
    image = load_image('cursor.png')
    screen.blit(image, (pos[0], pos[1]))


def change_text_start(pos):
    """
    Изменение цвета текста меню при наведении курсором
    :param pos: позиция курсора
    :return:
    """
    global f1, f2, f3, f4, f5, INTRO
    x, y = pos
    # Изменение цвета "Начать игру"
    if 475 <= x <= 475 + 250 and 295 <= y <= 295 + 61 and not f1:
        INTRO[0][1] = 1
        f1 = True
    elif f1 and not (475 <= x <= 475 + 295 and 295 <= y <= 250 + 61):
        INTRO[0][1] = 0
        f1 = False
    # Изменение цвета "Управление"
    elif 483 <= x <= 483 + 235 and 355 <= y <= 355 + 61 and not f2:
        INTRO[1][1] = 1
        f2 = True
    elif f2 and not (483 <= x <= 483 + 235 and 355 <= y <= 355 + 61):
        INTRO[1][1] = 0
        f2 = False
    # Изменение цвета "Об игре"
    elif 523 <= x <= 523 + 154 and 415 <= y <= 415 + 61 and not f3:
        INTRO[2][1] = 1
        f3 = True
    elif f3 and not (523 <= x <= 523 + 154 and 415 <= y <= 415 + 61):
        INTRO[2][1] = 0
        f3 = False
    # Изменение цвета "Таблица рекордов"
    elif 415 <= x <= 415 + 370 and 475 <= y <= 475 + 61 and not f4:
        INTRO[3][1] = 1
        f4 = True
    elif f4 and not (415 <= x <= 415 + 370 and 475 <= y <= 475 + 61):
        INTRO[3][1] = 0
        f4 = False
    # Изменение цвета "Выход"
    elif 532 <= x <= 532 + 137 and 535 <= y <= 535 + 61 and not f5:
        INTRO[4][1] = 1
        f5 = True
    elif f5 and not (532 <= x <= 532 + 137 and 535 <= y <= 535 + 61):
        INTRO[4][1] = 0
        f5 = False


def terminate():
    """
    Выход из игры
    :return:
    """
    pygame.quit()
    sys.exit()


def start_screen_on():
    """
    Стартовый интерфейс
    :return:
    """
    global mouse_on_screen, music_on
    while True:
        show_start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            # Включение/выключение музыки
            if pygame.key.get_pressed()[pygame.K_e]:
                if music_on:
                    pygame.mixer.music.pause()
                    music_on = False
                else:
                    pygame.mixer.music.unpause()
                    music_on = True

            elif event.type == pygame.MOUSEMOTION:
                change_text_start(event.pos)
                if pygame.mouse.get_focused():
                    change_place(event.pos)
                    mouse_on_screen = event.pos
            elif event.type == CONTINUEMOVE:
                for ghost in all_ghosts:
                    ghost.continue_moving()
                pygame.time.set_timer(CONTINUEMOVE, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    event.button == 1:
                # Кнопка "Начать игру"
                if f1:
                    return
                # Кнопка "Управление"
                elif f2:
                    controls_screen()
                    return
                # Кнопка "Об игре"
                elif f3:
                    about()
                # Кнопка "Таблица рекордов"
                elif f4:
                    record_menu()
                # Кнопка "Выход"
                elif f5:
                    terminate()
        pygame.display.flip()


def show_start_screen():
    """
    Отрисовка всех элементов стартового интерфейса
    :return:
    """
    global mouse_on_screen
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    StartScreen.print_text(start)
    for ghost in all_ghosts:
        ghost.move()
        if ghost.show_name == 1:
            screen.blit(ghost.text, (ghost.start_x, ghost.start_y))
    if mouse_on_screen and pygame.mouse.get_focused():
        change_place(mouse_on_screen)
    all_ghosts.update()
    all_ghosts.draw(screen)


def controls_screen():
    """
    Обработка действий с окном управления
    :return:
    """
    global mouse_on_screen, f6, color_back, music_on
    while True:
        show_controls()
        for event in pygame.event.get():
            # Выход из игры
            if event.type == pygame.QUIT:
                terminate()
            elif pygame.key.get_pressed()[pygame.K_e]:
                if music_on:
                    pygame.mixer.music.pause()
                    music_on = False
                else:
                    pygame.mixer.music.unpause()
                    music_on = True
            elif event.type == pygame.MOUSEMOTION:
                show_controls()
                # Изменение цвета кнопки "Назад" при наведении
                x, y = event.pos
                if 538 <= x <= 538 + 125 and 525 <= y <= 525 + 61 and not f6:
                    color_back = 1
                    f6 = True
                elif f6 and not (538 <= x <= 538 + 125 and 525 <= y <= 525 + 61):
                    color_back = 0
                    f6 = False
                # Обработка движения курсора
                if pygame.mouse.get_focused():
                    show_controls()
                    change_place(event.pos)
                    mouse_on_screen = event.pos
            elif event.type == CONTINUEMOVE:
                for ghost in all_ghosts:
                    ghost.continue_moving()
                pygame.time.set_timer(CONTINUEMOVE, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    event.button == 1:
                # Возвращение в главный экран
                if f6:
                    start_screen_on()
                    return
        pygame.display.flip()


def show_controls():
    """
    Вывод экрана с описанием упраления
    :return:
    """
    global mouse_on_screen, color_back
    screen.fill((0, 0, 0))
    # Текст на экране
    text_controls = ["Управление",
                     "Стрелки для управления пакмэном",
                     "Esc: Пауза/Продолжить",
                     "E: Включить/Выключить звук",
                     "Назад"]

    # Запуск движения призраков
    for ghost in all_ghosts:
        ghost.move()
        if ghost.show_name == 1:
            screen.blit(ghost.text, (ghost.start_x, ghost.start_y))
    all_ghosts.update()
    all_ghosts.draw(screen)

    # Изображение курсора на экране
    if mouse_on_screen and pygame.mouse.get_focused():
        change_place(mouse_on_screen)

    # Вывод текст на экран
    draw_back(text_controls, 'controls')
    all_sprites.draw(screen)


def draw_back(text_list, place):
    """
    Вывод текста в игре
    :param text_list: список строк текста
    :param place: экран вывода
    :return:
    """
    y = 0
    if color_back == 0:
        color = pygame.Color("white")
    else:
        color = pygame.Color("yellow")

    if place == "controls":
        size = 50
    elif place == "about":
        size = 30
    elif place == "menu_1" or place == "menu_2":
        size = 40
    elif place == 'start':
        color = pygame.Color("white")
        size = 40
        y = 10

    if place == 'points':
        for i in range(len(text_list)):
            font = pygame.font.Font(FULLNAME, 30)
            text = font.render(str(text_list[i]), 1, (pygame.Color("white")))
            x = 250 + i * 200
            y = 685
            screen.blit(text, (x, y))
    elif place == 'points_3':
        for i in range(len(text_list)):
            font = pygame.font.Font(FULLNAME, 30)
            text = font.render(str(text_list[i]), 1, (pygame.Color("white")))
            x = 500 + i * 200
            y = 540
            screen.blit(text, (x, y))
    elif place == 'go1' or place == 'go2':
        for i in range(len(text_list)):
            font = pygame.font.Font(FULLNAME, 40)
            text = font.render(str(text_list[i]), 1, (pygame.Color("white")))
            start_x = WIDTH // 2 - text.get_width() // 2
            start_y = HEIGHT // 2 - text.get_height() // 2
            text_x = start_x
            text_y = start_y + i * 60
            if i == 1:
                x, y = text_x, text_y
            screen.blit(text, (text_x, text_y))
        if place == "go2":
            text = font.render(text_list[len(text_list) - 1], 1, (pygame.Color("yellow")))
            screen.blit(text, (text_x, text_y))
        else:
            text = font.render(text_list[len(text_list) - 2], 1, (pygame.Color("yellow")))
            screen.blit(text, (x, y))
    else:
        for i in range(len(text_list)):
            font = pygame.font.Font(FULLNAME, size)
            text = font.render(text_list[i], 1, (pygame.Color("white")))
            start_x = WIDTH // 2 - text.get_width() // 2
            start_y = HEIGHT // 2 - text.get_height() // 2 - 60
            text_x = start_x
            text_y = start_y + i * 60
            if y:
                text_y = y
            screen.blit(text, (text_x, text_y))
        if place == "menu_2":
            text = font.render(text_list[len(text_list) - 1], 1, (pygame.Color("yellow")))
            screen.blit(text, (text_x, text_y))
        elif place == "menu_1":
            text = font.render(text_list[0], 1, (pygame.Color("yellow")))
            x = WIDTH // 2 - text.get_width() // 2
            y = HEIGHT // 2 - text.get_height() // 2 - 60
            screen.blit(text, (x, y))
        else:
            text = font.render(text_list[len(text_list) - 1], 1, (color))
            screen.blit(text, (text_x, text_y))


def about():
    """
    Обработка действий с окном описания игры
    :return:
    """
    global mouse_on_screen, f6, color_back, music_on
    f6 = False
    color_back = 0
    while True:
        show_about()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # Включение / выключение звука
            elif pygame.key.get_pressed()[pygame.K_e]:
                if music_on:
                    pygame.mixer.music.pause()
                    music_on = False
                else:
                    pygame.mixer.music.unpause()
                    music_on = True
            elif event.type == pygame.MOUSEMOTION:
                show_about()
                # Изменение цвета кнопки "Назад"
                x, y = event.pos
                if 563 <= x <= 563 + 75 and 597 <= y <= 597 + 37 and not f6:
                    color_back = 1
                    f6 = True
                elif f6 and not (563 <= x <= 563 + 75 and 597 <= y <= 597 + 37):
                    color_back = 0
                    f6 = False
                if pygame.mouse.get_focused():
                    show_about()
                    change_place(event.pos)
                    mouse_on_screen = event.pos
            # Обработка остановки призраков
            elif event.type == CONTINUEMOVE:
                for ghost in all_ghosts:
                    ghost.continue_moving()
                pygame.time.set_timer(CONTINUEMOVE, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    event.button == 1:
                # Обработка выхода в главное меню
                if f6:
                    start_screen_on()
                    return
        pygame.display.flip()


def show_about():
    """
    Вывод экрана с описанием игры
    :return:
    """
    global mouse_on_screen, color_back
    screen.fill((0, 0, 0))

    # Текст на экране
    text_about = ["Пакман - аркадная видеоигра, вышедшая в 1980 году.",
                  "Задача игрока — управляя Пакманом, съесть все точки в лабиринте, ",
                  "избегая встречи с привидениями.",
                  "Автор игры: Сербинова Милена",
                  "(с) Яндекс Лицей 2019",
                  "Назад"]

    # Запуск движения призраков
    for ghost in all_ghosts:
        ghost.move()
        if ghost.show_name == 1:
            screen.blit(ghost.text, (ghost.start_x, ghost.start_y))
    all_ghosts.update()
    all_ghosts.draw(screen)

    # Обработка движения курсора
    if mouse_on_screen and pygame.mouse.get_focused():
        change_place(mouse_on_screen)
    # Вывод текста на экран
    draw_back(text_about, 'about')
    all_sprites.draw(screen)


def pause_menu():
    """
    Меню во время паузы (обработка)
    :return:
    """
    global start_game, start, stop_game, \
        lives, score, map_on_screen_num, \
        music_on, stop
    button_1 = True
    show_menu(1)
    while True:
        for event in pygame.event.get():
            # Выход из игры
            if event.type == pygame.QUIT:
                terminate()
            # Включение / выключение звука
            if pygame.key.get_pressed()[pygame.K_e]:
                if music_on:
                    pygame.mixer.music.pause()
                    music_on = False
                else:
                    pygame.mixer.music.unpause()
                    music_on = True
            if pygame.key.get_pressed()[pygame.K_UP]:
                show_menu(1)
                button_1 = True
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                show_menu(2)
                button_1 = False
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                if button_1:
                    start_game = True
                    return
                else:
                    for pm in pacman_sprite:
                        pm.kill()
                    for rect in all_rects:
                        rect.kill()
                    for ghost in ghost_sprites:
                        ghost.kill()
                    lives = 3
                    score = 0
                    stop = False
                    map_on_screen_num = 1
                    before_game(map_on_screen_num)
                    return
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                start_game = True
                return
        pygame.display.flip()


def show_menu(button):
    """
    Отрисовка меню паузы
    :param button: кнопка, которая выбрана нажатием клавиатуры
    :return:
    """
    ghost_sprites.draw(screen)
    pygame.draw.rect(screen, (0, 175, 240), ([WIDTH // 2 - 225, HEIGHT // 2 - 100], [450, 150]), 10)
    pygame.draw.rect(screen, pygame.Color("black"), ([WIDTH // 2 - 225, HEIGHT // 2 - 100], [450, 150]))
    # Текст на экране
    text_menu = ["Вернуться в игру",
                 "Начать игру заново"]

    # Вывод текста на экран
    if button == 1:
        draw_back(text_menu, 'menu_1')
    elif button == 2:
        draw_back(text_menu, 'menu_2')


def before_game(map=1):
    """
    Загрузка карты и расстановка ее элементов перед игрой
    :param map: карта на экране
    :return:
    """
    global stop
    screen.fill(pygame.Color("black"))
    all_maps.draw(screen)
    all_maps.update()
    stop = False
    draw_back(['Чтобы начать игру, нажмите пробел'], 'start')
    if map == 2:
        for i in range(8):
            GhostPlay(i)
    elif map == 1:
        for i in range(4):
            GhostPlay(i)
    elif map == 3:
        for i in range(2):
            GhostPlay(i)
    pacman = Pacman(pacman_sprite, load_image("moving_pacman.png"), 2, 1, 24, 13)
    if map != 3:
        for i in range(lives):
            screen.blit(image_life, (100 + 43 * i, 685))
        draw_back(['Баллы', score], 'points')
    else:
        for i in range(lives):
            screen.blit(image_life, (315 + 43 * i, 540))
        draw_back(['Баллы', score], 'points_3')


def game_over():
    """
    Меню окончания игры
    :return:
    """
    global start_game, start, stop_game, \
        lives, score, music_on, map_on_screen_num, \
        map_on_screen
    button = True
    show_game_over(1)
    while True:
        for event in pygame.event.get():
            # Выход из игры
            if event.type == pygame.QUIT:
                terminate()

            if pygame.key.get_pressed()[pygame.K_e]:
                if music_on:
                    pygame.mixer.music.pause()
                    music_on = False
                else:
                    pygame.mixer.music.unpause()
                    music_on = True

            if pygame.key.get_pressed()[pygame.K_UP]:
                show_game_over(1)
                button = True
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                show_game_over(2)
                button = False

            if pygame.key.get_pressed()[pygame.K_RETURN]:
                if button:
                    for pm in pacman_sprite:
                        pm.kill()
                    for rect in all_rects:
                        rect.kill()
                    for ghost in ghost_sprites:
                        ghost.kill()
                    lives = 3
                    map_on_screen_num = 1
                    for map in all_maps:
                        map.kill()
                    for point in all_points:
                        point.kill()
                    map_on_screen = Map("map.png")
                    points = Points()
                    score = 0
                    before_game(map_on_screen_num)
                    return
                else:
                    terminate()
        pygame.display.flip()


def show_game_over(button):
    """
    Отрисовка экрана окончания игры
    :param button: кнопка, которая выбрана нажатием клавиатуры
    :return:
    """
    ghost_sprites.draw(screen)

    pygame.draw.rect(screen, (0, 175, 240),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]), 10)
    pygame.draw.rect(screen, pygame.Color("black"),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]))

    screen.blit(game_over_image, (WIDTH // 2 - 180,
                                  HEIGHT // 2 - 200))
    point = "Баллы: " + str(score)
    # Текст на экране
    text = [point,
            "Повторить попытку",
            "Выход"]

    # Вывод текста на экран
    if button == 1:
        draw_back(text, 'go1')
    elif button == 2:
        draw_back(text, 'go2')


def winn_lvl():
    """
    Меню окончания уровня
    :return:
    """
    global start_game, start, stop_game, \
        lives, score, map_on_screen_num, map_on_screen, music_on
    button = True
    show_winn_screen(1)
    while True:
        for event in pygame.event.get():
            # Выход из игры
            if event.type == pygame.QUIT:
                terminate()

            elif pygame.key.get_pressed()[pygame.K_UP]:
                show_winn_screen(1)
                button = True
            elif pygame.key.get_pressed()[pygame.K_DOWN]:
                show_winn_screen(2)
                button = False
            elif pygame.key.get_pressed()[pygame.K_e]:
                if music_on:
                    pygame.mixer.music.pause()
                    music_on = False
                else:
                    pygame.mixer.music.unpause()
                    music_on = True
            elif pygame.key.get_pressed()[pygame.K_RETURN]:
                if button:
                    for pm in pacman_sprite:
                        pm.kill()
                    for rect in all_rects:
                        rect.kill()
                    for ghost in ghost_sprites:
                        ghost.kill()
                    lives = 3
                    if map_on_screen_num == 1:
                        map_on_screen_num += 1
                        before_game(map_on_screen_num)
                    elif map_on_screen_num == 2:
                        map_on_screen_num += 1
                        for map in all_maps:
                            map.kill()
                        for point in all_points:
                            point.kill()
                        map_on_screen = Map("level.png")
                        points = Points()
                        before_game(map_on_screen_num)
                    return
                else:
                    terminate()
        pygame.display.flip()


def show_winn_screen(button):
    """
    Отрисовка экрана выигрыша уровня
    :param button: кнопка, которая выбрана нажатием клавиатуры
    :return:
    """
    ghost_sprites.draw(screen)

    pygame.draw.rect(screen, (0, 175, 240),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]), 10)
    pygame.draw.rect(screen, pygame.Color("black"),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]))

    screen.blit(winn_level, (WIDTH // 2 - 180,
                             HEIGHT // 2 - 200))
    # Текст на экране
    text = ['Поздравляем, вы прошли уровень!',
            "Cледующий уровень",
            "Выход"]

    # Вывод текста на экран
    if button == 1:
        draw_back(text, 'go1')
    elif button == 2:
        draw_back(text, 'go2')


def winn_game():
    """
    Меню окончания игры
    :return:
    """
    global start_game, start, stop_game, \
        lives, score, map_on_screen_num, map_on_screen, music_on
    button = True
    add_table(new_record())
    show_winn(1)
    while True:

        for event in pygame.event.get():
            # Выход из игры
            if event.type == pygame.QUIT:
                terminate()

            if pygame.key.get_pressed()[pygame.K_e]:
                if music_on:
                    pygame.mixer.music.pause()
                    music_on = False
                else:
                    pygame.mixer.music.unpause()
                    music_on = True

            if pygame.key.get_pressed()[pygame.K_UP]:
                show_winn(1)
                button = True
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                show_winn(2)
                button = False

            if pygame.key.get_pressed()[pygame.K_RETURN]:
                if button:
                    record_menu(True)
                    screen.fill((0, 0, 0))
                    show_winn(1)
                else:
                    terminate()
        pygame.display.flip()


def show_winn(button):
    """
    Отрисовка окна выигрыша
    :param button: кнопка, которая выбрана нажатием клавиатуры
    :return:
    """
    ghost_sprites.draw(screen)
    pygame.draw.rect(screen, (0, 175, 240),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]), 10)
    pygame.draw.rect(screen, pygame.Color("black"),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]))

    screen.blit(winn_level, (WIDTH // 2 - 180,
                             HEIGHT // 2 - 200))
    # Текст на экране
    text = ['Поздравляем, вы прошли игру!',
            "Таблица рекордов",
            "Выход"]
    # Вывод текста на экран
    if button == 1:
        draw_back(text, 'go1')
    elif button == 2:
        draw_back(text, 'go2')


def new_record():
    """
    Экран добавление рекорда игрока
    :return:
    """
    global mouse_on_screen
    name = '|'
    color_ok = None
    recorded = False
    while True:
        show_record()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and len(name) <= 8:
                if 97 <= event.key <= 122:
                    name = name[:-1] + chr(event.key).upper() + '|'
                elif event.key == 8:
                    name = name[:-2] + '|'
            elif event.type == pygame.MOUSEMOTION:
                show_record()
                if 552 <= event.pos[0] <= 608 and 395 <= event.pos[1] <= 440:
                    color_ok = pygame.Color("yellow")
                else:
                    color_ok = pygame.Color("white")
                if pygame.mouse.get_focused():
                    change_place(event.pos)
                    mouse_on_screen = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    event.button == 1:
                if 552 <= event.pos[0] <= 608 and 395 <= event.pos[1] <= 440:
                    player_name = name[:len(name) - 1]
                    name = 'RECORDED!'
                    recorded = True

        font = pygame.font.Font(FULLNAME, 50)
        string_rendered = font.render('Введите свое имя:', 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(410, 225)
        screen.blit(string_rendered, intro_rect)

        if color_ok:
            string_rendered = font.render('OK', 1, color_ok)
        else:
            string_rendered = font.render('OK', 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(WIDTH // 2 - 30, 400)
        screen.blit(string_rendered, intro_rect)

        string_rendered = font.render(name, 1, (0, 175, 240))
        intro_rect = string_rendered.get_rect().move(495, 315)
        screen.blit(string_rendered, intro_rect)

        pygame.display.flip()
        clock.tick(FPS)
        if recorded:
            pygame.time.delay(2000)
            return player_name


def show_record():
    """
    Отрисовка экрана добавления имени игрока
    :return:
    """
    global mouse_on_screen
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 175, 240),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]), 10)
    pygame.draw.rect(screen, pygame.Color("black"),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]))

    if mouse_on_screen and pygame.mouse.get_focused():
        change_place(mouse_on_screen)


def add_table(name):
    """
    Добавление нового рекорда в таблицу
    :param name: имя игрока
    :return:
    """
    # Добавление имени в файл с рекордами
    file_path = os.path.join('data', 'records.txt')
    file_records = open(file_path, mode='a')
    file_records.write(str(score) + ' ' + name + '\n')
    file_records.close()

    # Сортировка файла с рекордами
    file_records = open(file_path, mode='r')
    data = file_records.readlines()
    file_records.close()

    data.sort(key=lambda a: int(a.split()[0]),
              reverse=True)

    # Запись отсортированного файла с рекордами
    file_records = open(file_path, mode='w')
    for line in data:
        file_records.write(line)
    file_records.close()


def record_menu(end=False):
    """
    Меню рекордов
    :param end: выбор меню в начале или в конце игры
    :return:
    """
    global mouse_on_screen, mouse_on_screen, music_on
    color_back = pygame.Color("white")

    file_path = os.path.join('data', 'records.txt')
    file_records = open(file_path, mode='r')
    data = file_records.readlines()
    file_records.close()

    while True:
        if end:
            show_record_menu(data, color_back, True)
        else:
            show_record_menu(data, color_back)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            elif pygame.key.get_pressed()[pygame.K_e]:
                if music_on:
                    pygame.mixer.music.pause()
                    music_on = False
                else:
                    pygame.mixer.music.unpause()
                    music_on = True
            elif event.type == CONTINUEMOVE:
                for ghost in all_ghosts:
                    ghost.continue_moving()
                pygame.time.set_timer(CONTINUEMOVE, 0)

            elif event.type == pygame.MOUSEMOTION:
                if 534 <= event.pos[0] <= 643 and 596 <= event.pos[1] <= 637:
                    color_back = pygame.Color("yellow")
                else:
                    color_back = pygame.Color("white")
                if end:
                    show_record_menu(data, color_back, True)
                else:
                    show_record_menu(data, color_back)
                if pygame.mouse.get_focused():
                    change_place(event.pos)
                    mouse_on_screen = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    event.button == 1:
                if 534 <= event.pos[0] <= 643 and 596 <= event.pos[1] <= 637:
                    return
        pygame.display.flip()


def show_record_menu(data, color, end=False):
    """
    Отрисовка меню рекордов
    :param data: файл с рекордами
    :param color: цвет кнопки "Назад"
    :param end: выбор меню в начале или в конце игры
    :return:
    """
    global mouse_on_screen
    screen.fill((0, 0, 0))
    font = pygame.font.Font(FULLNAME, 45)

    pygame.draw.rect(screen, pygame.Color("white"),
                     ([100, 275],
                      [1000, 300]), 5)
    for i in range(3):
        pygame.draw.line(screen, pygame.Color("white"),
                         [350 + 250 * i, 275],
                         [350 + 250 * i, 575], 5)
    if data:
        if len(data) <= 4:
            data_1 = data[:len(data)]
            data_2 = []
        elif 4 <= len(data) <= 8:
            data_1 = data[:4]
            data_2 = data[4:8]
        elif len(data) > 8:
            data_1 = data[:4]
            data_2 = data[4:8]

        for i in range(len(data_1)):
            line = data_1[i]
            pos_1 = (150, 290 + i * 70)
            pos_2 = (400, 290 + i * 70)
            line = line.strip('\n').split()
            line[0], line[1] = line[1], line[0]

            string_rendered = font.render(line[0], 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect().move(pos_1)
            screen.blit(string_rendered, intro_rect)

            string_rendered = font.render(line[1], 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect().move(pos_2)
            screen.blit(string_rendered, intro_rect)

        for i in range(len(data_2)):
            line = data_2[i]
            pos_1 = (650, 290 + i * 70)
            pos_2 = (900, 290 + i * 70)
            line = line.strip('\n').split()
            line[0], line[1] = line[1], line[0]

            string_rendered = font.render(line[0], 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect().move(pos_1)
            screen.blit(string_rendered, intro_rect)

            string_rendered = font.render(line[1], 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect().move(pos_2)
            screen.blit(string_rendered, intro_rect)

    string_rendered = font.render('Назад', 1, color)
    intro_rect = string_rendered.get_rect().move(550, 600)
    screen.blit(string_rendered, intro_rect)

    if mouse_on_screen and pygame.mouse.get_focused():
        change_place(mouse_on_screen)
    if not end:
        all_sprites.draw(screen)
        for ghost in all_ghosts:
            ghost.move()
            if ghost.show_name == 1:
                screen.blit(ghost.text, (ghost.start_x, ghost.start_y))
        all_ghosts.update()
        all_ghosts.draw(screen)


# Начальные значения для главного меню
f1, f2, f3, f4, f5 = False, False, False, False, False
f6 = False
color_back = 0
ghost_on_screen = 0
Ghost(all_ghosts, GHOSTS[0])
running = True
mouse_on_screen = None

# Саундтрек игры
pygame.mixer.init()
song = os.path.join('data', 'music.mp3')
pygame.mixer.music.load(song)
pygame.mixer.music.play(100)
music_on = True
pygame.mixer.music.set_volume(0.3)

# Для игры

# Загрузка изображений
image_life = load_image('pacman_lives.png')
game_over_image = load_image("game_over.png")
winn_level = load_image('winn_level.png')

map_on_screen_num = 1

# Начало игры
start = StartScreen()
start_screen_on()

score = 0

lives = 3
stop_game = False
start_game = False
stop = False

map_on_screen = Map("map.png")
before_game(map_on_screen_num)

iteration_kill = 0
kill_num = 0
iterations = 0
points = Points()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        # Начало игры
        elif pygame.key.get_pressed()[pygame.K_SPACE] and \
                not start_game and not stop:
            pygame.time.set_timer(CHANGE, 2000)
            screen.fill(pygame.Color("black"))
            all_maps.draw(screen)
            start_game = True
        # Включение / выключение звука
        elif pygame.key.get_pressed()[pygame.K_e]:
            if music_on:
                pygame.mixer.music.pause()
                music_on = False
            else:
                pygame.mixer.music.unpause()
                music_on = True

        # Изменения направления призраков
        elif event.type == CHANGE:
            for ghost in ghost_sprites:
                ghost.change()
            pygame.time.set_timer(CHANGE, 3500)
        elif pygame.key.get_pressed()[pygame.K_ESCAPE] and start_game:
            start_game = False
            pause_menu()

        # Движение пакмана
        elif pygame.key.get_pressed()[pygame.K_RIGHT] and start_game:
            for hero in pacman_sprite:
                hero.move("right")
        elif pygame.key.get_pressed()[pygame.K_LEFT] and start_game:
            for hero in pacman_sprite:
                hero.move("left")
        elif pygame.key.get_pressed()[pygame.K_UP] and start_game:
            for hero in pacman_sprite:
                hero.move("up")
        elif pygame.key.get_pressed()[pygame.K_DOWN] and start_game:
            for hero in pacman_sprite:
                hero.move("down")

    # Игровой процесс
    if start_game:
        screen.fill(pygame.Color("black"))
        if map_on_screen_num != 3:
            draw_back(['Баллы', score], 'points')
        else:
            draw_back(['Баллы', score], 'points_3')
        # Отрисовка всех групп спрайтов
        all_points.draw(screen)
        all_rects.update()
        all_rects.draw(screen)
        all_maps.draw(screen)
        pacman_sprite.draw(screen)
        for pacman in pacman_sprite:
            pacman.move()

        # Отрисовка оставшихся жизней
        if map_on_screen_num != 3:
            for i in range(lives):
                screen.blit(image_life, (100 + 43 * i, 685))
        else:
            for i in range(lives):
                screen.blit(image_life, (315 + 43 * i, 540))
        if iterations == 10:
            pacman_sprite.update()
            iterations = 0
        for ghost in ghost_sprites:
            ghost.move()
        ghost_sprites.update()
        ghost_sprites.draw(screen)

        iterations += 1
        # Переключение на новый уровень
        if (score == 1840 and map_on_screen_num == 1) or \
                (score == 3680 and map_on_screen_num == 2):
            start_game = False
            winn_lvl()
        # Выигрыш
        if score == 4170 and map_on_screen_num == 3:
            start_game = False
            winn_game()

        if stop_game:
            lives -= 1
            start_game = False
            for pm in pacman_sprite:
                x, y = pm.rect.x, pm.rect.y
            kill_pacman = Pacman(pacman_kill, load_image("killing_pacman.png"),
                                 11, 1, 32, 32, x, y)

    # Остановка игрового процесса
    if stop_game:
        stop = True
        screen.fill(pygame.Color("black"))
        all_points.draw(screen)
        all_rects.draw(screen)
        all_maps.draw(screen)
        ghost_sprites.draw(screen)
        pacman_kill.draw(screen)
        # Анимация смерти пакмана
        iteration_kill += 1
        if iteration_kill == 10:
            pacman_kill.update()
            iteration_kill = 0
            kill_num += 1
        if kill_num == 11:
            kill_num = 0
            stop_game = False
            for ghost in ghost_sprites:
                ghost.kill()
            for pm in pacman_sprite:
                pm.kill()
            for pm in pacman_kill:
                pm.kill()
            if lives == -1:
                # Запись рекорда игрока и завершение игры
                add_table(new_record())
                game_over()
            else:
                before_game(map_on_screen_num)
                stop = False
    pygame.display.flip()
