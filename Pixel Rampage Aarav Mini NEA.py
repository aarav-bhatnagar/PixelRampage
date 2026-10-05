from gfx_pack import GfxPack, SWITCH_A, SWITCH_B, SWITCH_C, SWITCH_D, SWITCH_E
import time
import random
import math

class Game:
    class Gun:
        def __init__(self, shootingSpeed, range, maxTimeBetweenShots, pixels, gunHolderLocalXpos, gunHolderLocalYpos, barrelLocalXpos, barrelLocalYpos, damage):
            #Assigning values on creation inside the object to be used later
            self.shootingSpeed = shootingSpeed
            self.range = range
            self.maxTimeBetweenShots = maxTimeBetweenShots
            self.pixels = pixels

            #GunHandling
            self.gunHolderLocalXpos = gunHolderLocalXpos  #This marks the top left hand corner of the gun
            self.gunHolderLocalYpos = gunHolderLocalYpos
            self.barrelLocalXpos = barrelLocalXpos #  This marks the position of the barrel where bullet are shot from
            self.barrelLocalYpos = barrelLocalYpos
            
            self.damage = damage

    class Pickup:
        def __init__(self, Xpos, Ypos, pickupTypeNum):
            self.Xpos = Xpos
            self.Ypos = Ypos
            self.pickupTypeNum = pickupTypeNum
            self.destroyed = False

    class Bullet:
        def __init__(self, Xpos, Ypos, shootingSpeed, range, isDirectionRight, damage, angle):
            self.Xpos = Xpos
            self.Ypos = Ypos
            self.distanceTravelled = 0
            self.shootingSpeed = shootingSpeed
            self.range = range
            self.destroyed = False
            self.isDirectionRight = isDirectionRight
            self.damage = damage
            self.angle = angle

        def update(self):
            if self.isDirectionRight:
                self.Xpos += self.shootingSpeed * math.cos(self.angle)
                self.Ypos += self.shootingSpeed * math.sin(self.angle)
            else:
                self.Xpos -= self.shootingSpeed * math.cos(self.angle)
                self.Ypos -= self.shootingSpeed * math.sin(self.angle)
            self.distanceTravelled += self.shootingSpeed

            if self.distanceTravelled >= self.range:
                self.destroyed = True
    
    class Platform:
        def __init__(self, Xpos, Ypos, width):
            self.heightOfPlatform = 2    #This marks it from the top  going down (as y is positive)
            self.Xpos = Xpos
            self.Ypos = Ypos
            self.width = width
            
    class Enemy:
        def __init__(self, enemyTypeNum, Xpos, Ypos, platform, weaponNum, enemyFireRate, enemyHealth):
            self.enemyTypeNum = enemyTypeNum
            self.enemyXpos = Xpos
            self.enemyYpos = Ypos
            self.detectionDistance = 100
            self.fireRandomness = 5
            self.platform = platform
            self.enemyfireRate = enemyFireRate
            self.enemyTimeSinceLastShot = 0
            self.enemyHealth = enemyHealth
            self.enemyDirectionRight = False
            self.closestDistanceToPlayer = 16
            self.destroyed = False
            
        def update(self, playerXpos, GameScene):
            self.enemyDirectionRight = True if playerXpos - self.enemyXpos >= 0 else False
            
            if self.enemyHealth <= 0:
                self.destroyed = True
                return
            
            #Fire
            if abs(self.enemyXpos - playerXpos) <= self.detectionDistance:
                if self.enemyTimeSinceLastShot > self.enemyfireRate:
                    self.enemyTimeSinceLastShot = random.randint(-self.fireRandomness, self.fireRandomness) / 100
                    GameScene.enemy_shoot(self.enemyXpos, self.enemyYpos, self.enemyTypeNum, self.enemyDirectionRight)
                else:
                    self.enemyTimeSinceLastShot += 0.01
            
            #Move
            multiplier = 1 if self.enemyDirectionRight == True else -1
            self.targetPosition = max(self.platform.Xpos, min(playerXpos - multiplier * (len(GameScene.enemyTypes[self.enemyTypeNum][0]) + self.closestDistanceToPlayer) , self.platform.Xpos + self.platform.width - len(GameScene.enemyTypes[self.enemyTypeNum][0])))
            self.enemyXpos = self.enemyXpos + ((self.targetPosition - self.enemyXpos) * 0.08)    
        
    def __init__(self):
        #Initiliaze hardware
        self.gfx = GfxPack()
        self.display = self.gfx.display
        self.WIDTH, self.HEIGHT = self.display.get_bounds()
        
        #Set Font
        self.display.set_font("bitmap8")
        
        #colours
        self.Blue = (47,112,225, 1)
        self.Orange = (255, 10, 0, 1)
        self.Red = (255, 0, 0, 1)
        self.Green = (60, 230, 5, 1)
        self.defaultColour = self.Blue
        self.gfx.set_backlight(*self.defaultColour)
        
        
        self.physicalProperties = {
            "Gravity"  : 0.015
        }
        
        self.playerProperties = {
            "Xpos" : 30,          #Spawn Position, Xpos and Ypos mark the top left hand corner of the player
            "originalXpos" : 30,
            "Ypos" : 9,
            "colliderWidth" : 9,
            "colliderHeight" : 16,
            #MOVEMENT
            "Xspeed" : 0,
            "Yspeed" : 0,
            "accel" : 0.038,
            "minSpeed" : 0.2,
            "maxSpeed" : 1.8,
            "brakingForce" : 0.012,          #The lower this value, the easier it is to slide
            "jumpForce" : 0.38,
            "isJumping" : True,
            "readyToDoubleJump" : False,
            "hasJumped" : False,
            "isDoubleJumping" : True,
            "doubleJumpMultiplier" : 1.5,
            "isDirectionRight" : True,
            "canMoveX" : True,
            "maxHealth" : 100
        }
        
        self.playerFrame0 = [[0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 0, 0, 1, 1, 0, 0], [0, 1, 0, 0, 0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 1, 0, 0, 0], [0, 1, 1, 0, 0, 1, 1, 0, 0]]
        self.playerFrame1 = [[0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 0, 0, 1, 1, 0, 0], [0, 1, 0, 0, 0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 0, 1, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1, 0]]
        self.playerFrame2 = [[0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 0, 0, 1, 1, 0, 0], [0, 1, 0, 0, 0, 0, 1, 0, 0], [0, 0, 1, 0, 0, 0, 0, 1, 0], [0, 1, 0, 0, 0, 0, 0, 1, 1]]
        self.playerFrame3 = [[0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 0, 0, 1, 1, 0, 0], [0, 1, 0, 0, 0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 1, 0, 0, 0], [0, 1, 1, 0, 0, 1, 1, 0, 0]]
        self.playerFrame4 = [[0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 0, 0, 1, 1, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 0, 0]]
        self.playerFrame5 = [[0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 0, 0, 1, 1, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0, 1, 0, 0], [0, 0, 0, 1, 1, 1, 0, 0, 0]]
        
        self.playerFrames = [self.playerFrame0, self.playerFrame1, self.playerFrame2, self.playerFrame3, self.playerFrame4, self.playerFrame5]
        
        self.frameCounter = 0
        self.maxFrameLength = 8
        self.frameLength = self.maxFrameLength
        self.frameNum = 0
        
        self.gunProperties = {
            #non-specific
            "isShooting" : False,
            "currentWeaponNum" : 0,           #The current weapon is -1 when the character has no weapon, we will start with the most basic weapon Gun0
            "timeSinceLastShot" : 0,
            "currentWeaponList" : [0]
        }

        #GUNS
        Gun0 = self.__class__.Gun(3.25, 105, 0.1, [[0, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1], [1]], 0, 5, 10, 5, 20)
        Gun1 = self.__class__.Gun(2.58, 80, 0.2, [[1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 0], [1, 0, 1, 0, 0, 1, 1, 0], [1, 1, 1, 0, 0, 1, 0, 0], [1, 0, 0, 0, 0, 1, 0, 0]], -1, 5, 12, 5, 25)
        Gun2 = self.__class__.Gun(5.5, 115, 0.06, [[0, 0, 1, 1, 0, 0, 0, 0, 1, 0], [0, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [0, 1, 0, 1, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]], -1, 4, 13, 5, 18)
        Gun3 = self.__class__.Gun(3.4, 130, 0.08, [[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], -1, 4, 14, 4, 23)
        Gun4 = self.__class__.Gun(5, 120, 0.11, [[0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1], [1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0], [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]], -1, 4, 14, 5, 35)
        #GunX etc.
        self.guns = [Gun0, Gun1, Gun2, Gun3, Gun4]  #This order determines the weaponNum
        
        #PICKUPS
        self.chanceOfPickup = 3 #i.e. 1/5 or 0.2 probability
        self.pickups = []
        
        self.pickupHealth50Pixels = [[0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0], [0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]]
        self.pickupHealth100Pixels = [[0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0], [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]]
        
        self.pickupScore50Pixels = [[0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1], [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1], [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1], [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1], [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1]]
        self.pickupScore100Pixels = [[0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1], [0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1], [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1], [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1]]
        self.pickupScore500Pixels = [[0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1], [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1], [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1], [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1]]
        
        self.pickupTypes = [self.pickupHealth50Pixels, self.pickupHealth100Pixels, self.pickupScore50Pixels, self.pickupScore100Pixels, self.pickupScore500Pixels, Gun1.pixels, Gun2.pixels, Gun3.pixels, Gun4.pixels]
        self.bullets = []

        #Weapon Switching
        self.switchingWeapon = False
        
        #Enemies
        self.chanceOfEnemy = 4
        self.maxEnemies = 20
        self.enemies = []
        
        self.enemyPixels0 = [[0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1], [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1], [1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0], [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0], [1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0]]
        
        self.enemyPixels1 = [[0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1], [0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0]]
        
        self.enemyPixels2 = [[0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0], [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0]]

        self.enemyPixels3 = [[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1], [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1], [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0], [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0], [1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0], [0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0]]
        
        self.enemyPixels4 = [[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1], [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0], [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0], [0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0], [0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0], [0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0], [0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]]
        
        self.enemyTypes = [self.enemyPixels0, self.enemyPixels1, self.enemyPixels2, self.enemyPixels3, self.enemyPixels4]
        
        EnemyGun0 = self.__class__.Gun(5, 100, 0.1, [], 0, 0, 12, 6, 5)
        EnemyGun1 = self.__class__.Gun(4.2, 95, 0.4, [], 0, 0, 12, 0, 10)
        EnemyGun2 = self.__class__.Gun(3.8, 85, 0.3, [], 0, 0, 14, 0, 10)
        EnemyGun3 = self.__class__.Gun(3.1, 105, 0.4, [], 0, 0, 20, 4, 15)
        EnemyGun4 = self.__class__.Gun(2.2, 100, 0.5, [], 0, 0, 25, 3, 35)
        
        self.enemyGuns = [EnemyGun0, EnemyGun1, EnemyGun2, EnemyGun3, EnemyGun4]
        self.enemyHealths = [50, 60, 75, 130, 200]
        
        #enemyPixels = self.enemyTypes[enemy.enemyTypeNum]
        #enemyColliderWidth = len(self.enemyTypes[enemy.enemyTypeNum][0])
        #enemyColliderHeight = len(self.enemyTypes[enemy.enemyTypeNum])
        
        #Procedurally generate starting platforms
        self.platforms = []
        self.platformWidths = [35, 40, 45, 50, 55, 60, 65, 70, 80, 90, 95, 100, 110, 115] #Width of platform
        self.platformHeight = 2
        self.possiblePlatformHeights = [28, 30, 33, 35, 40, 43, 45, 48, 50]    #Possible Yposes of platform
        self.platformHeightDiff = 3 #The maximum change in height between platforms
        self.distanceBetweenPlatforms = 25
        self.platformsCovered = self.distanceBetweenPlatforms
        self.reboundStrength = 2.2
        self.FirstPlatform = True
        self.create_platforms(10)
        
        #Camera
        self.viewPortXpos = 0
        self.followCameraDistance = 20
        self.targetCameraDistance = 0
        
        #General
        self.playerRestart = False
        self.restartCounter = 0
        self.restartCounterLength = 40
        
        #Score
        self.SCORE = 0
        self.A_SCORE = 0 #Keeps track of the score generated from killing enemies and pickups etc
        #Health
        self.HEALTH = self.playerProperties["maxHealth"]
        self.healCounter = 0
        self.healRate = 20
        
        #Flashes
        self.flashCount = 0
        self.flashLength = 0
        self.flashColour = self.defaultColour
        
    def draw(self, pixels, startXpos, startYpos, viewPortXpos=0, flippedY=False):
        #This function will draw the pixels starting from the top left corner
        if startXpos - viewPortXpos - len(pixels[0]) > self.WIDTH or startXpos - viewPortXpos + len(pixels[0]) < 0 or startYpos > self.HEIGHT:
            return
        self.display.set_pen(15)
        multiplier = 1
        if flippedY:
            multiplier = -1
    
        for y in range(len(pixels)):
            for x in range(len(pixels[y])):
                if pixels[y][x] == 1:
                    self.display.pixel(int(startXpos + (x*multiplier) - viewPortXpos), int(startYpos + y))
    
    def main_menu(self):
        #PIXEL RAMPAGE
        self.clear_screen()
        self.gfx.set_backlight(*self.Green)
        self.display.set_pen(15)
        self.display.text("PIXEL RAMPAGE", 1, 1, scale=2.2)
        self.display.text("A - PLAY", 3, 20, scale= 1)
        self.display.text("B - LEADERBOARD", 54, 20, scale=1)
        self.display.text("C - HELP", 48, 30, scale=1)
        
        self.draw(self.enemyPixels4, 1, 43)
        self.draw(self.enemyPixels1, 30, 43)
        self.draw(self.enemyPixels1, 30, 54)
        self.draw(self.enemyPixels0, 46, 50)
        self.draw(self.playerFrame0, 59, 38)
        self.draw(self.guns[4].pixels, 67, 42)
        self.draw(self.enemyPixels0, 88, 50, 0, True)
        self.draw(self.enemyPixels2, 105, 39, 0, True)
        self.draw(self.enemyPixels2, 105, 52, 0, True)
        self.draw(self.enemyPixels3, 127, 47, 0, True)
        self.display.update()
        while True:
            if self.gfx.switch_pressed(SWITCH_A):
                time.sleep(0.5)
                self.run()
            elif self.gfx.switch_pressed(SWITCH_B):
                time.sleep(0.5)
                self.show_leaderboard()
            elif self.gfx.switch_pressed(SWITCH_C):
                time.sleep(0.5)
                self.help_menu()
    
    def help_menu(self):
        self.clear_screen()
        self.gfx.set_backlight(*self.Orange)
        self.display.set_pen(15)
        self.display.text("PIXEL RAMPAGE", 1, 1, scale=2.2)
        self.display.text("A - LEFT", 1, 17, scale=1)
        self.display.text("B - RIGHT", 1, 27, scale=1)
        self.display.text("C - SWITCH WEAPON->RESTART", 1, 37, scale=1)
        self.display.text("D - SHOOT", 1, 47, scale=1)
        self.display.text("E - JUMP->DOUBLE JUMP", 1, 57, scale=1)
        self.display.update()
        while True:
            if self.gfx.switch_pressed(SWITCH_A) or self.gfx.switch_pressed(SWITCH_B) or self.gfx.switch_pressed(SWITCH_C) or self.gfx.switch_pressed(SWITCH_D) or self.gfx.switch_pressed(SWITCH_E):
                time.sleep(0.5)
                self.main_menu()
    
    def game_over_screen(self):
        self.clear_screen()
        self.gfx.set_backlight(*self.Green)
        
        #Update leaderboard if needed
        scoreText = "{:06}".format(min(999999, self.SCORE))
        onLeaderboard = self.update_leaderboard(scoreText)

        self.display.set_pen(15)
        self.display.text("GAME OVER", 20, 1, scale=2.2)
        self.display.text("A - RESTART", 3, 20, scale= 1)
        self.display.text("B - MAIN MENU", 65, 20, scale=1)
        if onLeaderboard:
            self.display.text("your on the leaderboard!!!", 5, 31, scale=1)
        else:
            self.display.text("SCORE: ", 52, 31, scale=1)
        self.display.text(scoreText, 38, 40, scale=2)
        
        self.draw(self.enemyTypes[4], 1, 43)
        self.draw(self.guns[0].pixels, 33, 57)
        self.draw(self.guns[1].pixels, 48, 57)
        self.draw(self.guns[2].pixels, 63, 57)
        self.draw(self.guns[3].pixels, 78, 57)
        self.draw(self.guns[4].pixels, 93, 57)
        self.draw(self.enemyTypes[3], 127, 47, 0, True)
        self.display.update()
        while True:
            if self.gfx.switch_pressed(SWITCH_A):
                #Restart
                time.sleep(0.5)
                self.__init__()
                self.run()
            elif self.gfx.switch_pressed(SWITCH_B):
                #Main Menu
                time.sleep(0.5)
                self.__init__()
                self.main_menu()
    
    def clear_screen(self):
        self.display.set_pen(0)
        self.display.clear()
    
    def show_leaderboard(self):
        self.clear_screen()
        self.gfx.set_backlight(*self.Red)
        self.display.set_pen(15)
        
        with open("leaderboard.txt", "r") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            
        if lines == []:
            with open("leaderboard.txt", "w") as file:
                file.write("000000\n" * 10)
            lines = ["000000", "000000", "000000", "000000", "000000", "000000", "000000", "000000", "000000", "000000"]
                
        self.display.text("LEADERBOARD", 1, 1, scale=2.2)
        self.display.text("1. " + lines[0], 1, 17, scale=1)
        self.display.text("2. " + lines[1], 1, 27, scale=1)
        self.display.text("3. " + lines[2], 1, 37, scale=1)
        self.display.text("4. " + lines[3], 1, 47, scale=1)
        self.display.text("5. " + lines[4], 1, 57, scale=1)
        self.display.text("6. " + lines[5], 51, 17, scale=1)
        self.display.text("7. " + lines[6], 51, 27, scale=1)
        self.display.text("8. " + lines[7], 51, 37, scale=1)
        self.display.text("9. " + lines[8], 51, 47, scale=1)
        self.display.text("10. " + lines[9], 51, 57, scale=1)
        self.display.update()
            
        while True:
            if self.gfx.switch_pressed(SWITCH_A) or self.gfx.switch_pressed(SWITCH_B) or self.gfx.switch_pressed(SWITCH_C) or self.gfx.switch_pressed(SWITCH_D) or self.gfx.switch_pressed(SWITCH_E):
                time.sleep(0.5)
                self.main_menu()
    
    def update_leaderboard(self, newScore):
        with open("leaderboard.txt", "r") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            
        if lines == []:
            with open("leaderboard.txt", "w") as file:
                file.write("000000\n" * 10)
            lines = ["000000", "000000", "000000", "000000", "000000", "000000", "000000", "000000", "000000", "000000"]
                
        if int(newScore) > int(lines[-1]):
            lines.pop()
            lines.append(newScore)
            lines.sort(key=int, reverse=True)
            lines = list(map("{:06}".format, lines))
            with open("leaderboard.txt", "w") as file:
                file.write("\n".join(lines))
            return True
        else:
            return False

    def create_platforms(self, numberOfPlatforms):
        for x in range(numberOfPlatforms):
            if len(self.platforms) == 0:
                prevXpos = 0
                prevYIndex = len(self.possiblePlatformHeights) // 2
            else:
                prevXpos = self.platforms[-1].Xpos + self.platforms[-1].width
                prevYIndex = self.possiblePlatformHeights.index(self.platforms[-1].Ypos)
                
            platform = self.__class__.Platform(prevXpos + self.distanceBetweenPlatforms,
                                               self.possiblePlatformHeights[max(0, min(random.randint(prevYIndex - self.platformHeightDiff, prevYIndex + self.platformHeightDiff), len(self.possiblePlatformHeights) - 1))],
                                               self.platformWidths[random.randrange(0, len(self.platformWidths))])
            self.platformsCovered += self.distanceBetweenPlatforms + platform.width
            self.platforms.append(platform)
            
            #Add pickups to platform
            isPickup = random.randint(1, self.chanceOfPickup)
            if isPickup == 1 and self.FirstPlatform == False:
                pickupTypeNum = random.randint(0, len(self.pickupTypes) - 1)
                pixels = self.pickupTypes[pickupTypeNum]
                pickup = self.__class__.Pickup(platform.Xpos + random.randint(0, platform.width - len(pixels[0])), platform.Ypos - len(pixels) - 1, pickupTypeNum)
                self.pickups.append(pickup)
            
            #SpawnEnemy
            isSpawnEnemy = random.randint(1, int(self.chanceOfEnemy))
            if isSpawnEnemy == 1 and len(self.enemies) < self.maxEnemies and self.FirstPlatform == False:
                enemyTypeNum = random.randint(0, len(self.enemyGuns) - 1)
                enemy = self.__class__.Enemy(enemyTypeNum, platform.Xpos + (platform.width // 2) - (len(self.enemyTypes[enemyTypeNum][0]) // 2), platform.Ypos - (len(self.enemyTypes[enemyTypeNum])), platform, 0, self.enemyGuns[enemyTypeNum].maxTimeBetweenShots, self.enemyHealths[enemyTypeNum])
                self.enemies.append(enemy)

            self.FirstPlatform = False
        self.chanceOfEnemy = max(1, self.chanceOfEnemy - 0.4)
                
    def handle_input(self):
        #PLAYER MOVEMENT
        if self.playerProperties["canMoveX"]:
            if self.gfx.switch_pressed(SWITCH_A):
                self.playerProperties["Xspeed"] = min(max(-self.playerProperties["maxSpeed"], self.playerProperties["Xspeed"] - self.playerProperties["accel"]), -self.playerProperties["minSpeed"])
            elif self.gfx.switch_pressed(SWITCH_B):
                self.playerProperties["Xspeed"] = max(min(self.playerProperties["maxSpeed"], self.playerProperties["Xspeed"] + self.playerProperties["accel"]), self.playerProperties["minSpeed"])
            else:
                if abs(self.playerProperties["Xspeed"]) <= 0.05:
                    self.playerProperties["Xspeed"] = 0
                else:
                    self.playerProperties["Xspeed"] += -self.playerProperties["brakingForce"] if self.playerProperties["Xspeed"] > 0 else self.playerProperties["brakingForce"]

        if self.gfx.switch_pressed(SWITCH_E) and self.playerProperties["isJumping"] == False and self.playerProperties["hasJumped"] == False:
            
            self.playerProperties["Yspeed"] = -self.playerProperties["jumpForce"]
            self.playerProperties["hasJumped"] = True
            
        
        if self.gfx.switch_pressed(SWITCH_E) == False and self.playerProperties["isJumping"] == True and self.playerProperties["hasJumped"] == True:
            self.playerProperties["hasJumped"] = False
            self.playerProperties["readyToDoubleJump"] = True
        
        if self.gfx.switch_pressed(SWITCH_E) and self.playerProperties["isDoubleJumping"] == False and self.playerProperties["readyToDoubleJump"] == True:
            self.playerProperties["Yspeed"] = -self.playerProperties["jumpForce"] * self.playerProperties["doubleJumpMultiplier"]
            self.playerProperties["isDoubleJumping"] = True

        #SHOOTING
        self.gunProperties["isShooting"] = self.gfx.switch_pressed(SWITCH_D)

        #CHANGING WEAPON
        if self.gfx.switch_pressed(SWITCH_C) and self.gunProperties["isShooting"] == False and self.switchingWeapon == False:
            self.switchingWeapon = True
            
        
        if self.switchingWeapon == True and self.gfx.switch_pressed(SWITCH_C) == False:
            if self.gunProperties["currentWeaponNum"] != -1:
                currentWeaponIndex = self.gunProperties["currentWeaponList"].index(self.gunProperties["currentWeaponNum"])
            else:
                currentWeaponIndex = -1
            if currentWeaponIndex + 1 < len(self.gunProperties["currentWeaponList"]):
                self.gunProperties["currentWeaponNum"] = self.gunProperties["currentWeaponList"][currentWeaponIndex + 1]
            else:
                self.gunProperties["currentWeaponNum"] = -1
                
            self.switchingWeapon = False
        
        #RESTARTING
        if self.gfx.switch_pressed(SWITCH_C):
            if self.restartCounter < self.restartCounterLength:
                self.restartCounter += 1
            else:
                self.playerRestart = True
        else:
            self.restartCounter = 0

    def closest_enemy(self):
        closestDistance = math.inf
        closestEnemy = None
        
        min = -math.inf
        max = math.inf
        
        if self.playerProperties["isDirectionRight"]:
            min = self.playerProperties["Xpos"]
        else:
            max = self.playerProperties["Xpos"]
            
        for enemy in self.enemies:
            if min <= enemy.enemyXpos <= max:
                distance = abs(enemy.enemyXpos - self.playerProperties["Xpos"])
                if distance < closestDistance:
                    closestDistance = distance
                    closestEnemy = enemy
        
        if closestDistance >= 100 or closestEnemy == None:
            return -1
        else:
            return closestEnemy
    
    def shoot(self):
        if self.gunProperties["isShooting"] == True and self.gunProperties["currentWeaponNum"] != -1 and self.gunProperties["timeSinceLastShot"] <= 0:
            currentWeapon = self.guns[self.gunProperties["currentWeaponNum"]]
            closestEnemy = self.closest_enemy()
            if closestEnemy == -1:
                angle = 0
            else:
                if self.playerProperties["isDirectionRight"]:
                    startingPoint = self.playerProperties["Xpos"]  +  currentWeapon.gunHolderLocalXpos + currentWeapon.barrelLocalXpos
                else:
                    startingPoint = self.playerProperties["Xpos"]  -  currentWeapon.gunHolderLocalXpos - currentWeapon.barrelLocalXpos - 1
                dx = closestEnemy.enemyXpos + (len(self.enemyTypes[closestEnemy.enemyTypeNum][0]) // 2) + 5 - startingPoint
                dy = closestEnemy.enemyYpos - (len(self.enemyTypes[closestEnemy.enemyTypeNum]) // 2) - self.playerProperties["Ypos"] + currentWeapon.barrelLocalYpos

                angle = (math.atan2(dy, dx))
                if not self.playerProperties["isDirectionRight"]:
                    angle = angle - math.pi
                            
            if self.playerProperties["isDirectionRight"] == True:
                    bullet = self.__class__.Bullet(self.playerProperties["Xpos"]  +  currentWeapon.gunHolderLocalXpos + currentWeapon.barrelLocalXpos, self.playerProperties["Ypos"] + currentWeapon.barrelLocalYpos, currentWeapon.shootingSpeed, currentWeapon.range, True, currentWeapon.damage, angle)
            else:
                    bullet = self.__class__.Bullet(self.playerProperties["Xpos"]  -  currentWeapon.gunHolderLocalXpos - currentWeapon.barrelLocalXpos - 1, self.playerProperties["Ypos"] + currentWeapon.barrelLocalYpos, currentWeapon.shootingSpeed, currentWeapon.range, False, currentWeapon.damage, angle)
            self.bullets.append(bullet)
            self.gunProperties["timeSinceLastShot"] = currentWeapon.maxTimeBetweenShots

    def enemy_shoot(self, enemyXpos, enemyYpos, enemyTypeNum, enemyDirectionRight):

        currentWeapon = self.enemyGuns[enemyTypeNum]
        if enemyDirectionRight == True:
            bullet = self.__class__.Bullet(enemyXpos  +  currentWeapon.gunHolderLocalXpos + currentWeapon.barrelLocalXpos, enemyYpos + currentWeapon.barrelLocalYpos, currentWeapon.shootingSpeed, currentWeapon.range, enemyDirectionRight, currentWeapon.damage, 0)
        else:
            bullet = self.__class__.Bullet(enemyXpos  -  currentWeapon.gunHolderLocalXpos, enemyYpos + currentWeapon.barrelLocalYpos, currentWeapon.shootingSpeed, currentWeapon.range, enemyDirectionRight, currentWeapon.damage, 0)
        
        self.bullets.append(bullet)
        
    def update_objects(self, objects, objectNum):
        #ObjectNum: 1 - Bullets, 2 - Pickups, 3 - Enemies
        indexesToBeDestroyed = []

        for index in range(len(objects)):
            if objects[index].destroyed == True:
                indexesToBeDestroyed.append(index)
            else:
                if objectNum == 1:
                    objects[index].update()
                elif objectNum == 3:
                    objects[index].update(self.playerProperties["Xpos"], self)
        
        for index in sorted(indexesToBeDestroyed, reverse=True):
            if index < 0 or index > len(objects) - 1: continue
            object = objects.pop(index)
            if objectNum == 3:
                self.A_SCORE += ((object.enemyTypeNum + 1) * 100)
                self.flashColour = self.Green
                self.flashLength = 15
            del object

    def damage_bullets(self):
        for bullet in self.bullets:
            #Check if hit player
            if self.is_overlapping(bullet.Xpos, bullet.Ypos, 2, 2, self.playerProperties["Xpos"], self.playerProperties["Ypos"], self.playerProperties["colliderWidth"], self.playerProperties["colliderHeight"]):
                self.flashColour = self.Red
                self.flashLength = 10
                self.HEALTH -= bullet.damage
                bullet.destroyed = True
                continue
            
            #Check if hit enemy
            for enemy in self.enemies:
                if self.is_overlapping(bullet.Xpos, bullet.Ypos, 2, 2, enemy.enemyXpos, enemy.enemyYpos, len(self.enemyTypes[enemy.enemyTypeNum][0]), len(self.enemyTypes[enemy.enemyTypeNum])):
                    enemy.enemyHealth -= bullet.damage
                    bullet.destroyed = True
                    continue
            
            #Check if hit platform
            for platfrom in self.platforms:
                if self.is_overlapping(bullet.Xpos, bullet.Ypos, 2, 2, platfrom.Xpos, platfrom.Ypos, platfrom.width, self.platformHeight):
                    bullet.destroyed = True
                    continue
    
    
    def check_for_pickups(self):
        for pickup in self.pickups:
            #Check for any overlap between the two objects
            if self.is_overlapping(self.playerProperties["Xpos"], self.playerProperties["Ypos"], self.playerProperties["colliderWidth"], self.playerProperties["colliderHeight"], pickup.Xpos, pickup.Ypos, len(self.pickupTypes[pickup.pickupTypeNum][0]), len(self.pickupTypes[pickup.pickupTypeNum])) == True:
                pickup.destroyed = True
                self.pickup(pickup.pickupTypeNum)
      
    def pickup(self, pickupTypeNum):
        if pickupTypeNum == 0:
            self.HEALTH = min(100, self.HEALTH + 50)
        elif pickupTypeNum == 1:
            self.HEALTH = 100
        elif pickupTypeNum == 2:
            self.A_SCORE += 50
        elif pickupTypeNum == 3:
            self.A_SCORE += 100
        elif pickupTypeNum == 4:
            self.A_SCORE += 500
        elif pickupTypeNum == 5:
            if 1 in self.gunProperties["currentWeaponList"]: return
            self.gunProperties["currentWeaponList"].append(1)
            self.gunProperties["currentWeaponNum"] = 1
        elif pickupTypeNum == 6:
            if 2 in self.gunProperties["currentWeaponList"]: return
            self.gunProperties["currentWeaponList"].append(2)
            self.gunProperties["currentWeaponNum"] = 2
        elif pickupTypeNum == 7:
            if 3 in self.gunProperties["currentWeaponList"]: return
            self.gunProperties["currentWeaponList"].append(3)
            self.gunProperties["currentWeaponNum"] = 3
        elif pickupTypeNum == 8:
            if 4 in self.gunProperties["currentWeaponList"]: return
            self.gunProperties["currentWeaponList"].append(4)
            self.gunProperties["currentWeaponNum"] = 4

    def update_physics(self):
        if self.playerProperties["isJumping"]:
            self.playerProperties["Yspeed"] += self.physicalProperties["Gravity"]          #Applying Gravity
    
    def update_player(self):
        #New Collision detection code
        #We need to check the bottom of the player with the height of the platform
        isGrounded = False
        
        for platform in self.platforms:
            if platform.Xpos - self.viewPortXpos > self.WIDTH or platform.Xpos - self.viewPortXpos + platform.width < 0:
                continue
            if self.is_overlapping(self.playerProperties["Xpos"], self.playerProperties["Ypos"], self.playerProperties["colliderWidth"], self.playerProperties["colliderHeight"],
                                   platform.Xpos, platform.Ypos, platform.width, self.platformHeight):
                
                if (self.playerProperties["Ypos"] <= platform.Ypos and 
                    self.playerProperties["Ypos"] + self.playerProperties["colliderHeight"] >= platform.Ypos + self.platformHeight):
                    if self.playerProperties["Xspeed"] > 0:
                        self.playerProperties["Xpos"] -= self.reboundStrength * abs(self.playerProperties["Xspeed"])
                    elif self.playerProperties["Xspeed"] < 0:
                        self.playerProperties["Xpos"] += self.reboundStrength * abs(self.playerProperties["Xspeed"])
                    self.playerProperties["canMoveX"] = False
                    
                else:
                    # Top collision (landing)
                    if self.playerProperties["Yspeed"] > 0:
                        isGrounded = True
            
        if isGrounded == False or self.playerProperties["canMoveX"] == False:
            self.playerProperties["isJumping"] = True
        else:
            self.playerProperties["Yspeed"] = 0 
            self.playerProperties["isJumping"] = False
            self.playerProperties["isDoubleJumping"] = False
            self.playerProperties["readyToDoubleJump"] = False
            
        if self.playerProperties["canMoveX"]:
            self.playerProperties["Xpos"] += self.playerProperties["Xspeed"]
        
        self.playerProperties["Ypos"] += self.playerProperties["Yspeed"]
        
        #UpdateDirection
        if self.playerProperties["Xspeed"] > 0:
            self.playerProperties["isDirectionRight"] = True
        elif self.playerProperties["Xspeed"] < 0:
            self.playerProperties["isDirectionRight"] = False
    
    def is_overlapping(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return not (
            x1 + w1 < x2 or  # obj1 is completely to the left of obj2
            x1 > x2 + w2 or  # obj1 is completely to the right of obj2
            y1 + h1 < y2 or  # obj1 is completely above obj2
            y1 > y2 + h2     # obj1 is completely below obj2
        )
            
    def update_camera(self):
        if self.playerProperties["isDirectionRight"]:
            self.targetCameraDistance = max(25, 20 + self.playerProperties["Xspeed"] * 14.2)
        else:
            self.targetCameraDistance = min(self.WIDTH - 25, self.WIDTH - (20 + self.playerProperties["Xspeed"] * 14.2))
            
        # Smoothly move the followCameraDistance to targetCameraDistance
        self.followCameraDistance += (self.targetCameraDistance - self.followCameraDistance) * 0.022

    def update_map(self):
        if int(self.playerProperties["Xpos"]) + int(1.1 * self.WIDTH) > self.platformsCovered:
            self.create_platforms(10)
    
    def change_player_frame(self):
        if (not self.gfx.switch_pressed(SWITCH_A) and not self.gfx.switch_pressed(SWITCH_B)) or not self.playerProperties["canMoveX"]:
            self.frameNum = 0
            return
        if self.frameCounter < self.frameLength:
            self.frameCounter += 1
        else:
            self.frameNum = (self.frameNum + 1) % len(self.playerFrames)
            self.frameCounter = 0
    
    def render_game(self):
        self.viewPortXpos = self.playerProperties["Xpos"] - self.followCameraDistance
        
        if self.playerProperties["Xspeed"] == 0:
            self.frameLength = self.maxFrameLength
        else:
            self.frameLength = min(self.maxFrameLength, abs(int(self.maxFrameLength / self.playerProperties["Xspeed"])))

        #Clear Display
        self.clear_screen()
        
        #Set pen to black
        self.display.set_pen(15)
        #Draw Enviroment
        #Draw Platforms
        for platform in self.platforms:
            if platform.Xpos - self.viewPortXpos > self.WIDTH or platform.Xpos - self.viewPortXpos + platform.width < 0:
                continue
            self.display.rectangle(int(platform.Xpos - self.viewPortXpos), platform.Ypos, platform.width, self.platformHeight)
        
        #Draw Player
        if self.playerProperties["isDirectionRight"]:
            self.draw(self.playerFrames[self.frameNum], int(self.playerProperties["Xpos"]), int(self.playerProperties["Ypos"]), self.viewPortXpos)
        else:
            self.draw(self.playerFrames[self.frameNum], int(self.playerProperties["Xpos"] + self.playerProperties["colliderWidth"] - 1), int(self.playerProperties["Ypos"]), self.viewPortXpos, True)
        #Draw Gun
        if self.gunProperties["currentWeaponNum"] != -1:
            currentWeapon = self.guns[self.gunProperties["currentWeaponNum"]]
            if self.playerProperties["isDirectionRight"] == True:
                self.draw(currentWeapon.pixels, int(self.playerProperties["Xpos"]) + self.playerProperties["colliderWidth"] + currentWeapon.gunHolderLocalXpos, self.playerProperties["Ypos"] + currentWeapon.gunHolderLocalYpos, self.viewPortXpos)
            else:
                self.draw(currentWeapon.pixels, int(self.playerProperties["Xpos"]) - currentWeapon.gunHolderLocalXpos - 1, self.playerProperties["Ypos"] + currentWeapon.gunHolderLocalYpos, self.viewPortXpos, True)

        #Draw Bullets
        self.display.set_pen(15)
        for bullet in self.bullets:
            self.display.rectangle(int(bullet.Xpos - self.viewPortXpos), int(bullet.Ypos), 2, 2)
        
        #Draw pickups
        for pickup in self.pickups:
            self.draw(self.pickupTypes[pickup.pickupTypeNum], pickup.Xpos, pickup.Ypos, self.viewPortXpos)
        
        #Draw enemies
        for enemy in self.enemies:
            if enemy.enemyDirectionRight == True:
                self.draw(self.enemyTypes[enemy.enemyTypeNum], enemy.enemyXpos, enemy.enemyYpos, self.viewPortXpos)
            else:
                self.draw(self.enemyTypes[enemy.enemyTypeNum], enemy.enemyXpos + len(self.enemyTypes[enemy.enemyTypeNum][0]), enemy.enemyYpos, self.viewPortXpos, True)
        
        self.update_UI()
        
        self.display.update()  # Update display with the above items
    
    def update_default_colour(self):
        if self.HEALTH >= 75:
            self.defaultColour = self.Blue
        elif self.HEALTH >= 45:
            self.defaultColour = self.Orange
        else:
            self.defaultColour = self.Red
    
    def flash_colour(self):
        if self.flashColour == self.defaultColour: 
            self.gfx.set_backlight(*self.flashColour)
            return
        
        if self.flashCount > self.flashLength:
            self.flashCount = 0
            self.gfx.set_backlight(*self.defaultColour)
            self.flashColour = self.defaultColour
        else:
            self.gfx.set_backlight(*self.flashColour)
            self.flashCount += 1
    
    def update_UI(self):
        self.display.set_pen(15)
        #SCORE
        self.SCORE = max(self.SCORE - self.A_SCORE, int(self.playerProperties["Xpos"] - self.playerProperties["originalXpos"])) + self.A_SCORE

        self.flash_colour() #runs every second
        text = "SCORE: " + str(self.SCORE)
        self.display.text(text, 1, 1, scale=0.8)
        
        #HEALTH BAR
        self.display.rectangle(self.WIDTH - 51, self.HEIGHT - 9, 50, 8)
        self.display.set_pen(0)
        self.display.rectangle(self.WIDTH - 50, self.HEIGHT - 8, 48, 6)
        self.display.set_pen(15)
        self.display.rectangle(self.WIDTH - 49, self.HEIGHT - 7, ((self.HEALTH) * 46) // 100, 4)
    
    def is_Dead(self):
        if self.playerRestart:
            return True
        if (self.playerProperties["Ypos"] >= self.HEIGHT or self.HEALTH <= 0):
            #RESTART GAME
            return True
        return False
    
    def heal(self):
        if self.healCounter < self.healRate:
            self.healCounter += 1
        else:
            self.HEALTH = min(100, self.HEALTH + 1)
            self.healCounter = 0
      
    def debug(self):
        #print("Coordinates: (" + str(int(self.playerProperties["Xpos"])) + ", " + str(int(self.playerProperties["Ypos"])) + ")")
        #print("Xspeed: " + str(self.playerProperties["Xspeed"]))
        #print("Yspeed: " + str(self.playerProperties["Yspeed"]))
        print("isJumping: " + str(self.playerProperties["isJumping"]))
        print("isDoubleJumping: " + str(self.playerProperties["isDoubleJumping"]))
    
        
    def run(self):
        self.clear_screen()
        time.sleep(0.5)
        while not self.is_Dead():
            self.handle_input()
            self.update_physics()
            self.update_player()
            self.check_for_pickups()
            self.shoot()
            self.update_objects(self.bullets, 1)
            self.damage_bullets()
            self.update_objects(self.pickups, 2)
            self.update_objects(self.enemies, 3)
            self.update_camera()
            self.update_map()
            self.update_default_colour()
            self.change_player_frame()
            self.heal()
            #self.debug()
            self.render_game()
            frameRate = 1/60
            self.gunProperties["timeSinceLastShot"] -= frameRate
            #Game speed, i.e. waits for a fixes time before cycling (60FPS)
            time.sleep(frameRate)
        time.sleep(0.5)
        self.game_over_screen()    
        
if __name__ == "__main__":
    #del leaderboard
    #with open("leaderboard.txt", "w") as file:
    #    file.write("")
        
    game = Game()
    game.main_menu()