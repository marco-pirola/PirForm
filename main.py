import pygame
import sys
from pygame.locals import *
import os

def resource_path(relative_path):
    """Trova il percorso corretto dei file sia in Python che nell'EXE."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Fa funzionare i percorsi tipo 'assets/file.png'
# sia con main.py sia con l'EXE creato da PyInstaller.
os.chdir(os.path.dirname(resource_path("main.py")))

pygame.init()

clock = pygame.time.Clock()
fps = 60

lava_sound = pygame.mixer.Sound(resource_path('assets/lava.mp3'))
coin_sound = pygame.mixer.Sound(resource_path('assets/coin.wav'))
albero_img = pygame.image.load(resource_path('assets/albero.png'))

screen_width = 1000
screen_height = 1000     

screen = pygame.display.set_mode((screen_width, screen_height))
ponte_sinistra = pygame.image.load('assets/ponte_sinistra.png').convert_alpha()
ponte_centro = pygame.image.load('assets/ponte_centro.png').convert_alpha()
ponte_destra = pygame.image.load('assets/ponte_destra.png').convert_alpha()
small_font = pygame.font.SysFont("PixelOperator8.ttf", 20)
pygame.display.set_caption('PirForm')   
enemy_img = pygame.image.load('assets/nemico.png').convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (37, 50))
enemy_img_3 = pygame.image.load('assets/nemico3.png').convert_alpha()
enemy_img_3 = pygame.transform.scale(enemy_img_3, (37, 50))  # dimensioni a piacere
enemy_img_4 = pygame.image.load('assets/nemico4.png').convert_alpha()
enemy_img_4 = pygame.transform.scale(enemy_img_4, (37, 47))
enemy_img_6 = pygame.image.load('assets/nemico6.png').convert_alpha()
enemy_img_6 = pygame.transform.scale(enemy_img_6, (39, 45))  # stessa dimensione di enemy_img
enemy_img_7 = pygame.image.load('assets/nemico7.png').convert_alpha()
enemy_img_7 = pygame.transform.scale(enemy_img_7, (37, 50))  # stessa dimensione del nemico3
font = pygame.font.Font('PixelOperator8.ttf', 25)
title_font = pygame.font.Font('PixelOperator8.ttf', 70)  # font più grande per il titolo
settings_img = pygame.image.load('assets/impostazioni.png')
settings_img = pygame.transform.scale(settings_img, (40, 40))
settings_rect = settings_img.get_rect()
settings_rect.bottomright = (screen_width - 10, screen_height - 10)


# define game variables
tile_size = 50
azzurro = (0, 217, 255)
sfondo = pygame.image.load('assets/sfondo1.png').convert()
sfondo = pygame.transform.scale(sfondo, (screen_width, screen_height))
sfondo2 = pygame.image.load('assets/sfondo2.png').convert()
sfondo2 = pygame.transform.scale(sfondo2, (screen_width, screen_height))
sfondo3 = pygame.image.load('assets/sfondo3.png').convert()
sfondo3 = pygame.transform.scale(sfondo3, (screen_width, screen_height))
start_x = 100
start_y = screen_height - 130
score = 0
pygame.mixer.music.load('assets/musica_sfondo.mp3')  # metti il file nella cartella
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)  # -1 = loop infinito

# VITE
lives = 3
max_lives = 3

# Carica immagini cuori
heart_imgs = []
for i in range(1, 4):  # cuore1.png, cuore2.png, cuore3.png rossi
    img = pygame.image.load(f'assets/cuore{i}.png').convert_alpha()
    img = pygame.transform.scale(img, (40, 40))
    heart_imgs.append(img)

heart_empty = pygame.image.load('assets/cuore4.png').convert_alpha()
heart_empty = pygame.transform.scale(heart_empty, (40, 40))

def draw_lives(screen, lives, max_lives=3):
    for i in range(max_lives):
        if i < lives:
            screen.blit(heart_imgs[i], (10 + i * 45, 50))
        else:
            screen.blit(heart_empty, (10 + i * 45, 50))

spawn_points = [
    (100, screen_height - 130),  # livello 0
    (100, screen_height - 130),  # livello 1
    (100, screen_height - 130)   # livello 2 (nuova mappa)
]


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'assets/guy{num}.png').convert_alpha()
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 1
        self.on_ground = False

    def reset_position(self):
        self.rect.x = start_x
        self.rect.y = start_y
        self.vel_y = 0

    def update(self):
        global score, lives, current_level

        dx = 0
        dy = 0
        walk_cooldown = 5

        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -13
            self.on_ground = False

        if key[pygame.K_LEFT]:
            dx -= 5
            self.counter += 1
            self.direction = -1
        if key[pygame.K_RIGHT]:
            dx += 5
            self.counter += 1
            self.direction = 1
        if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
            self.counter = 0
            self.index = 0
            self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]

        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]

        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        self.on_ground = False

        for tile in world.tile_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.on_ground = True

        # Collisione con piattaforme mobili
        for platform in moving_platforms:
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y >= 0 and self.rect.bottom <= platform.rect.centery:
                    dy = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.on_ground = True
                    if platform.direction_type == 'horizontal':
                        dx += platform.move_direction

        # Collisioni con lava
        if pygame.sprite.spritecollide(self, lava_group, False):
            lava_sound.play()
            lives -= 1
            self.reset_position()
            if lives <= 0:
                print("Game Over")
                pygame.quit()
                exit()

        # Collisioni con nemici
        if pygame.sprite.spritecollide(self, enemy_group, False):
            lives -= 1
            self.reset_position()
            if lives <= 0:
                print("Game Over")
                pygame.quit()
                exit()

        # Collisione con porta per cambiare livello
        if pygame.sprite.spritecollide(self, door_group, False):
            if current_level == len(levels) - 1:
                final_time = (pygame.time.get_ticks() - start_time) // 1000
                print(f"Hai completato il gioco con {score} punti in {final_time} secondi!")
                pygame.quit()
                exit()
            else:
                current_level += 1
                lives = max_lives
                load_level(current_level)
                self.reset_position()



        # Limiti schermo
        if self.rect.x + dx < 0:
            dx = -self.rect.x
        elif self.rect.x + dx > screen_width - self.width:
            dx = screen_width - self.width - self.rect.x

        self.rect.x += dx
        self.rect.y += dy

        coins_collected = pygame.sprite.spritecollide(self, coin_group, True)
        if coins_collected:
            coin_sound.play()
            score += len(coins_collected)

        screen.blit(self.image, self.rect)


class World():
    def __init__(self, data):
        self.tile_list = []
        self.tree_list = []

        dirt_img = pygame.image.load('assets/terra.png').convert_alpha()
        grass_img = pygame.image.load('assets/erba.png').convert_alpha()

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                x = col_count * tile_size
                y = row_count * tile_size
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                elif tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                elif tile == 5:
                    img = pygame.transform.scale(albero_img, (50, 100))
                    rect = img.get_rect(topleft=(x, y - 50))
                    self.tree_list.append((img, rect))
                elif tile == 6:
                    lava = Lava(x, y + tile_size // 2)
                    lava_group.add(lava)
                elif tile == 7:
                    coin = Coin(x, y)
                    coin_group.add(coin)
                elif tile == 8:
                    enemy = Enemy(x, y)
                    enemy_group.add(enemy)
                elif tile == 9:
                    enemy_flying = EnemyFlying(x, y)
                    enemy_group.add(enemy_flying)
                elif tile == 10:
                    platform = MovingPlatform(x, y, direction='vertical', move_range=50)  # range standard
                    moving_platforms.add(platform)
                elif tile == 11:
                    platform = MovingPlatform(x, y, direction='horizontal')
                    moving_platforms.add(platform)
                elif tile == 12:
                    door = Door(x, y)
                    door_group.add(door)
                elif tile == 13:  # ponte_sinistra
                    img = pygame.transform.scale(ponte_sinistra, (tile_size, tile_size // 2))
                    rect = img.get_rect(topleft=(x, y - 25))  # metà superiore
                    self.tile_list.append((img, rect))
                elif tile == 14:  # ponte_destra
                    img = pygame.transform.scale(ponte_destra, (tile_size, tile_size // 2))
                    rect = img.get_rect(topleft=(x, y - 25))  # metà superiore, come il 13
                    self.tile_list.append((img, rect))
                elif tile == 15:
                    enemy3 = Enemy3(x, y)
                    enemy_group.add(enemy3)
                elif tile == 16:
                    platform = MovingPlatform(x, y, direction='vertical', move_range=100)  # range più ampio
                    moving_platforms.add(platform)
                elif tile == 17:
                    enemy4 = Enemy4(x, y)
                    enemy_group.add(enemy4)
                elif tile == 18:
                    enemy5 = Enemy5(x, y)
                    enemy_group.add(enemy5)
                elif tile == 19:
                    enemy6 = Enemy6(x, y)
                    enemy_group.add(enemy6)
                elif tile == 20:
                    enemy7 = Enemy7(x, y)
                    enemy_group.add(enemy7)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
        for tree in self.tree_list:
            screen.blit(tree[0], tree[1])


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('assets/lava.png').convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        coin_size = 30
        for i in range(1, 13):
            img = pygame.image.load(f'assets/moneta{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (coin_size, coin_size))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x + tile_size // 2
        self.rect.bottom = y + tile_size
        self.counter = 0

    def update(self):
        animation_speed = 5
        self.counter += 1
        if self.counter > animation_speed:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]
        screen.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_right = enemy_img 
        self.image_left = pygame.transform.flip(enemy_img, True, False)
        self.image = self.image_right
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

        if self.move_direction == 1:
            self.image = self.image_right
        else:
            self.image = self.image_left

        screen.blit(self.image, self.rect)

class EnemyFlying(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('assets/nemico2.png').convert_alpha()
        self.image = pygame.transform.scale(img, (48, 37))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction * 2
        self.move_counter += 1

        if abs(self.move_counter) > 40:
            self.move_direction *= -1
            self.move_counter *= -1

        screen.blit(self.image, self.rect)

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, direction='vertical', move_range=50):
        super().__init__()
        if direction == 'vertical':
            img = pygame.image.load('assets/piattaformay.png').convert_alpha()
        else:
            img = pygame.image.load('assets/piattaformax.png').convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.move_direction = 1
        self.speed = speed if 'speed' in locals() else 1
        self.direction_type = direction
        self.move_range = move_range
        if direction == 'vertical':
            self.start_pos = y
        else:
            self.start_pos = x
        self.move_counter = 0

    def update(self):
        if self.direction_type == 'vertical':
            self.rect.y += self.move_direction * self.speed
            if abs(self.rect.y - self.start_pos) >= self.move_range:
                self.move_direction *= -1
        else:
            self.rect.x += self.move_direction
            if abs(self.rect.x - self.start_pos) >= self.move_range:
                self.move_direction *= -1

        screen.blit(self.image, self.rect)



class Enemy3(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img_3
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.move_direction = 1  # 1 = giù, -1 = su
        self.move_counter = 0
        self.move_speed = 3
        self.move_range = 150

    def update(self):
        self.rect.y += self.move_direction * self.move_speed
        self.move_counter += self.move_direction * self.move_speed  # <-- aggiorna qui il contatore con la direzione

        if self.move_counter >= self.move_range or self.move_counter <= 0:
            self.move_direction *= -1

        screen.blit(self.image, self.rect)

class Enemy4(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_right = enemy_img_4
        self.image_left = pygame.transform.flip(enemy_img_4, True, False)
        self.image = self.image_right
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

        self.image = self.image_right if self.move_direction == 1 else self.image_left
        screen.blit(self.image, self.rect)

class Enemy5(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_right = pygame.image.load('assets/nemico5.png').convert_alpha()
        self.image_right = pygame.transform.scale(self.image_right, (50, 30))
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y + 22

        self.move_direction = 1
        self.move_counter = 0
        self.speed = 1  # velocità, puoi cambiare

    def update(self):
        self.rect.x += self.move_direction * self.speed
        self.move_counter += 1

        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

        if self.move_direction == 1:
            self.image = self.image_right
        else:
            self.image = self.image_left

        screen.blit(self.image, self.rect)

class Enemy6(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_right = enemy_img_6
        self.image_left = pygame.transform.flip(enemy_img_6, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y + 5

        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1

        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

        if self.move_direction == 1:
            self.image = self.image_right
        else:
            self.image = self.image_left

        screen.blit(self.image, self.rect)

class Enemy7(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_up = enemy_img_7
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.x = x + 5
        self.rect.y = y

        self.move_direction = 1  # 1 = giù, -1 = su
        self.move_counter = 0

    def update(self):
        self.rect.y += self.move_direction
        self.move_counter += 1

        if abs(self.move_counter) > 70 :
            self.move_direction *= -1
            self.move_counter *= -1

        if self.move_direction == 1:
            self.image = self.image_up

        screen.blit(self.image, self.rect)


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/door.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 75))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y + tile_size  # allinea il fondo della porta con il fondo del tile

world_data1 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 7, 0, 2, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 9, 0, 0, 2, 0, 11, 0, 0, 2, 2, 0, 0, 0, 0], 
    [0, 0, 0, 2, 0, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 2, 2, 2, 0, 2, 7, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 5], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 2, 1, 1, 1], 
    [0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 0, 2, 2, 1, 1, 1, 1], 
    [0, 0, 0, 0, 0, 0, 2, 2, 1, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
    [5, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

world_data2 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 0, 0, 0, 2, 2, 0, 2], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 7, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 2, 0, 13, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 17, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 10, 0, 7, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 7, 0, 0, 0], 
    [0, 0, 2, 2, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 0], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 13, 14, 0, 0, 0], 
    [0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5], 
    [2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

world_data3 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 2, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 11, 0, 0, 0, 2, 0, 2, 2, 0, 0, 0, 0],
    [0, 0, 0, 7, 2, 2, 6, 6, 6, 6, 6, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 2, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0],
    [0, 0, 2, 0, 0, 11, 0, 0, 2, 0, 0, 19, 0, 0, 2, 2, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 16, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 2, 2, 0, 0, 0, 0, 0],
    [5, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 13, 14, 0, 0, 0, 0, 0, 0, 5],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

levels = [world_data1, world_data2, world_data3]
current_level = 0
guy1_img = pygame.image.load("assets/guy1.png").convert_alpha()
guy1_img = pygame.transform.scale(guy1_img, (50, 70))  # opzionale: ridimensiona

lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
moving_platforms = pygame.sprite.Group()
door_group = pygame.sprite.Group()

world = None

player = Player(start_x, start_y)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def main_menu():
    menu = True
    pygame.mixer.music.load('assets/menu_music.mp3')
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)  # loop infinito

    while menu:
        screen.fill((0, 217, 255))  # sfondo azzurro

        draw_text("PirForm", title_font, (0, 0, 0), screen_width // 2 - 200, 50)
        screen.blit(guy1_img, (screen_width // 2 + 235, 50))  # puoi modificare la posizione

        mx, my = pygame.mouse.get_pos()

        # Crea rettangoli per i pulsanti
        button_play = pygame.Rect(screen_width // 2 - 75, 250, 150, 50)
        button_quit = pygame.Rect(screen_width // 2 - 75, 320, 150, 50)

        # Disegna i pulsanti
        pygame.draw.rect(screen, (255, 255, 255), button_play)
        pygame.draw.rect(screen, (255, 255, 255), button_quit)

        draw_text("Gioca", font, (0, 0, 0), button_play.x + 26, button_play.y + 10)
        draw_text("Esci", font, (0, 0, 0), button_quit.x + 35, button_quit.y + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.collidepoint(mx, my):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('assets/musica_sfondo.mp3')
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                    menu = False
                if button_quit.collidepoint(mx, my):
                    pygame.quit()
                    exit()

        pygame.display.update()
        clock.tick(60)

def mostra_menu_fine(screen, score, elapsed_time):
    font_big = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)

    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0,0))

    screen_center = screen.get_rect().center

    text_title = font_big.render("FINE DEL GIOCO", True, (255, 255, 255))
    text_score = font_small.render(f"Punti: {score}", True, (255, 255, 255))
    text_time = font_small.render(f"Tempo: {elapsed_time}s", True, (255, 255, 255))
    text_restart = font_small.render("Premi R per ricominciare", True, (255, 255, 255))
    text_quit = font_small.render("Premi ESC per uscire", True, (255, 255, 255))

    screen.blit(text_title, text_title.get_rect(center=(screen_center[0], screen_center[1] - 100)))
    screen.blit(text_score, text_score.get_rect(center=(screen_center[0], screen_center[1] - 20)))
    screen.blit(text_time, text_time.get_rect(center=(screen_center[0], screen_center[1] + 20)))
    screen.blit(text_restart, text_restart.get_rect(center=(screen_center[0], screen_center[1] + 80)))
    screen.blit(text_quit, text_quit.get_rect(center=(screen_center[0], screen_center[1] + 120)))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    waiting = False  # esce dal menu per ricominciare
def tutorial_screen():
    running = True
    while running:
        screen.fill((0, 217, 255))
        draw_text("Tutorial", title_font, (0, 0, 0), 180, 50)

        instructions = [
            "Muovi il giocatore con le frecce.",
            "Raccogli le monete per fare punti.",
            "Evita la lava e i nemici.",
            "Vai nella porta per passare al prossimo livello.",
        ]

        y = 150
        for line in instructions:
            draw_text(line, font, (0, 0, 0), 50, y)
            y += 40

        draw_text("Torna al menu (ESC)", font, (0, 0, 0), 50, y + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.update()
        clock.tick(60)

def level_select_screen():
    selecting = True

    button_levels = []
    for i in range(len(levels)):
        button = pygame.Rect(screen_width // 2 - 100, 150 + i * 70, 200, 50)
        button_levels.append(button)

    while selecting:
        screen.fill((0, 217, 255))
        draw_text("Seleziona livello", title_font, (0, 0, 0), 30, 30)

        mx, my = pygame.mouse.get_pos()

        for i, button in enumerate(button_levels):
            if button.collidepoint(mx, my):
                pygame.draw.rect(screen, (180, 180, 255), button)
            else:
                pygame.draw.rect(screen, (255, 255, 255), button)

            draw_text(f"Livello {i+1}", font, (0, 0, 0), button.x , button.y + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # click sinistro
                    for i, button in enumerate(button_levels):
                        if button.collidepoint(mx, my):
                            global current_level
                            current_level = i
                            selecting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    selecting = False

        pygame.display.update()
        clock.tick(60)

def main_menu():
    menu = True
    pygame.mixer.music.load('assets/menu_music.mp3')
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)

    button_play = pygame.Rect(screen_width // 2 - 75, 250, 150, 50)
    button_quit = pygame.Rect(screen_width // 2 - 75, 320, 150, 50)
    button_levels = pygame.Rect(screen_width // 2 - 75, 390, 150, 50)
    button_help = pygame.Rect(screen_width // 2 - 75, 460, 150, 50)

    while menu:
        screen.fill((0, 217, 255))
        draw_text("PirForm", title_font, (0, 0, 0), screen_width // 2 - 230, 50)
        screen.blit(guy1_img, (screen_width // 2 + 235, 50))

        mx, my = pygame.mouse.get_pos()

        for button in [button_play, button_quit, button_levels, button_help]:
            if button.collidepoint(mx, my):
                pygame.draw.rect(screen, (180, 180, 255), button)
            else:
                pygame.draw.rect(screen, (255, 255, 255), button)

        draw_text("Gioca", font, (0, 0, 0), button_play.x + 24, button_play.y + 10)
        draw_text("Esci", font, (0, 0, 0), button_quit.x + 34, button_quit.y + 10)
        draw_text("Livelli", font, (0, 0, 0), button_levels.x + 12, button_levels.y + 10)
        draw_text("Tutorial", font, (0, 0, 0), button_help.x - 5, button_help.y + 10)

        # Disegna l'icona impostazioni in basso a destra
        screen.blit(settings_img, settings_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_play.collidepoint(mx, my):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('assets/musica_sfondo.mp3')
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                    menu = False
                elif button_quit.collidepoint(mx, my):
                    pygame.quit()
                    exit()
                elif button_levels.collidepoint(mx, my):
                    level_select_screen()
                elif button_help.collidepoint(mx, my):
                    tutorial_screen()
                elif settings_rect.collidepoint(mx, my):
                    settings_menu()

        pygame.display.update()
        clock.tick(60)



def settings_menu():
    run_settings = True
    volume = 5
    music_on = True

    while run_settings:
        screen.fill((135, 206, 235))

        draw_text("Impostazioni", title_font, (0, 0, 0), screen_width // 2 - 350, 20)

        # Volume
        draw_text(f"Volume {volume}", font, (0, 0, 0), screen_width // 2 - 79, 150)
        vol_minus = pygame.Rect(screen_width // 2 - 120, 145, 40, 40)
        vol_plus = pygame.Rect(screen_width // 2 + 90, 145, 40, 40)
        pygame.draw.rect(screen, (200, 200, 200), vol_minus)
        pygame.draw.rect(screen, (200, 200, 200), vol_plus)
        draw_text("-", font, (0, 0, 0), vol_minus.x + 10, vol_minus.y + 5)
        draw_text("+", font, (0, 0, 0), vol_plus.x + 10, vol_plus.y + 5)

        # Musica ON/OFF
        draw_text("Musica:", font, (0, 0, 0), screen_width // 2 - 90, 230)
        music_rect = pygame.Rect(screen_width // 2 + 55, 225, 60, 40)
        pygame.draw.rect(screen, (100, 200, 100) if music_on else (200, 100, 100), music_rect)
        draw_text("ON" if music_on else "OFF", font, (0, 0, 0), music_rect.x + 7, music_rect.y + 10)

        # Crediti
        credits_button = pygame.Rect(screen_width // 2 - 60, 320, 120, 50)
        pygame.draw.rect(screen, (180, 180, 180), credits_button)
        draw_text("Crediti", font, (0, 0, 0), credits_button.x + 30, credits_button.y + 17)

        # Indietro
        back_button = pygame.Rect(screen_width // 2 - 60, 400, 120, 50)
        pygame.draw.rect(screen, (180, 180, 180), back_button)
        draw_text("Indietro", font, (0, 0, 0), back_button.x + 25, back_button.y + 10)

        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if vol_minus.collidepoint(mx, my) and volume > 1:
                    volume -= 1
                    pygame.mixer.music.set_volume(volume / 10)
                if vol_plus.collidepoint(mx, my) and volume < 10:
                    volume += 1
                    pygame.mixer.music.set_volume(volume / 10)
                if music_rect.collidepoint(mx, my):
                    music_on = not music_on
                    if music_on:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                if credits_button.collidepoint(mx, my):
                    show_credits()
                if back_button.collidepoint(mx, my):
                    run_settings = False

        pygame.display.update()
        clock.tick(fps)


def show_credits():
    run_credits = True
    while run_credits:
        screen.fill((135, 206, 235))
        draw_text("Crediti", title_font, (0, 0, 0), screen_width // 2 - 60, 50)
        credits_lines = [
            "Creato da: Marco",
            "Grazie per aver giocato!"
        ]
        y = 150
        for line in credits_lines:
            draw_text(line, font, (0, 0, 0), screen_width // 2 - 180, y)
            y += 40

        back_button = pygame.Rect(screen_width // 2 - 60, 450, 120, 50)
        pygame.draw.rect(screen, (180, 180, 180), back_button)
        draw_text("Indietro", font, (0, 0, 0), back_button.x + 25, back_button.y + 10)

        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(mx, my):
                    run_credits = False

        pygame.display.update()
        clock.tick(fps)


def load_level(level_index):
    global world, lava_group, coin_group, enemy_group, moving_platforms, door_group
    lava_group.empty()
    coin_group.empty()
    enemy_group.empty()
    moving_platforms.empty()
    door_group.empty()

    world = World(levels[level_index])
    spawn_x, spawn_y = spawn_points[level_index]
    player.rect.x = spawn_x
    player.rect.y = spawn_y
    player.vel_y = 0


# --- Avvio programma ---

main_menu()        # Mostra il menu principale (con impostazioni accessibili solo qui)
load_level(current_level)
start_time = pygame.time.get_ticks()
font = pygame.font.Font('PixelOperator8.ttf', 25)

run = True
paused = False

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if paused:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                resume_button = pygame.Rect(screen_width // 2 - 75, 220, 150, 50)
                quit_button = pygame.Rect(screen_width // 2 - 75, 290, 150, 50)
                if resume_button.collidepoint(mx, my):
                    paused = False
                elif quit_button.collidepoint(mx, my):
                    paused = False
                    current_level = 0
                    main_menu()
                    load_level(current_level)
                    start_time = pygame.time.get_ticks()
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True

    if paused:
        s = pygame.Surface((screen_width, screen_height))
        s.set_alpha(180)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))

        resume_button = pygame.Rect(screen_width // 2 - 75, 220, 150, 50)
        quit_button = pygame.Rect(screen_width // 2 - 75, 290, 150, 50)

        pygame.draw.rect(screen, (255, 255, 255), resume_button)
        pygame.draw.rect(screen, (255, 255, 255), quit_button)

        draw_text("Avanti", font, (0, 0, 0), resume_button.x + 20, resume_button.y + 10)
        draw_text("Menu", font, (0, 0, 0), quit_button.x + 29, quit_button.y + 10)

        pygame.display.update()
        clock.tick(fps)
        continue

    # Disegno livello, sprite, HUD ecc.
    if current_level == 0:
        screen.blit(sfondo, (0, 0))
    elif current_level == 1:
        screen.blit(sfondo2, (0, 0))
    elif current_level == 2:
        screen.blit(sfondo3, (0, 0))

    world.draw()
    lava_group.draw(screen)
    coin_group.update()
    enemy_group.update()
    moving_platforms.update()
    door_group.draw(screen)
    player.update()

    draw_text(f'Pt: {score}', font, (0, 0, 255), 9, 10)
    draw_lives(screen, lives)

    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    draw_text(f'Sec: {elapsed_time}s', font, (255, 255, 0), screen_width - 180, 10)

    for door in door_group:
        if player.rect.colliderect(door.rect):
            if current_level < len(levels) - 1:
                current_level += 1
                load_level(current_level)
                start_time = pygame.time.get_ticks()
            else:
                mostra_menu_fine(screen, score, elapsed_time)
                current_level = 0
                score = 0
                load_level(current_level)
                start_time = pygame.time.get_ticks()

    # NON mostrare più icona impostazioni nel gioco:
    # screen.blit(settings_img, settings_rect)

    pygame.display.update()
    clock.tick(fps)

pygame.quit()
