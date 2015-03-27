import pygame
import pygame.font
import pygame.image
from pygame.locals import *

__all__ = ['init']

screen = None
background = None
bw = None
bh = None
surfarr = None
screenScale = None

fps = 0

def set_fps(v):
	global fps
	fps = v

def init(size = (640, 480), scale = 1, title = 'Simple Canvas'):
	global screen, background, surfarr, bw, bh, screenScale
	screenScale = scale
	pygame.init()
	screen = pygame.display.set_mode([x*scale for x in size])
	pygame.display.set_caption(title)
	bw, bh = size
	background = pygame.Surface(size).convert()
	background.fill((0,0,0))
	surfarr = pygame.PixelArray(background)
	return background

changed = False
runComplete = False

def clear(c):
	global changed
	changed = True
	background.fill(c)
	if runComplete:
		raise SystemError("Main thread die")

def load_image(image_name):
	return pygame.image.load(image_name)

def draw_image(x, y, image, scale = 1):
	global surfarr, changed
	changed = True
	del surfarr
	x=int(x)
	y=int(y)
	if scale == 1:
		background.blit(image, (x,y))
	else:
		sz = image.get_size()
		sz = [int(sz[0] * scale), int(sz[1] * scale)]
		newImage = pygame.transform.scale(image, sz)
		background.blit(newImage, (x,y))
	surfarr = pygame.PixelArray(background)

def text(x, y, text, size, color, font = None, antialias = False):
	x=int(x)
	y=int(y)
	global surfarr, changed
	changed = True
	if font is None:
		font = pygame.font.SysFont("", size)
	else:
		font = pygame.font.Font(font, size)
	surface = font.render(text, antialias, color)
	del surfarr
	background.blit(surface, (x,y))
	surfarr = pygame.PixelArray(background)

def putpixel(x, y, c):
	x=int(x)
	y=int(y)
	global changed
	changed = True
	if x >= 0 and x < bw and y >= 0 and y < bh:
		surfarr[x][y] = tuple(c)
	if runComplete:
		raise SystemError("Main thread die")

def oneloop():
	global changed
	if changed:
		changed = False
		pygame.transform.scale(background, screen.get_size(), screen)
		#screen.blit(background, (0,0))
		pygame.display.flip()

def run(f = None, eventHandler = None, 
		onMouseMotion = None, onMouseButtonUp = None, onMouseButtonDown = None,
		onKeyDown = None, onKeyUp = None, onUserEvent = None, onActivate = None
		):
	global runComplete, changed

	if eventHandler is None and any((onMouseMotion, onMouseButtonDown, onMouseButtonUp,
		 onKeyDown, onKeyUp, onActivate, onUserEvent)):
		eventHandler = Dispatcher()
		if onMouseMotion: eventHandler.OnMouseMotion = onMouseMotion
		if onMouseButtonUp: eventHandler.OnMouseButtonUp = onMouseButtonUp
		if onMouseButtonDown: eventHandler.OnMouseButtonDown = onMouseButtonDown
		if onKeyDown: eventHandler.OnKeyDown = onKeyDown
		if onKeyUp: eventHandler.OnKeyUp = onKeyUp
		if onUserEvent: eventHandler.OnUserEvent = onUserEvent
		if onActivate: eventHandler.OnActivate = onActivate

	import threading
	class Runner(threading.Thread):
		def run(self):
			f()

	t = Runner()
	t.daemon = False
	t.start()
	clock = pygame.time.Clock()
	changed = True
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				runComplete = True
				return
			elif eventHandler:
				eventHandler(event)
		clock.tick(fps)
		if t.isAlive() or changed:
			oneloop()

def mainloop(updateHandler = None, eventHandler = None, 
		onMouseMotion = None, onMouseButtonUp = None, onMouseButtonDown = None,
		onKeyDown = None, onKeyUp = None, onUserEvent = None, onActivate = None
		):

	if eventHandler is None and any((onMouseMotion, onMouseButtonDown, onMouseButtonUp,
		 onKeyDown, onKeyUp, onActivate, onUserEvent)):
		eventHandler = Dispatcher()
		if onMouseMotion: eventHandler.OnMouseMotion = onMouseMotion
		if onMouseButtonUp: eventHandler.OnMouseButtonUp = onMouseButtonUp
		if onMouseButtonDown: eventHandler.OnMouseButtonDown = onMouseButtonDown
		if onKeyDown: eventHandler.OnKeyDown = onKeyDown
		if onKeyUp: eventHandler.OnKeyUp = onKeyUp
		if onUserEvent: eventHandler.OnUserEvent = onUserEvent
		if onActivate: eventHandler.OnActivate = onActivate

	clock = pygame.time.Clock()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif eventHandler:
				eventHandler(event)
		if updateHandler:
			updateHandler()
		clock.tick(fps)
		oneloop()

class Dispatcher(object):
	def __call__(self, event):
		if event.type == ACTIVEEVENT:
			self.OnActivate(event.gain, event.state)
		elif event.type == KEYDOWN:
			self.OnKeyDown(event.key, event.mod)
		elif event.type == KEYUP:
			self.OnKeyUp(event.key, event.mod)
		elif event.type == USEREVENT:
			self.OnUserEvent(event.code)
		elif event.type == MOUSEMOTION:
			self.OnMouseMotion([x//screenScale for x in event.pos], [x*1.0/screenScale for x in event.rel], event.buttons)
		elif event.type == MOUSEBUTTONUP:
			self.OnMouseButtonUp([x//screenScale for x in event.pos], event.button)
		elif event.type == MOUSEBUTTONDOWN:
			self.OnMouseButtonDown([x//screenScale for x in event.pos], event.button)

	def OnUserEvent(self, code):
		pass
	def OnActivate(self, gain, state):
		pass
	def OnKeyDown(self, key, mod):
		pass
	def OnKeyUp(self, key, mod):
		pass
	def OnMouseButtonUp(self, pos, button):
		pass
	def OnMouseButtonDown(self, pos, button):
		pass
	def OnMouseMotion(self, pos, rel, buttons):
		pass

