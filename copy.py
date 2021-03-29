# import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import copy 

Left_pressed = False
Right_pressed = False
degree1 = 0.
degree2 = 0.
init_pos = np.array([0,0])
eye = np.array([0.,0.,.1])
at = np.array([0.,0.,0.])
cameraUp = np.array([0.,1.,0.])
scale = 1.
trans = np.array([0.,0.,0.])
t1 = 0.


full_list = []
START_FLAG = False
ENABLE_FLAG = False
tree = []
motion_start = 0 
sum_channel = 0
cur_index = 0
count = 0
Frames = 0

class Node:
    def __init__(self, name=""):
        self.name = name
        self.offset = np.zeros(3)
        self.child = []

class Skeleton:
    def __init__(self, root=None, joint_num=0):
        self.root = root
        self.joint_num = joint_num

class Posture:
    def __init__(self, origin=[], Rmatrix_list=[]):
        self.origin = origin
        self.Rmatrix = Rmatrix_list

class Motion:
    def __init__(self, skeleton=None, postures=[], frames=0):
        self.skeleton = skeleton
        self.postures = postures
        self.frames = frames

class Parsing:
    def __init__(self):
        self.joint_num = 0
        self.frames = 0
    
    # Make tree structure for parsing hierarchical model
    # make_tree(full_list, root, 0, channel_list)
    def make_tree(self, full_list, parent, line_num, channel_list):
        while True:
            line = full_list[line_num].lstrip().split(' ')
            if line[0] == "JOINT" or line[0] == "ROOT":
                self.joint_num += 1
                new_node = Node(line[1].rstrip('\n'))
                # offset
                offset_data = full_list[line_num+2].lstrip().split(' ')
                new_Node.offset = np.array([float(offset_data[1]),float(offset_data[2]),float(offset_data[3])])
                # channel
                channel_data = full_list[line_num+3].lstrip().split(' ')
                for j in range(3):
                    channel = channel_data[2+j].rstrip('\n')
                    if channel == "XROTATION" or channel == "Xrotation":
                        channel_list.append("X")
                    elif channel == "YROTATION" or channel == "Yrotation":
                        channel_list.append("Y")
                    elif channel == "ZROTATION" or channel == "Zrotation":
                        channel_list.append("Z")
                
                if(line[0] != "ROOT"):
                    parent.child.append(new_node)
                line_num += 4
                parent = new_node
                line_num, channel_list = make_tree(full_list, parent, line_num, channel_list)
                parent = new_node
            elif line[0] == "End":
                new_Node = Node("__END__")
                # offset
                offset_data = full_list[line_num+2].lstrip().split(' ')
                new_Node.offset = np.array([float(offset_data[1]),float(offset_data[2]),float(offset_data[3])])
                
                parent.child.append(new_node)
                line_num += 3
            elif line[0] == '}\n':
                line_num += 1
                return line_num, channel_list
            else:
                line_num += 1
        
    def make_postures(self, full_list, start_line_num, channel_list):
        line_num = start_line_num + 3
        self.frames = int((full_list[line_num-1].split('\t'))[1])
        postures = []
        for i in range(self.frames):
            line = full_list[line_num+i].split(' ')
            posture = Posture()
            posture.origin = [float(line[0]), float(line[1]), float(line[2])]
            for j in range(self.joint_num):
                M = np.identity(4)
                for k in range(3):
                    R = np.identity(4)
                    channel_value = channel_list[3*j+k]
                    th = np.radians(float(line[3*(j+1)+k])
                    if channel_value == "X":
                        R[:3,:3] = [[1., 0., 0.],
                                    [0., np.cos(th), -np.sin(th)],
                                    [0., np.sin(th), np.cos(th)]
                                    ]
                    elif channel_value == "Y":
                        R[:3,:3] = [[np.cos(th), 0., np.sin(th)],
                                    [0., 1., 0.],
                                    [-np.sin(th), 0., np.cos(th)]
                                    ]
                    elif channel_value == "Z":
                        R[:3,:3] = [[np.cos(th), -np.sin(th), 0.],
                                    [np.sin(th), np.cos(th), 0.],
                                    [0., 0., 1.]
                                    ]
                    M = M @ R
                posture.Rmatrix.append(M)
            posture.Rmatrix[0][:-1,3] = posture.origin
            postures.append(posture)
        
        return postures
     
class Draw:
    def __init__(self, motion):
        self.motion = motion
    
    def drawframe(self):
        glBegin(GL_LINES)
        glColor3ub(255,0,0)
        glVertex3fv(np.array([-.1,0.,0.]))
        glVertex3fv(np.array([.1,0.,0.]))
        glColor3ub(0,255,0)
        glVertex3fv(np.array([0.,-.1,0.]))
        glVertex3fv(np.array([0.,.1,0.]))
        glColor3ub(0,0,255)
        glVertex3fv(np.array([0.,0.,-.1]))
        glVertex3fv(np.array([0.,0.,.1]))
        glEnd()

    def createVertexAndIndexArrayIndexed(self):
        varr = np.array([
                (-0.5773502691896258, 0.5773502691896258, 0.5773502691896258),
                ( -1 ,  1 ,  1 ), # v0
                (0.8164965809277261, 0.4082482904638631, 0.4082482904638631),
                (  1 ,  1 ,  1 ), # v1
                (0.4082482904638631, -0.4082482904638631, 0.8164965809277261),
                (  1 , -1 ,  1 ), # v2
                (-0.4082482904638631, -0.8164965809277261, 0.4082482904638631),
                ( -1 , -1 ,  1 ), # v3
                (-0.4082482904638631, 0.4082482904638631, -0.8164965809277261),
                ( -1 ,  1 , -1 ), # v4
                (0.4082482904638631, 0.8164965809277261, -0.4082482904638631),
                (  1 ,  1 , -1 ), # v5
                (0.5773502691896258, -0.5773502691896258, -0.5773502691896258),
                (  1 , -1 , -1 ), # v6
                (-0.8164965809277261, -0.4082482904638631, -0.4082482904638631),
                ( -1 , -1 , -1 ), # v7
                ], 'float32')
        iarr = np.array([
                (0,2,1),
                (0,3,2),
                (4,5,6),
                (4,6,7),
                (0,1,5),
                (0,5,4),
                (3,6,2),
                (3,7,6),
                (1,2,6),
                (1,6,5),
                (0,7,3),
                (0,4,7),
                ])
        return varr, iarr

    def drawCube_glDrawElements(self):
        global gVertexArrayIndexed, gIndexArray
        varr = gVertexArrayIndexed
        iarr = gIndexArray
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
        glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
        glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT,iarr)

    def get_RotationM(self, offset):
        a = 1.0
        b = np.sqrt(np.dot(offset,offset))
        temp = offset - np.array([1.0,0.,0.])
        c = np.sqrt(np.dot(temp,temp))
        th = np.arccos((a*a + b*b - c*c)/(2.*a*b))
        u = np.cross(np.array([1.0,0.,0.]),offset)
        u /= np.sqrt(np.dot(u,u))
        R = np.array([[np.cos(th)+u[0]*u[0]*(1.-np.cos(th)), u[0]*u[1]*(1.-np.cos(th))-u[2]*np.sin(th), u[0]*u[2]*(1.-np.cos(th))+u[1]*np.sin(th)],
                    [u[1]*u[0]*(1.-np.cos(th))+u[2]*np.sin(th), np.cos(th)+u[1]*u[1]*(1.-np.cos(th)), u[1]*u[2]*(1.-np.cos(th))-u[0]*np.sin(th)],
                    [u[2]*u[0]*(1.-np.cos(th))-u[1]*np.sin(th), u[2]*u[1]*(1.-np.cos(th))+u[0]*np.sin(th), np.cos(th)+u[2]*u[2]*(1.-np.cos(th))]
                    ])
        return R

    def draw_proper_cube(self, offset):
        global gVertexArrayIndexed
        M = np.identity(4)
        half = np.sqrt(np.dot(offset,offset)) / 2.
        M[:3,:3] = get_RotationM(offset)
        
        glPushMatrix()
        glMultMatrixf(M.T)
        glTranslatef(half,0.,0.)
        scale_x = half * 0.9
        scale_yz = scale_x * 0.2 
        glScalef(scale_x, scale_yz, scale_yz)
        drawCube_glDrawElements()
        glPopMatrix()

# motion_index = 0
# def draw_Model(node,motion_data):
#     global motion_index
#     # End site
#     glPushMatrix()
#     M = np.identity(4)
#     if node.channel_count == 0:
#         ###cube draw
#         draw_proper_cube(node.offset)
#         #######
#     # joint & root
#     else:
#         # root
#         if node.tree_index == 0:
#             glTranslatef(motion_data[0],motion_data[1],motion_data[2])
#             motion_index = 3
#         ######cube draw
#         draw_proper_cube(node.offset)
#         #######
#         M[:-1,3] = [node.offset[0], node.offset[1], node.offset[2]]
        
#         for i in node.channel:
#             R = np.identity(4)
#             th = np.radians(motion_data[motion_index])
#             if i == "XROT":
#                 R[:3,:3] = [[1., 0., 0.],
#                             [0., np.cos(th), -np.sin(th)],
#                             [0., np.sin(th), np.cos(th)]
#                             ]
#             elif i == "YROT":
#                 R[:3,:3] = [[np.cos(th), 0., np.sin(th)],
#                             [0., 1., 0.],
#                             [-np.sin(th), 0., np.cos(th)]
#                             ]
#             elif i == "ZROT":
#                 R[:3,:3] = [[np.cos(th), -np.sin(th), 0.],
#                             [np.sin(th), np.cos(th), 0.],
#                             [0., 0., 1.]
#                             ]
#             M = M @ R
#             motion_index += 1
#         glMultMatrixf(M.T)
    
#         for child in node.child:
#             draw_Model(child,motion_data)
#     glPopMatrix()

def render():
    global full_list, START_FLAG, ENABLE_FLAG, motion_start, tree, sum_channel, cur_index, motion_index, Frames, count
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-scale,scale,-scale,scale,-1,1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    real_eye = eye + trans
    real_at = at + trans
    gluLookAt(real_eye[0],real_eye[1],real_eye[2],real_at[0],real_at[1],real_at[2],cameraUp[0],cameraUp[1],cameraUp[2])
    
    drawframe()
    drawgrid()
    
    glPushMatrix()
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_LIGHT3)
    glEnable(GL_LIGHT4)
    glEnable(GL_NORMALIZE)
    
    # Light setting
    lightPos0 = (1., 1., 1., 1.)
    lightPos1 = (1., 1., -1., 1.)
    lightPos2 = (-1., 1., 1., 1.)
    lightPos3 = (-1., 1., -1., 1.)
    lightPos4 = (0., -1., 0., 0.)
    glLightfv(GL_LIGHT0,GL_POSITION,lightPos0)
    glLightfv(GL_LIGHT1,GL_POSITION,lightPos1)
    glLightfv(GL_LIGHT2,GL_POSITION,lightPos2)
    glLightfv(GL_LIGHT3,GL_POSITION,lightPos3)
    glLightfv(GL_LIGHT4,GL_POSITION,lightPos4)
    
    lightColor1 = (.45, .45, .45, .45)
    lightColor2 = (.3, .3, .3, .3)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT0,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT0,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT1,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT1,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT1,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT2,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT2,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT2,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT3,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT3,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT3,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT4,GL_DIFFUSE,lightColor2)
    glLightfv(GL_LIGHT4,GL_SPECULAR,lightColor2)
    glLightfv(GL_LIGHT4,GL_AMBIENT,ambientLightColor)
    
    # Object color setting
    objectColor = (.3, .3, .7, 1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,100)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    motion_data = []
    scale_ratio = 0.3

    # Drawing
    if ENABLE_FLAG: 
        if START_FLAG:
            if count == Frames:
                cur_index = motion_start + 3
                count = 0
            motion_data = full_list[cur_index].split(' ')
            if len(motion_data) == 1:
                motion_data = full_list[cur_index].split('\t')
            for i in range(sum_channel):
                motion_data[i] = float(motion_data[i])
            cur_index += 1
            count += 1
        else:
            motion_data = np.zeros(sum_channel)
        glColor3ub(0,0,200)
        glScalef(scale_ratio,scale_ratio,scale_ratio)
        motion_index = 0
        draw_Model(tree[0], motion_data)
    
    glDisable(GL_LIGHTING)
    glPopMatrix()

def button_callback(window,button,action,mod):
    global Left_pressed,Right_pressed,init_pos
    if action == glfw.PRESS:
        init_pos = glfw.get_cursor_pos(window)
        
        if button == glfw.MOUSE_BUTTON_LEFT:
            Left_pressed = True
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            Right_pressed = True
    elif action == glfw.RELEASE:
        if button == glfw.MOUSE_BUTTON_LEFT:
            Left_pressed = False
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            Right_pressed = False

def cursor_callback(window,xpos,ypos):
    global eye,at,degree1,degree2,trans,cameraUp
    if Left_pressed:
        degree1 += (init_pos[0] - xpos) * 0.02
        degree2 += (-init_pos[1] + ypos) * 0.02
        if degree2 >= 0.:
            degree2 %= 360.
        else:
            degree2 %= -360.
        
        if 90. <= degree2 and degree2 <= 270.:
            cameraUp[1] = -1.
        elif -90. >= degree2 and degree2 >= -270.:
            cameraUp[1] = -1.
        else:
            cameraUp[1] = 1.
        eye[0] = 0.1 * np.cos(np.radians(degree2)) * np.sin(np.radians(degree1))
        eye[1] = 0.1 * np.sin(np.radians(degree2))
        eye[2] = 0.1 * np.cos(np.radians(degree2)) * np.cos(np.radians(degree1))
        
    elif Right_pressed:
        cameraFront = eye - at
        temp1 = np.cross(cameraFront,cameraUp)
        u = temp1/np.sqrt(np.dot(temp1,temp1))
        temp2 = np.cross(u,cameraFront)
        w = temp2/np.sqrt(np.dot(temp2,temp2))
        trans += u *(-init_pos[0]+xpos)*0.0001
        trans += w *(-init_pos[1]+ypos)*0.0001
        
def scroll_callback(window,xoffset,yoffset):
    global scale
    if scale <= 0.1 and yoffset == 1:
        scale = 0.1
        return
    scale -= 0.1 * yoffset

def drop_callback(window,paths):
    global full_list, ENABLE_FLAG, START_FLAG
    
    ENABLE_FLAG = True
    START_FLAG = False
    file_name = ''.join(paths)
    file = open(file_name,'r')
    full_list = file.readlines()
    make_tree()
    print("File name: %s"%(file_name))
    print_data()
    print("###########################################################")
    file.close()

def key_callback(window, key, scancode, action, mods):
    global START_FLAG
    if action==glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_SPACE:
            START_FLAG = True
            
gVertexArrayIndexed = None
gIndexArray = None
def main():
    
    global t1, gVertexArrayIndexed, gIndexArray
    if not glfw.init():
        return
    t1 = glfw.get_time()
    window = glfw.create_window(700,700,'2015004302', None,None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_cursor_pos_callback(window,cursor_callback)
    glfw.set_mouse_button_callback(window,button_callback)
    glfw.set_scroll_callback(window,scroll_callback)
    glfw.set_drop_callback(window,drop_callback)
    glfw.set_key_callback(window,key_callback)
    glfw.swap_interval(1)
    
    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()