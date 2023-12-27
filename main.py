import pygame, sqlite3 #imports
from classes.player import Player
from classes.box import Box,Sky,EndPoint,Invisible,Shop
from classes.enemies import Sword, Bat, Shooter,Spike
from classes.coin import Coin
from classes.textbox import Text

print("\n\u001b[31;1mTO COMMIT ON GITHUB ON PYCHARM \nTOP BAR - GIT - COMMIT \nTHEN GIT - PUSH - SELECT COMMITS\n\u001b[0m")

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
coins = []
interactables = []
level = 0 #indicates what level to load
levels = ["Level1.txt","Level2.txt","Level3.txt"] #prebuilt game levels
animationIndex = 0
gameTime = 0 #game timer (miliseconds)
score = 0
userID = None
textbox = Text(10,40)

title = pygame.image.load("menuImages/catlegendstitle.png")
loadimages = ["menuImages/bg1.png","menuImages/bg2.png","menuImages/bg3.png","menuImages/bg4.png","menuImages/bg5.png","menuImages/bg6.png","menuImages/bg6.png"]
images = [pygame.image.load(image) for image in loadimages]
font0 = pygame.font.SysFont('freesanbold.ttf', 60)
font1 = pygame.font.SysFont('freesanbold.ttf', 50)
font2 = pygame.font.SysFont('freesanbold.ttf', 40)

def createUser(name):
	global userID
	connection = sqlite3.connect('Database.db')
	cursor = connection.cursor()
	rec = (name,)
	sql = '''
        INSERT INTO User (Name) VALUES (?)
        '''
	try:
		cursor.execute(sql, rec)
		connection.commit()
	except Exception as e:
		print("Error Message :", str(e))
		connection.rollback()

	sql = '''
	        SELECT UserID FROM User ORDER BY UserID DESC LIMIT 1;
	        '''
	try:
		cursor.execute(sql)
		connection.commit()
		rows = cursor.fetchall()
		userID = rows[0][0]

	except Exception as e:
		print("Error Message :", str(e))
		connection.rollback()
	
	print(f"created user {name}")
	print(f"ID {userID}")

def readData():
	connection = sqlite3.connect('Database.db')
	rows = []
	# preparing a cursor object
	cursor = connection.cursor()
	sql = '''
	        SELECT Score, Time, Level, Name 
	        FROM Leaderboard, User
	        WHERE Leaderboard.userID = User.UserID 
	        ORDER BY Score DESC, Time DESC 
	        LIMIT 10;
	        '''
	# executing sql statement with try and except incase of errors
	try:
		cursor.execute(sql)
		connection.commit()
		rows = cursor.fetchall()

	except Exception as e:
		print("Error Message :", str(e))
		connection.rollback()
		return "error"

	return rows

def insertData():
	if userID != None:
		connection = sqlite3.connect('Database.db')
		cursor = connection.cursor()
		rec = (userID, gameTime//1000, score, level+1)
		sql = '''
			INSERT INTO Leaderboard (userID, Time, Score, Level) VALUES (?, ?, ?, ?)
			'''
		try:
			cursor.execute(sql, rec)
			connection.commit()
		except Exception as e:
			print("Error Message :", str(e))
			connection.rollback()

def createMap(fileName,player):
	global boxes,enemies,coins
	boxes = [] #resets boxes and enemies lists
	enemies = []
	coins = []
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
			elif map[row][column] == "X":#invisible wall
				boxes.append(Invisible(column*75, row*75))
			else:
				boxes.append(Sky(column*75, row*75)) #background sky for all sprites

			if map[row][column] == "/":#sword skeleton
				enemies.append(Sword((column*75)+16, (row*75)+18)) #+29 for height correction
			elif map[row][column] == ">":#bat
				enemies.append(Bat((column*75+5), (row*75)+5)) 
			elif map[row][column] == "+":#shooter
				enemies.append(Shooter((column*75+5), (row*75)+18)) 
			elif map[row][column] == "^":#spike
				enemies.append(Spike((column*75+5), (row*75)+26)) 
			elif map[row][column] == "#":#END
				boxes.append(EndPoint(column*75, 380))#flag goes from base to top
			elif map[row][column] == "@":#player
				player.rect.x,player.rect.y = column*75,row*75+20
			elif map[row][column] == "0":#coin
				coins.append(Coin((column*75), (row*75)+21)) 
			elif map[row][column] == "$":#shop
				boxes.append(Shop((column*75-12), (row*75-6))) 

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
		global gameTime,done,score,coins

		pygame.event.pump()
		for events in pygame.event.get():#quit game event
			if events.type == pygame.QUIT:
				done = True
				pygame.quit() 
			if player.dead == True and events.type == pygame.KEYDOWN: #redirect to deathloop
				return "gameOver"
	#----------------- GAME LOGIC START--------------------------------
		if player.dead == False:
			gameTime += clock.get_time()
		#onscreen text statistics
		timeText,scoreText,ammoText,moneyText = font1.render(str(gameTime//1000),True,(0,255,0)),font2.render(str(f"score:{score}"),True,(255,255,0)),font2.render(f"ammo:{player.ammo}",True,(255,255,0)),font2.render(f"coins:{player.money}",True,(255,255,0))
		timeRect,scoreRect,ammoRect,moneyRect = timeText.get_rect(),scoreText.get_rect(),ammoText.get_rect(),moneyText.get_rect()
		timeRect.right,timeRect.y = WIDTH-10,10
		scoreRect.x,scoreRect.y = 15,105
		ammoRect.x,ammoRect.y = 15,45
		moneyRect.x,moneyRect.y = 15,75
	
		surface.fill(BACKGROUND)
		for box in boxes:
			box.draw(surface) #draws background so it doesnt cover up projectile arc

		if player.update(dt,clock,surface):
			return "shop"
		IDs = player.collisions(boxes,dt)

		if IDs[0]:#if collision with end flag loads next level
			print("flag collision?")
			if LoadNextLevel(player):
				return "gameOver" #player has reached end of levels#
		
		if IDs[1] == None: #touching a box to trigger different image
			for box in boxes:
				if box.type == "shop":
					box.animationIndex = 0
		else:
			IDs[1].animationIndex = 1

		for enemy in enemies: #interactions with all enemies
			enemy.update(dt,player) #updates enemies for movement/calculations
			if enemy.type == "bat":
				enemy.boxCollisions(dt,boxes)#collide with the terrain
			if enemy.type == "shooter":
				if enemy.updateProjectiles(dt,boxes,player) == "playerCollision":
					if player.damagetime >=1300:
						player.takeDamage()
			if enemy.checkCollisions(player.rect) == True: #collisions with player
				if player.damagetime >=1300: 
					player.takeDamage()
					if enemy.type != "sword" and enemy.type != "spike": 
						enemies.remove(enemy)
						break #enemies like bats die
			for attack in player.getAttacks(): #collisions with player attacks
				if enemy.checkCollisions(attack.rect) == True and enemy.type != "spike": #player kills an enemy. adds 100 to score
					enemies.remove(enemy)
					score += 10
					if attack.type == "projectile":
						player.removeAttack(attack)

		for attack in player.getAttacks():#updates player attack for movement/removal
			if attack.type == "projectile":
				update = attack.update(dt,boxes) #player projectile attack
			else:
				update = attack.update(clock,player.rect,player.right, dt) #player slash attack
			if update == "remove":
				player.removeAttack(attack)

		#check coins
		for coin in coins:
			if coin.checkCollisions(player):
				score += 10
				player.money += 1
				coins.remove(coin)
			else:
				coin.animation(dt)

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

		for coin in coins:
			coin.draw(surface)

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

def shopLoop(surface,screen,buttons):
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

	ammoText,moneyText,topText = font2.render(f"ammo:{player.ammo}",True,(255,255,0)),font2.render(f"coins:{player.money}",True,(255,255,0)),font0.render("Shop", True, (255,255,255))

	if clicked == "ammo" and player.money >= 1:
		player.ammo += 3
		player.money -= 1

	elif clicked == "heart" and player.money >= 1:
		player.health += 1
		player.money -= 1
	
	elif clicked == "exit":
		return "game"

	if player.money <= 0:
		moneyText = font2.render(f"coins:{player.money}",True,(255,75,75))
	
	ammoRect,moneyRect,topTextRect = ammoText.get_rect(),moneyText.get_rect(),topText.get_rect()
	ammoRect.x,ammoRect.y = 15,45
	moneyRect.x,moneyRect.y = 15,75
	topTextRect.centerx, topTextRect.centery = WIDTH // 2, 80

	surface.fill(BACKGROUND)

	surface.blit(ammoText,ammoRect) #ammo top left
	surface.blit(moneyText,moneyRect) #money top left
	surface.blit(topText,topTextRect) #money top left

	player.drawHealth(surface)

	for b in buttons:
		surface.blit(buttons[b][0],buttons[b][1]) #blits to surface (button image,button rect)

	scaledSurface = pygame.transform.scale(surface, (1280, 720)) #screen scaling
	screen.blit(scaledSurface, (0, 0))
	return "shop"

def menuLoop(dt,surface,screen,buttons):
	global done,level,levels,player,gameTime,animationIndex
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

		if events.type == pygame.KEYDOWN:
			textbox.update(events)
			if events.key == pygame.K_RETURN and textbox.value != "":
				textbox.setGreen()
				createUser(textbox.value)

	if clicked == "start": #BUTTON FUNCTIONS
		levels = ["Level1.txt","Level2.txt","Level3.txt"]
		level = 0
		player = Player(100,100)
		gameTime = 0
		createMap(levels[level],player)
		return "game"
	elif clicked == "loadTxt":
		print("loading custom map")
		levels = ["custom.txt"]
		#txt = input("map txt name"),createmap(txt), levels = [txt,bossfight], loop = "game"
		#levels = ["customMap.txt","BossLevel.txt"]
		level = 0
		player = Player(100, 100)
		gameTime = 0
		createMap(levels[level],player)
		return "game"	
	elif clicked == "leaderboard":
		print("loading leaderboard") #load a leaderboard page
		return "leaderboard"
	elif clicked == "exit":
		print("quitting game")
		done = True
		pygame.quit()

	animationIndex = animationIndex+0.15*dt
	if animationIndex >= 6*15:
		animationIndex = 0		
	#------------------ DRAWING SURFACE ---------------------
	surface.blit(images[round(animationIndex//15)],(0,0))
	surface.blit(title,(0,0))

	textbox.draw(surface)

	for b in buttons:
		surface.blit(buttons[b][0],buttons[b][1]) #blits to surface (button image,button rect)
	
	scaledSurface = pygame.transform.scale(surface, (1280, 720)) #screen scaling
	screen.blit(scaledSurface, (0, 0))
	return "menu"

def deathLoop(screen,surface,buttons):
	global done
	pygame.event.pump()
	clicked = None
	for events in pygame.event.get():
		if events.type == pygame.QUIT:
			pygame.quit()
			done = True
		if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
			pos = pygame.mouse.get_pos()
			for b in buttons:
				if buttons[b][1].collidepoint(pos) == True:
					print(b + " was clicked")
					clicked = b
	if clicked == "title":
		insertData() #adds data to leaderboard
		return "menu"	
	elif clicked == "leaderboard":
		insertData()
		return "leaderboard"

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

def leaderboardLoop(screen,surface):
	global done
	pygame.event.pump()

	for events in pygame.event.get():
		if events.type == pygame.QUIT:
			pygame.quit()
			done = True
		if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
			pos = pygame.mouse.get_pos()
			if pygame.Rect(150,500,250,100).collidepoint(pos):
				print("title " + " was clicked")

				return "menu"

	topText = font0.render("Leaderboard", True, (255,255,255))
	topTextRect = topText.get_rect()
	topTextRect.centerx, topTextRect.centery = WIDTH // 2, 100

	surface.fill(BACKGROUND)
	surface.blit(topText, topTextRect)

	rows = readData()
	if rows == "error":
		print("error fetching leaderboard data - returning to menu")
		return "menu"

	for i in range(len(rows)):
		text = font2.render(f"{str(i+1).ljust(2,' ')}. {rows[i][3].ljust(8,' ')} |  \
					  Score: {str(rows[i][0]).ljust(4,' ')} | \
					  Time: {str(rows[i][1]).ljust(4,' ')} | \
					  Level:{str(rows[i][2]).ljust(2,' ')}", True, (255,255,255))
		rect = text.get_rect()
		rect.x,rect.y = WIDTH/2 - 300,150 + i*40
		surface.blit(text, rect)

	surface.blit(pygame.image.load("menuImages/MENUbutton.png"), pygame.Rect(150,500,250,100))

	scaledSurface = pygame.transform.scale(surface, (1280, 720))  # screen scaling
	screen.blit(scaledSurface, (0, 0))
	return "leaderboard"

#-------------------- MAIN LOOP -----------------------
def main():#initial game initialisation
	global player
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
		"title":[pygame.image.load("menuImages/MENUbutton.png"),pygame.Rect(300,450,250,100)],
		"leaderboard":[pygame.image.load("menuImages/SCOREbutton.png"),pygame.Rect(WIDTH-250-300,450,250,100)]
	}

	shopbuttons = { 
		"ammo":[pygame.image.load("menuImages/AMMObutton.png"),pygame.Rect(250,250,250,100)],
		"heart":[pygame.image.load("menuImages/HEARTbutton.png"),pygame.Rect(780,250,250,100)],
		"exit":[pygame.image.load("menuImages/EXITbutton.png"), pygame.Rect(150,500,250,100)]
		

	}

	pygame.mixer.music.load("Grasslands Theme.mp3")
	pygame.mixer.music.set_volume(0.25)
	pygame.mixer.music.play(loops=-1)

#----------------- MAIN GAME LOOP START----------------------------	
	while done == False:
		if loop == "game":
			loop = gameLoop(dt,surface,screen,clock)
		elif loop == "shop":
			loop = shopLoop(surface,screen,shopbuttons)
		elif loop == "menu":
			loop = menuLoop(dt,surface,screen,menubuttons)
		elif loop == "gameOver":
			loop = deathLoop(screen,surface,deathbuttons)
		elif loop == "leaderboard":
			loop = leaderboardLoop(screen,surface)

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