#make a pygame window with a blue background
import pygame
import sys
from pygame.sprite import Sprite
import random



 
class Game(Sprite):
	""" a class the creates a window with a blue screen """
	def __init__(self):
		pygame.init()
		super().__init__()


		#--------------------------------------------------------------------------------------------
		#screen size, color, caption
		self.screen = pygame.display.set_mode((1200,800))	#create attribute to hold display settings
		self.bg_color = (0,0,0)							#create attribute to hold RGB color (blue)
		pygame.display.set_caption("Blue Screen")
		#--------------------------------------------------------------------------------------------


		#--------------------------------------------------------------------------------------------
		#tank drawing
		self.screen_rect = self.screen.get_rect()				#get the screen rect dim
		self.image = pygame.image.load('images/tank.bmp')		#load the image from directory
		self.rect = self.image.get_rect()						#get the image rect dim
		self.rect.center = self.screen_rect.center				#store the screens center x/y coord 

		self.x = float(self.rect.x)
		self.y = float(self.rect.y)

		#tank movement
		self.tank_moving_left = False
		self.tank_moving_right = False
		self.tank_moving_up = False
		self.tank_moving_down = False
		self.tank_speed = 0.5														#tank pixels
		self.direction_right = self.image										#holds right image
		self.direction_left = pygame.transform.flip(self.image, True, False)	#holds left image
		#--------------------------------------------------------------------------------------------


		#--------------------------------------------------------------------------------------------
		#healthbar
		self.health = 100
		self.visable = True
		#--------------------------------------------------------------------------------------------


		#--------------------------------------------------------------------------------------------
		#bullet
		self.bullets = pygame.sprite.Group()
		self.current_direction = self.direction_right
		#--------------------------------------------------------------------------------------------

		#--------------------------------------------------------------------------------------------
		#asteroids
		self.asteroids = pygame.sprite.Group()
		self.next_object_time = 0
		self.time_interval = 250
		#self._create_asteroids()
		#--------------------------------------------------------------------------------------------

	def _create_asteroids(self):
		""" create the asteroid shower """
		#create a asteroid
		number_of_aliens = 1
		for asteroid_num in range(number_of_aliens):
			self._create_asteroid()
			print(len(self.asteroids))




	def _create_asteroid(self):
		asteroid = Asteroid(self)
		if asteroid.x <= 0:
			asteroid.direction = 1
		elif asteroid.x >= 1160:
			asteroid.direction = -1
		self.asteroids.add(asteroid)

		

	def move(self):
		""" move tnak tank_speed based on direction of movement (key pressed)
			also detect collision """ 
		if self.tank_moving_right and self.rect.right < self.screen_rect.right:
			self.x += self.tank_speed
			self.rect.x = self.x
		if self.tank_moving_left and self.rect.left > self.screen_rect.left:
			self.x -= self.tank_speed
			self.rect.x = self.x
		if self.tank_moving_down and self.rect.bottom < self.screen_rect.bottom:
			self.y += self.tank_speed
			self.rect.y = self.y
		if self.tank_moving_up and self.rect.top > self.screen_rect.top:
			self.y -= self.tank_speed
			self.rect.y = self.y

	def draw_healthbar(self):
		pygame.draw.rect(self.screen, (255,0,0), (self.rect.x, self.rect.y - 20, 100, 10))
		pygame.draw.rect(self.screen, (0,255,0), (self.rect.x, self.rect.y - 20, 100 - (100 - self.health), 10))

	def blitme(self):
		""" draw the image of the tank """
		self.screen.blit(self.image, self.rect)

	def tank_asteroid_collision(self):
		#get rid of asteroids that collide with tank
		for asteroid in self.asteroids.copy():
			if pygame.Rect.colliderect(self.rect, asteroid.rect):
				if self.health > 0:
					self.health -= 25  
					self.asteroids.remove(asteroid)
					print(self.health)


	def _update_screen(self):
		""" update screen """
		self.screen.fill(self.bg_color)
		self.blitme()

		for bullet in self.bullets.sprites():
			self.bullets.draw(self.screen)
			#print(bullet.rect)

		collisions = pygame.sprite.groupcollide(self.bullets, self.asteroids, True, True)

		self.asteroids.draw(self.screen)
		self.draw_healthbar()
		pygame.display.flip()

	def _check_KEYDOWN(self, event):
		""" when key is press either quit, or move direction of arrow pressed and flip image """
		if event.key == pygame.K_q:
			sys.exit()
		elif event.key == pygame.K_RIGHT:
			self.tank_moving_right = True
			self.image = self.direction_right
			self.current_direction = self.direction_right
		elif event.key == pygame.K_LEFT:
			self.tank_moving_left = True
			self.image = self.direction_left
			self.current_direction = self.direction_left
		elif event.key == pygame.K_UP:
			self.tank_moving_up = True
		elif event.key == pygame.K_DOWN:
			self.tank_moving_down = True
		elif event.key == pygame.K_SPACE:
			self._fire_bullet()	
	

	def _check_KEYUP(self, event):
		""" when key is let go stop moving """
		if event.key == pygame.K_RIGHT:
			self.tank_moving_right = False
		elif event.key == pygame.K_LEFT:
			self.tank_moving_left = False
		elif event.key == pygame.K_UP:
			self.tank_moving_up = False
		elif event.key == pygame.K_DOWN:
			self.tank_moving_down = False

	def _fire_bullet(self):
		""" create a bullet and add it to the bullets group """
		if self.current_direction == self.direction_left:
			#create new bullet and set bullet path
			new_bullet = Bullet(self)
			new_bullet.bullet_shootRight = False
			new_bullet.bullet_shootLeft = True

			#change direction of bullet starting point
			new_bullet.x -= 100

			#add bullet to sprite list
			self.bullets.add(new_bullet)

		elif self.current_direction == self.direction_right:
			#create new bullet and set bullet path
			new_bullet = Bullet(self)
			new_bullet.bullet_shootRight = True
			new_bullet.bullet_shootLeft = False
			
			#add bullet to sprite list
			self.bullets.add(new_bullet)	


	def run_game(self):
		""" loops the game/ updates screen/ checks for key clicks"""
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					self._check_KEYDOWN(event)
				elif event.type == pygame.KEYUP:
					self._check_KEYUP(event)

			self.move()
			self.bullets.update()
			self.tank_asteroid_collision()

			#after certain number of time create a asteroid
			current_time = pygame.time.get_ticks()
			if current_time > self.next_object_time:
				self.next_object_time += self.time_interval
				self._create_asteroids()

			self.asteroids.update()

			#get rid of asteroids that have disapeared
			for asteroid in self.asteroids.copy():
				if asteroid.x >= 1200 or asteroid.x <= 0:
					self.asteroids.remove(asteroid)
			
			#get rid of bullets that have disapeared
			for bullet in self.bullets.copy():
				if bullet.rect.left >= 1200 or bullet.rect.right <= 0:
					self.bullets.remove(bullet)

			
			self._update_screen()




class Bullet(Sprite):
	""" A class to manage bullets fired from the ship """
	def __init__(self, game):
		""" create a bullet object at the ships current position """
		super().__init__()
		self.screen = game.screen
		self.bullet_speed = 2.0
		self.bullet_width = 20
		self.bullet_height = 5
		self.bullet_color = (0, 200, 200)
		self.bullet_shootRight = False
		self.bullet_shootLeft = False



		self.image = pygame.Surface((self.bullet_width, self.bullet_height))
		self.image.fill(self.bullet_color)
		self.rect = self.image.get_rect()
		self.rect.midright = game.rect.midright
		self.rect.y -= 5 #the tanks barrel is 5 pixels above center
		self.rect.x += 15
	

		#store the bullets position as a decimal value
		self.y = float(self.rect.y)
		self.x = float(self.rect.x)

	def update(self):
		""" move the bullet up the screen """
		#update the decimal position of the bullet.
		if self.bullet_shootRight:
			self.x += self.bullet_speed
			self.rect.x = self.x
		elif self.bullet_shootLeft:
			self.x -= self.bullet_speed
			self.rect.x = self.x


class Asteroid(Sprite):
	""" a class that represents a single asteroid """
	def __init__(self, game):
		""" initialize the asteroid and set its starting position """
		super().__init__()
		self.screen = game.screen
		self.speed = 0.1
		self.direction = 1

		#load the asteroid image onto the screen
		self.image = pygame.image.load('images/asteroid.bmp')
		self.rect = self.image.get_rect()

		#start each new asteroid in a random part just outside the map on either the left or right
		self.rect.x = random.randint(*random.choice([(0, 0), (1160, 1160)]))
		self.rect.y = random.randint(0, 760)

		#store the asteroid's exact horizontal positon
		self.x = float(self.rect.x)
		self.y = float(self.rect.y)


	def update(self):
		""" move the asteroid to the right or left """
		self.x += self.speed * self.direction
		self.rect.x = self.x




if __name__ == '__main__':
	a = Game()
	a.run_game()
