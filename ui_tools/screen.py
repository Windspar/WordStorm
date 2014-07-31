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
    
class Handler(object):
    def __init__(self, caption, size, flags=0, depth=0):
        self.scenes = {}
        self.current_scene = Scene()
        
        self.screen = pygame.display.set_mode(size, flags, depth)
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        
    def get_size(self):
        return self.screen.get_size()
        
    def get_rect(self):
        return self.screen.get_rect()
        
    def loop(self, start_scene=None, fps=60):
        self.set_scene = start_scene
        self.running = True
        self.fps = fps
        while self.running:
            if self.set_scene:
                self.current_scene.leaving()
                self.current_scene = self.scenes[self.set_scene]
                self.current_scene.entrance()
                self.set_scene = None
        
            for event in pygame.event.get():
                self.current_scene.event(event)
                self.current_scene.auto_event(event)
                
            self.current_scene.blit(self.screen)
            self.current_scene.auto_blit(self.screen)
            tick = pygame.time.get_ticks()
            self.current_scene.update(tick)
            self.current_scene.auto_update(tick)
            
            pygame.display.flip()
            self.clock.tick(self.fps)
