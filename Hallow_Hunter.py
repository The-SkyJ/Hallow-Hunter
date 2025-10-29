# --- Setup ---
import pygame, random, math, sys, os
from pygame import JOYBUTTONDOWN

pygame.init()
pygame.joystick.init()
# Detects Controller
joysticks = []
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)
    print(f"Detected joystick: [{joystick.get_name()}]")


# New screen size
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎃 Hallow Hunter 🎃")

clock = pygame.time.Clock()
font = pygame.font.SysFont("chiller", 40, bold=True)

# --- Load Images and Scale Automatically ---
background_img = pygame.image.load("Cornfield.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))


# Helper function for proportional scaling
def scale_by_percent(image, percent):
    """Scale an image based on a percentage of the screen width."""
    w = int(WIDTH * percent)
    aspect_ratio = image.get_height() / image.get_width()
    h = int(w * aspect_ratio)
    return pygame.transform.smoothscale(image, (w, h))

# Load and scale sprites proportionally
player_img = scale_by_percent(pygame.image.load("Hunter.png").convert_alpha(), 0.05)   # 5% of width
enemy_img = scale_by_percent(pygame.image.load("Reaper.png").convert_alpha(), 0.045)   # 4.5% of width
bullet_img = scale_by_percent(pygame.image.load("Bullet.png").convert_alpha(), 0.015)  # 1.5% of width
candy_img = scale_by_percent(pygame.image.load("Candy.png").convert_alpha(), 0.03)     # 3% of width

    

# --- Player ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = player_img
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.angle = 0
        self.velocity = pygame.Vector2(0, 0)
        self.lives = 3

    def rotate(self, direction):
        self.angle += direction * 5
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def accelerate(self):
        radians = math.radians(self.angle)
        self.velocity.x += math.sin(radians) * 0.3
        self.velocity.y -= math.cos(radians) * 0.3

    def update(self):
        self.rect.center += self.velocity
        if self.rect.left > WIDTH:
            self.rect.right = 0
        if self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        self.velocity *= 0.98

# --- Bullet ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=pos)
        radians = math.radians(angle)
        self.velocity = pygame.Vector2(math.sin(radians) * 10, -math.cos(radians) * 10)

    def update(self):
        self.rect.center += self.velocity
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# --- Enemy (Reaper) ---
class Reaper(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(
            center=(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        )
        if self.rect.centerx > (WIDTH / 3) and self.rect.centerx < (WIDTH / 1.5):
            self.rect.centerx = 900
        if self.rect.centery > (HEIGHT / 1.5) and self.rect.centery < (HEIGHT / 3):
            self.rect.centery = 700
        self.velocity = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))

    def update(self):
        self.rect.center += self.velocity
        if self.rect.left > WIDTH:
            self.rect.right = 0
        if self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT

# --- Candy (collectible) ---
class Candy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = candy_img
        self.rect = self.image.get_rect(
            center=(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        )

def HandleRotation(value):
    player.rotate(value)


# --- Groups ---
player = Player()
player_group = pygame.sprite.Group(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
candies = pygame.sprite.Group()

for _ in range(8):
    enemies.add(Reaper())
for _ in range(3):
    candies.add(Candy())

# --- Game Variables ---
score = 0
game_over = False
fire = False

def draw_text(text, size, color, y):
    t = pygame.font.SysFont("chiller", size, bold=True).render(text, True, color)
    rect = t.get_rect(center=(WIDTH / 2, y))
    screen.blit(t, rect)

# --- Game Loop ---
while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if not game_over and event.key == pygame.K_SPACE:
                bullets.add(Bullet(player.rect.center, player.angle))
            if event.key == pygame.K_r:
                # restart
                player = Player()
                player_group = pygame.sprite.Group(player)
                bullets.empty()
                enemies.empty()
                candies.empty()
                for _ in range(8):
                    enemies.add(Reaper())
                for _ in range(3):
                    candies.add(Candy())
                score = 0
                game_over = False
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 3:
                # restart
                player = Player()
                player_group = pygame.sprite.Group(player)
                bullets.empty()
                enemies.empty()
                candies.empty()
                for _ in range(8):
                    enemies.add(Reaper())
                for _ in range(3):
                    candies.add(Candy())
                score = 0
                game_over = False


    if not game_over:
        # --- Controls ---
        # Player movement
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player.rotate(-1)
        if keys[pygame.K_RIGHT]:
            player.rotate(1)
        if keys[pygame.K_UP]:
            player.accelerate()

        if event.type == pygame.JOYAXISMOTION:
            if event.axis is 2:
                HandleRotation(event.value)
            if event.axis is 1:
                if event.value < 0:
                    player.accelerate()
                if event.value > 0:
                    player.accelerate()
            #print(event)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button is 5 and fire == False:
                bullets.add(Bullet(player.rect.center, player.angle))
                fire = True
        if event.type == pygame.JOYBUTTONUP:
            if event.button is 5:
                fire = False



        # --- Update ---
        player_group.update()
        bullets.update()
        enemies.update()

        # --- Collisions ---
        # Bullets hit enemies
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        score += len(hits) * 10
        for _ in range(len(hits)):
            enemies.add(Reaper())
            

        # Player collides with enemies
        if pygame.sprite.spritecollideany(player, enemies):
            player.lives -= 1
            if player.lives <= 0:
                game_over = True
            else:
                player.rect.center = (WIDTH / 2, HEIGHT / 2)
                player.velocity = pygame.Vector2(0, 0)

        # Player collects candy
        candy_hits = pygame.sprite.spritecollide(player, candies, True)
        score += len(candy_hits) * 5
        for _ in range(len(candy_hits)):
            candies.add(Candy())

        # --- Draw ---
        screen.blit(background_img, (0, 0))  # 🌾 Cornfield background
        candies.draw(screen)
        enemies.draw(screen)
        bullets.draw(screen)
        player_group.draw(screen)

        # HUD
        draw_text(f"Soul Count: {score}", 36, (255, 120, 0), 30)
        draw_text(f"Lives: {player.lives}", 32, (255, 200, 0), 70)

    else:
        screen.blit(background_img, (0, 0))
        draw_text("GAME OVER", 80, (255, 50, 50), HEIGHT / 2 - 40)
        draw_text(f"Final Soul Count: {score}", 50, (255, 150, 0), HEIGHT / 2 + 10)
        draw_text("Press R to Restart", 40, (255, 255, 255), HEIGHT / 2 + 80)

    pygame.display.flip()
