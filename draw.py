from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import copy
class Node:
    def __init__(self, name=None):
        self.name = name
        self.offset = np.zeros(3)
        self.child = []

class Skeleton:
    def __init__(self, root=None, joint_num=0):
        self.root = root
        self.joint_num = joint_num

class Posture:
    def __init__(self, origin=None, Rmatrix=[]):
        self.origin = origin
        self.Rmatrix = Rmatrix

class Motion:
    def __init__(self, skeleton=None, postures=None, frames=0):
        self.skeleton = skeleton
        self.postures = postures
        self.frames = frames

class Parsing:
    def __init__(self):
        self.joint_num = 0
        self.frames = 0
    
    # Make tree structure for parsing hierarchical model
    def make_tree(self, full_list, parent, line_num, channel_list):
        while True:
            line = full_list[line_num[0]].lstrip().split(' ')
            if line[0] == "JOINT" or line[0] == "ROOT":
                self.joint_num += 1
                new_node = Node(line[1].rstrip('\n'))
                # print(new_node.name)
                # offset
                offset_data = full_list[line_num[0]+2].lstrip().split(' ')
                new_node.offset = np.array([float(offset_data[1]),float(offset_data[2]),float(offset_data[3])])
                # channel
                channel_data = full_list[line_num[0]+3].lstrip().split(' ')
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

                if line[0] != "ROOT":
                    parent.child.append(new_node)
                # else:
                #     parent = new_node
                line_num[0] += 4
                self.make_tree(full_list, new_node, line_num, channel_list)
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
                return new_node
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
        # start posture
        temp_rmatrix = []
        for num in range(self.joint_num):
            M = np.identity(4)
            temp_rmatrix.append(M)
        temp_origin = [0., 0., 0.]
        postures.append(Posture(temp_origin, temp_rmatrix))

        for i in range(self.frames):
            line = full_list[line_num+i].split(' ')
            if len(line) == 1:
                line = full_list[line_num+i].split('\t')
            # posture = Posture()
            # origin = [float(line[0]), float(line[1]), float(line[2])]
            origin = [float(line[0]), float(line[1]), float(line[2])]
            
            rmatrix = []
            for j in range(self.joint_num):
                M = np.identity(4)
                for k in range(3):
                    R = np.identity(4)
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
                # posture.Rmatrix.append(M)
                rmatrix.append(M)
            # if i < 3:
            #     print(origin)
            rmatrix[0][:-1,3] = origin
            # posture = Posture(origin, rmatrix)
            # posture.Rmatrix[0][:-1,3] = posture.origin
            # if i < 3:
            #     print(rmatrix[0])
            # if i < 10:
            #     print(posture.Rmatrix[0])
            postures.append(Posture(origin, rmatrix))
            # if i == 400:
            #     print(postures[0].origin)
            #     print(postures[1].origin)
            #     print(postures[2].origin)
        
        return postures
     
class Draw:
    def __init__(self):
        self.opengl = None
        self.varr = None
        self.iarr = None
        self.cur_index = 0
    
    def setOpengl(self, opengl):
        self.opengl = opengl
    
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
        if b != 0.0:
            th = np.arccos((a*a + b*b - c*c)/(2.*a*b))
        else:
            th = 0.
        u = np.cross(np.array([1.0,0.,0.]),offset)
        temp = np.sqrt(np.dot(u,u))
        if temp != 0.:
            u /= temp
        else:
            u = np.zeros(3)
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
        # print("model_node_name:%s"%node.name)
        glPushMatrix()
        # End site
        if node.name == "__END__":
            self.draw_proper_cube(node.offset)
        
        # joint & root
        else:
            self.draw_proper_cube(node.offset)
            glTranslatef(node.offset[0], node.offset[1], node.offset[2])
            # M = self.opengl.motion.postures[index[0]][index[1]]
            posture = self.opengl.motion.postures[index[0]]
            # for i in temp_M:
            #     print(i)
            # print(" index[0] index[1]: %d %d"%(index[0],index[1]))   
            M = posture.Rmatrix[index[1]]
            # M = np.identity(4)
            # print(posture.origin)
            # print(M)
            glMultMatrixf(M.T)
            index[1] += 1

            for child in node.child:
                self.draw_Model(child, index)
        glPopMatrix()
    
    def render(self):
        # print("Called")
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        scale = self.opengl.scale
        glOrtho(-scale,scale,-scale,scale,-1,1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        real_eye = self.opengl.eye + self.opengl.trans
        real_at = self.opengl.at + self.opengl.trans
        cameraUp = self.opengl.cameraUp
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
        
        # Model drawing
        # timeline = self.opengl.timeline
        if self.opengl.timeline_changed:
            if self.opengl.timeline < 0:
                self.opengl.timeline = 0
            if self.opengl.timeline > self.opengl.motion.frames:
                self.opengl.timeline = self.opengl.motion.frames
            # self.cur_index = self.opengl.timeline
            self.opengl.timeline_changed = False

        
        scale_ratio = 0.005
        if self.opengl.ENABLE_FLAG:
            myMotion = self.opengl.motion
            if self.opengl.timeline >= myMotion.frames:
                self.opengl.START_FLAG = False
                # self.cur_index -= 1
                self.opengl.timeline = myMotion.frames
            # index = [self.cur_index, 0]
            index = [self.opengl.timeline, 0]
            

            glColor3ub(0,0,200)
            glScalef(scale_ratio,scale_ratio,scale_ratio)
            if not self.opengl.START_FLAG:
                self.draw_Model(myMotion.skeleton.root, index)
                glDisable(GL_LIGHTING)
                glPopMatrix()
                return

            # self.cur_index += 1
            
            self.opengl.timeline += 1
            self.draw_Model(myMotion.skeleton.root, index)
            glDisable(GL_LIGHTING)
            glPopMatrix()
            self.opengl.update()
            return
        
        glDisable(GL_LIGHTING)
        glPopMatrix()