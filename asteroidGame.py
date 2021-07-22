#make a pygame window with a blue background
import pygame
import sys
from pygame.sprite import Sprite
import random
from time import sleep
import pygame.font


 
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
		self.background_image = pygame.image.load("images/space.bmp")

		#--------------------------------------------------------------------------------------------


		#--------------------------------------------------------------------------------------------
		#tank drawing
		self.screen_rect = self.screen.get_rect()				#get the screen rect dim
		self.image = pygame.image.load('images/tank.gif')		#load the image from directory
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
		#UI
		self.health = 100
		self.visable = True
		self.sb = Scoreboard(self)
		self.level = 1
		self.level_increment = 100
		#--------------------------------------------------------------------------------------------


		#--------------------------------------------------------------------------------------------
		#bullet
		self.bullets = pygame.sprite.Group()
		self.current_direction = self.direction_right
		#--------------------------------------------------------------------------------------------

		#--------------------------------------------------------------------------------------------
		#asteroids
		self.asteroids = pygame.sprite.Group()
		self.next_object_time = 1
		self.time_interval = 250
		self.current_time = 0
		#self._create_asteroids()
		#--------------------------------------------------------------------------------------------


		#--------------------------------------------------------------------------------------------
		#button
		self.game_active = False
		self.play_button = Button(self, "Play")
		#--------------------------------------------------------------------------------------------


	def _create_asteroids(self):
		""" create the asteroid shower """
		#create a asteroid
		number_of_aliens = 1
		for asteroid_num in range(number_of_aliens):
			self._create_asteroid()



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
		if self.tank_moving_up and (self.rect.top - 30) > self.screen_rect.top:
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
				if self.health > 25:
					self.health -= 25  
					self.asteroids.remove(asteroid)
					print(self.health)
				else:
					self._tank_death()
					self.sb.reset_score()
					self.game_active = False
					pygame.mouse.set_visible(True)					



	def _update_screen(self):
		""" update screen """
		self.screen.fill(self.bg_color)
		self.screen.blit(self.background_image, [0, 0])
		self.blitme()
		for bullet in self.bullets.sprites():
			self.bullets.draw(self.screen)
		collisions = pygame.sprite.groupcollide(self.bullets, self.asteroids, True, True)
		if collisions:
			for asteroids in collisions.values():
				self.sb.score += 10 * len(asteroids)
			self.sb.prep_score()
			self.sb.check_high_score()
			if self.sb.score > self.level_increment:
				self.level_increment += 100
				self.sb.level += 1
				self.sb.prep_level()
		#draw healthbar if game active
		if self.game_active:
			self.draw_healthbar()
			self.asteroids.draw(self.screen)

		#draw the play button and other buttons if game is paused
		if not self.game_active:
			self.play_button.draw_button()

		self.sb.show_score()

		pygame.display.flip()



	def _tank_death(self):
		sleep(0.5)
		self.bullets.empty()
		self.asteroids.empty()
		self.center_ship()
		self.health = 100		



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



	def center_ship(self):
		""" centers the ship in middle of screen """
		self.rect.center = self.screen_rect.center
		self.x = float(self.rect.x)
		self.y = float(self.rect.y)



	def _update_tank(self):
		""" move tank or quit game based on keypress """
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				self._check_KEYDOWN(event)
			elif event.type == pygame.KEYUP:
				self._check_KEYUP(event)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos()
				self._check_play_button(mouse_pos)



	def _check_play_button(self, mouse_pos):
		button_clicked = self.play_button.rect.collidepoint(mouse_pos)
		if button_clicked and self.play_button.rect.collidepoint(mouse_pos):
			self.game_active = True
			pygame.mouse.set_visible(False)	

			self.next_object_time = pygame.time.get_ticks() + self.time_interval



	def _update_asteroids(self):
		""" afer 'x' milliseconds create a new asteroid """
		self.current_time = pygame.time.get_ticks()
		if self.current_time > self.next_object_time:
			self.next_object_time += self.time_interval
			self._create_asteroids()		



	def run_game(self):
		""" loops the game/ updates screen/ checks for key clicks"""
		while True:
			self._update_tank()
			if self.game_active:
				self.move()
				self.bullets.update()
				self.tank_asteroid_collision()
				#after certain number of time create a asteroid
				self._update_asteroids()
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
		self.image = pygame.image.load('images/asteroid.gif')
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

		self.y += (self.speed / 3) * self.direction
		self.rect.y = self.y






class Button:

	def __init__(self, game, msg):
		""" Initialize button """
		self.screen = game.screen
		self.screen_rect = self.screen.get_rect()

		#set the dimensions and properties of the button
		self.width, self.height = 200, 50
		self.button_color = (0, 255, 0)
		self.text_color = (255, 255, 255)
		self.font = pygame.font.SysFont(None, 48)

		#Build the button's rect object and center it.
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.center = self.screen_rect.center

		self._prep_msg(msg)



	def _prep_msg(self, msg):
		""" Turn msg into a rendered image and center text on the button """
		self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
		self.msg_image_rect = self.msg_image.get_rect()
		self.msg_image_rect.center = self.rect.center



	def draw_button(self):
		""" draw blank button then draw message """
		self.screen.fill(self.button_color, self.rect)
		self.screen.blit(self.msg_image, self.msg_image_rect)




class Scoreboard:
	""" A class to report scoring information """

	def __init__(self, game):
		""" initialize scorekeeping attributes """
		self.screen = game.screen
		self.screen_rect = self.screen.get_rect()
		self.score = 0
		self.highscore = 0
		self.level = 1

		# Font settings for scoring information
		self.text_color = (30, 30, 30)
		self.font = pygame.font.SysFont(None, 48)

		
		self.prep_score()
		self.prep_highscore()
		self.prep_level()
		self.prep_bar()



	def reset_score(self):
		self.score = 0
		self.level = 1

		self.prep_score()
		self.prep_level()


	def prep_bar(self):
		""" create UI on top of screen """
		line = "____________________________________________________________"
		self.line_image = self.font.render(line, True, (255, 255, 255), (255, 255, 255))

		#position the line on the top of screen
		self.line_rect = self.line_image.get_rect()
		self.line_rect.top = self.screen_rect.top
		self.line_rect.centerx = self.screen_rect.centerx

	def prep_level(self):
		""" Turn the level into a rendered image """
		level_str = f"Level: {str(self.level)}"
		self.level_image = self.font.render(level_str, True, self.text_color, (255, 255, 255))

		#position the level on left side of screen
		self.level_rect = self.level_image.get_rect()
		self.level_rect.left = self.screen_rect.left
		self.level_rect.top = self.screen_rect.top


	def prep_highscore(self):
		""" Turn the high score into a rendered image. """
		high_score = round(self.highscore, -1)
		high_score_str = "High Score: {:,}".format(high_score)
		self.high_score_image = self.font.render(high_score_str, True, self.text_color, (255, 255, 255))

		#center the high score at the top of the screen
		self.high_score_rect = self.high_score_image.get_rect()
		self.high_score_rect.centerx = self.screen_rect.centerx
		self.high_score_rect.top = (self.score_rect.top - 3)



	def check_high_score(self):
		""" check to see if there's a new high score """
		if self.score > self.highscore:
			self.highscore = self.score
			self.prep_highscore()


	def prep_score(self):
		""" Turn the score into a renered image """
		rounded_score = round(self.score, -1)

		score_str = "Score: {:,}".format(rounded_score)
		self.score_image = self.font.render(score_str, True, self.text_color, (255, 255, 255))

		#Display the score at the top of the screen
		self.score_rect = self.score_image.get_rect()
		self.score_rect.right = self.screen_rect.right
		self.score_rect.top = 0

	def show_score(self):
		""" draw the score to the screen """
		self.screen.blit(self.line_image, self.level_rect)
		self.screen.blit(self.score_image, self.score_rect)
		self.screen.blit(self.high_score_image, self.high_score_rect)
		self.screen.blit(self.level_image, self.level_rect)


if __name__ == '__main__':
	a = Game()
	a.run_game()
