import pygame #imports
from classes.player import Player
from classes.box import Box,Sky,EndPoint,Invisible
from classes.enemies import Slime, Bat

pygame.init()
pygame.mixer.init()
pygame.font.init()

WIDTH = 1280
HEIGHT = 720
BACKGROUND = (69,127,187) #blue

done = False
player = None
boxes = []
enemies = []
level = 0 #indicates what level to load
levels = ["Level1.txt","Level2.txt","Level3.txt"] #prebuilt game levels
gameTime = 0 #game timer (miliseconds)
score = 0

bg = pygame.image.load("menuImages/catlegendsbackground.png")
font0 = pygame.font.SysFont('freesanbold.ttf', 60)
font1 = pygame.font.SysFont('freesanbold.ttf', 50)
font2 = pygame.font.SysFont('freesanbold.ttf', 40)

def createMap(fileName,player):
	global boxes,enemies
	boxes = [] #resets boxes and enemies lists
	enemies = []
	print("creating map.....")
	file = open(fileName, "r")
	map = []
	
	for line in file:#converts text map into a 2d array of characters
		map.append(list(line))
	file.close()
	
	for column in range(len(map[0])): #appends through the array and places the tilesd
		for row in range(len(map)-1):
			if map[row][column] == "=":#grass
				boxes.append(Box(column*75, row*75,0))
			elif map[row][column] == "-":#dirt
				boxes.append(Box(column*75, row*75,1))
			elif map[row][column] == ".":#sky
				boxes.append(Sky(column*75, row*75))
			elif map[row][column] == "^":#slime
				boxes.append(Sky(column*75, row*75))
				enemies.append(Slime((column*75)+16, (row*75)+29)) #+29 for height correction
			elif map[row][column] == ">":#bat
				boxes.append(Sky(column*75, row*75))
				enemies.append(Bat((column*75+5), (row*75)+5)) 
			elif map[row][column] == "#":#END
				boxes.append(Sky(column*75, row*75))
				boxes.append(EndPoint(column*75, 380))#flag goes from base to top
			elif map[row][column] == "@":#player
				boxes.append(Sky(column*75, row*75))
				player.rect.x,player.rect.y = column*75,row*75+20
			elif map[row][column] == "X":#invisible wall
				boxes.append(Invisible(column*75, row*75))

def LoadNextLevel(player): #loads future levels
	global level
	print("starting next level")
	pygame.display.flip()
	player.attacks = []
	player.xVel,player.yVel,player.grounded = 0.00001,0,True #resets player values, v != 0 to reset cameraoffset
	level += 1 #increments level by 1
	if level >= len(levels):
		return True
	createMap(levels[level],player)
	return False

def gameLoop(dt,surface,screen,clock):	
		global gameTime,done,score

		pygame.event.pump()
		for events in pygame.event.get():#quit game event
			if events.type == pygame.QUIT:
				done = True
				pygame.quit() 
			if player.dead == True and events.type == pygame.KEYDOWN: #redirect to deathloop
				return "gameOver"
	#----------------- GAME LOGIC START--------------------------------
		gameTime += clock.get_time()
		#onscreen text statistics
		timeText,scoreText,ammoText,moneyText = font1.render(str(gameTime//1000),True,(0,255,0)),font2.render(str(f"score:{score}"),True,(255,255,0)),font2.render(f"ammo:{player.ammo}",True,(255,255,0)),font2.render(f"coins:{player.money}",True,(255,255,0))
		timeRect,scoreRect,ammoRect,moneyRect = timeText.get_rect(),scoreText.get_rect(),ammoText.get_rect(),moneyText.get_rect()
		timeRect.right,timeRect.y = WIDTH-10,10
		scoreRect.x,scoreRect.y = 15,75
		ammoRect.x,ammoRect.y = 15,45
		moneyRect.x,moneyRect.y = 15,105
	
		surface.fill(BACKGROUND)
		for box in boxes:
			box.draw(surface) #draws background so it doesnt cover up projectile arc

		player.update(dt,clock,surface)
		if player.collisions(boxes,dt):#if collision with end flag loads next level
			print("flag collision?")
			if LoadNextLevel(player):
				return "gameOver" #player has reached end of levels

		for enemy in enemies: #interactions with all enemies
			enemy.update(dt,player) #updates enemies for movement/calculations
			if enemy.type == "bat":
				enemy.boxCollisions(dt,boxes)#collide with the terrain
			if enemy.checkCollisions(player.rect) == True: #collisions with player
				if player.damagetime >=1300: 
					player.damagetime = 0
					player.health = player.health-1 #player takes damage
					print(f"player health:{player.health}")
					if player.health == 0: # player dies at 0 health
						player.dead = True
						#"click a button to exit"
						#check for any button press
						#load death menu, show score & time,"do you want to update leaderboard", redirect to menu page
					if enemy.type == "bat": 
						enemies.remove(enemy)
						break #enemies like bats die
			for attack in player.getAttacks(): #collisions with player attacks
				if enemy.checkCollisions(attack.rect) == True: #player kills an enemy. adds 100 to score
					enemies.remove(enemy)
					score += 100
					if attack.type == "projectile":
						player.removeAttack(attack)

		for attack in player.getAttacks():#updates player attack for movement/removal
			if attack.type == "projectile":
				update = attack.update(dt,boxes) #player projectile attack
			else:
				update = attack.update(clock,player.rect,player.right, dt) #player slash attack
			if update == "remove":
				player.removeAttack(attack)

		if player.dead == True: #gameover screen - redirects to deathLoop()
			GameOver = font1.render("Game Over",True,(255,255,255))
			GameOverRect = GameOver.get_rect()
			GameOverRect.centerx,GameOverRect.centery = WIDTH//2,HEIGHT//3
			surface.blit(GameOver,GameOverRect)

			inputText = font2.render("Press any button to continue",True,(255,255,255))
			inputTextRect = inputText.get_rect()
			inputTextRect.centerx,inputTextRect.top = WIDTH//2,GameOverRect.bottom + 5
			surface.blit(inputText,inputTextRect)

	#----------------- DRAWING START-----------------------------------
		for enemy in enemies:
			enemy.draw(surface)

		player.draw(surface)

		for attack in player.getAttacks():
			attack.draw(surface)
		
		surface.blit(timeText,timeRect) #time top right
		surface.blit(scoreText,scoreRect) #score top left
		surface.blit(ammoText,ammoRect) #ammo top left
		surface.blit(moneyText,moneyRect) #money top left

		scaledSurface = pygame.transform.scale(surface, (1280, 720)) #screen scaling
		screen.blit(scaledSurface, (0, 0))
		return "game"

	#------------------ END OF GAME LOOP --------------------------------

def shopLoop(screen):
	pygame.event.pump()
	#shop pages, buttons, coin counter

def menuLoop(surface,screen,buttons):
	global done,level,levels,player
	pygame.event.pump()
	
	#check for mouse button click
	clicked = None
	for events in pygame.event.get():
		if events.type == pygame.QUIT:
			pygame.quit()
		if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
			pos = pygame.mouse.get_pos()
			for b in buttons:
				if buttons[b][1].collidepoint(pos) == True:
					print(b + " was clicked")
					clicked = b

	if clicked == "start": #MAKE THESE LINK TO THEIR FUNCTIONS
		levels = ["Level1.txt","Level2.txt","Level3.txt"]
		level = 0
		player = Player(100,100)
		createMap(levels[level],player)
		return "game"
	elif clicked == "loadTxt":
		print("loading custom map")
		#txt = input("map txt name"),createmap(txt), levels = [txt,bossfight], loop = "game"
		#levels = ["customMap.txt","BossLevel.txt"]
		level = 0
		player = Player(100, 100) 
		createMap(levels[level],player)
		return "game"	
	elif clicked == "leaderboard":
		print("loading leaderboard") #load a leaderboard page
		#return "leaderboard"
	elif clicked == "exit":
		print("quitting game")
		done = True
		pygame.quit()		
	#------------------ DRAWING SURFACE ---------------------
	surface.blit(bg,(0,0))
	for b in buttons:
		surface.blit(buttons[b][0],buttons[b][1]) #blits to surface (button image,button rect)
	
	scaledSurface = pygame.transform.scale(surface, (1280, 720)) #screen scaling
	screen.blit(scaledSurface, (0, 0))
	return "menu"
	#------------------ END OF MENU LOOP ---------------------

def deathLoop(screen,surface,buttons):
	global done
	pygame.event.pump()
	clicked = None
	for events in pygame.event.get():
		if events.type == pygame.QUIT:
			pygame.quit()
		if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
			pos = pygame.mouse.get_pos()
			for b in buttons:
				if buttons[b][1].collidepoint(pos) == True:
					print(b + " was clicked")
					clicked = b
	if clicked == "title": #MAKE THESE LINK TO THEIR FUNCTIONS
		return "menu"	
	elif clicked == "leaderboard":
		print("loading leaderboard") #load a leaderboard page
		#return "leaderboard"

	textColour = (255,255,255)

	GameOver = font0.render("Game Over!",True,textColour)
	GameOverRect = GameOver.get_rect()
	GameOverRect.centerx,GameOverRect.centery = WIDTH//2,HEIGHT//4+50

	scoreText = font2.render(f"Total Score: {score + player.money*10}",True,textColour)
	scoreRect = scoreText.get_rect()
	scoreRect.x,scoreRect.centery = WIDTH//3,HEIGHT//3+50

	time = font2.render(f"Time: {gameTime//1000}",True,textColour)
	timeRect = time.get_rect()
	timeRect.x,timeRect.centery = WIDTH//3,HEIGHT//3 +100

	levelText = font2.render(f"Level: {level+1}",True,textColour)
	levelRect = levelText.get_rect()
	levelRect.x,levelRect.centery = WIDTH//3,HEIGHT//3 +150

	surface.fill(BACKGROUND)
	for b in buttons:
		surface.blit(buttons[b][0],buttons[b][1]) #blits to surface (button image,button rect)
	
	surface.blit(GameOver,GameOverRect)
	surface.blit(scoreText,scoreRect)
	surface.blit(time,timeRect)
	surface.blit(levelText,levelRect)

	scaledSurface = pygame.transform.scale(surface, (1280, 720)) #screen scaling
	screen.blit(scaledSurface, (0, 0))
	return "gameOver"
	#death screen, your score, time taken, update leaderboard

#-------------------- MAIN LOOP -----------------------
def main():#initial game initialisation
	global player
	print("starting game")
	surface = pygame.Surface((WIDTH, HEIGHT))
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	clock = pygame.time.Clock()
	dt = 0
	player = Player(100, 100) 
	loop = "menu" #switches between menus and game
	menubuttons = { 
		"start":[pygame.image.load("menuImages/PLAYbutton.png"),pygame.Rect(160,250,250,100)],
		"loadTxt":[pygame.image.load("menuImages/LOADbutton.png"),pygame.Rect(160,400,250,100)],
		"leaderboard":[pygame.image.load("menuImages/SCOREbutton.png"),pygame.Rect(870,250,250,100)],
		"exit":[pygame.image.load("menuImages/EXITbutton.png"),pygame.Rect(870,400,250,100)]
	}

	deathbuttons = {
		#"title":[pygame.image.load("menuImage/TITLEbutton.png")]
		"title":[pygame.image.load("menuImages/MENUbutton.png"),pygame.Rect(300,450,250,100)],
		"leaderboard":[pygame.image.load("menuImages/SCOREbutton.png"),pygame.Rect(WIDTH-250-300,450,250,100)]
	}

	pygame.mixer.music.load("Grasslands Theme.mp3")
	pygame.mixer.music.set_volume(0.25)
	pygame.mixer.music.play(loops=-1)

#----------------- MAIN GAME LOOP START----------------------------	
	while done == False:
		if loop == "game":
			loop = gameLoop(dt,surface,screen,clock)
		elif loop == "shop":
			shopLoop(surface,screen)
		elif loop == "menu":
			loop = menuLoop(surface,screen,menubuttons)
		elif loop == "gameOver":
			loop = deathLoop(screen,surface,deathbuttons)

		pygame.display.flip()

#----------------- DRAWING END-------------------------------------
		
		dt = clock.tick(60)
		pygame.display.set_caption("Platformer (xVelocity:"+("%.0f"%(player.xVel*100))+",yVelocity:"+("%.0f"% (player.yVel*100)) + ",fps:" + str(int(clock.get_fps())) + ")") #shows player velocities

#----------------- MAIN GAME LOOP END ----------------------------
	pygame.quit()

if __name__ == "__main__":
    main()

#https://www.pygame.org/project-Pygame+Text+Input-3013-.html
#text box input for the debugging?