import pygame
import random
import math

from pygame.locals import *

# Credit to Dr. Robert Collier for providing me with the original majority of this code!

# the window is the actual window onto which the camera view is resized and blitted
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
LINE_LENGTH = 500

STATE_GAMEOVER = 0
STATE_PLAYING = 1

FONTS = {} # Add fonts in init

# the frame rate is the number of frames per second that will be displayed and although
# we could (and should) measure the amount of time elapsed, for the sake of simplicity
# we will make the (not unreasonable) assumption that this "delta time" is always 1/fps
frame_rate = 40
delta_time = 1 / frame_rate

# In normal code, we shouldn't use globals - but for prototyping it will make our life significantly easier.
game_data = {}


class playerOne:
    def __init__(self, position, radius):
        # parameters
        self.position = position
        self.radius = radius
        # movement attributes
        self.currMovement = 'Left'
        self.movement = False
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        # other
        self.velocity = 18
        self.colliding = False
        self.score = 0
        self.point = False
        self.img = pygame.transform.scale(pygame.image.load("resources/pxl-cat-orange.png"), (128, 128))
        # list of projectiles
        self.projectiles = []
        self.shot = False

    def render(self, screen):
        # draw the circle hitbox, in red if there has been a collision or players image otherwise
        if self.colliding:
            pygame.draw.circle(screen, (255, 0, 0), self.position, self.radius)
            game_data["laserSound"].play()
            if self.score > 0:
                self.score -= 1
        elif self.point:
            game_data["yarnSound"].play()
            self.score += 1
        else:
            self.position = list(self.position)
            screen.blit(self.img, (self.position[0] - (self.radius*2), self.position[1] - (self.radius*2)))
            self.position = tuple(self.position)


class playerTwo:
    def __init__(self, position, radius):
        # parameters
        self.position = position
        self.radius = radius
        # movement attributes
        self.currMovement = 'Right'
        self.movement = False
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        # other
        self.velocity = 18
        self.colliding = False
        self.score = 0
        self.point = False
        self.img = pygame.transform.scale(pygame.image.load("resources/pxl-cat-black.png"), (128, 128))
        # list of projectiles
        self.projectiles = []
        self.shot = False
        

    def render(self, screen):
        # draw the circle hitbox, in red if there has been a collision or players image otherwise
        if self.colliding:
            pygame.draw.circle(screen, (255, 0, 0), self.position, self.radius)
            game_data["laserSound"].play()
            if self.score > 0:
                self.score -= 1
        elif self.point:
            game_data["yarnSound"].play()
            self.score += 1
        else:    
            self.position = list(self.position)
            screen.blit(self.img, (self.position[0] - (self.radius*2), self.position[1] - (self.radius*2)))
            self.position = tuple(self.position)
        
class Projectile:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius
        self.facing = 'NA'
        self.velocity = 20
        self.shooting = False
        self.img = pygame.transform.scale(pygame.image.load("resources/pxl-paw-green.png"), (64, 64))

    def render(self, screen):
        screen.blit(self.img, (self.position[0] - (self.radius*2), self.position[1] - (self.radius*2)))
        

class GameCircle:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius
        self.colliding = False
        self.hit = False
        self.img = pygame.transform.scale(pygame.image.load("resources/ball-of-yarn.png"), (80, 80))

    def render(self, screen):
        self.position = list(self.position)
        screen.blit(self.img, (self.position[0] - self.radius, self.position[1] - self.radius))
        self.position = tuple(self.position)

class RotatingLine:
     ### Intervals Example ###
    # An "intervals" variable of [ (0.00, 0.50), (0.75, 1.00) ] represents a line with a gap
    # starting halfway through the line, the gap is 25% of the length of the line, followed by
    # the remaining 25% being a collidable line.

    def __init__(self, origin, angle, intervals, color, length):
        self.origin = origin        # This is the origin point that the line will rotate around
        self.angle = angle          # This is the initial angle that the line will face, in degrees
        self.intervals = intervals  # This is a list of tuples representing the visible segments that create gaps
        self.segments = []          # Represents the actual segments we'll draw, handled in update
        self.collided = False
        self.color = color
        self.length = length
        self.rotation = 10
        

    def render(self, screen):
        # draw each of the rotating line segments
        for seg in self.segments:
            pygame.draw.aaline(screen, self.color, seg[0], seg[1])

    def rotate(self, deg=1):
        # Rotate the line by 1 degree
        # Return TRUE if the line reset to 90 degrees, FALSE otherwise
        reset = False

        # increase the angle of the rotating line
        self.angle = (self.angle + deg)

        # the rotating line angle ranges between 0 and 360 degrees
        if self.angle > 360:
            # when it reaches an angle of 0 degrees, reset it 
            self.angle = 0
            reset = True
            self.rotation -= 1
            # once 5 rotations have happened second laser appears
            if self.rotation == 5:
                game_data["lines"].append( RotatingLine( (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 180, [ (0.00, 0.50), (0.75, 1.00) ], (255, 0, 0), 500) )
            # once 10 rotations have happened game ends
            if self.rotation == 0:
                game_data["current_state"] = STATE_GAMEOVER
                # Play game over sound (produced on logic pro)
                game_data["gameOverSound"].play()
            self.collided = False

        self._update_line_segments()
    
        return reset

    def _update_line_segments(self):
        # This function is going to set up the coordinates for the enpoints
        # of each "segment" of our line.

        # The points associated with each line segment must be recalculated as the angle changes
        self.segments = []
        
        # consider every line segment length
        for partial_line in self.intervals:
            # compute the start of the line...
            sol_x = self.origin[0] + math.cos(math.radians(self.angle)) * self.length * partial_line[0]
            sol_y = self.origin[1] + math.sin(math.radians(self.angle)) * self.length * partial_line[0]
            
            # ...and the end of the line...
            eol_x = self.origin[0] + math.cos(math.radians(self.angle)) * self.length * partial_line[1]
            eol_y = self.origin[1] + math.sin(math.radians(self.angle)) * self.length * partial_line[1]
            
            # ...and then add that line to the list
            self.segments.append( ((sol_x, sol_y), (eol_x, eol_y)) )

def main():
    # initialize pygame
    pygame.init()
    pygame.font.init()
    
    #load music (music produced on logic pro)
    music = pygame.mixer.music.load('resources/sounds/country boi.wav') 
    pygame.mixer.music.play(-1)


    # create the window and set the caption of the window
    screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )
    pygame.display.set_caption('Yarn Wars')

    # create a clock
    clock = pygame.time.Clock()

    initialize()

    #image to be rotated
    pointer = pygame.transform.scale(pygame.image.load("resources/pointer.png"), (20, 10))
    angle = 0

    # the game loop is a postcondition loop controlled using a Boolean flag
    while not game_data["quit_game"]:
        if game_data["current_state"] == STATE_PLAYING:
            handle_inputs()
            update() 
            render(screen)

            #rotate image
            angle -= 1
            if angle == -360:
                angle = 0
            img = pygame.transform.rotate(pointer, angle)
            img_rect = pointer.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(img, img_rect)
            pygame.display.update()
            
        elif game_data["current_state"] == STATE_GAMEOVER:
            handle_input_gameover()
            render_gameover(screen)

        
        # enforce the minimum frame rate
        clock.tick(frame_rate)


def initialize():
    # Setup all of our initial data for the game
    FONTS["score"] = pygame.font.SysFont("Comic Sans Ms", 20)
    FONTS["gameover"] = pygame.font.SysFont("Comic Sans Ms", 60)
    FONTS["countdown"] = pygame.font.SysFont("Comic Sans Ms", 400)
    
    game_data["current_state"] = STATE_PLAYING
    game_data["quit_game"] = False
    game_data["lines"] = []
    game_data["circles"] = []
    game_data["playerOne"] = []
    game_data["playerTwo"] = []

    # original sounds produced on logic pro
    game_data["gameOverSound"] = pygame.mixer.Sound('resources/sounds/game over.wav')
    game_data["laserSound"] = pygame.mixer.Sound('resources/sounds/laser.wav')
    game_data["yarnSound"] = pygame.mixer.Sound('resources/sounds/yarn.wav')
    game_data["shotSound"] = pygame.mixer.Sound('resources/sounds/shot.wav')

    # Just one line and one circle for the initial toy
    game_data["lines"].append( RotatingLine( (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 0, [ (0.00, 0.50), (0.75, 1.00) ], (255, 0, 0), 500) )
    game_data["circles"].append( GameCircle( (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 32 ) )

    #add cat obj to cats*
    game_data["playerOne"].append( playerOne( (715, 60), 30))
    game_data["playerTwo"].append( playerTwo( (185, 60), 30))


    

# from full-final.py code
def handle_input_gameover():
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                game_data["quit_game"] = True

        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            game_data["quit_game"] = True

def handle_inputs():
    
    # look in the event queue for the quit event
    for event in pygame.event.get():
        if event.type == QUIT:
            game_data["quit_game"] = True
        

        # Handle Key Presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                handle_key_escape(game_data)
            elif event.key == pygame.K_x:
                game_data["current_state"] = STATE_GAMEOVER
                game_data["gameOverSound"].play()
            elif event.key == pygame.K_r:
                game_data["current_state"] = STATE_PLAYING
                for line in game_data["lines"]:
                    line.rotation = 10
            elif event.key == pygame.K_LEFT:
                handle_key_left(game_data, 'down', game_data["playerOne"])
            elif event.key == pygame.K_RIGHT:
                handle_key_right(game_data, 'down', game_data["playerOne"])
            elif event.key == pygame.K_UP:
                handle_key_up(game_data, 'down', game_data["playerOne"])
            elif event.key == pygame.K_DOWN:
                handle_key_down(game_data, 'down', game_data["playerOne"])
            elif event.key == pygame.K_m:
                handle_key_shoot(game_data, 'down', game_data["playerOne"])
            elif event.key == pygame.K_a:
                handle_key_left(game_data, 'down', game_data["playerTwo"])
            elif event.key == pygame.K_d:
                handle_key_right(game_data, 'down', game_data["playerTwo"])
            elif event.key == pygame.K_w:
                handle_key_up(game_data, 'down', game_data["playerTwo"])
            elif event.key == pygame.K_s:
                handle_key_down(game_data, 'down', game_data["playerTwo"])
            elif event.key == pygame.K_q:
                handle_key_shoot(game_data, 'down', game_data["playerTwo"])
        # Handle Key Releases
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                handle_key_left(game_data, 'up', game_data["playerOne"])
            elif event.key == pygame.K_RIGHT:
                handle_key_right(game_data, 'up', game_data["playerOne"])
            elif event.key == pygame.K_UP:
                handle_key_up(game_data, 'up', game_data["playerOne"])
            elif event.key == pygame.K_DOWN:
                handle_key_down(game_data, 'up', game_data["playerOne"])
            elif event.key == pygame.K_a:
                handle_key_left(game_data, 'up', game_data["playerTwo"])
            elif event.key == pygame.K_d:
                handle_key_right(game_data, 'up', game_data["playerTwo"])
            elif event.key == pygame.K_w:
                handle_key_up(game_data, 'up', game_data["playerTwo"])
            elif event.key == pygame.K_s:
                handle_key_down(game_data, 'up', game_data["playerTwo"])    

#############                                           HANDLERS                                                   #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

##### FIRST PLAYER #####
def handle_key_left(game_data, key, entity):
    for p in entity:
        if key == 'down':
            p.movement = True
            p.left = True
            p.currMovement = 'Left'
        elif key == 'up':
            p.movement = False
            p.left = False
    return

def handle_key_right(game_data, key, entity):
    for p in entity:
        if key == 'down':
            p.movement = True
            p.right = True
            p.currMovement = 'Right'
        elif key == 'up':
            p.movement = False
            p.right = False
    return

def handle_key_up(game_data, key, entity):
    for p in entity:
        if key == 'down':
            p.movement = True
            p.up = True
            p.currMovement = 'Up'
        elif key == 'up':
            p.movement = False
            p.up = False
    return

def handle_key_down(game_data, key, entity):
    for p in entity:
        if key == 'down':
            p.movement = True
            p.down = True
            p.currMovement = 'Down'
        elif key == 'up':
            p.movement = False
            p.down = False
    return

def handle_key_shoot(game_data, key, entity):
    for p in entity:
        if len(p.projectiles) < 3:
            p.projectiles.append( Projectile(p.position, 10))
            for proj in p.projectiles:
                if proj.shooting == False:
                    proj.shooting = True
                    proj.facing = p.currMovement
    return


def handle_key_escape(game_data):
    game_data["quit_game"] = True
    return

########### DATA UPDATES ###########    
def update():
    line_did_reset = False

    # Rotate each line, and see if they reset at all
    for line in game_data["lines"]:
        line_did_reset = line.rotate()
        
    # Now we'll update the data for our circle(s)
    # Presently, that means looking for collisions with other line segments
    # Note: I did not put these methods into the class as they rely on global information
    for circle in game_data["circles"]:
        update_circle_line_collisions(circle)
        
        # Lets reset the position of the circle if the line reset
        if circle.colliding or circle.hit:
            circle.position = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            circle.hit = False
            line.collided = False
    
    for p1 in game_data["playerOne"]:
        update_player_line_collisions(p1)
        update_circle_player_collisions(p1)
        for proj in p1.projectiles:
            update_player_projectile_collisions(proj, p1, game_data["playerTwo"])
            p1.shot = False
        update_player(p1)
    
    for p2 in game_data["playerTwo"]:
        update_player_line_collisions(p2)
        update_circle_player_collisions(p2)
        for proj in p2.projectiles:
            update_player_projectile_collisions(proj, p2, game_data["playerOne"])
            p2.shot = False
        update_player(p2)

def update_player_projectile_collisions(projectile, player, target):
    # Look at every line and see if the input player collides with any of them; return if collided
    # Assume we aren't colliding

    if detect_collision_circ_circ(projectile, target, 'p'):
        projectile.shooting = False
        player.projectiles.remove(projectile)

def update_circle_player_collisions(player):
    # Look at every line and see if the input player collides with any of them; return if collided
    # Assume we aren't colliding
    player.point = False

    if detect_collision_circ_circ(player, game_data["circles"], 'c'):
        player.point = True

    return player.point

def update_player_line_collisions(player):
    # Look at every line and see if the input player collides with any of them; return if collided
    # Assume we aren't colliding
    player.colliding = False

    # We'll need to look at each of our lines, if we had more than one
    # If any of them are colliding, we can break out because we only need one
    for line in game_data["lines"]:
        # Look at each segment of the line
        for segment in line.segments:
            if detect_collision_line_circ(segment, player):
                player.colliding = True
                break

    return player.colliding

def update_circle_line_collisions(circle):
    # Look at every line and see if the input circle collides with any of them; return if collided
    # Assume we aren't colliding
    circle.colliding = False

    # We'll need to look at each of our lines, if we had more than one
    # If any of them are colliding, we can break out because we only need one
    for line in game_data["lines"]:
        # Look at each segment of the line
        for segment in line.segments:
            if detect_collision_line_circ(segment, circle):
                circle.colliding = True
                if line.collided == False:
                    line.collided = True
                    break

    return circle.colliding

def update_player(p):

    # change position to list so it can be modified
    p.position = list(p.position)

    # handle movement in all directions
    if p.left:
        if not(p.position[0] - p.radius - p.velocity < 0):
            p.position[0] -= p.velocity
    if p.right:
        if not(p.position[0] + p.radius + p.velocity > SCREEN_WIDTH):
            p.position[0] += p.velocity
    if p.up:
        if not(p.position[1] - p.radius - p.velocity < 30):
            p.position[1] -= p.velocity
    if p.down:
        if not(p.position[1] + p.radius + p.velocity > SCREEN_HEIGHT):
            p.position[1] += p.velocity
    
    # update player's projectiles movements
    update_proj(p)

    # change position back to tuple
    p.position = tuple(p.position)

    return


def update_proj(player):
        # handle projectile movement
    for proj in player.projectiles:
        proj.position = list(proj.position)
        if proj.shooting == True:
            if proj.facing == 'Left':
                if proj.position[0] - proj.velocity < 0:
                    player.projectiles.remove(proj)
                proj.position[0] -= proj.velocity
            if proj.facing == 'Right':
                if proj.position[0] + proj.radius*2 + proj.velocity > SCREEN_WIDTH:
                    player.projectiles.remove(proj)
                proj.position[0] += proj.velocity
            if proj.facing == 'Up':
                if proj.position[1] - proj.velocity < 30:
                    player.projectiles.remove(proj)
                proj.position[1] -= proj.velocity
            if proj.facing == 'Down':
                if proj.position[1] + proj.radius*2 + proj.velocity > SCREEN_HEIGHT:
                    player.projectiles.remove(proj)
                proj.position[1] += proj.velocity
        proj.position = tuple(proj.position)

########### RENDERING ###########
def render(screen):
    # clear the window surface (by filling it with black)
    bg = pygame.transform.scale(pygame.image.load("resources/pxl-bg.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
    # screen.fill( (30,30,30) )
    screen.blit(bg, (0, 30))

    # Draw score bar
    pygame.draw.rect(screen, (255,255,255), (0,0,SCREEN_WIDTH,30))
    
    i = 1
    # Draw the line(s)
    for line in game_data["lines"]:
        if i == 1:
            totalRotations = FONTS["countdown"].render(str(line.rotation), False, (150, 125, 116))
            text_img_rect = totalRotations.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(totalRotations, text_img_rect)
            i += 1
        line.render(screen)
    i = 1
    # Draw the circle(s)
    for circle in game_data["circles"]:
        circle.render(screen)


    # Draw the player(s)
    for p1 in game_data["playerOne"]:
        p1.render(screen)

        #draw p1 score
        p1Score = FONTS["score"].render(' Yarn: ' + str(p1.score), False, (255, 153, 0))
        text_img_rect = p1Score.get_rect(topright = (SCREEN_WIDTH - 150, 0))
        screen.blit(p1Score, text_img_rect)
        
        #draw p1 projectiles
        for proj in p1.projectiles:
            if proj.shooting == True:
                proj.render(screen)
    
    for p2 in game_data["playerTwo"]:
        p2.render(screen)

        #draw p2 score
        p2Score = FONTS["score"].render(' Yarn: ' + str(p2.score), False, (0, 0, 0))
        text_img_rect = p2Score.get_rect(topleft = (150, 0))
        screen.blit(p2Score, text_img_rect)
        
        #draw p2 projectiles
        for proj in p2.projectiles:
            if proj.shooting == True:
                proj.render(screen)
    
    # update the display
    pygame.display.update()      
    

def render_gameover(screen):
    # Draw a background
    pygame.draw.rect(screen, (200,230,200), Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    render_gameover_title(screen)
    render_gameover_text(screen)

    # And of course, update the screen
    pygame.display.update()

def render_gameover_title(screen):
    game_over = FONTS["gameover"].render('GAME OVER', False, (0, 0, 0))
    text_img_rect = game_over.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(game_over, text_img_rect)

def render_gameover_text(screen):
    
    for p1 in game_data["playerOne"]:
        scoreP1 = p1.score
    for p2 in game_data["playerTwo"]:
        scoreP2 = p2.score

    # find out who won!
    if scoreP1 > scoreP2:
        winner = FONTS["score"].render('Orange Cat Wins with ' + str(scoreP1) + ' balls of yarn!', False, (255, 255, 255))
    elif scoreP1 < scoreP2:
        winner = FONTS["score"].render('Black Cat Wins with ' + str(scoreP2) + ' balls of yarn!', False, (255, 255, 255))
    else:
        winner = FONTS["score"].render('A tie... how boring.', False, (255, 255, 255))

    # Then we find its bounding box, but adjusted as if it were centred in the screen centre
    text_img_rect = winner.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2+50))

    # Finally, we place it on the screen, using the image rect as the positioning reference
    screen.blit(winner, text_img_rect)  

############## CODE HELPERS ################
def detect_collision_circ_circ(p_circ, data, c_type):
    
    p_rad = p_circ.radius
    p_pos = list(p_circ.position)

    for circle in data:
        c_rad = circle.radius
        c_pos = list(circle.position)

    for line in game_data["lines"]:
        collided = line.collided

    # calculate total distance between centre of circles
    d_x = abs(p_pos[0] - c_pos[0])
    d_y = abs(p_pos[1] - c_pos[1])
    d_tot = math.sqrt(d_x **2 + d_y **2)

    # calculate total radius
    r_tot = p_rad + c_rad
    
    if c_type == 'c':
        # check if ball has already been hit
        if collided == False:
            if circle.hit == False:
                # compare distance to radius
                if d_tot < r_tot:
                    circle.hit = True
                    return True # they collided
        else:
            return False
    else:
        if d_tot < r_tot:
            circle.shot = True
            game_data["shotSound"].play()
            if circle.score > 0:
                circle.score -= 1
            
            return True # they collided
        else:
            return False

def detect_collision_line_circ(line_points, circle):
    # line_points is a pair of points, where each point is a tuple of (x, y) coordinates.
    # Eg. line_points = ( (0, 0), (100, 100) ) represents a line down and right.
    # circle is just a circle class
    
    # unpack u; a line is an ordered pair of points and a point is an ordered pair of co-ordinates
    (u_sol, u_eol) = line_points
    (u_sol_x, u_sol_y) = u_sol
    (u_eol_x, u_eol_y) = u_eol

    # unpack v; a circle is a center point and a radius (and a point is still an ordered pair of co-ordinates)
    (v_ctr, v_rad) = (circle.position, circle.radius)
    (v_ctr_x, v_ctr_y) = v_ctr

    # the equation for all points on the line segment u can be considered u = u_sol + t * (u_eol - u_sol), for t in [0, 1]
    # the center of the circle and the nearest point on the line segment (that which we are trying to find) define a line 
    # that is is perpendicular to the line segment u (i.e., the dot product will be 0); in other words, it suffices to take
    # the equation v_ctr - (u_sol + t * (u_eol - u_sol)) · (u_evol - u_sol) and solve for t
    
    t = ((v_ctr_x - u_sol_x) * (u_eol_x - u_sol_x) + (v_ctr_y - u_sol_y) * (u_eol_y - u_sol_y)) / ((u_eol_x - u_sol_x) ** 2 + (u_eol_y - u_sol_y) ** 2)

    # this t can be used to find the nearest point w on the infinite line between u_sol and u_sol, but the line is not 
    # infinite so it is necessary to restrict t to a value in [0, 1]
    t = max(min(t, 1), 0)
    
    # so the nearest point on the line segment, w, is defined as
    w_x = u_sol_x + t * (u_eol_x - u_sol_x)
    w_y = u_sol_y + t * (u_eol_y - u_sol_y)
    
    # Euclidean distance squared between w and v_ctr
    d_sqr = (w_x - v_ctr_x) ** 2 + (w_y - v_ctr_y) ** 2
    
    # if the Eucliean distance squared is less than the radius squared
    if (d_sqr <= v_rad ** 2):
    
        # the line collides
        return True  # the point of collision is (int(w_x), int(w_y))
        
    else:
    
        # the line does not collide
        return False

    # visit http://ericleong.me/research/circle-line/ for a good supplementary resource on collision detection



if __name__ == "__main__":
    main()
