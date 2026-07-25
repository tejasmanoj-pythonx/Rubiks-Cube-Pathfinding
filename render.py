import pygame
import numpy as np
import math

# Colours
bg_colour = (35, 35, 35)
black = (0, 0, 0)
white = (255, 255, 255)
red = (220, 30, 30)
green = (0, 130, 0)
blue = (0, 50, 150)
yellow = (255, 215, 10)
orange = (255, 135, 35)

camera_distance = 6
fov = 300
cube_scale = 0.45

# Rotation Matrices
def rotate_x(angle):
    x_rotation = np.array([
        [1, 0, 0],
        [0, math.cos(angle), -math.sin(angle)],
        [0, math.sin(angle), math.cos(angle)]
    ])
    return x_rotation

def rotate_y(angle):
    y_rotation = np.array([
        [math.cos(angle), 0, math.sin(angle)],
        [0, 1, 0],
        [-math.sin(angle), 0, math.cos(angle)]
    ])
    return y_rotation

def rotate_z(angle):
    z_rotation = np.array([
        [math.cos(angle), -math.sin(angle), 0],
        [math.sin(angle), math.cos(angle), 0],
        [0, 0, 1]
    ])
    return z_rotation

class Cubie:
    def __init__(self, grid_position):
        self.x = grid_position[0]
        self.y = grid_position[1]
        self.z = grid_position[2]

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

        self.vertices = (self.vertices * cube_scale) + grid_position

        if self.x == 1:
            right = red
        else:
            right = black
        if self.x == -1:
            left = orange
        else:
            left = black

        if self.y == 1:
            top = white
        else:
            top = black   
        if self.y == -1:
            bottom = yellow
        else:
            bottom = black

        if self.z == 1:
            front = green
        else:
            front = black   
        if self.z == -1:
            back = blue
        else:
            back = black

        self.faces = [
            ([4, 5, 6, 7], front),  # Front
            ([3, 2, 1, 0], back),   # Back
            ([3, 7, 6, 2], top),  # Top
            ([5, 4, 0, 1], bottom), # Bottom 
            ([6, 5, 1, 2], right),    # Right
            ([3, 0, 4, 7], left), # Left
        ]

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = pygame.display.get_window_size()[0]
        self.screen_height = pygame.display.get_window_size()[1]

        self.rotation = np.eye(3) # 3x3 Identity Matrix

        cubie_positions =[(-1, -1, -1), (-1, -1,  0), (-1, -1,  1),
                          (-1,  0, -1), (-1,  1, -1), ( 0, -1, -1),
                          ( 1, -1, -1), (-1,  0,  0), (-1,  0,  1),
                          (-1,  1,  0), (-1,  1,  1), ( 0, -1,  0),
                          ( 0, -1,  1), ( 0,  0, -1), ( 0,  0,  0),
                          ( 0,  0,  1), ( 0,  1, -1), ( 0,  1,  0),
                          ( 0,  1,  1), ( 1, -1,  0), ( 1, -1,  1),
                          ( 1,  0, -1), ( 1,  0,  0), ( 1,  0,  1),
                          ( 1,  1, -1), ( 1,  1,  0), ( 1,  1,  1)]

        self.cubies = []
        for position in cubie_positions:
            self.cubies.append(Cubie(position))
        
        self.animating = False
        self.increment_angle = 3
    
    def project_point(self, point):
        x = point[0]
        y = point[1]
        z = point[2]

        projected_x = int((x / (camera_distance - z)) * fov + (self.screen_width / 2))
        projected_y = int((y / (camera_distance - z)) * fov + (self.screen_height / 2))

        return projected_x, projected_y
    
    def draw_cube(self):
        self.screen.fill(bg_colour)
        self.animate_face()

        visible_faces = []
        for cubie in self.cubies:
            rotated = np.dot(cubie.vertices, self.rotation.T)

            projected = []
            for vertex in rotated:
                projected_point = self.project_point(vertex)
                projected.append(projected_point)
            
            
            for points, colour in cubie.faces:
                rotated_points = []
                for point in points[0:3]:
                    rotated_point = rotated[point]
                    rotated_points.append(rotated_point)

                vector1 = rotated_points[1] - rotated_points[0]
                vector2 = rotated_points[2] - rotated_points[0]
                normal_vector = np.cross(vector1, vector2)

                if normal_vector[2] <= 0:
                    continue

                z_total = 0
                for point in points:
                    z_total = z_total + rotated[point][2]
                z_average = z_total / 4


                vertices = []
                for point in points:
                    projected_point = projected[point]
                    vertices.append(projected_point)
                visible_faces.append((colour, vertices, z_average))
        
        visible_faces.sort(key=lambda depth: depth[2])

        for colour, vertices, z_average in visible_faces:
            pygame.draw.polygon(self.screen, colour, vertices)
        pygame.display.update()

    def get_cubies_face(self, face):
        face_cubies = []
    
        for cubie in self.cubies:
            x = cubie.x
            y = cubie.y
            z = cubie.z

            if face == "right" and x == 1:
                face_cubies.append(cubie)
            elif face == "left" and x == -1:
                face_cubies.append(cubie)
            elif face == "up" and y == 1:
                face_cubies.append(cubie)
            elif face == "down" and y == -1:
                face_cubies.append(cubie)
            elif face == "front" and z == 1:
                face_cubies.append(cubie)
            elif face == "back" and z == -1:
                face_cubies.append(cubie)
        return face_cubies

    def start_animating_face(self, face):
        self.animating = True
        self.face = face
        self.face_cubies = self.get_cubies_face(self.face)
        self.current_angle = 0
        print(face)

    def animate_face(self):
        if self.animating == False:
            return
        
        if self.current_angle == 90:
            self.animating = False
            return
        
        self.current_angle += self.increment_angle

        angle = math.radians(self.increment_angle)

        for cubie in self.face_cubies:
            if self.face == "right":
                rotation = rotate_x(angle)
            elif self.face == "left":
                rotation = rotate_x(angle*-1)
            elif self.face == "up":
                rotation = rotate_y(angle)
            elif self.face == "down":
                rotation = rotate_y(angle*-1)
            elif self.face == "front":
                rotation = rotate_z(angle)
            elif self.face == "back":
                rotation = rotate_z(angle*-1)
            
            cubie.vertices = np.dot(cubie.vertices, rotation.T)