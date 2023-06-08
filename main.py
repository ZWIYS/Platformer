# подключение библиотек
import pygame
import pickle
from os import path
import asyncio

# инициализация окна игры
pygame.init()
# разрешение экрана + настройки окна
screen_height = 700
screen_width = 1000

# вывод окна на экран
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platformer game!")

# значение ограничения fps
fps = 60
clock = pygame.time.Clock()


# глобальные переменные
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 2

# добавление всех изображений
background = pygame.image.load("img/back_ground.jpeg")
background = pygame.transform.scale(background, (screen_width, screen_height))
restart_img = pygame.image.load("img/restart_btn.png")

up_arrow_img = pygame.image.load("img/up_arrow.png")
up_arrow_img = pygame.transform.scale(up_arrow_img, (tile_size, tile_size))
left_arrow_img = pygame.image.load("img/left_arrow.png")
left_arrow_img = pygame.transform.scale(left_arrow_img, (tile_size, tile_size))
right_arrow_img = pygame.image.load("img/right_arrow.png")
right_arrow_img = pygame.transform.scale(right_arrow_img, (tile_size, tile_size))
start_btn_img = pygame.image.load("img/start_btn.png")
exit_btn_img = pygame.image.load("img/exit_btn.png")

# функция перезапуска уровня
def reset_level(level):
    player.reset(50, 450)
    slime_group.empty()
    lava_group.empty()
    exit_group.empty()

    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

# класс кнопок
class Buttons:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        # отслеживание мышки
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # отрисовка клавиш
        screen.blit(self.image, self.rect)

        return action


# класс игрока
class Player:
    def __init__(self, x, y):
        self.reset(50, 450)

    # (в плане характеристик) класса игрока
    def update(self, game_over):

        # характеристики игрока
        dx = 0
        dy = 0
        speed = 3.5
        walk_cooldown = 1  # скорость анимации ходьбы
        action = False
        self.clicked = False

        if game_over == 0:
            # реагирование нажатие кнопок
            keys = pygame.key.get_pressed()
            pos = pygame.mouse.get_pos()
            touch = pygame.FINGERDOWN
            # управление игроком
            if up_arrow.rect.collidepoint(pos) and self.jumped is False:
                    if pygame.mouse.get_pressed()[0] == 1:
                        self.vel_y = -15
                        self.jumped = True
                        self.clicked = True
            if left_arrow.rect.collidepoint(pos):
                if pygame.mouse.get_pressed()[0] == 1:
                    dx -= speed
                    self.counter += 1
                    self.direction = -1
            if right_arrow.rect.collidepoint(pos):
                if pygame.mouse.get_pressed()[0] == 1:
                    dx += speed
                    self.counter += 1
                    self.direction = 1
            if right_arrow.rect.collidepoint(pos) or left_arrow.rect.collidepoint(pos):
                if pygame.mouse.get_pressed()[0] == 0:
                    self.counter = 0
                    self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]

            # хендлер анимации
            if right_arrow.rect.collidepoint(pos) or left_arrow.rect.collidepoint(pos) and touch:
                if pygame.mouse.get_pressed()[0] == 1:
                    if self.counter > walk_cooldown:
                        self.counter = 0
                        self.index += 1
                        if self.index >= len(self.images_right):
                            self.index = 0
                        if self.direction == 1:
                            self.image = self.images_right[self.index]
                        if self.direction == -1:
                            self.image = self.images_left[self.index]

            # гравитация (прыжок)
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy -= self.vel_y

            # проверка коллизии
            for tile in world.tile_list:
                # коллизия по X
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # коллизия по Y
                if tile[1].colliderect(self.rect.x, self.rect.y - dy, self.width, self.height):

                    # в прыжке
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    # в падении
                    if self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.jumped = False

            if pygame.sprite.spritecollide(self, slime_group, False):
                game_over = -1

            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # отрисовка нового положения
            self.rect.x += dx
            self.rect.y -= dy

        # отрисовка анимации смерти
        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        # отрисовка персонажа
        screen.blit(self.image, self.rect)


        return game_over

    # отрисовка персонажа после смерти
    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 12):
            player_image_right = pygame.image.load(f"img/PNG/p1_walk{num}.png")
            player_image_right = pygame.transform.scale(player_image_right, (35, 60))
            player_image_left = pygame.transform.flip(player_image_right, True, False)
            self.images_right.append(player_image_right)
            self.images_left.append(player_image_left)
        self.dead_image = pygame.image.load("img/Daco_508411.png")
        self.dead_image = pygame.transform.scale(self.dead_image, (tile_size, tile_size))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.jump_counter = 0

# класс врагов
class Enemies(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        # изображения врагов
        self.image = pygame.image.load("img/blob.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

# класс лавы
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        # изображения
        img = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# выход из игры
class Exit_gate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        # изображения
        img = pygame.image.load("img/exit.png")
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# класс мира (отрисовка карты)
class World:
    def __init__(self, data):
        self.tile_list = []

        # загрузка изображений
        dirt = pygame.image.load("img/dirtCenter.png")
        grass = pygame.image.load("img/grass.png")
        # цикл отрисовки
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 2:
                    img = pygame.transform.scale(grass, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 3:
                    slime = Enemies(col_count * tile_size, row_count * tile_size + 15)
                    slime_group.add(slime)

                if tile == 4:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)

                if tile == 5:
                    exit_gate = Exit_gate(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit_gate)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

            # отрисовка сетки (для отладки)
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

# отрисовка изображений на карте
player = Player(tile_size * 2, tile_size)
slime_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# матрица карты
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# кнопки
restart_button = Buttons(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
up_arrow = Buttons(850, 600, up_arrow_img)
left_arrow = Buttons(50, 600, left_arrow_img)
right_arrow = Buttons(150, 600, right_arrow_img)
start_btn = Buttons(screen_width // 2 - 350, screen_height // 2, start_btn_img)
exit_btn = Buttons(screen_width // 2 + 50, screen_height // 2, exit_btn_img)


# основной цикл игры
game_is_running = True
while game_is_running:

    # ограничение фпс
    clock.tick(fps)

    # отображение всех изображений (важен порядок строки 316-319)
    screen.blit(background, (0, 0))

    # отрисовка классов/кнопок
    if main_menu == True:
        if exit_btn.draw():
            game_is_running = False

        if start_btn.draw():
            main_menu = False

    else:
        world.draw()

        if game_over == 0:
            slime_group.update()

        slime_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        up_arrow.draw()
        left_arrow.draw()
        right_arrow.draw()


        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0

        if game_over == 1:
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                if restart_button.draw():
                    level = 1

                    world_data = []
                    world = reset_level

    # закрытие окна игры
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_is_running = False

    # отрисовка всех изображений
    pygame.display.update()

# завершение сеанса игры
pygame.quit()
