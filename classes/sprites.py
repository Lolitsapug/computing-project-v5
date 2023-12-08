import pygame
cameraOffset = 0

class Sprite(pygame.sprite.Sprite): #abstract class - shouldn't ever be implemented
	def __init__(self, images, startx, starty,type):
		super().__init__()
		self.images = [pygame.image.load(image) for image in images]
		#replace self.images for dictionary of arrays when animating
		self.animationIndex = 0
		self.rect = self.images[self.animationIndex].get_rect()
		self.rect.center = [startx, starty] 
		self.type = type

	def draw(self, surface):
		global cameraOffset
		cameraOffset = getOffset() #retrieves cameraoffset from player
		surface.blit(self.images[self.animationIndex], (self.rect.x-cameraOffset, self.rect.y))

def adjustOffset(offset): #changes the camera offset to the players
	global cameraOffset
	cameraOffset = offset

def getOffset(): #returns camera offset for drawing
	global cameraOffset
	return cameraOffset