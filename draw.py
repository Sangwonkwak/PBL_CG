from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class Node:
    def __init__(self, name=None):
        self.name = name
        self.offset = np.zeros(3)
        self.child = []
        self.parent = None
        self.bufferIndex = None

class Skeleton:
    def __init__(self, root=None, joint_num=0):
        self.root = root
        self.joint_num = joint_num
        self.joint_list = []

    def make_jointList(self, node, str):
        if node.name != "__END__":
            self.joint_list.append(str+node.name)
            temp_str = str + "-"
            for child in node.child:
                self.make_jointList(child, temp_str)

    def make_endEffectorList(self, node, e_list, name_list):
        if node.name == "__END__":
            e_list.append(node)
            temp_str = "End_Effector#" + str(len(e_list))
            name_list.append(temp_str)
        
        for child in node.child:
            self.make_endEffectorList(child, e_list, name_list)
        
        return e_list, name_list
    
class Posture:
    def __init__(self, origin=None, Rmatrix=[]):
        self.origin = origin
        self.Rmatrix = Rmatrix
        self.framebuffer = []

class Motion:
    def __init__(self, skeleton=None, postures=None, frames=0, frame_rate=0):
        self.skeleton = skeleton
        self.postures = postures
        self.frames = frames
        self.frame_rate = frame_rate

class Parsing:
    def __init__(self):
        self.joint_num = 0
        self.frames = 0
        self.frame_rate = 0
    
    # Make tree structure for parsing hierarchical model
    def make_tree(self, full_list, parent, line_num, channel_list, bufferIndex):
        while True:
            line = full_list[line_num[0]].lstrip().split(' ')
            if line[0] == "JOINT" or line[0] == "ROOT":
                self.joint_num += 1
                new_node = Node(line[1].rstrip('\n'))
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

                new_node.parent = parent
                new_node.bufferIndex = bufferIndex[0]
                bufferIndex[0] += 1

                if line[0] != "ROOT":
                    parent.child.append(new_node)
                line_num[0] += 4
                self.make_tree(full_list, new_node, line_num, channel_list, bufferIndex)
            elif line[0] == "End":
                new_node = Node("__END__")
                # offset
                offset_data = full_list[line_num[0]+2].lstrip().split(' ')
                new_node.offset = np.array([float(offset_data[1]),float(offset_data[2]),float(offset_data[3])])
                
                new_node.parent = parent
                parent.child.append(new_node)
                line_num[0] += 3
                self.make_tree(full_list, new_node, line_num, channel_list, bufferIndex)
                
            elif line[0] == '}\n':
                line_num[0] += 1
                return
                
            elif line[0] == "MOTION\n":
                return new_node
            else:
                line_num[0] += 1
        
    def make_postures(self, full_list, start_line_num, channel_list):
        # get frames
        temp_frame= full_list[start_line_num+1].split()
        self.frames = int(temp_frame[1])
        temp_frame_rate = full_list[start_line_num+2].split()
        self.frame_rate = float(temp_frame_rate[2])
        print(self.frame_rate)

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
            
            rmatrix[0][:-1,3] = origin
            postures.append(Posture(origin, rmatrix))
        #     posture.Rmatrix[0][:-1,3] = origin
        #     posture.origin = origin
        #     postures.append(posture)
        # for i in range(4):
        #     print(postures[i].Rmatrix[0])
        #     print(postures[i].Rmatrix[1])
        #     print(postures[i].origin)
        return postures
     
class Draw:
    def __init__(self):
        self.opengl = None
        self.varr = None
        self.iarr = None
    
    def setOpengl(self, opengl):
        self.opengl = opengl
    
    def draw_unit_quad(self):
        glPushMatrix()
        glBegin(GL_POLYGON)
        glVertex3fv(np.array([0.1, 0., 0.1]))
        glVertex3fv(np.array([0.1, 0., -0.1]))
        glVertex3fv(np.array([-0.1, 0., -0.1]))
        glVertex3fv(np.array([-0.1, 0., 0.1]))
        glEnd()
        glPopMatrix()

    
    def drawgrid(self):
        glPushMatrix()
        glColor3ub(80,80,80)
        glTranslatef(.9, 0., .9)
        for i in range(10):
            glPushMatrix()
            for j in range(5):
                self.draw_unit_quad()
                glTranslatef(0., 0., -0.4)
            glPopMatrix()
            if i % 2 == 0:
                glTranslatef(-0.2, 0., -0.2)
            else:
                glTranslatef(-0.2, 0., 0.2)
        glPopMatrix()

        glPushMatrix()
        glColor3ub(180,180,180)
        glTranslatef(.9, 0., .7)
        for i in range(10):
            glPushMatrix()
            for j in range(5):
                self.draw_unit_quad()
                glTranslatef(0., 0., -0.4)
            glPopMatrix()
            if i % 2 == 0:
                glTranslatef(-0.2, 0., 0.2)
            else:
                glTranslatef(-0.2, 0., -0.2)
        glPopMatrix()
        
    def drawframe(self):
        glBegin(GL_LINES)
        glColor3ub(255,0,0)
        glVertex3fv(np.array([-1.,0.,0.]))
        glVertex3fv(np.array([1.,0.,0.]))
        glColor3ub(0,255,0)
        glVertex3fv(np.array([0.,0.,0.]))
        glVertex3fv(np.array([0.,1.,0.]))
        glColor3ub(0,0,255)
        glVertex3fv(np.array([0.,0.,-1.]))
        glVertex3fv(np.array([0.,0.,1.]))
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
    
    def draw_unit_sphere(self):
        radius = 1.
        maxAngle = 360
        glPushMatrix()
        glBegin(GL_LINE_STRIP)
        for i in range(maxAngle):
            glPushMatrix()
            glRotatef(i, 0, 1, 0)
            for j in range(maxAngle):
                theta = np.radians(j)
                glVertex3f(np.cos(theta)*radius, np.sin(theta)*radius, 0.)
            glPopMatrix()
        glEnd()
        glPopMatrix()


    def make_framebuffer(self, node, posture, index, mat):
        if node.name != "__END__":
            M = np.array(posture.Rmatrix[index[0]])
            if index[0] > 0:
                M[:-1,3] = [node.offset[0], node.offset[1], node.offset[2]]
            mat = mat @ M
            posture.framebuffer.append(mat)
            index[0] += 1
            for child in node.child:
                self.make_framebuffer(child, posture, index, np.array(mat))

    # mat은 이전까지의 current_matrix
    def draw_Model(self, node, posture, index, mat):
        glPushMatrix()
        glMultMatrixf(mat.T)
        self.draw_proper_cube(node.offset)
        glPopMatrix()
        # joint&root  
        if node.name != "__END__":
            num = index[0]
            index[0] += 1
            for child in node.child:
                self.draw_Model(child, posture, index, posture.framebuffer[num])
    
    def draw_process(self, motion, timeline):
        print("timeLine: %d"%timeline)
        if timeline != 0:
            for i in range(-1,1):
                posture = motion.postures[timeline + i]
                if len(posture.framebuffer) == 0:
                    self.make_framebuffer(motion.skeleton.root, posture, [0], np.identity(4))
            self.draw_Model(motion.skeleton.root, motion.postures[timeline], [0], np.identity(4))
        else:
            posture = motion.postures[0]
            self.make_framebuffer(motion.skeleton.root, posture, [0], np.identity(4))
            self.draw_Model(motion.skeleton.root, motion.postures[0], [0], np.identity(4))

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        scale = self.opengl.scale
        glOrtho(-scale,scale,-scale,scale,-scale,scale)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        real_eye = self.opengl.eye + self.opengl.trans
        real_at = self.opengl.at + self.opengl.trans
        cameraUp = self.opengl.cameraUp
        gluLookAt(real_eye[0],real_eye[1],real_eye[2],real_at[0],real_at[1],real_at[2],cameraUp[0],cameraUp[1],cameraUp[2])
        
        glPushMatrix()
        glScalef(200, 200, 200)
        self.drawframe()
        # self.drawgrid()
        glPopMatrix()

        # glPushMatrix()
        # glScalef(scale, scale, scale)
        # self.drawgrid()
        # glPopMatrix()


        # self.draw_unit_sphere()

        if self.opengl.POINT_FLAG:
            glPushMatrix()
            glColor3f(1.0, 0., 0.)
            ratio = 0.1
            glTranslatef(self.opengl.point[0], self.opengl.point[1], self.opengl.point[2])
            glScalef(ratio, ratio, ratio)
            # self.draw_unit_sphere()
            self.drawCube_glDrawElements()
            glPopMatrix()
        
        if self.opengl.LINE_FLAG:
            glPushMatrix()
            glColor3f(0., 1., 0.)
            ratio = 0.03
            for i in range(2):
                glPushMatrix()
                glTranslatef(self.opengl.line[i][0], self.opengl.line[i][1], self.opengl.line[i][2])
                glScalef(ratio, ratio, ratio)
                self.drawCube_glDrawElements()
                glPopMatrix()
                # self.draw_unit_sphere()
            
            glBegin(GL_LINES)
            for i in range(2):
                glVertex3f(self.opengl.line[i][0], self.opengl.line[i][1], self.opengl.line[i][2])
            glEnd()
            glPopMatrix()
        
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
    

        # Model drawing        
        motion_scale_ratio = self.opengl.motion_scale_ratio
        if self.opengl.ENABLE_FLAG:
            motion = self.opengl.motion
            if self.opengl.timeline_changed:
                if self.opengl.timeline < 0:
                    self.opengl.timeline = 0
                if self.opengl.timeline > motion.frames:
                    self.opengl.timeline = motion.frames
                self.opengl.timeline_changed = False
            
            if self.opengl.timeline >= motion.frames:
                self.opengl.START_FLAG = False
                self.opengl.timeline = motion.frames

            timeline = self.opengl.timeline

            objectColor = (.3, .3, .7, 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
            glScalef(motion_scale_ratio, motion_scale_ratio, motion_scale_ratio)
            if not self.opengl.START_FLAG:
                self.draw_process(motion, timeline)
                # self.highlight_joint()
                # self.Limb_IK_Draw()
                self.Jacobian_IK_Draw()
                glDisable(GL_LIGHTING)
                glPopMatrix()
                return


            objectColor = (.3, .3, .7, 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
            self.draw_process(motion, timeline)
            self.highlight_joint()
            self.opengl.timeline += 1
            glDisable(GL_LIGHTING)
            glPopMatrix()
            self.opengl.update()
            return
        
        glDisable(GL_LIGHTING)
        glPopMatrix()
    
    # 선택된 joint 표시 및 그 linear velocity 표시
    def highlight_joint(self):
        if self.opengl.Is_Joint_Selected:
            motion_scale_ratio = self.opengl.motion_scale_ratio
            timeline = self.opengl.timeline
            motion = self.opengl.motion
            current_matrix = motion.postures[timeline].framebuffer[self.opengl.selected_joint]
            
            origin = np.array([0., 0., 0., 1.])
            position = current_matrix @ origin
            # for i in range(3):
            #     position[i] *= motion_scale_ratio
            velocity_point = None
            if timeline == 0:
                velocity_point = np.array([0., 0., 0., 1.])
            elif timeline == 1:
                next_matrix = motion.postures[timeline+1].framebuffer[self.opengl.selected_joint]
                next_position = next_matrix @ origin
                velocity_point = (next_position - position) / motion.frame_rate
            else:
                previous_matrix = motion.postures[timeline-1].framebuffer[self.opengl.selected_joint]
                previous_position = previous_matrix @ origin
                velocity_point = (position - previous_position) / motion.frame_rate

            objectColor = (1., 1., 0., 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)

            glPushMatrix()
            ratio = 3
            glScalef(motion_scale_ratio, motion_scale_ratio, motion_scale_ratio)
            glTranslatef(position[0], position[1], position[2])
            glPushMatrix()
            glBegin(GL_LINES)
            glVertex3fv(np.array([0., 0., 0.]))
            glVertex3fv(velocity_point[:-1])
            glEnd()
            glPopMatrix()
            glScalef(ratio, ratio, ratio)
            self.drawCube_glDrawElements()
            glPopMatrix()
    
    # a의 각도를 구한다.
    def cal_angleByDot(self, a, b, c):
        ab = b - a
        ac = c - a
        ab_len = self.l2norm(ab[:-1])
        ac_len = self.l2norm(ac[:-1])
        up = np.dot(ab,ac)
        down = ab_len * ac_len
        x = up / down
        if x > 1.:
            x = 1.
        elif x < -1.:
            x = -1.
        return np.arccos(x)
    
    def cal_angleByLen(self, ab, bc, ac):
        up = ab*ab + ac*ac - bc*bc
        down = 2 * ab * ac
        x = up / down
        if x > 1.:
            x = 1.
        elif x < -1.:
            x = -1.
        return np.arccos(x)
    
    def l2norm(self, v):
        return np.sqrt(np.dot(v, v))

    def normalized(self, v):
        l = self.l2norm(v)
        if l == 0.:
            return np.zeros(3)
        return 1/l * np.array(v)
    
    # 3차원 rotation vector를 4차원 rotation matrix로 변환
    def exp(self, rv):
        M = np.identity(4) 
        u = self.normalized(rv)
        a = self.l2norm(rv)
        R = np.array([[np.cos(a)+u[0]*u[0]*(1-np.cos(a)), u[0]*u[1]*(1-np.cos(a))-u[2]*np.sin(a), u[0]*u[2]*(1-np.cos(a))+u[1]*np.sin(a)],
                    [u[1]*u[0]*(1-np.cos(a))+u[2]*np.sin(a), np.cos(a)+u[1]*u[1]*(1-np.cos(a)), u[1]*u[2]*(1-np.cos(a))-u[0]*np.sin(a)],
                    [u[2]*u[0]*(1-np.cos(a))-u[1]*np.sin(a), u[2]*u[1]*(1-np.cos(a))+u[0]*np.sin(a), np.cos(a)+u[2]*u[2]*(1-np.cos(a))]
                    ])
        M[:-1, :-1] = R
        return M
    
    def Limb_IK_Draw(self):
        if self.opengl.START_FLAG:
            return
        
        if self.opengl.Is_Endeffector_Selected:
            
            end = self.opengl.selected_endEffector
            posture = self.opengl.motion.postures[self.opengl.timeline]
            origin = np.array([0., 0., 0., 1.])

            # get a,b,c postion
            parent = end.parent
            g_parent = parent.parent
            
            end_trans = np.identity(4)
            end_trans[:-1, 3] = end.offset
            
            g_parent_frame = np.array(self.opengl.Limb_IK_framebuffer[0])
            parent_frame = np.array(self.opengl.Limb_IK_framebuffer[1])

            end_pos = parent_frame @ end_trans @ origin 
            parent_pos = parent_frame @ origin
            g_parent_pos = g_parent_frame @ origin
            print("g_parent_POS: ")
            print(g_parent_pos)

            temp_mat = np.identity(4)
            temp_mat[:-1,3] = end.offset 
            init_end_pos = posture.framebuffer[parent.bufferIndex] @ temp_mat @ origin 

            final_end_pos = np.array([0., 0., 0., 1.])
            final_end_pos[:-1] = np.array(init_end_pos[:-1]) + self.opengl.endEffector_trans[:-1]
            final_ac = final_end_pos - g_parent_pos
            
            final_ac_len = self.l2norm(final_ac[:-1])
            ab_len = self.l2norm(parent.offset)
            bc_len = self.l2norm(end.offset)

            if ab_len + bc_len < final_ac_len:
                print("STOP")
                # end effector 그려내기
                objectColor = (1., .1, .1, 1.)
                specularObjectColor = (1.,1.,1.,1.)
                glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
                glMaterialfv(GL_FRONT,GL_SHININESS,100)
                glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
                
                ratio = .5
                glPushMatrix()
                glTranslatef(init_end_pos[0],init_end_pos[1],init_end_pos[2])
                glScalef(ratio, ratio, ratio)
                self.drawCube_glDrawElements()
                glPopMatrix()

                glPushMatrix()
                # glTranslatef(final_end_pos[0],final_end_pos[1],final_end_pos[2])
                glTranslatef(end_pos[0],end_pos[1],end_pos[2])
                glScalef(ratio, ratio, ratio)
                self.drawCube_glDrawElements()
                glPopMatrix()

                # Link 그려내기
                objectColor = (.8, .4, .2, 1.)
                specularObjectColor = (1.,1.,1.,1.)
                glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
                glMaterialfv(GL_FRONT,GL_SHININESS,100)
                glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)

                
                glPushMatrix()
                glMultMatrixf(g_parent_frame.T)
                self.draw_proper_cube(parent.offset)
                glPopMatrix()

                
                glPushMatrix()
                glMultMatrixf(parent_frame.T)
                self.draw_proper_cube(end.offset)
                glPopMatrix()

                self.opengl.endEffector_trans = end_pos - init_end_pos
                return

            theta_a1 = self.cal_angleByDot(g_parent_pos, parent_pos, end_pos)
            theta_b1 = self.cal_angleByDot(parent_pos, end_pos, g_parent_pos)
            theta_a2 = self.cal_angleByLen(ab_len, bc_len, final_ac_len)
            theta_b2 = self.cal_angleByLen(ab_len, final_ac_len, bc_len)

            ac = end_pos - g_parent_pos
            ac_len = self.l2norm(ac[:-1])
            ab = parent_pos - g_parent_pos
            
            a_rv1_axis = np.cross(ac[:-1],ab[:-1])
            a_rv1_axis_len = self.l2norm(a_rv1_axis)
            a_rv1_axis /= a_rv1_axis_len
            a_rv1 = (theta_a2 - theta_a1) * a_rv1_axis
            a_rv1_temp = np.array([0., 0., 0., 0.])
            a_rv1_temp[:-1] = np.array(a_rv1) 
            a_rv1 = np.linalg.inv(g_parent_frame) @ a_rv1_temp
            a_rm1 = self.exp(a_rv1[:-1])
            # a_rm1 = self.exp(a_rv1)
            
            g_parent_framebuffer1 = g_parent_frame @ a_rm1 
            # g_parent_framebuffer1 = a_rm1 @ posture.framebuffer[g_parent.bufferIndex]

            ba = g_parent_pos - parent_pos
            bc = end_pos - parent_pos
            b_rv1_axis = np.cross(ba[:-1], bc[:-1])
            b_rv1_axis_len = self.l2norm(b_rv1_axis)
            b_rv1_axis /= b_rv1_axis_len
            b_rv1 = (theta_b2 - theta_b1) * b_rv1_axis
            b_rv1_temp = np.array([0., 0., 0., 0.])
            b_rv1_temp[:-1] = np.array(b_rv1)
            b_rv1 = np.linalg.inv(parent_frame) @ b_rv1_temp
            b_rm1 = self.exp(b_rv1[:-1])
            # b_rm1 = self.exp(b_rv1)
            parent_new_orientation = parent_frame @ b_rm1
            # parent_new_orientation = b_rm1 @ posture.framebuffer[parent.bufferIndex]

            parent_new_orientation[:-1,3] = np.array([0., 0., 0.])

            a_rv2_axis = np.cross(final_ac[:-1],ac[:-1])
            a_rv2_axis_len = self.l2norm(a_rv2_axis)
            if a_rv2_axis_len != 0.:
                a_rv2_axis /= a_rv2_axis_len
                final_delta_theta_a = (-1) * self.cal_angleByDot(g_parent_pos, end_pos, final_end_pos)
                a_rv2 = final_delta_theta_a * a_rv2_axis
            else:
                a_rv2 = np.zeros(3)
            
            # if final_delta_theta_a == -0.:
            #     a_rv2 = np.zeros(3)
            
            a_rv2_temp = np.array([0., 0., 0., 0.])
            a_rv2_temp[:-1] = np.array(a_rv2)
            a_rv2 = np.linalg.inv(g_parent_framebuffer1) @ a_rv2_temp
            a_rm2 = self.exp(a_rv2[:-1])
            # print("final_delta_theta_a: ")
            # print(final_delta_theta_a)
            print("a_rv2_temp: ")
            print(a_rv2_temp)
            print("a_rv2: ")
            print(a_rv2)
            print("a_rm2: ")
            print(a_rm2)
            # a_rm2 = self.exp(a_rv2)
            g_parent_framebuffer2 = g_parent_framebuffer1 @ a_rm2
            # g_parent_framebuffer2 = a_rm2 @ g_parent_framebuffer1


            # end effector 그려내기
            objectColor = (1., .1, .1, 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
            
            ratio = .5
            glPushMatrix()
            glTranslatef(init_end_pos[0],init_end_pos[1],init_end_pos[2])
            glScalef(ratio, ratio, ratio)
            self.drawCube_glDrawElements()
            glPopMatrix()

            glPushMatrix()
            glTranslatef(final_end_pos[0],final_end_pos[1],final_end_pos[2])
            glScalef(ratio, ratio, ratio)
            self.drawCube_glDrawElements()
            glPopMatrix()

            # Link 그려내기
            objectColor = (.8, .4, .2, 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)

            glPushMatrix()
            glMultMatrixf(g_parent_framebuffer2.T)
            self.draw_proper_cube(parent.offset)
            glPopMatrix()

            temp_offset = np.identity(4)
            temp_offset[:-1,3] = np.array(parent.offset)
            
            final_parent_pos = g_parent_framebuffer2 @ temp_offset @ origin
            parent_new_framebuffer = np.array(parent_new_orientation)
            parent_new_framebuffer[:,3] = final_parent_pos
            

            glPushMatrix()
            glMultMatrixf(parent_new_framebuffer.T)
            self.draw_proper_cube(end.offset)
            glPopMatrix()

            self.opengl.Limb_IK_framebuffer[0] = g_parent_framebuffer2
            self.opengl.Limb_IK_framebuffer[1] = parent_new_framebuffer

            # temp = np.identity(4)
            # temp[:-1,3] = end.offset
            # test_final_pos = parent_new_framebuffer @ temp @ origin
            # print("g_parent_framebuffer1: ")
            # print(g_parent_framebuffer1)
            # print("parent_new_framebuffer: ")
            # print(parent_new_framebuffer)
            # print("g_parent_framebuffer2: ")
            # print(g_parent_framebuffer2)
            # print("final pos: ",end='')
            # print(test_final_pos)
            # print("correct final: ",end='')
            # print(final_end_pos) 

    def Jacobian_IK_Draw(self):
        if self.opengl.Is_Endeffector_Selected:
            J_framebuffer = self.opengl.Jacobian_IK_framebuffer
            J_nodeList = self.opengl.Jacobian_nodeList
            end = self.opengl.selected_endEffector
            posture = self.opengl.motion.postures[self.opengl.timeline]
            joint_num = len(self.opengl.Jacobian_IK_framebuffer)
            origin = np.array([0., 0., 0., 1.])
            M = np.identity(4)
            M[:-1,3] = end.offset

            current_end_pos = J_framebuffer[joint_num-1] @ M @ origin
            # root_origin = J_framebuffer[0][:,3]
            init_end_pos = posture.framebuffer[end.parent.bufferIndex] @ M @ origin
            final_end_pos = np.array([0.,0.,0.,1.])
            # final_end_pos[:-1] = np.array(current_end_pos[:-1]) + self.opengl.endEffector_trans[:-1]
            final_end_pos[:-1] = np.array(init_end_pos[:-1]) + self.opengl.endEffector_trans[:-1]
            # print(self.opengl.endEffector_trans[:-1])
            # total_difference = final_end_pos - init_end_pos

            # while(True):
            for num in range(100):
                # current_end_pos = J_framebuffer[joint_num-1] @ M @ origin
                J = np.zeros((3,joint_num*3))
                # print(joint_num)
                # Get delta_joint by Jacobian Matrix
                for i in range(joint_num):
                    current_joint_pos = J_framebuffer[i] @ origin
                    another_vector = current_end_pos - current_joint_pos
                    for j in range(3):
                        axis_vector = np.array(J_framebuffer[i][:,j])
                        change_vector = np.cross(axis_vector[:-1],another_vector[:-1])
                        index = 3*i + j
                        
                        J[:,index] = change_vector
                
                total_difference = final_end_pos - current_end_pos
                ratio = 0.01
                delta_end = ratio * total_difference
                delta_joint = J.T @ delta_end[:-1]
                # print("delta_joint: ")
                # print(delta_joint)

                # Add delta_joint to each local frame by ZXY Euler angle(root is ZYX), update orientation 
                for i in range(joint_num):
                    index = 3*i
                    x_delta = np.radians(delta_joint[index])
                    y_delta = np.radians(delta_joint[index+1])
                    z_delta = np.radians(delta_joint[index+2])
                    X = np.identity(4)
                    X[:3,:3] = [[1., 0., 0.],
                                [0., np.cos(x_delta), -np.sin(x_delta)],
                                [0., np.sin(x_delta), np.cos(x_delta)]
                                ]
                    Y = np.identity(4)
                    Y[:3,:3] = [[np.cos(y_delta), 0., np.sin(y_delta)],
                                [0., 1., 0.],
                                [-np.sin(y_delta), 0., np.cos(y_delta)]
                                ]
                    Z = np.identity(4)
                    Z[:3,:3] = [[np.cos(z_delta), -np.sin(z_delta), 0.],
                                [np.sin(z_delta), np.cos(z_delta), 0.],
                                [0., 0., 1.]
                                ]
                    if i != 0:
                        R = Z @ X @ Y
                    else:
                        R = Z @ Y @ X
                    J_framebuffer[i] = J_framebuffer[i] @ R
                
                # get each joint origin
                for i in range(joint_num-1):
                    child_node = J_nodeList[i+1]
                    P = np.identity(4)
                    P[:-1,3] = child_node.offset
                    next_origin = J_framebuffer[i] @ P @ origin
                    J_framebuffer[i+1][:,3] = next_origin
                P = np.identity(4)
                P[:-1,3] = end.offset
                current_end_pos = J_framebuffer[joint_num-1] @ P @ origin
                
                # if self.Is_Close(current_end_pos, final_end_pos):
                #     break
                # break
            # print("current_end_pos: ")
            # print(current_end_pos)
            # print("final_end_pos: ")
            # print(final_end_pos)
            
            # Link 그려내기
            objectColor = (1., 1., 1., 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)

            for i in range(joint_num):
                glPushMatrix()
                glMultMatrixf(J_framebuffer[i].T)
                temp_offset = None
                if (i + 1) == joint_num:
                    temp_offset = end.offset
                else:
                    temp_offset = J_nodeList[i+1].offset
                self.draw_proper_cube(temp_offset)
                glPopMatrix()
            
            # end effector 그려내기
            objectColor = (1., .1, .1, 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
            
            ratio = .5
            glPushMatrix()
            glTranslatef(current_end_pos[0],current_end_pos[1],current_end_pos[2])
            glScalef(ratio, ratio, ratio)
            self.drawCube_glDrawElements()
            glPopMatrix()


    def Is_Close(self, current, final):
        temp = final - current
        sum = self.l2norm(temp[:-1])
        print(sum)
        threshold = 0.05
        if sum < threshold:
            return True
        else:
            return False

                


            



            