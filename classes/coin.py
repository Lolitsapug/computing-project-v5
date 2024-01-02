from .sprites import Sprite,getOffset

class Coin(Sprite): #ground box
    def __init__(self, startx, starty):
        images = ["animations/coin/coin (1).png","animations/coin/coin (2).png","animations/coin/coin (3).png","animations/coin/coin (4).png","animations/coin/coin (5).png","animations/coin/coin (6).png","animations/coin/coin (7).png","animations/coin/coin (8).png","animations/coin/coin (9).png","animations/coin/coin (10).png","animations/coin/coin (11).png","animations/coin/coin (12).png","animations/coin/coin (13).png","animations/coin/coin (14).png"]
        super().__init__(images, startx, starty,"coin")
        self.value = 10

    def checkCollisions(self,player):
        if self.rect.colliderect(player.rect):
            return True
        else:
            return False
    
    def animation(self,dt):
        self.animationIndex = self.animationIndex+0.125*dt
        if self.animationIndex >= len(self.images)*15:
            self.animationIndex = 0

    def draw(self, screen):
        cameraOffset = getOffset()
        screen.blit(self.images[round(self.animationIndex//15)], (self.rect.x-cameraOffset, self.rect.y))