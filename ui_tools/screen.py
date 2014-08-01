import pygame

class Scene(object):
    def __init__(self):
        self.internal_events = {}
        self.internal_blits = []
        self.internal_updates = []
        
    def entrance(self): pass
    def leaving(self): pass
    def blit(self, surface): pass
    def auto_blit(self, surface):
        for item in self.internal_blits:
            item(surface)
    
    def update(self, tick): pass    
    def auto_update(self, tick):
        for item in self.internal_updates:
            item(tick)
    
    def event(self, event): pass
    def auto_event(self, event):
        if self.internal_events.get(event.type, None):
            for callback in self.internal_events[event.type]:
                callback(event)
    
    def bind_event(self, pygame_event, callback):
        self.internal_events[pygame_event] = self.internal_events.get(pygame_event, []) + [callback]
        
    def bind_blit(self, callback):
        self.internal_blits.append(callback)
        
    def bind_update(self, callback):
        self.internal_updates.append(callback)
        
class handler(object):
    scenes = {}
    fps = None
    running = True
    set_scene = None
    rect = None        
    
class Handler(object):
    def __init__(self, caption, size, flags=0, depth=0):
        handler.scenes = {}
        handler.rect = pygame.Rect((0,0), size)
        self.current_scene = Scene()
        self.screen = pygame.display.set_mode(size, flags, depth)
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        
    
    def loop(self, start_scene=None, fps=60):
        handler.set_scene = start_scene
        handler.running = True
        handler.fps = fps
        while handler.running:
            if handler.set_scene:
                self.current_scene.leaving()
                self.current_scene = handler.scenes[handler.set_scene]
                self.current_scene.entrance()
                self.mouseover = False
                handler.set_scene = None
        
            for event in pygame.event.get():
                self.current_scene.event(event)
                self.current_scene.auto_event(event)
                
            self.current_scene.blit(self.screen)
            self.current_scene.auto_blit(self.screen)
            tick = pygame.time.get_ticks()
            self.current_scene.update(tick)
            self.current_scene.auto_update(tick)
            
            pygame.display.flip()
            self.clock.tick(handler.fps)
