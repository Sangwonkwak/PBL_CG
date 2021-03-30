# import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
# import copy

import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic




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
    def make_tree(self, full_list, parent, line_num, channel_list):
        # print(line_num[0])
        while True:
            # print(line_num[0])
            line = full_list[line_num[0]].lstrip().split(' ')
            if line[0] == "JOINT" or line[0] == "ROOT":
                self.joint_num += 1
                new_node = Node(line[1].rstrip('\n'))
                # offset
                offset_data = full_list[line_num[0]+2].lstrip().split(' ')
                new_node.offset = np.array([float(offset_data[1]),float(offset_data[2]),float(offset_data[3])])
                # channel
                channel_data = full_list[line_num[0]+3].lstrip().split(' ')
                # print(self.joint_num)
                for j in range(3):
                    if line[0] == "ROOT":
                        j += 3
                    channel = channel_data[2+j].rstrip('\n')
                    if channel == "XROTATION" or channel == "Xrotation":
                        channel_list.append("X")
                    elif channel == "YROTATION" or channel == "Yrotation":
                        channel_list.append("Y")
                    elif channel == "ZROTATION" or channel == "Zrotation":
                        channel_list.append("Z")
                print(len(channel_list))

                if line[0] != "ROOT":
                    parent.child.append(new_node)
                else:
                    parent = new_node
                line_num[0] += 4
                # parent = new_node
                # print(new_node.name)
                self.make_tree(full_list, new_node, line_num, channel_list)
                # parent = new_node
                # print(new_node.name)
            elif line[0] == "End":
                new_node = Node("__END__")
                # offset
                offset_data = full_list[line_num[0]+2].lstrip().split(' ')
                new_node.offset = np.array([float(offset_data[1]),float(offset_data[2]),float(offset_data[3])])
                
                parent.child.append(new_node)
                line_num[0] += 3
                self.make_tree(full_list, new_node, line_num, channel_list)
                
            elif line[0] == '}\n':
                line_num[0] += 1
                return
                
            elif line[0] == "MOTION\n":
                return
            else:
                line_num[0] += 1
        
    def make_postures(self, full_list, start_line_num, channel_list):
        # get frames
        temp_frame= full_list[start_line_num+1].split(' ')
        if len(temp_frame) == 1:
            temp_frame = full_list[start_line_num+1].split('\t')
        self.frames = int(temp_frame[1])

        line_num = start_line_num + 3
        postures = []
        # print(self.frames)
        # print(self.joint_num)
        # print(len(channel_list))
        for i in range(self.frames):
            line = full_list[line_num+i].split(' ')
            posture = Posture()
            posture.origin = [float(line[0]), float(line[1]), float(line[2])]
            for j in range(self.joint_num):
                M = np.identity(4)
                for k in range(3):
                    R = np.identity(4)
                    channel_index = 3*j+k
                    # print(channel_index)
                    channel_value = channel_list[3*j+k]
                    th = np.radians(float(line[3*(j+1)+k]))
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
    def __init__(self, event_handle):
        self.event_handle = event_handle
        self.varr = None
        self.iarr = None
        self.cur_index = 0
    
    def drawgrid(self):
        for i in range(21):
            glPushMatrix()
            glBegin(GL_LINES)
            glColor3ub(80,80,80)
            glVertex3fv(np.array([-1.0+0.1*i,0.,1.0]))
            glVertex3fv(np.array([-1.0+0.1*i,0.,-1.0]))
            glVertex3fv(np.array([1.0,0.,-1.0+0.1*i]))
            glVertex3fv(np.array([-1.0,0.,-1.0+0.1*i]))
            glEnd()
            glPopMatrix()
    
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
        self.varr = np.array([
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
        self.iarr = np.array([
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
        
    def drawCube_glDrawElements(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 6*self.varr.itemsize, self.varr)
        glVertexPointer(3, GL_FLOAT, 6*self.varr.itemsize, ctypes.c_void_p(self.varr.ctypes.data + 3*self.varr.itemsize))
        glDrawElements(GL_TRIANGLES, self.iarr.size, GL_UNSIGNED_INT,self.iarr)

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
        M = np.identity(4)
        half = np.sqrt(np.dot(offset,offset)) / 2.
        M[:3,:3] = self.get_RotationM(offset)
        
        glPushMatrix()
        glMultMatrixf(M.T)
        glTranslatef(half,0.,0.)
        scale_x = half * 0.9
        scale_yz = scale_x * 0.2 
        glScalef(scale_x, scale_yz, scale_yz)
        self.drawCube_glDrawElements()
        glPopMatrix()

    # draw_Model(motion.skeleton.root, index), index의 0은 몇번째 posture 사용할지 1은 몇번째 Rmatrix 사용할지
    def draw_Model(self, node, index):
        glPushMatrix()
        # End site
        if node.name == "__END__":
            self.draw_proper_cube(node.offset)
        
        # joint & root
        else:
            self.draw_proper_cube(node.offset)
            glTranslatef(node.offset[0], node.offset[1], node.offset[2])
            M = self.event_handle.motion.postures[index[0]][index[1]]
            glMultMatrixf(M.T)
            index[1] += 1

            for child in node.child:
                self.draw_Model(child, index)
        glPopMatrix()
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        scale = self.event_handle.scale
        glOrtho(-scale,scale,-scale,scale,-1,1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        real_eye = self.event_handle.eye + self.event_handle.trans
        real_at = self.event_handle.at + self.event_handle.trans
        cameraUp = self.event_handle.cameraUp
        gluLookAt(real_eye[0],real_eye[1],real_eye[2],real_at[0],real_at[1],real_at[2],cameraUp[0],cameraUp[1],cameraUp[2])
        
        self.drawframe()
        self.drawgrid()
        
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
        
        # # Model drawing
        # if self.event_handle.timeline_changed:
        #     self.cur_index = self.event_handle.timeline
        #     self.event_handle.timeline_changed = False
        
        # scale_ratio = 0.3
        # if self.event_handle.ENABLE_FLAG:
        #     myMotion = self.event_handle.motion
        #     if self.cur_index == myMotion.frames:
        #         self.event_handle.START_FLAG = False
        #     index = [self.cur_index, 0]
        #     if self.event_handle.START_FLAG:
        #         self.cur_index += 1
        #     glColor3ub(0,0,200)
        #     glScalef(scale_ratio,scale_ratio,scale_ratio)
        #     self.draw_Model(myMotion.skeleton.root, index)
        
        glDisable(GL_LIGHTING)
        glPopMatrix()


class Event_handle:
    def __init__(self):
        self.Left_pressed = False
        self.Right_pressed = False
        self.degree1 = 0.
        self.degree2 = 0.
        self.init_pos = np.array([0,0])
        self.eye = np.array([0.,0.,.1])
        self.at = np.array([0.,0.,0.])
        self.cameraUp = np.array([0.,1.,0.])
        self.scale = 1.
        self.trans = np.array([0.,0.,0.])
        self.full_list = []
        self.START_FLAG = False
        self.ENABLE_FLAG = False
        self.timeline_changed = False
        self.timeline = 0

        self.motion = None

    # def button_callback(self,window,button,action,mod):
    #     if action == glfw.PRESS:
    #         self.init_pos = glfw.get_cursor_pos(window)
            
    #         if button == glfw.MOUSE_BUTTON_LEFT:
    #             self.Left_pressed = True
    #         elif button == glfw.MOUSE_BUTTON_RIGHT:
    #             self.Right_pressed = True
    #     elif action == glfw.RELEASE:
    #         if button == glfw.MOUSE_BUTTON_LEFT:
    #             self.Left_pressed = False
    #         elif button == glfw.MOUSE_BUTTON_RIGHT:
    #             self.Right_pressed = False

    # def cursor_callback(self,window,xpos,ypos):
    #     if self.Left_pressed:
    #         self.degree1 += (self.init_pos[0] - xpos) * 0.02
    #         self.degree2 += (-self.init_pos[1] + ypos) * 0.02
    #         if self.degree2 >= 0.:
    #             self.degree2 %= 360.
    #         else:
    #             self.degree2 %= -360.
            
    #         if 90. <= self.degree2 and self.degree2 <= 270.:
    #             self.cameraUp[1] = -1.
    #         elif -90. >= self.degree2 and self.degree2 >= -270.:
    #             self.cameraUp[1] = -1.
    #         else:
    #             self.cameraUp[1] = 1.
    #         self.eye[0] = 0.1 * np.cos(np.radians(self.degree2)) * np.sin(np.radians(self.degree1))
    #         self.eye[1] = 0.1 * np.sin(np.radians(self.degree2))
    #         self.eye[2] = 0.1 * np.cos(np.radians(self.degree2)) * np.cos(np.radians(self.degree1))
            
    #     elif self.Right_pressed:
    #         cameraFront = self.eye - self.at
    #         temp1 = np.cross(cameraFront, self.cameraUp)
    #         u = temp1/np.sqrt(np.dot(temp1,temp1))
    #         temp2 = np.cross(u,cameraFront)
    #         w = temp2/np.sqrt(np.dot(temp2,temp2))
    #         self.trans += u *(-self.init_pos[0]+xpos)*0.0001
    #         self.trans += w *(-self.init_pos[1]+ypos)*0.0001
        
    # def scroll_callback(self,window,xoffset,yoffset): 
    #     if self.scale <= 0.1 and yoffset == 1:
    #         self.scale = 0.1
    #         return
    #     self.scale -= 0.1 * yoffset

    def drop_callback(self, paths):
        self.ENABLE_FLAG = True
        self.START_FLAG = False
        self.timeline_changed = True
        self.timeline = 0
        file_name = ''.join(paths)
        file = open(file_name,'r')
        
        # Make "motion" object
        parsing = Parsing()
        self.full_list = file.readlines()
        # for i in self.full_list:
        #     print(i)
        # print(len(self.full_list))
        root = Node()
        line_num = [0]
        channel_list = []
        postures = []
        parsing.make_tree(self.full_list, root, line_num, channel_list)
        # print("motion Num: %d"%(line_num[0]))
        # print(channel_list)
        postures = parsing.make_postures(self.full_list, line_num[0], channel_list)
        skeleton = Skeleton(root, parsing.joint_num)
        self.motion = Motion(skeleton, postures, parsing.frames)

        print("File name: %s"%(file_name))
        # print_data()
        print("###########################################################")
        file.close()

    # def key_callback(self,window, key, scancode, action, mods):
    #     if action==glfw.PRESS or action == glfw.REPEAT:
    #         if key == glfw.KEY_SPACE:
    #             self.START_FLAG = True

form_class = uic.loadUiType("MotionViewer.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
# QMainWindow
class WindowClass(QDialog, form_class) :
    def __init__(self, draw) :
        super().__init__()
        self.draw = draw
        self.event_handle = self.draw.event_handle
        self.setupUi(self)
        self.setWindowTitle("moooti")
        self.setAcceptDrops(True)

        self.openGLWidget.initializeGL()
        self.openGLWidget.paintGL = self.draw.render

        # event handle
        self.start_button.clicked.connect(self.button1Function)
        
        # self.openGLWidget.
        
        # self.btn_2.clicked.connect(self.button2Function)

    def button1Function(self):
        print("btn_1 Clicked")
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_path = [unicode(u.toLocalFile()) for u in event.mimeData().urls()]
        self.event_handle.drop_callback(file_path)

def main():
    app = QApplication(sys.argv)
    event_handle = Event_handle()
    draw = Draw(event_handle)
    draw.createVertexAndIndexArrayIndexed()
    myWindow = WindowClass(draw)
    myWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__" :
    main()


# t1 = 0.
# def main():
#     global t1
#     event_handle = Event_handle()
#     draw = Draw(event_handle)
#     draw.createVertexAndIndexArrayIndexed()

#     if not glfw.init():
#         return
#     t1 = glfw.get_time()
#     window = glfw.create_window(700,700,'2015004302', None,None)
#     if not window:
#         glfw.terminate()
#         return
    
#     glfw.make_context_current(window)
#     glfw.set_cursor_pos_callback(window,cursor_callback)
#     glfw.set_mouse_button_callback(window,button_callback)
#     glfw.set_scroll_callback(window,scroll_callback)
#     glfw.set_drop_callback(window,drop_callback)
#     glfw.set_key_callback(window,key_callback)
#     glfw.swap_interval(1)
    
#     while not glfw.window_should_close(window):
#         glfw.poll_events()
#         render()
#         glfw.swap_buffers(window)

#     glfw.terminate()

# if __name__ == "__main__":
#     main()