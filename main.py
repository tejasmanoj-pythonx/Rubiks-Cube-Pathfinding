import pygame
import render

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Rubik's Cube Pathfinding")
        self.clock = pygame.time.Clock()
        self.running = False
        self.renderer = render.Renderer(self.screen)

    def run(self):
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.clock.tick(60)
            self.renderer.draw_cube()
        pygame.quit()

if __name__ == "__main__":
    main = Main()
    main.run()