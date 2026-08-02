import pygame      # Used for creating the window and event handling.
import render      # Used for importing the Renderer class and rotation matrix functions.
import numpy as np # Used for combining matrices with matrix dot product.

# Main class handles the pygame window, the game loop, and all the event handling. 
class Main:
    def __init__(self):
        pygame.init()                                          # Initialise the pygame modules
        self.screen = pygame.display.set_mode((800, 600))      # Sets the height and width of the pygame window
        pygame.display.set_caption("Rubik's Cube Pathfinding") # Sets the title of the pygame window
        self.clock = pygame.time.Clock()                       # Used to control the frame rate of the window
        self.running = False                                   # Used to start and stop the pygame window
        self.renderer = render.Renderer(self.screen)           # Initialise the Renderer class from render.py and pass in self.screen so it can draw directly onto the pygame surface.

        # Used for the mouse drag state. 
        # self.drag becomes true when the left mouse button is pressed and false when it is released.
        # mouse_position stores where the mouse was on the previous frame so that we can calculate how for it moved on each MOUSEMOTION event.
        self.drag = False
        self.mouse_position = (0, 0)

    def run(self):
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Checks if the user clicks the window's close button.
                    self.running = False      # Setting running to false to exit the while loop and into the pygame.quit().
    
                elif event.type == pygame.KEYDOWN: # Check for any keypress.
                    # Only allow these key presses if there is nothing being animated.
                    # If it was allowed the cubies would move around into eachother overlapping and deform the cube.
                    # The start_animating_face() method takes in what face to be animated and the incremental angle for each frame.
                    # The incremental angle is the amount all the cubies are being moved in the direction of the rotation.
                    # A greater angle means each frame the distance moved is further giving the effect that it is moving faster.
                    # This is why scramble() method uses an angle of 9 instead of 3 so that the 10 consecutive moves finish faster.
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

                # Handles the cube rotation using mouse drag.
                elif event.type == pygame.MOUSEBUTTONDOWN: 
                    # Check if either the left or right mouse button is pressed down.
                    # Change the drag state to True and record the current mouse position as the starting point.
                    # Used for the MOUSEMOTION event as a reference to compare positions and find the distance in mouse movements.
                    self.drag = True
                    self.mouse_position = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Check if either the left or right mouse button is pressed up.
                    # Change the drag state to false so that it stops rotating the cube.
                    self.drag = False
                elif event.type == pygame.MOUSEMOTION:
                    # Only rotate the cube if the user is actively dragging.
                    if self.drag:
                        # Get the current x and y position of the mouse
                        x_current = pygame.mouse.get_pos()[0]
                        y_current = pygame.mouse.get_pos()[1]

                        # Find the difference between the current x and y from the starting x and y.
                        # x_difference is the horizontal distance so a positive x moves rightwards and vice versa.
                        # y_difference is the vertical distance but due to pygame's positive y value moving downwards, the vertical movement is inverted.
                        # To counteract this we multiple the y value by -1 to flip the axis so that positive y moves up and vice versa.
                        x_difference = x_current - self.mouse_position[0]
                        y_difference = (y_current - self.mouse_position[1])*-1

                        # Convert the differences in x and y into rotation angles.
                        # 0.005 is the sensitivity that scales everything down to smaller angle.
                        # y_difference controls the rotation of the x axis as rotating upon it moves it up and down.
                        # x_difference controls the rotation of the y axis as rotating upon it moves it left and right.
                        x_angle = 0.005 * y_difference
                        y_angle = 0.005 * x_difference

                        # Make 2 rotation matrices that account for the rotation from the mouse differences.
                        # Combine these two rotation matrices into one so that it can be directly multiplied in one go.
                        x_rotated = render.rotate_x(x_angle)
                        y_rotated = render.rotate_y(y_angle)
                        combined = np.dot(x_rotated, y_rotated)

                        # Multiple the combined rotation matrices into the render's already accumulated rotation.
                        self.renderer.rotation = np.dot(combined, self.renderer.rotation)
                        
                        # Make this mouse position the new starting point for the next iteration.
                        self.mouse_position = pygame.mouse.get_pos()

             # Sets the frame rate of the window to 60 frames per second.
            self.clock.tick(60)

            # Clears the screen, draws all the visible faces in order of their depth and then updates the display.
            # It's called every frame regardless if anything needs to be animated or not. 
            self.renderer.draw_cube() 
        pygame.quit()

# Only run when this specific file is the main program.
# Instantiate the Main class and call the run() method.
if __name__ == "__main__":
    main = Main()
    main.run()