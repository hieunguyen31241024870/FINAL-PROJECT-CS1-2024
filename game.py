import pygame
import random
import button
import os
import csv

pygame.init() #Chạy lệnh mặc định thư viện pygame trước


SCREEM_WIDTH = 800 #độ dài của màn hình
SCREEN_HEIGHT  = int(SCREEM_WIDTH * 0.8) #Chiều cao của màn hình = 800 * 0.8

screen = pygame.display.set_mode((SCREEM_WIDTH, SCREEN_HEIGHT)) #Lệnh hiện ra màn hình game
pygame.display.set_caption('Huy') #Hiện tên Game

clock = pygame.time.Clock()
FPS = 60

GRAVITY = 0.75 #Khai báo biến trọng lực của nhân vật
SCROLL_THRESH = 200 
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS 
TILE_TYPES = 21 
MAX_LEVELS = 3 
screen_scroll = 0
bg_scroll = 0
level = 1 
start_game = False

moving_left = False #Biến di chuyển nhân vật sang trái 
moving_right = False#Biến di chuyển nhân vật sang trái
shoot = False
grenade = False
grenade_thrown  = False

start_img = pygame.image.load('Shooter_main/Shooter_main/img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('Shooter_main/Shooter_main/img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('Shooter_main/Shooter_main/img/restart_btn.png').convert_alpha()
pine1_img = pygame.image.load('Shooter_main/Shooter_main/img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('Shooter_main/Shooter_main/img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('Shooter_main/Shooter_main/img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('Shooter_main/Shooter_main/img/Background/sky_cloud.png').convert_alpha()

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'Shooter_main/Shooter_main/img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

bullet_img = pygame.image.load('Shooter_main/Shooter_main/img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('Shooter_main/Shooter_main/img/icons/grenade.png').convert_alpha()
health_box_img = pygame.image.load('Shooter_main/Shooter_main/img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('Shooter_main/Shooter_main/img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('Shooter_main/Shooter_main/img/icons/health_box.png').convert_alpha()
item_boxes = {
    'Health'   : health_box_img,
    'Ammo'     : ammo_box_img,
    'Grenade'  : grenade_box_img
}


BG = (144, 201, 120) #Màu Background
RED = (0, 0, 0) #Màu của dòng gạch ngang
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = 0 

font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))


def draw_bg(): #Hàm này có ý nghĩa là vẽ Background
    screen.fill(BG) #Hàm fill có 1 tham số đó color
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8  , SCREEN_HEIGHT - pine2_img.get_height()))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty() 
    exit_group.empty()

    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)    

    return data 

class Soldier(pygame.sprite.Sprite): 
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type 
        self.speed = speed
        self.ammo = ammo 
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades 
        self.health = 100
        self.max_health = self.health 
        self.direction = 1
        self.frame_index = 0
        self.vel_y = 0
        self.jump = False 
        self.in_air = True
        self.flip = False 
        self.animation_list = []
        self.index = 0 
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0 
        self.vision = pygame.Rect(0, 0 , 150 , 20)
        self.idling = False
        self.idling_counter = 0 


        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f"Shooter_main/Shooter_main/img/{self.char_type}/{animation}"))
            for i in range(num_of_frames): #C:\Users\Huy\Downloads\Python\Shooter_main\Shooter_main\img\player\Idle\0.png
                img = pygame.image.load(f"Shooter_main/Shooter_main/img/{self.char_type}/{animation}/{i}.png")
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() *scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)    
            temp_list = []     
            
        self.image = self.animation_list[self.action][self.frame_index]    
        self.rect = self.image.get_rect()
        self.rect.center = (x,y) 
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1



    def move(self,moving_left,moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:  
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump == True and  self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True 


        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y


        for tile  in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1 
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):  
                
                if self.vel_y < 0:
                    self.vel_y = 0 
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom    


        if pygame.srite.spritecollide(self, water_group, False):
            self.health = 0

        level_complete = False 
        if pygame.srite.spritecollide(self, exit_group, False):   
            level_complete = True

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0     


        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEM_WIDTH:
                dx = 0            
                  

        self.rect.x += dx
        self.rect.y += dy 


        if self.char_type == 'player':
            if (self.rect.right > SCREEM_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEM_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx 
                screen_scroll = -dx

        return screen_scroll, level_complete           


    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0 :
            self.shoot_cooldown = 20
            bullet = Bullet(player.rect.centerx + (0.75 * (player.rect.size[0] * player.direction)), player.rect.centery, player.direction)
            bullet_group.add(bullet)
            self.ammo -= 1



    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50 
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()   
            else:    
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False 
                    ai_moving_left = not ai_moving_right 
                    self.move(ai_moving_left, ai_moving_right)  
                    self.update_action(1)  
                    self.move_counter += 1 
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                  


                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1 
                        self.move_counter *= -1  
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False


        self.rect.x += screen_scroll


    def update_animation(self):
        animation_cooldown = 100 
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):   
            if self.action == 3:  
                self.frame_index = len(self.animation_list[self.action]) - 1 
            else:    
                self.frame_index = 0 

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0 
            self.update_time = pygame.time.get_ticks()


    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False 
            self.update_action(3)




    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, RED, self.rect, 1)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img ,x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img ,x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier("player",x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)  #Khai báo biến nhân vật
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        enemy = Soldier('enemy',x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 0) #khai báo địch
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox('Ammo',x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(img ,x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar                   

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll     

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll     

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.img = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))        

    def update(self):
        self.rect.x += screen_scroll 

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def upadte(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                print(player.health)
                player.health += 25
            if player.health > player.max_health:
                player.health = player.max_health    
                print(player.health)    
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenade +=3         
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))   
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))    
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio , 20)) 


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img 
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)  + screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEM_WIDTH:
            self.kill() 

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(player, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25 
                    self.kill()
                    

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100 
        self.vel_y = -11 
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction  


    def update(self):
        self.vel_y = GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y      


        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0 
        

        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEM_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            Explosion_group.add(explosion)
            if abs(self.rect.centerx - player.rect.centerx ) < TILE_SIZE * 2 and \
                abs(self.rect.centerx - player.rect.centerx ) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx ) < TILE_SIZE * 2 and \
                    abs(self.rect.centerx - enemy.rect.centerx ) < TILE_SIZE * 2:
                    enemy.health -= 50    

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale ):
        pygame.sprite.Sprite.__init__(self)
        self.image = []
        for num  in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0    
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0 


    def update(self):
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4 
        self.counter += 1


        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:    
                self.image = self.images[self.frame_index]


start_button = button.Button(SCREEM_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEM_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEM_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
Explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
bullet_group.draw(screen)
grenade_group.draw(screen)

item_box = ItemBox('Health', 100, 300)
item_box_group.add(item_box)
item_box = ItemBox('Health', 400, 300) 
item_box_group.add(item_box)
item_box = ItemBox('Grenade', 500, 300) 
item_box_group.add(item_box)





world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

with open(f'Shooter_main/Shooter_main/level{level}_data.csv', newline = '') as csvfile:
    reader = csv.reader(csvfile, delimiter= ',') 
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run: #While True

    clock.tick(FPS) #Chỉnh tốc độ chạy Frames per second (chạy nhiều khung hình trong 1 giây)

    if start_game == False:
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
    else:

        draw_bg() #Hiển thị background

        world.draw()

        health_bar.draw(player.health)
        draw_text(f'AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen. blit(bullet_img, (90 + (x * 10), 40))

        draw_text(f'GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen. blit(grenade_img, (135 + (x * 15), 60))
        
        
        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

    
        bullet_group.update()
        bullet_group.draw(screen)

        grenade_group.update()
        grenade_group.draw(screen)

        Explosion_group.update()
        Explosion_group.draw(screen)

        item_box_group.update()
        item_box_group.draw(screen)

        decoration_group.update()
        decoration_group.draw(screen)

        water_group.update()
        water_group.draw(screen)

        exit_group.update()
        exit_group.draw(screen)
        
        
        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top, player.direction)
                grenade_group.add(grenade)
                player.grenades -= 1 
                grenade_thrown = True
                print(player.grenades)
            if player.in_air:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)   
            screen_scroll, level_complete  = player.move(moving_left, moving_right)
            print(level_complete)
            bg_scroll -= screen_scroll

            if level_complete:
                level += 1 
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f'level{level}_data.csv', newline = '') as csvfile:
                        reader = csv.reader(csvfile, delimiter= '') 
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
                        

        else:
            screen_scroll = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                with open(f'level{level}_data.csv', newline = '') as csvfile:
                    reader = csv.reader(csvfile, delimiter= '') 
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)

        

    for event in pygame.event.get(): #quit game
        if event.type == pygame.quit:
            run = False #Thoát khỏi vòng lặpqq
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True    
            if event.key == pygame.K_q:
                grenade = True    
            if event.key == pygame.K_w and player.alive:
                player.jump = True     
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False   
            if event.key == pygame.K_SPACE:
                shoot = False  
            if event.key == pygame.K_q:
                grenade = False 
                grenade_thrown = False               
    pygame.display.update()
pygame.quit()            




