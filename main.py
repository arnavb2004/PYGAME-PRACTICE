import random
import pygame

SCREEN = WIDTH, HEIGHT = (600, 200)

class Ground():
	def __init__(self):
		self.image = pygame.image.load('Assets/ground.png')
		self.rect = self.image.get_rect()

		self.width = self.image.get_width()
		self.x1 = 0
		self.x2 = self.width
		self.y = 150

	def update(self, speed):
		self.x1 -= speed
		self.x2 -= speed

		if self.x1 <= -self.width:
			self.x1 = self.width

		if self.x2 <= -self.width:
			self.x2 = self.width

	def draw(self, win):
		win.blit(self.image, (self.x1, self.y))
		win.blit(self.image, (self.x2, self.y))


class Dino():
	def __init__(self, x, y):
		self.x, self.base = x, y

		self.run_list = []
		self.duck_list = []

		for i in range(1, 4):
			img = pygame.image.load(f'Assets/Dino/{i}.png')
			img = pygame.transform.scale(img, (52, 58))
			self.run_list.append(img)

		for i in range(4, 6):
			img = pygame.image.load(f'Assets/Dino/{i}.png')
			img = pygame.transform.scale(img, (70, 38))
			self.duck_list.append(img)

		self.dead_image = pygame.image.load(f'Assets/Dino/8.png')
		self.dead_image = pygame.transform.scale(self.dead_image, (52,58))

		self.reset()

		self.vel = 0
		self.gravity = 1
		self.jumpHeight = 15
		self.isJumping = False

	def reset(self):
		self.index = 0
		self.image = self.run_list[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.bottom = self.base

		self.alive = True
		self.counter = 0

	def update(self, jump, duck):
		if self.alive:
			if not self.isJumping and jump:
				self.vel = -self.jumpHeight
				self.isJumping = True

			self.vel += self.gravity
			if self.vel >= self.jumpHeight:
				self.vel = self.jumpHeight

			self.rect.y += self.vel
			if self.rect.bottom > self.base:
				self.rect.bottom = self.base
				self.isJumping = False

			if duck:
				self.counter += 1
				if self.counter >= 6:
					self.index = (self.index + 1) % len(self.duck_list)
					self.image = self.duck_list[self.index]
					self.rect = self.image.get_rect()
					self.rect.x = self.x
					self.rect.bottom = self.base
					self.counter = 0

			elif self.isJumping:
				self.index = 0
				self.counter = 0
				self.image = self.run_list[self.index]
			else:
				self.counter += 1
				if self.counter >= 4:
					self.index = (self.index + 1) % len(self.run_list)
					self.image = self.run_list[self.index]
					self.rect = self.image.get_rect()
					self.rect.x = self.x
					self.rect.bottom = self.base
					self.counter = 0

			self.mask = pygame.mask.from_surface(self.image)

		else:
			self.image = self.dead_image

	def draw(self, win):
		win.blit(self.image, self.rect)

class Cactus(pygame.sprite.Sprite):
	def __init__(self, type):
		super(Cactus, self).__init__()

		self.image_list = []
		for i in range(5):
			scale = 0.65
			img = pygame.image.load(f'Assets/Cactus/{i+1}.png')
			w, h = img.get_size()
			img = pygame.transform.scale(img, (int(w*scale), int(h*scale)))
			self.image_list.append(img)

		self.image = self.image_list[type-1]
		self.rect = self.image.get_rect()
		self.rect.x = WIDTH + 10
		self.rect.bottom = 165

	def update(self, speed, dino):
		if dino.alive:
			self.rect.x -= speed
			if self.rect.right <= 0:
				self.kill()

			self.mask = pygame.mask.from_surface(self.image)

	def draw(self, win):
		win.blit(self.image, self.rect)

class Bird(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(Bird, self).__init__()

		self.image_list = []
		for i in range(2):
			scale = 0.65
			img = pygame.image.load(f'Assets/Bird/{i+1}.png')
			w, h = img.get_size()
			img = pygame.transform.scale(img, (int(w*scale), int(h*scale)))
			self.image_list.append(img)

		self.index = 0
		self.image = self.image_list[self.index]
		self.rect = self.image.get_rect(center=(x, y))

		self.counter = 0

	def update(self, speed, dino):
		if dino.alive:
			self.rect.x -= speed
			if self.rect.right <= 0:
				self.kill()

			self.counter += 1
			if self.counter >= 6:
				self.index = (self.index + 1) % len(self.image_list)
				self.image = self.image_list[self.index]
				self.counter = 0

			self.mask = pygame.mask.from_surface(self.image)

	def draw(self, win):
		win.blit(self.image, self.rect)
		
pygame.init()
win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)

clock = pygame.time.Clock()
FPS = 60

WHITE = (225, 225, 225)
BLACK = (0, 0, 0)
GRAY = (32, 33, 36)

start_img = pygame.image.load('Assets/start_img.png')
start_img = pygame.transform.scale(start_img, (60, 64))

game_over_img = pygame.image.load('Assets/game_over.png')
game_over_img = pygame.transform.scale(game_over_img, (200, 36))

replay_img = pygame.image.load('Assets/replay.png')
replay_img = pygame.transform.scale(replay_img, (40, 36))
replay_rect = replay_img.get_rect()
replay_rect.x = WIDTH // 2 - 20
replay_rect.y = 100

numbers_img = pygame.image.load('Assets/numbers.png')
numbers_img = pygame.transform.scale(numbers_img, (120, 12))

jump_fx = pygame.mixer.Sound('Sounds/jump.wav')
die_fx = pygame.mixer.Sound('Sounds/die.wav')
checkpoint_fx = pygame.mixer.Sound('Sounds/checkPoint.wav')

ground = Ground()
dino = Dino(50, 160)

cactus_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

def reset():
    global counter, SPEED, score, high_score, last_score_checkpoint

    if score and score >= high_score:
        high_score = score

    counter = 0
    SPEED = 5
    score = 0
    last_score_checkpoint = 0

    cactus_group.empty()
    bird_group.empty()

    dino.reset()

DAYMODE = True

counter = 0
enemy_time = 100

SPEED = 5
jump = False
duck = False

score = 0
high_score = 0
last_score_checkpoint = 0

start_page = True
mouse_pos = (-1, -1)

running = True
while running:
    jump = False
    if score % 50 == 0 and score != last_score_checkpoint:
        DAYMODE = not DAYMODE
        last_score_checkpoint = score
    if DAYMODE:
        win.fill(WHITE)
    else:
        win.fill(GRAY)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_SPACE:
                if start_page:
                    start_page = False
                elif dino.alive:
                    jump = True
                    jump_fx.play()
                else:
                    reset()
            if event.key == pygame.K_UP:
                jump = True
                jump_fx.play()

            if event.key == pygame.K_DOWN:
                duck = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                jump = False
            if event.key == pygame.K_DOWN:
                duck = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = (-1, -1)
    if start_page:
        win.blit(start_img, (50, 100))
    else:
        if dino.alive:
            counter += 1
            if counter % int(enemy_time) == 0:
                if random.randint(1, 10) == 5:
                    y = random.choice([85, 130])
                    bird = Bird(WIDTH, y)
                    bird_group.add(bird)
                else:
                    type = random.randint(1, 4)
                    cactus = Cactus(type)
                    cactus_group.add(cactus)
            if counter % 100 == 0:
                SPEED += 0.1
                enemy_time -= 0.5
            if counter % 5 == 0:
                score += 1
            if score and score % 100 == 0:
                checkpoint_fx.play()
            for cactus in cactus_group:
                if pygame.sprite.collide_mask(dino, cactus):
                    SPEED = 0
                    dino.alive = False
                    die_fx.play()

            for bird in bird_group:
                if pygame.sprite.collide_mask(dino, bird):
                    SPEED = 0
                    dino.alive = False
                    die_fx.play()
        ground.update(SPEED)
        ground.draw(win)
        cactus_group.update(SPEED, dino)
        cactus_group.draw(win)
        bird_group.update(SPEED-1, dino)
        bird_group.draw(win)
        dino.update(jump, duck)
        dino.draw(win)
        string_score = str(score).zfill(5)
        for i, num in enumerate(string_score):
            win.blit(numbers_img, (520+11*i, 10), (10*int(num), 0, 10, 12))

        if high_score:
            win.blit(numbers_img, (425, 10), (100, 0, 20, 12))
            string_score = f'{high_score}'.zfill(5)
            for i, num in enumerate(string_score):
                win.blit(numbers_img, (455+11*i, 10), (10*int(num), 0, 10, 12))

        if not dino.alive:
            win.blit(game_over_img, (WIDTH//2-100, 55))
            win.blit(replay_img, replay_rect)
            if replay_rect.collidepoint(mouse_pos):
                reset()
    pygame.draw.rect(win, WHITE, (0, 0, WIDTH, HEIGHT), 4)
    clock.tick(FPS)
    pygame.display.update()
pygame.quit()