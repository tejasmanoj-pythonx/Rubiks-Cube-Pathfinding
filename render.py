import pygame
import numpy as np

# Colours
bg_colour = (35, 35, 35)
black = (0, 0, 0)
white = (255, 255, 255)
red = (220, 30, 30)
green = (0, 130, 0)
blue = (0, 50, 150)
yellow = (255, 215, 10)
orange = (255, 135, 35)

camera_distance = 5
fov = 300

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = pygame.display.get_window_size()[0]
        self.screen_height = pygame.display.get_window_size()[1]

        self.vertices = np.array([
            [-1, -1, -1],
            [ 1, -1, -1],
            [ 1,  1, -1],
            [-1,  1, -1],
            [-1, -1,  1],
            [ 1, -1,  1],
            [ 1,  1,  1],
            [-1,  1,  1],
        ])

        self.faces = [
            ([4, 5, 6, 7], green),  # Front
            ([0, 1, 2, 3], blue),   # Back
            ([2, 3, 6, 7], white),  # Top
            ([0, 1, 4, 5], yellow), # Bottom 
            ([1, 2, 5, 6], red),    # Right
            ([0, 3, 4, 7], orange), # Left
        ]
    
    def project_point(self, point):
        x = point[0]
        y = point[1]
        z = point[2]

        projected_x = int((x / (camera_distance - z)) * fov + (self.screen_width / 2))
        projected_y = int((y / (camera_distance - z)) * fov + (self.screen_height / 2))

        return projected_x, projected_y
    
    def draw_cube(self):
        self.screen.fill(bg_colour)

        projected = []
        for vertex in self.vertices:
            projected_point = self.project_point(vertex)
            projected.append(projected_point)
        
        for points, colour in self.faces:
            vertices = []
            for point in points:
                projected_point = projected[point]
                vertices.append(projected_point)
            pygame.draw.polygon(self.screen, colour, vertices)
        
        pygame.display.update()