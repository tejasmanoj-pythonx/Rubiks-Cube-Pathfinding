import pygame      # Used to draw squares and update the display.
import numpy as np # Used to format lists into matrices and perform matrix operations like dot and cross product.
import math        # Used for the sine and cosine functions in the rotation matrices.
import random      # Used to pick random faces for the scramble() method.

# Colours
# Each colour is a tuple that represents an RGB value, three values between 0 and 255.
# Each value represents how much red, green and blue is mixed together.
bg_colour = (35, 35, 35) # This is used for the background of the pygame window.
black = (0, 0, 0) # This is used for colouring the faces that are within the cube.

# These are the standard Rubik's cube colours.
white = (255, 255, 255)
red = (220, 30, 30)
green = (0, 130, 0)
blue = (0, 50, 150)
yellow = (255, 255, 0)
orange = (255, 135, 35)

# camera_distance is how far back along the z axis the camera is sitting.
# The middle of the cube is at x, y and z all equalling 0.
# This means we are sitting at about 6 units away from the middle of the cube, otherwise we would be inside the cube. 
camera_distance = 6 

# fov is the scale factor that controls how zoomed into the cube we are.
# A larger value would make the cube look bigger on the screen and vice versa.
fov = 300 

# Each cubie is originally two units and went from -1 to +1 on each axis making the size 2 (-1 to 0, 0 to +1).
# So by multiplying by 0.5 we reduce the size to 1 but because they are all 1 unit away from each other on the grid it gives the effect that the 27 cubies are all combined into 1 big cube.
# To fix this instead of multiplying by 0.5 we go a little under to leave a gap between them, in this case each cubie would be 0.9 units and each gap is 0.1 units.
cube_scale = 0.45

# Rotation Matrices
# When a point is multiplied by one of these matrices, it returns a new point rotated by that angle upon that respective axis.
# Each of these functions takes the angle in radians and returns the rotation matrix as a 3x3 numpy array.
# It's used for the mouse drag and face turns.

# Rotating around the X axis moves the cube up and down which is also known as pitch.
def rotate_x(angle):
    x_rotation = np.array([
        [1, 0, 0],
        [0, math.cos(angle), -math.sin(angle)],
        [0, math.sin(angle), math.cos(angle)]
    ])
    return x_rotation

# Rotating around the Y axis moves the cube left and right which is also known as yaw.
def rotate_y(angle):
    y_rotation = np.array([
        [math.cos(angle), 0, math.sin(angle)],
        [0, 1, 0],
        [-math.sin(angle), 0, math.cos(angle)]
    ])
    return y_rotation

# Rotating around the Z axis moves the cube clockwise or counter clockwise which is also known as roll.
# This isn't needed for mouse drag but is used for animating the front and back turns.
def rotate_z(angle):
    z_rotation = np.array([
        [math.cos(angle), -math.sin(angle), 0],
        [math.sin(angle), math.cos(angle), 0],
        [0, 0, 1]
    ])
    return z_rotation

# A cubie is one of 27 small cubes that make up the rubik's cube.
# Each cubie has a position on the 3x3x3 grid, and have 8 vertices within that position. 
class Cubie:
    def __init__(self, grid_position):
        # Split the grid position into it's respective x, y and z.
        # Each value is either -1, 0 or 1.
        self.x = grid_position[0]
        self.y = grid_position[1]
        self.z = grid_position[2]

        # There are 8 vertices for each cubie where each vertex is a corner of the cubie.
        self.vertices = np.array([
            [-1, -1, -1], # left, bottom, back
            [ 1, -1, -1], # right, bottom, back
            [ 1,  1, -1], # right, top, back
            [-1,  1, -1], # left, top, back
            [-1, -1,  1], # left, bottom, front
            [ 1, -1,  1], # right, bottom, front
            [ 1,  1,  1], # right, top, front
            [-1,  1,  1], # left, top, front
        ])

        # Scale the cubie down and then shift it to it's respective grid position.
        # Numpy treats cube_scale as a scalar value and applies it individually to every number in the matrix.
        # Numpy also does the addition by adding the tuple grid position, to each row in the matrix. 
        self.vertices = (self.vertices * cube_scale) + grid_position

        # This decides which colour each face gets depending on the cubie's grid position.
        # A face only gets its actual colour if it is on the outer surface of the entire cube.
        # Inner faces would become black because they are squished between a neighbouring cubie's face, meaning that it wouldn't show on a real cube.
        # Corner cubies would be true for 3 if conditions and hence have 3 colours.
        # Edge cubies would be true for 2 if conditions and hence have 2 colours.
        # The cubies that are on the centre of each face would be true for 1 if condition and hence have 1 colour.
        # The cubie in the very centre at 0, 0, 0 wouldn't satisfy any of these which is why it is entirely black.
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

        # self.faces is a list of 6 tuples, one for each face.
        # Each tuple has a list of 4 vertices that are the corners that make up that face, and what colour to draw that face.
        # This specific order of vertices was chosen to when iterated over go around in a circular motion, this is known as the winding order of the face. 
        # We have to keep the winding order consistent because otherwise later on when we caclulate the normal for each face, the cross product would result in a vector facing the opposite direction.
        self.faces = [
            ([4, 5, 6, 7], front),  # Front
            ([3, 2, 1, 0], back),   # Back
            ([3, 7, 6, 2], top),    # Top
            ([5, 4, 0, 1], bottom), # Bottom 
            ([6, 5, 1, 2], right),  # Right
            ([3, 0, 4, 7], left),   # Left
        ]

# Renderer class does everything that's visual, stores the 27 cubies, projects the 3D points onto the 2D screen, runs back face culling, sorts faces by depth and draws them with pygame.
class Renderer:
    def __init__(self, screen):
        # Take the window from the Main class along with it's dimensions.
        self.screen = screen
        self.screen_width = pygame.display.get_window_size()[0]
        self.screen_height = pygame.display.get_window_size()[1]

        # Used as the camera rotation matrix.
        # It starts as an identity matrix meaning that no rotation has been applied yet.
        # Every frame all cubie vertices are multiplied by this matrix before projection so that the cube rotates together as one object.
        # The mouse drag from main.py multiply small rotations into this matrix so that the rotation can accumulate.
        self.rotation = np.eye(3)

        # All 27 grid positions are listed here as tuples.
        # A Cubie object is created for each of these positions and stored in self.cubies.
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
        
        # self.animating is true while a face turn is in progress, and false while it isn't.
        # It is used to block multiple turns trying to animate at the same time in main.py and is also checked in draw_cube() to start the next scrambled face.
        self.animating = False

        # self.choices acts as a queue and is a list of face names that are applied in that order.
        # scramble() fills this list with 10 random faces and draw_cube() will animate it and remove from it, on move at a time, only when the previous is done animating.
        self.choices = []
    
    # Converts a single 3D point into a 2D screen point.
    def project_point(self, point):
        # Split the point into it's respesctive x, y and z.
        x = point[0]
        y = point[1]
        z = point[2]

        # Uses the standard perspective projection formula.
        # camera_distance - z is the distance between the camera and the point along the z axis.
        # Dividing by this is what gives the perspective effect.
        # Adding self.screen_width / 2 and self.screen_height / 2 moves the origin from pygame's default which is the top left, to the centre of the screen.
        # This is done so that the point 0, 0, 0 would project to the middle of the screen.
        # int() converts the values into whole numbers because screen coordinates can't be floats.
        projected_x = int((x / (camera_distance - z)) * fov + (self.screen_width / 2))
        projected_y = int((y / (camera_distance - z)) * fov + (self.screen_height / 2))

        return projected_x, projected_y
    
    # Called every frame to redraw the entire cube.
    def draw_cube(self):
        # First check if the scramble queue has anything moves pending and there is nothing being currently animated.
        # If so then start animating that face which is the first argument and remove it from the queue.
        # The second arguement is the incremental angle, which controls the speed for the face turns.
        # An angle of 9 means the face is rotating for 10 frames up til 90 degrees.
        # This is faster than the regular 3 degree turns as it can take time for 10 moves to be animated.
        if not self.animating and self.choices:
            self.start_animating_face(self.choices[0], 9)
            self.choices.pop(0)

        self.screen.fill(bg_colour) # Clear the screen by painting over it with grey.
        self.animate_face()         # Rotate any points that need to be turned.

        # visible_faces is a list holding all the faces that passes the back face culling for all 27 cubies before anything is being drawn.
        visible_faces = []
        for cubie in self.cubies:
            # Apply the rotation from mouse drag to every vertex.
            # The .T stands for transpose and in this case is used to switch self.rotation from being a matrix meant for column vectors to instead be for row vectors.
            # self.rotation was meant to be used against a point that would be in the form of a column (3x1).
            # cubie.vertices stores all 8 points as rows so they are defined as row vectors.
            # This means when applying the dot product the rotation is reversed because of the mismatch.
            # Using the transpose we fix this mismatch without changing any values just the fact that it is now in row vector form.
            rotated = np.dot(cubie.vertices, self.rotation.T)

            # Project all 8 rotated vertices into 2D screen coordinates.
            projected = []
            for vertex in rotated:
                projected_point = self.project_point(vertex)
                projected.append(projected_point)
            
            for points, colour in cubie.faces:
                # Back face culling is used to skip drawing faces that aren't pointing towards the camera.
                # It works by first taking a point in a face and the two points directly next to it.
                # Then find the differences between the adjacent points from the origin point, these are two  vectors.
                # After calculating the cross product between these two vectors, we get another vector that is perpendicular to both vectors in the Z dimension.
                # This new vector is called the normal, when it is pointing towards the camera, the Z would be positive and vice versa.
                # This means any faces with negative normals don't need to be drawn and are culled out, hence skipped.
                rotated_points = []
                for point in points[0:3]:
                    rotated_point = rotated[point]
                    rotated_points.append(rotated_point)

                vector1 = rotated_points[1] - rotated_points[0]
                vector2 = rotated_points[2] - rotated_points[0]
                normal_vector = np.cross(vector1, vector2)

                if normal_vector[2] <= 0:
                    continue

                # Add all four points from a face and divide by 4 for the average Z value of that face.
                # This is done only for the Z value because it represents how close the face is to the camera.
                # This average is  how far the face as a whole is from the camera.
                # We have to use the 3D Z values because the projected point doesn't have a Z value.
                z_total = 0
                for point in points:
                    z_total = z_total + rotated[point][2]
                z_average = z_total / 4

                # Make a list of 2D points that have passed back face culling and have their z_average calculated, passed alongside it's colours and vertices to later be drawn. 
                vertices = []
                for point in points:
                    projected_point = projected[point]
                    vertices.append(projected_point)
                visible_faces.append((colour, vertices, z_average))
        
        # Sort all the visible faces from all cubies together by their z_average which is index 2 in visible faces.
        # The smallest z_average would be further away from the camera and will hence be drawn first.
        # The largest z_average would be closer to the camera and will hence be drawn last.
        # This is painter's algorithm where you draw the background first and then progress your way to the foreground.
        # This is so that you are painting over faces that are behind them and doesn't cause any colours to bleed through.
        visible_faces.sort(key=lambda depth: depth[2])

        # Draw each square onto the pygame window using it's respective colour and points.
        for colour, vertices, z_average in visible_faces:
            pygame.draw.polygon(self.screen, colour, vertices)
        pygame.display.update()

    # Returns 9 cubies that belong to the given face.
    def get_cubies_face(self, face):
        face_cubies = []
    
        for cubie in self.cubies:
            x = cubie.x
            y = cubie.y
            z = cubie.z

            # Uses the x, y and z grid positions to check which face each cubie belongs to.
            # For example, all cubies on the right would share x as 1 and would therefore belong to the right turn.
            # The grid positions are always updated after a turn is completed so that this function will select the correct cubies to belong to a face.
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

    # Used to start an animation by setting up all the information animate_face() needs to perform a face turn.
    def start_animating_face(self, face, angle):
        # animate_face() needs to know what face to animate, what cubies are in that face and the speed of the animation which is given in degrees.
        # Passing in 3 degrees are for manual face turns and finish in 90 degrees / 3 degrees = 30 frames.
        # Passing in 9 degrees are for scramble face turns and finish in 90 degrees / 9 degrees = 10 frames.
        self.animating = True
        self.face = face
        self.face_cubies = self.get_cubies_face(self.face)
        self.current_angle = 0
        self.increment_angle = angle

    # Used at the start of every draw_cube() call to animate any face turns if needed.
    def animate_face(self):
        # If no face turns needs to be animated then return immediately. 
        if self.animating == False:
            return
        
        # Once the face has finished a complete 90 degree turn stop animating in the future.
        if self.current_angle == 90:
            self.animating = False
            
            # Make a 90 degree rotation matrix for this face.
            # This is applied once so that the cubie's grid position is updated to it's new location
            # Since pi is a transcendental number, the numbers past the decimal point go on forever.
            # This means when using the rotation matrices the values are only an estimate and are eventually rounded.
            # This causes an issue called floating point error and is not really noticed when using the rotation matrix once.
            # But if we were to do 30 3 degree turns the ever so slight floating point error would accumulate and break the cube.
            angle = math.radians(90)
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
            
                # Apply the 90 degree turn to the cubies old grid position.
                # Then take that position, apply the rotation and use that as the new grid position.
                # round() is used because all the grid positions need to be whole numbers and negate any issues with floating point.
                old_position = np.array([cubie.x, cubie.y, cubie.z])
                new_position = np.dot(rotation, old_position)
                cubie.x = int(round(new_position[0]))
                cubie.y = int(round(new_position[1]))
                cubie.z = int(round(new_position[2]))

            return
        
        # Add the increment angle onto the current animation angle. 
        self.current_angle += self.increment_angle

        # Make a 3 or 9 degree rotation matrix.
        # This works the same way as the 90 degree turn but instead uses the increment angle of 3 or 9.
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
            
            # Apply the rotation onto the cubie's vertices.
            # This is permanently changes the vertex position for every frame.
            # Due to the earlier reasons floating point error does occur here.
            # round() cannot be used to fix this because rotation doesn't necessarily need to be a whole number.
            cubie.vertices = np.dot(cubie.vertices, rotation.T)
    
    # Fills a self.choices with 10 random face names.
    def scramble(self):
        # draw_cube() will remove a face, one move at a time so that the 10 chosen moves will be animated in sequence.
        # The reason why it is 10 moves as any longer will make the algorithm take too long to solve.
        faces = ["right", "left", "up", "down", "front", "back"]
        for i in range(10):
            choice = random.choice(faces)
            self.choices.append(choice)