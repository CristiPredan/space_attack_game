import pygame
from pygame import mixer
from pygame.locals import *
import random
import math
import time
import sys


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

#fps setting
clock = pygame.time.Clock()
fps = 75

PLAYTIME = 73
start_time = 73

screen_width = 950
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Attack')


# load sounds
intro_fx = pygame.mixer.Sound("assets/intro.wav")
intro_fx.set_volume(0.25)

end_fx = pygame.mixer.Sound("assets/end_theme.wav")
end_fx.set_volume(0.25)

power_fx = pygame.mixer.Sound("assets/power_down.wav")
power_fx.set_volume(0.25)

explosion_fx = pygame.mixer.Sound("assets/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("assets/explosion2.wav")
explosion2_fx.set_volume(0.25)

lasers_fx = pygame.mixer.Sound("assets/lasers.wav")
lasers_fx.set_volume(0.25)
 

 # declare fonts
font20 = pygame.font.SysFont('Impact', 20)
font30 = pygame.font.SysFont('Impact', 30)
font40 = pygame.font.SysFont('Impact', 40)

# declare game variables
rows = 5
cols = 8
countdown = 5
last_count = pygame.time.get_ticks()
game_over = 0  # 0 is no game over, 1 means player has won, -1 means player has lost
alien_shoot = 1000  # bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()


# declare colors
red = (200, 16, 46)
green = (46, 139, 87)
white = (255, 255, 255)
yellow = (234, 169, 63)

score_value = 0
# font = pygame.font.SysFont('Roboto', 32)

textX = 10
testY = 10

# load image
bg = pygame.image.load("assets/bg.png")
bg2 = pygame.image.load("assets/bg-intro.png")


def delay():
	time.sleep(0.5)


def draw_bg():
    screen.blit(bg, (0, 0))

# define function for creating text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# define score
def show_score(x, y):
    score = font20.render("Score: " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))

# define countdown
def draw_timer(screen, x, y, time_left):
    text = font20.render("Time Left: " + str(time_left) +
                         " seconds", 1, (255, 255, 255))
    screen.blit(text, (x, y))
    if int(time_left) <= 30 and int(time_left) >= 16:
        text = font20.render(
            "Time Left: " + str(time_left) + " seconds", 1, (234, 169, 63))
        screen.blit(text, (x, y))
    elif int(time_left) < 16 and int(time_left) > 0:
        text = font20.render(
            "Time Left: " + str(time_left) + " seconds", 1, (200, 16, 16))
        screen.blit(text, (x, y))

# define start screens
def game_intro():
    intro = True
    intro_fx.play()
    while intro:
        time_left = pygame.time.get_ticks() - start_time
        time_left = time_left / 1000
        time_left = PLAYTIME - time_left
        time_left = int(time_left)
        if time_left <= 64:
            intro = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

        screen.blit(bg2, (0, 0))
        pygame.display.update()
        clock.tick(5000)

# spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        time_left = pygame.time.get_ticks() - start_time
        time_left = time_left / 1000
        time_left = PLAYTIME - time_left
        time_left = int(time_left)
        # set movement speed
        speed = 8
        if time_left < 30:
            speed = 4
        if time_left < 15:
            speed = 1
        cooldown = 500  # milliseconds
        game_over = 0

        # get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        # record current time
        time_now = pygame.time.get_ticks()
        # shoot
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            lasers_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        # update mask
        self.mask = pygame.mask.from_surface(self.image)

        # draw health bar
        pygame.draw.rect(
            screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 7))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 7))              
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over

# bullets class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill() 
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

# aliens class
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            "assets/alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

# alien Bullets class
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
        if spaceship.health_remaining == 1:
       		draw_text('Shields down!', font20, red, int(screen_width / 2 - 70), int(screen_height / 2 - 340)) 
       		# shield_fx.play(5000)
       		# shield_fx.stop()

# explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"assets/exp{num}.png")
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


# sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


def create_aliens():
    # generate aliens
    time_left = pygame.time.get_ticks() - start_time
    time_left = time_left / 1000
    time_left = PLAYTIME - time_left
    time_left = int(time_left)
    for row in range(rows):
        for item in range(cols):
            descent = 100
            alien = Aliens(100 + item * 100, descent + row * 70)
            alien_group.add(alien)


create_aliens()

# create player
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)


# call the start screen
game_intro()

run = True
while run:

    clock.tick(fps)

    # draw background
    draw_bg()

    if countdown == 0:
        # create random alien bullets
        # record current time
        time_now = pygame.time.get_ticks()
        # shoot
        if time_now - last_alien_shot > alien_shoot and len(alien_bullet_group) < 5 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullets(
                attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now

        # check if all the aliens have been killed
        if len(alien_group) == 0:
            game_over = 1

        if game_over == 0:
            # update spaceship
            game_over = spaceship.update()
            # update sprite groups
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()
        else:
            if game_over == -1:
                draw_text('GAME OVER!', font40, white, int(
                    screen_width / 2 - 100), int(screen_height / 2 + 10))
                draw_text('Press Q to exit', font30, white, int(
                    screen_width / 2 - 95), int(screen_height / 2 + 75))
        # create ranks
                if score_value <= 25:
                    draw_text('Ooops. This is not for you. Your Rank is Rookie', font30, white, int(
                        screen_width / 2 - 300), int(screen_height / 2 + 120))
                if score_value <= 30 and score_value > 25:
                    draw_text('Try harder. Your Rank is Corporal', font30, white, int(
                        screen_width / 2 - 215), int(screen_height / 2 + 120))
                if score_value <= 33 and score_value > 30:
                    draw_text('Pretty good! Your Rank is Sergeant', font30, white, int(
                        screen_width / 2 - 215), int(screen_height / 2 + 120))
                if score_value <= 36 and score_value > 33:
                    draw_text('Great! Your Rank is Lieutenant', font30, white, int(
                        screen_width / 2 - 210), int(screen_height / 2 + 120))
                if score_value <= 39 and score_value > 36:
                    draw_text('Congratulations, your Rank is Commender', font30, white, int(
                        screen_width / 2 - 240), int(screen_height / 2 + 120))
                if score_value == 40:
                    draw_text('You are the best! Your Rank is Captain', font30, white, int(
                        screen_width / 2 - 240), int(screen_height / 2 + 120))
                if time_left > 0:
                    def draw_timer(screen, x, y, time_left):
                        return False                     
                end_fx.play()

            if game_over == 1:
                draw_text('YOU WIN!', font40, white, int(
                    screen_width / 2 - 90), int(screen_height / 2 + 10))
                draw_text('Press Q to exit', font30, white, int(
                    screen_width / 2 - 110), int(screen_height / 2 + 75))
                if score_value <= 39 and score_value > 36:
                    draw_text('Congratulations, your Rank is Commender', font30, white, int(
                        screen_width / 2 - 240), int(screen_height / 2 + 120))
                if score_value == 40:
                    draw_text('You are the best! Your Rank is Captain', font30, white, int(
                        screen_width / 2 - 240), int(screen_height / 2 + 120))
                if time_left > 0:
                    def draw_timer(screen, x, y, time_left):
                        return False      
                end_fx.play()          

    if countdown > 0:
        draw_text('Get ready soldier!', font40, white, int(
            screen_width / 2 - 150), int(screen_height / 2 + 55))
        draw_text(str(countdown), font30, white, int(
            screen_width / 2 - 10), int(screen_height / 2 + 105))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer
    else:
        time_left = pygame.time.get_ticks() - start_time
        time_left = time_left / 1000
        time_left = PLAYTIME - time_left
        time_left = int(time_left)
        show_score(textX, testY)
        if time_left > 0:
            draw_timer(screen, 200, 10, time_left)
        else:
            draw_timer(screen, 200, 10, " 0")
        score_value = -(len(alien_group)-40)+(spaceship.health_remaining-3)
        # score_value++3
        if time_left < 31:
            alien_shoot = 700
        if time_left == 30:
            power_fx.play()        
        if time_left <= 30 and time_left > 26 and game_over == 0:
            draw_text('Ship is losing power!', font20, yellow, int(screen_width / 2 + 120), int(screen_height / 2 - 340)) 
        if time_left < 16:
            alien_shoot = 300
        if time_left == 15:
            power_fx.play()        
        if time_left <= 15 and time_left > 11  and game_over == 0:
            draw_text('Ship lost main engine!', font20, red, int(screen_width / 2 + 100), int(screen_height / 2 - 340))    
        if time_left == 0:
            game_over = -1
        # create_aliens()
        if time_left <= 50:
            descent = 130

    # update explosion group
    explosion_group.update()

    # draw sprite groups
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                intro = False
            if event.key == pygame.K_q:
                pygame.quit()
                quit()
            if event.key == pygame.K_r:
                pygame.init()

    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                pygame.init()

    # def gameOverScreen():
    pygame.display.update()
pygame.quit()
