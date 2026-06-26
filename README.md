# Rubiks-Cube-Pathfinding

Rubiks Cube in General<br>
The total amount of permutations for a rubiks cube is ~4.3 x 10^19 which is about 4 quintillion.<br>
Proven maximum of 20 moves to solve any scambled cube from any state (God's Number).<br>
Standard cube notation (U, D, F, B, L, R).

How to Use Pathfinding to Solve the Cube<br>
My intention is to treat the cube like a maze that A* can navigate.<br>
The algorithm is trying to find the shortest path from the scambled cube to the solved state.

Heuristic<br>
Heuristic in this case is basically a guess at how far am I from being solved.<br>
If the guess is bad, A* will be become slower as it is just brute force.<br>
If the guess is good, it will find the solution faster.

Idea For an Admissable Heuristic<br>
For each piece I should be asking how far is this piece from where it is supposed to be.<br>
Add up these distances to get a number that estimates how close the cube is to being solved.<br>
Do this because each sticker on the pieces don't actually tell you much by itself, whereas if a corner piece is next to where it is supposed to be, then the cube is closer to being solved then if that same piece was on the other side.

Meaningful Pieces<br>
There are 26 visbile pieces (center piece is not movable).<br>
Of these 26, 8 are corner pieces that show 3 stickers each and 12 edge pieces that show 2 stickers each.<br>
The remaining 6 pieces only 1 colour each but they never change position relative to eachother. <br>
This means that the centres define which colour belongs on which face.<br>
Since they don't move they would not be checked in the heuristic.<br>
Hence, there are 26-6=20 pieces that can move and need to be checked with the heuristic.

How Would I Build This<br>
Each of the 20 pieces has one correct home position when the cube is solved.<br>
This means for each piece I would have to check, Is the piece in the right position and is it twisted or flipped even if it is in the right spot.<br>
If a piece is in the incorrect spot, give it a cost based on roughly how many moves it is away.<br>
If it is in the right spot but twisted then give it a smaller cost.<br>
Take the largest cost across all the pieces so that the heuristic is still admissable as it should never guess higher than the true cost of moves.

How Should I Store The Cube in Code<br>
Simplest way is probably to store a list of 54 colours.<br>
There are more complicated ways to track each individual piece's position and rotation, which is used in real solvers but looks kinda hard to setup.

Math For 3D Rendering<br>
1. Perspective Projection <br>
I need to use perspective projection to display a 3D object onto a 2D screen.
The formula for me would look something like:<br>
screen_x = (x / (camera_z - z)) * FOV + screen_width / 2<br>
screen_y = (y / (camera_z - z)) * FOV + screen_height / 2<br>
Where camera_z - z is the distance between the camera and the point along the depth axis.<br>
FOV is how zoomed in things would look.<br>
screen_width / 2 and screen_height / 2 are so that the coordinates (0,0) are shifted to the center of the screen instead of the top left corner set by pygame.<br><br>
2. Rotation Matrices<br>
The cube needs to spin so that the user can see all angles, meaning that all the vertices need to be rotated before being projected.<br>
The formula for each axis is given as:<br>
x = [1   0        0  ]
    [0 cos(a) -sin(a)]
    [0 sin(a)  cos(a)]<br>
y = [cos(a) 0 sin(a)]
    [0 1 0]
    [-sin(a) 0 cos(a)]<br>
z = [cos(a) -sin(a) 0]
    [sin(a) cos(a) 0]
    [0 0 1]<br><br>