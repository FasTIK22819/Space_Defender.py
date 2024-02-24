import math

import pygame
from pygame import mixer
import random
import button

pygame.init()

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# fps
clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Defender')

# define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

# Sounds
explosion_fx = pygame.mixer.Sound("img/img_explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("img/img_explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("img/img_laser.wav")
laser_fx.set_volume(0.25)

# Buttons
resume_img = pygame.image.load("img/button_resume.png").convert_alpha()
options_img = pygame.image.load("img/button_options.png").convert_alpha()
quit_img = pygame.image.load("img/button_quit.png").convert_alpha()
video_img = pygame.image.load('img/button_video.png').convert_alpha()
audio_img = pygame.image.load('img/button_audio.png').convert_alpha()
keys_img = pygame.image.load('img/button_keys.png').convert_alpha()
back_img = pygame.image.load('img/button_back.png').convert_alpha()
resume_button = button.Button(204, 225, resume_img, 1)
options_button = button.Button(197, 350, options_img, 1)
quit_button = button.Button(236, 475, quit_img, 1)
video_button = button.Button(126, 175, video_img, 1)
audio_button = button.Button(125, 300, audio_img, 1)
keys_button = button.Button(146, 425, keys_img, 1)
back_button = button.Button(232, 550, back_img, 1)

# define game variables
n = 0
pressed_word = ''
chosen_word = ''
text = ''
word_x = ''
word_y = ''
count_win = 0
level = 1
record = 1
menu_state = "main"
game_paused = True
game_status = ''

# colors
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# Background
bg = pygame.image.load("img/bg.png")


# draw bg
def draw_bg():
    screen.blit(bg, (0, 0))


class Spaceship(pygame.sprite.Sprite):  # create Spaceship class
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        # update mask
        self.mask = pygame.mask.from_surface(self.image)

        # draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (
                self.rect.x, (self.rect.bottom + 10),
                int(self.rect.width * (self.health_remaining / self.health_start)),
                15))
        elif self.health_remaining <= 0:
            Explosion(self.rect.centerx, self.rect.centery, 3)
            self.kill()


class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            "img/alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
        self.bullet = Alien_Bullets(300, 480)
        self.speed = 1

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y - 10))
        return self.rect.y

    def update(self):
        if self.rect.y < 480 or self.rect.centerx != 300:
            self.rect.y += self.speed
            if self.rect.centerx > 300:
                self.rect.centerx -= self.speed
            if self.rect.centerx < 300:
                self.rect.centerx += self.speed
        else:
            # enemy fire if he has right coordinates
            self.bullet.draw()
            self.bullet.update()


class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.flag = 1

    def draw(self):
        if self.flag == 1:
            screen.blit(self.image, (self.rect.centerx, self.rect.centery))

    def update(self):
        self.rect.y += 3
        # check if bullet out of screen
        if self.rect.y > screen_height:
            self.flag = 0
        # check collision
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask) and self.flag == 1:
            self.flag = 0
            explosion2_fx.play()
            # reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            # add the image to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


class Word:  # Create class for word
    def __init__(self, textt, speed, y_pos, x_pos, raz):
        self.text = textt
        self.speed = speed
        self.y_pos = y_pos
        self.x_pos = x_pos
        self.raz = raz

    def draw(self):
        color = 'blue'
        screen.blit(font.render(self.text, True, color), (self.x_pos, self.y_pos))
        act_len = len(pressed_word)
        if pressed_word == self.text[:act_len]:
            screen.blit(font.render(pressed_word, True, 'green'), (self.x_pos, self.y_pos))

    def update(self):
        if self.y_pos < 500:
            self.y_pos += self.speed
        if self.x_pos != 300 - self.raz:
            if self.x_pos > 300 - self.raz:
                self.x_pos -= self.speed
            if self.x_pos < 300 - self.raz:
                self.x_pos += self.speed


# Function for generate word for enemies
def generate_word():
    global chosen_word, x_pos, y_pos
    speed = 1
    x_pos = random.randint(100, 450)
    y_pos = -50
    if level <= 3:
        lines = open(f"words_{level}.txt").read().splitlines()
    else:
        lines = open(f"words_3.txt").read().splitlines()
    chosen_word = random.choice(lines)
    if len(chosen_word) > 8:
        new_word = Word(chosen_word, speed, y_pos, x_pos - 60, 60)
    elif 4 < len(chosen_word) < 8:
        new_word = Word(chosen_word, speed, y_pos, x_pos - 40, 40)
    else:
        new_word = Word(chosen_word, speed, y_pos, x_pos - 30, 30)
    return new_word


def create_alien():  # function for create enemies
    alien = Aliens(x_pos, y_pos, 3)
    return alien


def print_text(message, x, y, font_color=(255, 255, 255), font_type="ComicSansMs", font_size=30):
    font_type = pygame.font.SysFont(font_type, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))


font = pygame.font.SysFont("ComicSansMs", 32)
this_word = font.render(str(pressed_word), True, (30, 30, 255))

# create base setting
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
explosion_group = pygame.sprite.Group()
spaceship_group = pygame.sprite.Group()
spaceship_group.add(spaceship)

run = True
word_objects = generate_word()
alien_object = create_alien()
bullet = Alien_Bullets(x_pos, 480)

while run:
    clock.tick(fps)
    draw_bg()
    if menu_state == "main":
        # draw pause screen buttons
        print_text("Space Defender", 175, 100)
        print_text(f"Level: {level}", 10, 5)
        print_text(f"{game_status}", 425, 5)
        print_text(f"Record:{record}", 10, 750)
        if resume_button.draw(screen):
            game_paused = False
            menu_state = "OK"
        if options_button.draw(screen):
            menu_state = "options"
        if quit_button.draw(screen):
            run = False
    # draw background
    else:
        if menu_state == "options":
            # draw the different options buttons
            if video_button.draw(screen):
                print("Video Settings")
            if audio_button.draw(screen):
                print("Audio Settings")
            if keys_button.draw(screen):
                menu_state = 'Keys_option'
            if back_button.draw(screen):
                menu_state = "main"
        else:
            if menu_state == 'Keys_option':
                print_text("Escape  =>  Pause", 175, 200)
                print_text("Left CTRL + Space  =>  Delete All text", 50, 300)
                print_text("Backspace  =>  Delete 1 symbol", 100, 400)
                if back_button.draw(screen):
                    menu_state = "options"
            else:
                if not (game_paused):
                    # draw objects
                    spaceship.draw()
                    spaceship.update()
                    word_objects.draw()
                    word_objects.update()
                    alien_object.draw()
                    alien_object.update()
                    explosion_group.update()
                    explosion_group.draw(screen)
                    # draw interface
                    PointCaption = font.render(f'Points:{str(count_win)}', True, (30, 30, 255))
                    text_now = font.render(str(pressed_word), True, (30, 255, 30))
                    level_now = font.render(f'Level:{level}', True, (255, 30, 30))
                    goal = font.render(f'Enemies left:{3 * level - count_win}', True, (255, 30, 30))
                    screen.blit(PointCaption, (10, 5))
                    screen.blit(text_now, (450, 5))
                    screen.blit(level_now, (450, 750))
                    screen.blit(goal, (10, 750))
                    time_now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_BACKSPACE]:
                # Delete 1 symbol
                pressed_word = pressed_word[:-1]
            else:
                if keys[pygame.K_ESCAPE]:
                    # Pause
                    menu_state = 'main'
                else:
                    # Delete full string
                    if event.key == pygame.K_SPACE and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        pressed_word = ''
                    else:
                        if not (keys[pygame.K_LCTRL]):
                            pressed_word += pygame.key.name(event.key)  # Us word + key, that you pressed
                            if pressed_word == chosen_word:  # Kill enemies
                                count_win += 1
                                explosion = Explosion(alien_object.update(), alien_object.draw(), 2)
                                explosion_group.add(explosion)
                                word_objects = generate_word()
                                alien_object = create_alien()
                                pressed_word = ''
                                if count_win == 3 * level:
                                    # if we win
                                    menu_state = 'main'
                                    game_status = "YOU WIN"
                                    count_win = 0
                                    level += 1
                                    record = level

    if spaceship.health_remaining == 0:  # if we die
        # Recreate all objects
        menu_state = 'main'
        spaceship.health_remaining = 3
        game_status = "YOU LOSE"
        level = 1
        word_objects = generate_word()
        alien_object = create_alien()
        spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
        explosion_group = pygame.sprite.Group()
        spaceship_group = pygame.sprite.Group()
        spaceship_group.add(spaceship)
        count_win = 0
        pressed_word = ''
    pygame.display.update()

pygame.quit()
