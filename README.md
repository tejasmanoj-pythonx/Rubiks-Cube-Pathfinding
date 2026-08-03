# Rubiks-Cube-Pathfinding

Sources:<br>
https://en.wikipedia.org/wiki/Rotation_matrix<br>
https://en.wikipedia.org/wiki/3D_projection#Perspective_projection<br>
https://www.cube20.org/
https://www.cube20.org/<br>
https://en.wikipedia.org/wiki/Cross_product

**Rubiks Cube in General**<br>
The total amount of permutations for a rubiks cube is ~4.3 x 10^19 which is about 4 quintillion.<br>
Proven maximum of 20 moves to solve any scambled cube from any state (God's Number).<br>
Standard cube notation (U, D, F, B, L, R).

**How to Use Pathfinding to Solve the Cube**<br>
My intention is to treat the cube like a maze that A* can navigate.<br>
The algorithm is trying to find the shortest path from the scambled cube to the solved state.

**Heuristic**<br>
Heuristic in this case is basically a guess at how far am I from being solved.<br>
If the guess is bad, A* will be become slower as it is just brute force.<br>
If the guess is good, it will find the solution faster.

**Idea For an Admissable Heuristic**<br>
For each piece I should be asking how far is this piece from where it is supposed to be.<br>
Add up these distances to get a number that estimates how close the cube is to being solved.<br>
Do this because each sticker on the pieces don't actually tell you much by itself, whereas if a corner piece is next to where it is supposed to be, then the cube is closer to being solved then if that same piece was on the other side.

**Meaningful Pieces**<br>
There are 26 visbile pieces (center piece is not movable).<br>
Of these 26, 8 are corner pieces that show 3 stickers each and 12 edge pieces that show 2 stickers each.<br>
The remaining 6 pieces only 1 colour each but they never change position relative to eachother. <br>
This means that the centres define which colour belongs on which face.<br>
Since they don't move they would not be checked in the heuristic.<br>
Hence, there are 26-6=20 pieces that can move and need to be checked with the heuristic.

**How Would I Build This**<br>
Each of the 20 pieces has one correct home position when the cube is solved.<br>
This means for each piece I would have to check, Is the piece in the right position and is it twisted or flipped even if it is in the right spot.<br>
If a piece is in the incorrect spot, give it a cost based on roughly how many moves it is away.<br>
If it is in the right spot but twisted then give it a smaller cost.<br>
Take the largest cost across all the pieces so that the heuristic is still admissable as it should never guess higher than the true cost of moves.

**How Should I Store The Cube in Code?**<br>
Simplest way is probably to store a list of 54 colours.<br>
There are more complicated ways to track each individual piece's position and rotation, which is used in real solvers but looks kinda hard to setup.

**Math For 3D Rendering**<br>
1. **Perspective Projection**<br>
I need to use perspective projection to display a 3D object onto a 2D screen.
The formula for me would look something like:<br>
screen_x = (x / (camera_z - z)) * FOV + screen_width / 2<br>
screen_y = (y / (camera_z - z)) * FOV + screen_height / 2<br>
Where camera_z - z is the distance between the camera and the point along the depth axis.<br>
FOV is how zoomed in things would look.<br>
The screen_width / 2 and screen_height / 2 are so that the coordinates (0,0) are shifted to the center of the screen instead of the top left corner set by pygame.<br><br>
2. **Rotation Matrices**<br>
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
3. **How to Fix Faces Bleeding On Eachother (Back-Face Culling)**<br>
A cube has 6 faces, but when viewing it from any angle, at most 3 of them can ever be visible to the camera.<br> The other 3 faces are facing away from the camera and are on the far side.<br> By drawing all 6 faces, the ones facing away end up showing through as pygame doesn't understand that this shape is behind another shape in 3D.<br> It would just draw the shape in whatever order that it is programmed to, flat on the screen.<br>
Back-face culling solves this by not drawing the faces that are hidden to the camera and only rendering the ones that are visible.<br><br>
Every face of the cube has a normal vector, which is a direction perpindicular to the face's surface that points straight outwards from it.<br> If we imagine a 3D plane, the front face's normal would point toward the positive z direction, the top face's normal would point towards positive y and the right face's would point towards positive x.<br> Every face has only point vector pointing outward.<br><br>
If a face's normal was pointing roughly towards the camera, then the camera is looking at the front of that face meaning that it should be drawn. If the normal was pointing roughly away from the camera, then the camera is looking away from the face meaning it shouldn't be drawn.<br><br>
A face is made from 4 points, meaning that between each point is an edge.<br> If you were to take two of these edges as vectors and calculate their cross product, you would result with a vector that is perpindicular to both.<br> This new vector is the face's normal direction.<br> Of the four points only three will be needed as one point needs to be shared as both vectors will orginate from it.<br><br>
The cross product's direction depends on the order that the two edges are fed in.<br> By swapping the order the normal will point in the opposite direction.<br> This means that I have to be consistent in the order of vectors I am using for each face otherwise the normal will be pointing in the wrong way.<br><br>
Besides just fixing the face bleeding problem, culling faces also means that about half of them will never need to be projected of drawn at a given time.<br> For a single cube like right now, it might not be that much of a difference but once it becomes 27 of them it does become a meaningful optimisation.<br><br>  
4. **How to fix overlapping faces (Painter's algorithm)**<br>
Even after back-face culling removes the faces pointing away from the camera, multiple of the visible faces can overlap each other at certain angles.<br> Since pygame has no understanding which face is closer to the camera in 3D space, the faces get drawn in whatever order they were in the code, regardless of which one should actually be in front.<br> This causes a face that should be hidden behind another face to inccorectly "paint" on top of it.<br><br> 
The algorithm is named after a painter usually creates an artwork by painting the background first with the details on top. If the faces that are furthest away are drawb first and the closest faces are drawn last, each new layer is covering up what is behind it correctly.<br><br> 
An exact distance isn't really needed, really only a number that lets us compare the faces against eachother. From the projection formula we know that camera_z - z gives us the distance from the camera. This means that a face with a larger z_coordinate would be closer to the camera, and a face with a smaller z coordinate would be further.<br><br>
Since each face has 4 vertices, and they don't necessarily have to share the exact same z value after being rotated, we could take the average of all of the z values and use that number as a representation of the depth for that face.<br>
Depth = (z0 + z1 + z2 + z3) / 4<br><br>

**How to Animate Face Rotations?**<br>
Idea<br>
User will press a key like L for the left face to turn, then I will need to find the 9 cubies that are on that face do this by using the fact that either their x, y, or z will all have the same value.<br> Then for every frame rotate all the vertices by a small angle until it reaches 90 degrees.<br>

Steps to Implement<br>
1. Map all the keys to their respective faces like U for up and so on.
2. Find the 9 cubies that are on that face so for up, it would be where grid_position[1] == 1.
3. For every frame, apply a small rotation matrix, maybe like 2 or 3 degrees, to the cubies vertices, and then keep accumalating this rotation until 90 degrees is reached