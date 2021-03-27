import pygame
from pygame.locals import *
import numpy as np
import random as r
import math

np.random.seed(int(r.random()*999999))
screen_width = 1200
screen_height = 800

# This function returns a boolean for whether pos2 (a point in the form of (x, y)) is to the left of an
# imaginary ray drawn from pos1 (a point in the form of (x, y)) at an angle of theta (in radians).
# Given pos1, theta, and pos2, is pos2 to the left of the ray drawn through pos1 at the angle theta?
def left_of(pos1, theta, pos2):
  theta %= math.pi * 2
  a = pos2[0] - pos1[0]
  b = pos2[1] - pos1[1]
  dist = math.sqrt(a * a + b * b)
  if dist == 0:
    return True
  theta2 = math.acos(a / dist)
  if b < 0:
    theta2 = math.pi * 2 - theta2
  if theta <= math.pi:
    if theta2 > theta and theta2 <= theta + math.pi:
      return True
    else:
      return False
  else:
    if theta2 < theta and theta2 >= theta - math.pi:
      return False
    else:
      return True
      
def dist(pos1, pos2):
  return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

class Brain:

  num_input_nodes = 2
  num_hidden_layers = 1
  size_hidden_layers = 20
  num_output_nodes = 3

  def __init__(self, w1, b1, wbh, w2, b2):
    self.w1 = w1
    self.b1 = b1
    self.wbh = wbh
    self.w2 = w2
    self.b2 = b2
    
  def calc(self, inputs):
    z1 = inputs.dot(self.w1) + self.b1
    a1 = np.tanh(z1)
    ah = a1
    for wh, bh in self.wbh:
      zh = ah.dot(wh) + bh
      ah = np.tanh(zh)
    z2 = ah.dot(self.w2) + self.b2
    a2 = np.tanh(z2)
    return a2
    
  def list_from_brain(self):
    array = np.append(self.w1, self.b1)
    for wh, bh in self.wbh:
      array = np.append(np.append(array, wh), bh)
    return np.append(np.append(array, self.w2), self.b2).tolist()

  @staticmethod
  def random_brain():
    w1 = np.random.randn(Brain.num_input_nodes, Brain.size_hidden_layers)
    b1 = np.random.randn(1, Brain.size_hidden_layers)
    
    wbh = []
    for i in range(Brain.num_hidden_layers-1):
      wh = np.random.randn(Brain.size_hidden_layers, Brain.size_hidden_layers)
      bh = np.random.randn(1, Brain.size_hidden_layers)
      wbh.append((wh, bh))

    w2 = np.random.randn(Brain.size_hidden_layers, Brain.num_output_nodes)
    b2 = np.random.randn(1, Brain.num_output_nodes)
    return Brain(w1, b1, wbh, w2, b2)
  
  @staticmethod
  def brain_from_list(array):
    w1_end = Brain.num_input_nodes * Brain.size_hidden_layers
    b1_end = w1_end + Brain.size_hidden_layers
    w1_part = array[:w1_end]
    b1_part = array[w1_end:b1_end]
    w1 = np.asarray(np.array_split(w1_part, Brain.num_input_nodes))
    b1 = np.asarray([b1_part])
    
    wbh = []
    wbh_end = b1_end
    for i in range(Brain.num_hidden_layers-1):
      wh_end = wbh_end + (Brain.size_hidden_layers ** 2)
      bh_end = wh_end + Brain.size_hidden_layers
      wh_part = array[wbh_end:wh_end]
      bh_part = array[wh_end:bh_end]
      wh = np.asarray(np.array_split(wh_part, Brain.size_hidden_layers))
      bh = np.asarray([bh_part])
      wbh.append((wh, bh))
      wbh_end = bh_end
      
    w2_end = wbh_end + (Brain.size_hidden_layers * Brain.num_output_nodes)
    b2_end = w2_end + Brain.num_output_nodes
    w2_part = array[wbh_end:w2_end]
    b2_part = array[w2_end:b2_end]
    w2 = np.asarray(np.array_split(w2_part, Brain.size_hidden_layers))
    b2 = np.asarray([b2_part])
    
    return Brain(w1, b1, wbh, w2, b2)
  
  
class Bot:
  
  dtheta_max = math.pi / 16
  
  def __init__(self, color=None, brain=None):
    self.color = color
    self.brain = brain
    if brain is None:
      self.brain = Brain.random_brain()
    if color is None:
      self.color = Bot.random_color()
    self.health = 1.0
    self.num_updates = 0
    self.x = r.random() * screen_width
    self.y = r.random() * screen_height
    self.speed = 0.
    self.theta = 0.
    self.dtheta = 0.
    self.width = 20
    self.height = 20
    self.building_wall = False
    self.current_wall = None
       
  def get_dna(self):
    dna = self.brain.list_from_brain()
    for value in self.color:
      dna.append((value-127.5)/127.5)
    return dna
    
  def mutate(self):
    dna = self.get_dna()
    num_mut = int(r.random() * 10)
    for i in range(num_mut):
      index = int(r.random() * len(dna))
      dna[index] = r.random() * 2 - 1
    return Bot.bot_from_dna(dna)
    
  def draw(self, screen):
    x1 = int(self.x + self.width * math.cos(self.theta))
    y1 = int(self.y + self.height * math.sin(self.theta))
    x2 = int(self.x)
    y2 = int(self.y)
    pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.width)
    pygame.draw.line(screen, (0, 0, 0), (x1, y1), (x2, y2), 6)
    width = int(self.width * (self.health if self.health < 1 else 1))
    left = self.x - self.width / 2
    top = self.y + self.height / 2 + 2
    height = 3
    screen.fill((255, 0, 0), Rect(left, top, self.width, height))
    screen.fill((0, 255, 0), Rect(left, top, width, height))
    
  def update(self, engine):
    self.num_updates += 1
    self.health -= 0.002
  
    food_distr = 100000000
    food_distl = 100000000

    for food in engine.foods:
      food_dist = dist((self.x, self.y), (food.x, food.y))
      left = left_of((self.x, self.y), self.theta, (food.x, food.y))
      if left:
        if food_dist < food_distl:
          food_distl = food_dist
      else:
        if food_dist < food_distr:
          food_distr = food_dist
          
    inputs = [[food_distl, food_distr]]
    outputs = self.brain.calc(np.asarray(inputs))
    self.speed = outputs[0][0]
    self.dtheta = outputs[0][1]
    self.building_wall = outputs[0][2] >= 0
    if abs(self.speed) > 1:
      self.speed /= abs(self.speed) # This makes speed either 1 or -1      
    if abs(self.dtheta) > 1:
      self.dtheta /= abs(self.dtheta)
    if not self.building_wall:
      self.current_wall = None
    
  def move(self, engine):
    if self.building_wall:
      if self.current_wall is None:
        self.current_wall = Wall(self.color)
        engine.add_wall(self.current_wall)
      self.current_wall.add_point((int(self.x), int(self.y)))
    self.theta += self.dtheta * Bot.dtheta_max
    self.x += 5 * self.speed * math.cos(self.theta)
    self.y += 5 * self.speed * math.sin(self.theta)
    
    for food in engine.foods:
      if dist((self.x, self.y), (food.x, food.y)) <= self.width:
        self.health += 0.05
        engine.foods.remove(food)
 
  @staticmethod
  def random_color():
    return (r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))
 
  @staticmethod
  def bot_from_dna(dna):
    color = (int(127.5*dna[-3]+127.5), int(127.5*dna[-2]+127.5), int(127.5*dna[-1]+127.5))
    brain = Brain.brain_from_list(dna[0:-3])
    return Bot(color, brain)
  
  @staticmethod
  def make_child(bot1, bot2):
    dna1 = bot1.get_dna()
    dna2 = bot2.get_dna()
    dna = []
    for i in range(len(dna1)):
      if r.random() > 0.5:
        dna.append(dna1[i])
      else:
        dna.append(dna2[i])
    new_bot = Bot.bot_from_dna(dna)
    if r.random() < 0.2:
      new_bot = new_bot.mutate()
    return new_bot


class Wall:
  def __init__(self, color=Bot.random_color()):
    self.color = color
    self.points = []
    self.num_updates = 0
    
  def add_point(self, point):
    if len(self.points) > 0:
      if dist(point, self.points[-1]) > 10:
        self.points.append(point)
    else:
     self.points.append(point)
    
  def draw(self, screen):
    if len(self.points) > 1:
      pygame.draw.lines(screen, self.color, False, self.points, 2)
    
  def update(self):
    self.num_updates += 1
    
class Food:
  def __init__(self):
    self.x = int(r.random() * screen_width)
    self.y = int(r.random() * screen_height)
    
  def draw(self, screen):
    pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 3)


class Engine:
  def __init__(self, num_bots):
    self.all_bots = []
    self.bots = []
    self.recent_bots = []
    self.walls = []
    self.foods = []
    self.num_bots = num_bots
    self.num_updates = 0
    
  def draw(self, screen):
    for bot in self.bots:
      bot.draw(screen)
    for wall in self.walls:
      wall.draw(screen)
    for food in self.foods:
      food.draw(screen)
    screen.fill((0, 0, 0), Rect(0, 0, 250, 100))
    font = pygame.font.SysFont("monospace", 15)
    text = font.render("Number of bots: " + str(len(self.all_bots)), 0, (255, 255, 255))
    text2 = font.render("Highest Fitness: " + str(self.all_bots[0].num_updates), 0, (255, 255, 255))
    avg_fitness = 0
    if len(self.recent_bots) > 0:
      avg_fitness = sum(map(lambda bot: bot.num_updates, self.bots)) / len(self.bots)
    text3 = font.render("Avgerage Fitness: " + str(avg_fitness), 0, (255, 255, 255))
    screen.blit(text, (20, 20))
    screen.blit(text2, (20, 40))
    screen.blit(text3, (20, 60))
      
  def update(self):
    self.num_updates += 1
    if self.num_updates % 2000 == 0:
      self.all_bots.sort(key=lambda bot: -bot.num_updates)
      f = open("log.txt", "a")
      f.write("\n\nUpdate #: " + str(self.num_updates))
      f.write("\n" + str(self.all_bots[0].get_dna()))
      f.write("\nHighest Fitness: " + str(self.all_bots[0].num_updates))
      f.close()
    remove_bots = []
    for bot in self.bots:
      bot.update(self)
      if bot.health <= 0:
        remove_bots.append(bot)
    for bot in remove_bots:
      self.bots.remove(bot)
      self.recent_bots.append(bot)
    while len(self.recent_bots) > self.num_bots:
      self.recent_bots.remove(self.recent_bots[0])
    
    if len(self.bots) < self.num_bots:
      self.all_bots.sort(key=lambda bot: -bot.num_updates)
      reproduce_bots = self.recent_bots[:] + self.bots[:]
      reproduce_bots.sort(key=lambda bot: -bot.num_updates)
      good_bots = reproduce_bots[:5]
      for i in range(2):
        good_bots.append(r.choice(reproduce_bots[5:]))
      while len(self.bots) < self.num_bots:
        bot1 = r.choice(good_bots)
        bot2 = r.choice(good_bots)
        if bot1 != bot2:
          new_bot = Bot.make_child(bot1, bot2)
          self.add_bot(new_bot)
    
    remove_walls = []
    for wall in self.walls:
      wall.update()
      if wall.num_updates > 200:
        remove_walls.append(wall)
    for wall in remove_walls:
      self.walls.remove(wall)
      
    while len(self.foods) < 100:
      self.foods.append(Food())
      
  def move(self):
    for bot in self.bots:
      bot.move(self)
      
  def add_bot(self, bot):
    self.bots.append(bot)
    self.all_bots.append(bot)
    if len(self.recent_bots) < self.num_bots:
      self.recent_bots.append(bot)
    
  def add_wall(self, wall):
    self.walls.append(wall)


pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('Genetic Programming Example')
clock = pygame.time.Clock()
running = True

engine = Engine(20)
for i in range(20):
  engine.add_bot(Bot())

while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      quit()
    elif event.type == KEYDOWN:
      if event.unicode == 'r':
        running = not running

  if running:
    engine.update()
    engine.move()
    screen.fill((0, 0, 0))
    engine.draw(screen)
    pygame.display.update()
  #clock.tick(30)