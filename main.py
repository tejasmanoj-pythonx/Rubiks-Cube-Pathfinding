import pygame
import render
import numpy as np

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Rubik's Cube Pathfinding")
        self.clock = pygame.time.Clock()
        self.running = False
        self.renderer = render.Renderer(self.screen)

        self.drag = False
        self.mouse_position = (0, 0)

    def run(self):
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if self.renderer.animating == False:
                        if event.key == pygame.K_r or event.key == pygame.K_1:
                            self.renderer.start_animating_face("right", 3)
                        elif event.key == pygame.K_l or event.key == pygame.K_2:
                            self.renderer.start_animating_face("left", 3)
                        elif event.key == pygame.K_u or event.key == pygame.K_3:
                            self.renderer.start_animating_face("up", 3)
                        elif event.key == pygame.K_d or event.key == pygame.K_4:
                            self.renderer.start_animating_face("down", 3)
                        elif event.key == pygame.K_f or event.key == pygame.K_5:
                            self.renderer.start_animating_face("front", 3)
                        elif event.key == pygame.K_b or event.key == pygame.K_6:
                            self.renderer.start_animating_face("back", 3)
                        elif event.key == pygame.K_s:
                            self.renderer.scramble()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.drag = True
                    self.mouse_position = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.drag = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.drag:
                        x_current = pygame.mouse.get_pos()[0]
                        y_current = pygame.mouse.get_pos()[1]

                        x_difference = x_current - self.mouse_position[0]
                        y_difference = y_current - self.mouse_position[1]

                        x_angle = 0.005 * y_difference
                        y_angle = 0.005 * x_difference

                        x_rotated = render.rotate_x(x_angle)
                        y_rotated = render.rotate_y(y_angle)

                        combined = np.dot(y_rotated, x_rotated)
                        self.renderer.rotation = np.dot(combined, self.renderer.rotation)
                        
                        self.mouse_position = pygame.mouse.get_pos()

            self.clock.tick(60)
            self.renderer.draw_cube()
        pygame.quit()

if __name__ == "__main__":
    main = Main()
    main.run()