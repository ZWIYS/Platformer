import pygame

screen_width = 1000
screen_height = 700

pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platformer game!")

up_arrow_img = pygame.image.load("img/up_arrow.png")


class Buttons:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

        def draw():
            action = False

            # отслеживание мышки
            pos = pygame.mouse.get_pos()

            if self.rect.collidepoint(pos):
                if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                    action = True
                    self.clicked = True
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            screen.blit(self.image, self.rect)

            return action


up_arrow = Buttons(screen_width // 2 + 50, screen_height // 2 + 100, up_arrow_img)


run = True
while run:

    up_arrow.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()