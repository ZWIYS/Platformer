import pygame


# инициализация окна игры
pygame.init()
# разрешение экрана + настройки окна
screen_height = 700
screen_width = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platformer game!")

# значение ограничения fps
fps = 60
clock = pygame.time.Clock()


# глобальные переменные
tile_size = 50
game_over = 0

# добавление всех изображений
background = pygame.image.load("img/back_ground.jpeg")
background = pygame.transform.scale(background, (screen_width, screen_height))
restart_img = pygame.image.load("img/restart_btn.png")


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
        self.reset(x, y)

    # все связанное с изменениями
    # (в плане характеристик) класса игрока
    def update(self, game_over):

        # характеристики игрока
        dx = 0
        dy = 0
        speed = 3.5
        walk_cooldown = 1  # скорость анимации ходьбы

        if game_over == 0:
            # реагирование нажатие кнопок
            keys = pygame.key.get_pressed()
            # управление игроком
            if keys[pygame.K_UP] and self.jumped is False:
                self.vel_y = -15
                self.jumped = True
            if keys[pygame.K_LEFT]:
                dx -= speed
                self.counter += 1
                self.direction = -1
            if keys[pygame.K_RIGHT]:
                dx += speed
                self.counter += 1
                self.direction = 1
            if keys[pygame.K_LEFT] is False and keys[pygame.K_RIGHT] is False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # хендлер анимации
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
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
                # коллизия по Y
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # коллизия по Y
                if tile[1].colliderect(self.rect.x, self.rect.y - dy, self.width, self.height):
                    # в прыжке
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    # падает
                    if self.vel_y > 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.jumped = False

            if pygame.sprite.spritecollide(self, slime_group, False):
                game_over = -1

            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            # отрисовка нового положения
            self.rect.x += dx
            self.rect.y -= dy

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        # отрисовка персонажа
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 12):
            player_image_right = pygame.image.load(f"sprite_pack/Base pack/Player/p1_walk/PNG/p1_walk{num}.png")
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


class Enemies(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        # изображения
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


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        # изображения
        img = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# класс мира (отрисовка карты)
class World:
    def __init__(self, data):
        self.tile_list = []

        # загрузка изображений
        dirt = pygame.image.load("sprite_pack/Base pack/Tiles/dirtCenter.png")
        grass = pygame.image.load("sprite_pack/Base pack/Tiles/grass.png")
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

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


# матрица карты
world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 2, 0, 0, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 2, 2, 4, 4, 4, 4, 4, 4, 4, 2, 2, 0, 0, 3, 0, 1],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
]


player = Player(50, screen_height - 127)
slime_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
world = World(world_data)

# кнопки
restart_button = Buttons(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)

# основной цикл игры
game_is_running = True
while game_is_running:

    # ограничение фпс
    clock.tick(fps)

    # отображение всех изображений (важен порядок)
    screen.blit(background, (0, 0))

    # отрисовка классов
    world.draw()

    if game_over == 0:
        slime_group.update()

    slime_group.draw(screen)
    lava_group.draw(screen)

    game_over = player.update(game_over)

    if game_over == -1:
        if restart_button.draw():
            player.reset(50, screen_height - 127)
            game_over = 0

    # закрытие окна -> игры
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_is_running = False

    # отрисовка изображений
    pygame.display.update()

# завершение сеанса игры
pygame.quit()
