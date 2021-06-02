
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from data import *
from particleSystem import *
from particleSolver import *

class Draw:
    def __init__(self, opengl_data, motion):
        self.opengl_data = opengl_data
        self.motion = motion
        self.varr = None
        self.iarr = None
    
    def setOpenglData(self, opengl_data):
        self.opengl_data= opengl_data

    def setMotion(self, motion):
        self.motion = motion
    
    def setTimeWarpingMotion(self, motion):
        self.timeWarpingMotion = motion

    def setMotionWarpingMotion(self, motion):
        self.motionWarpingMotion = motion

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

    # mat은 이전까지의 current_matrix
    def drawModel(self, node, posture):
        if node.bufferIndex != 0:
            glPushMatrix()
            # print(node.name)
            M = posture.framebuffer[node.parent.bufferIndex]
            glMultMatrixf(M.T)
            self.draw_proper_cube(node.offset)
            glPopMatrix()
        # joint&root  
        if node.name != "__END__":
            for child in node.child:
                self.drawModel(child, posture)
    
    def makeParticle2D(self, ks, kd):
        self.opengl_data.particleSystem = ParticleSystem()
        self.opengl_data.dampingDataSet = []
        self.opengl_data.particleSolver = ParticleSolver(self.opengl_data.particleSystem)

        pos1 = np.array([40.,40.,0.])
        pos2 = np.array([60.,70.,0.])
        pos3 = np.array([30.,90.,0.])
        vel1 = np.zeros(3)
        vel2 = np.zeros(3)
        vel3 = np.zeros(3)
        f1 = np.zeros(3)
        f2 = np.zeros(3)
        f3 = np.zeros(3)
        m1 = 3.
        m2 = 3.
        m3 = 3.
        particle1 = np.concatenate((pos1,vel1,f1,m1),axis=None)
        particle2 = np.concatenate((pos2,vel2,f2,m2),axis=None)
        particle3 = np.concatenate((pos3,vel3,f3,m3),axis=None)
        # ks = 30
        # kd = 3
        dampingData1 = DampingData(ks,kd,[0,1],uti.l2norm(pos1-pos2))
        dampingData2 = DampingData(ks,kd,[1,2],uti.l2norm(pos2-pos3))
        dampingData3 = DampingData(ks,kd,[0,2],uti.l2norm(pos1-pos3))

        self.opengl_data.particleSystem.addParticle(particle1)
        self.opengl_data.particleSystem.addParticle(particle2)
        self.opengl_data.particleSystem.addParticle(particle3)
        self.opengl_data.dampingDataSet.append(dampingData1)
        self.opengl_data.dampingDataSet.append(dampingData2)
        self.opengl_data.dampingDataSet.append(dampingData3)
        self.opengl_data.Is_particleSystem_Empty = False

    def makeParticle3D(self, ks, kd):
        self.opengl_data.particleSystem = ParticleSystem()
        self.opengl_data.dampingDataSet = []
        self.opengl_data.particleSolver = ParticleSolver(self.opengl_data.particleSystem)

        pos = [None for i in range(8)]
        T = np.identity(4)
        S = np.identity(4)
        R = np.identity(4)

        T[0:3,3] = np.array([20,28,20])
        S[:3,:3] = 10 * S[:3,:3]
        theta = np.radians(52)
        R[:3,:3] = [[np.cos(theta), -np.sin(theta), 0.],
                    [np.sin(theta), np.cos(theta), 0.],
                    [0., 0., 1.]
                    ]
        M =  T @ S @ R
        for i in range(8):
            origin_pos = np.concatenate((self.varr[2*i+1],1.),axis=None)
            pos[i] = (M @ origin_pos)[:-1]
            # print(pos[i])

        mass = [3,3,3,3,3,3,3,3]
        particles = []
        for p,m in zip(pos,mass):
            particles.append(np.concatenate((p,np.zeros(3),np.zeros(3),m),axis=None))
        # ks = 300
        # kd = 10
        # springPairSet = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7),(0,2),(1,3),(1,6),(2,5),(4,6),(5,7),(0,7),(4,3),(0,5),(1,4),(3,6),(2,7)]
        springPairSet = []
        for i in range(8):
            for j in range(i+1,8):
                springPairSet.append([i,j])
        dampingDataSet = []
        for pair in springPairSet:
            # p1 = self.opengl_data.particleSystem.particles[pair[0]][0:3]
            p1 = pos[pair[0]]
            p2 = pos[pair[1]]
            dampingDataSet.append(DampingData(ks,kd,pair,uti.l2norm(p1-p2)))

        for particle in particles:
            self.opengl_data.particleSystem.addParticle(particle)
        for dampingData in dampingDataSet:
            self.opengl_data.dampingDataSet.append(dampingData)
        self.opengl_data.Is_particleSystem_Empty = False

    def drawParticleSystem(self, timestep, normal_v):
        # euler integration
        self.opengl_data.particleSolver.eulerIntegration(timestep, self.opengl_data.dampingDataSet, normal_v)
        glBegin(GL_LINES)
        glColor3f(1.,0.,0.)
        for dampingData in self.opengl_data.dampingDataSet:
            x1 = self.opengl_data.particleSystem.particles[dampingData.particle_nums[0]][0:3]
            x2 = self.opengl_data.particleSystem.particles[dampingData.particle_nums[1]][0:3]
            glVertex3f(x1[0],x1[1],x1[2])
            glVertex3f(x2[0],x2[1],x2[2])
        glEnd()

    def render(self):
       
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        data = self.opengl_data
        scale = data.scale
        glOrtho(-scale,scale,-scale,scale,-scale,scale)
        # gluPerspective(10, 1, 1, 50)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        real_eye = data.eye + data.trans
        real_at = data.at + data.trans
        cameraUp = data.cameraUp
        gluLookAt(real_eye[0],real_eye[1],real_eye[2],real_at[0],real_at[1],real_at[2],cameraUp[0],cameraUp[1],cameraUp[2])
        
        glPushMatrix()
        glScalef(200, 200, 200)
        # self.drawframe()
        self.drawgrid()
        glPopMatrix()

        # self.draw_unit_sphere()

        # Particle Dynamics
        if not self.opengl_data.Is_particleSystem_Empty:
            self.drawParticleSystem(self.opengl_data.timestep, self.opengl_data.normal_v)

        if data.POINT_FLAG:
            glPushMatrix()
            glColor3f(1.0, 0., 0.)
            ratio = 5.
            glTranslatef(data.point[0], data.point[1], data.point[2])
            glScalef(ratio, ratio, ratio)
            # self.draw_unit_sphere()
            self.drawCube_glDrawElements()
            glPopMatrix()
        
        if data.LINE_FLAG:
            glPushMatrix()
            glColor3f(0., 1., 0.)
            ratio = 5.
            for i in range(2):
                glPushMatrix()
                glTranslatef(data.line[i][0], data.line[i][1], data.line[i][2])
                glScalef(ratio, ratio, ratio)
                self.drawCube_glDrawElements()
                glPopMatrix()
                # self.draw_unit_sphere()
            
            glBegin(GL_LINES)
            for i in range(2):
                glVertex3f(data.line[i][0], data.line[i][1], data.line[i][2])
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
    


        # Time warping
        if data.TIME_WARPING_FLAG:
            Tmotion = self.timeWarpingMotion
            objectColor = (.7, .7, .7, 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
            if data.TW_timeline == Tmotion.frames:
                data.TIME_WARPING_FLAG = False
            self.drawModel(Tmotion.skeleton.root, Tmotion.postures[data.TW_timeline-1])
            data.TW_timeline += 1
        
        # Motion warping
        if data.MOTION_WARPING_FLAG:
            Mmotion = self.motionWarpingMotion
            objectColor = (.7, .7, .7, 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
            if data.MW_timeline == Mmotion.frames:
                data.MOTION_WARPING_FLAG = False
            # print("timeline: %d"%data.MW_timeline)
            self.drawModel(Mmotion.skeleton.root, Mmotion.postures[data.MW_timeline-1])
            data.MW_timeline += 1

        # Model drawing        
        motion_scale_ratio = data.motion_scale_ratio
        motion = self.motion
        if data.ENABLE_FLAG:
            frames = motion.frames
            if data.timeline_changed:
                if data.timeline < 0:
                    data.timeline = 0
                if data.timeline > frames:
                    data.timeline = frames
                data.timeline_changed = False
            
            if data.timeline >= frames:
                data.START_FLAG = False
                data.timeline = frames

            objectColor = (.3, .3, .7, 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
            # glScalef(motion_scale_ratio, motion_scale_ratio, motion_scale_ratio)
            if not data.START_FLAG:
                self.drawModel(motion.skeleton.root, motion.postures[data.timeline])
                self.highlight_joint()
                self.Limb_IK_Draw()
                self.Jacobian_IK_Draw()
                glDisable(GL_LIGHTING)
                glPopMatrix()
                return

            # objectColor = (.3, .3, .7, 1.)
            # specularObjectColor = (1.,1.,1.,1.)
            # glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            # glMaterialfv(GL_FRONT,GL_SHININESS,100)
            # glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
            self.drawModel(motion.skeleton.root, motion.postures[data.timeline])
            # print("timeline: %d"%data.timeline)
            
            self.highlight_joint()
            data.timeline += 1
            glDisable(GL_LIGHTING)
            glPopMatrix()
            # data.update()
            return
        
        glDisable(GL_LIGHTING)
        glPopMatrix()
    
    # 선택된 joint 표시 및 그 linear velocity 표시
    def highlight_joint(self):
        data = self.opengl_data
        motion = self.motion
        if not data.fk_first_check:
            return 
        if data.Is_Joint_Selected:
            motion_scale_ratio = data.motion_scale_ratio
            timeline = data.timeline
            current_matrix = motion.postures[timeline].framebuffer[data.selected_joint]
            

            origin = np.array([0., 0., 0., 1.])
            position = current_matrix @ origin
            
            data.current_joint_pos = np.array(position[:-1])
            # for i in range(3):
            #     position[i] *= motion_scale_ratio
            velocity_point = None
            if timeline == 0:
                velocity_point = np.array([0., 0., 0., 1.])
            elif timeline == 1:
                next_matrix = motion.postures[timeline+1].framebuffer[data.selected_joint]
                next_position = next_matrix @ origin
                velocity_point = (next_position - position) / motion.frame_rate
            else:
                previous_matrix = motion.postures[timeline-1].framebuffer[data.selected_joint]
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
        data = self.opengl_data
        motion = self.motion
        if not data.Limb_IK_first_check:
            return
        
        if data.Is_Endeffector_Selected:
            
            end = data.selected_endEffector
            posture = motion.postures[data.timeline]
            origin = np.array([0., 0., 0., 1.])

            # get a,b,c postion
            parent = end.parent
            g_parent = parent.parent
            
            end_trans = np.identity(4)
            end_trans[:-1, 3] = end.offset
            
            g_parent_frame = np.array(data.Limb_IK_posture.framebuffer[g_parent.bufferIndex])
            parent_frame = np.array(data.Limb_IK_posture.framebuffer[parent.bufferIndex])
            
            end_pos = parent_frame @ end_trans @ origin 
            parent_pos = parent_frame @ origin
            g_parent_pos = g_parent_frame @ origin

            temp_mat = np.identity(4)
            temp_mat[:-1,3] = end.offset 
            init_end_pos = posture.framebuffer[parent.bufferIndex] @ temp_mat @ origin 

            final_end_pos = np.array([0., 0., 0., 1.])
            final_end_pos[:-1] = np.array(init_end_pos[:-1]) + data.endEffector_trans[:-1]
            final_ac = final_end_pos - g_parent_pos
            
            final_ac_len = self.l2norm(final_ac[:-1])
            ab_len = self.l2norm(parent.offset)
            bc_len = self.l2norm(end.offset)

            # if False:
            # # if ab_len + bc_len < final_ac_len:
            #     print("STOP")
            #     # end effector 그려내기
            #     objectColor = (1., .1, .1, 1.)
            #     specularObjectColor = (1.,1.,1.,1.)
            #     glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            #     glMaterialfv(GL_FRONT,GL_SHININESS,100)
            #     glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
                
            #     ratio = .5
            #     glPushMatrix()
            #     glTranslatef(init_end_pos[0],init_end_pos[1],init_end_pos[2])
            #     glScalef(ratio, ratio, ratio)
            #     self.drawCube_glDrawElements()
            #     glPopMatrix()

            #     glPushMatrix()
            #     # glTranslatef(final_end_pos[0],final_end_pos[1],final_end_pos[2])
            #     glTranslatef(end_pos[0],end_pos[1],end_pos[2])
            #     glScalef(ratio, ratio, ratio)
            #     self.drawCube_glDrawElements()
            #     glPopMatrix()

            #     # Link 그려내기
            #     objectColor = (.8, .4, .2, 1.)
            #     specularObjectColor = (1.,1.,1.,1.)
            #     glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            #     glMaterialfv(GL_FRONT,GL_SHININESS,100)
            #     glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)

                
            #     glPushMatrix()
            #     glMultMatrixf(g_parent_frame.T)
            #     self.draw_proper_cube(parent.offset)
            #     glPopMatrix()

                
            #     glPushMatrix()
            #     glMultMatrixf(parent_frame.T)
            #     self.draw_proper_cube(end.offset)
            #     glPopMatrix()

            #     data.endEffector_trans = end_pos - init_end_pos
            #     return

            theta_a1 = self.cal_angleByDot(g_parent_pos, parent_pos, end_pos)
            theta_b1 = self.cal_angleByDot(parent_pos, end_pos, g_parent_pos)
            theta_a2 = self.cal_angleByLen(ab_len, bc_len, final_ac_len)
            theta_b2 = self.cal_angleByLen(ab_len, final_ac_len, bc_len)

            ac = end_pos - g_parent_pos
            # ac_len = self.l2norm(ac[:-1])
            ab = parent_pos - g_parent_pos
            
            a_rv1_axis = np.cross(ac[:-1],ab[:-1])
            a_rv1_axis_len = self.l2norm(a_rv1_axis)
            a_rv1_axis /= a_rv1_axis_len
            a_rv1 = (theta_a2 - theta_a1) * a_rv1_axis
            a_rv1_temp = np.array([0., 0., 0., 0.])
            a_rv1_temp[:-1] = np.array(a_rv1) 
            a_rv1 = np.linalg.inv(g_parent_frame) @ a_rv1_temp
            a_rm1 = self.exp(a_rv1[:-1])
            
            data.Limb_IK_posture.Rmatrix[g_parent.bufferIndex] = data.Limb_IK_posture.Rmatrix[g_parent.bufferIndex] @ a_rm1
            g_parent_framebuffer1 = g_parent_frame @ a_rm1 
            

            ba = g_parent_pos - parent_pos
            bc = end_pos - parent_pos
            b_rv1_axis = np.cross(ba[:-1], bc[:-1])
            b_rv1_axis_len = self.l2norm(b_rv1_axis)
            b_rv1_axis /= b_rv1_axis_len

            # print("theta_b2 - theta_b1:")
            # print(theta_b2 - theta_b1)

            b_rv1 = (theta_b2 - theta_b1) * b_rv1_axis
            b_rv1_temp = np.array([0., 0., 0., 0.])
            b_rv1_temp[:-1] = np.array(b_rv1)
            b_rv1 = np.linalg.inv(parent_frame) @ b_rv1_temp
            b_rm1 = self.exp(b_rv1[:-1])
            
            data.Limb_IK_posture.Rmatrix[parent.bufferIndex] = data.Limb_IK_posture.Rmatrix[parent.bufferIndex] @ b_rm1
            parent_new_orientation = parent_frame @ b_rm1
            parent_new_orientation[:-1,3] = np.array([0., 0., 0.])

            a_rv2_axis = np.cross(final_ac[:-1],ac[:-1])
            a_rv2_axis_len = self.l2norm(a_rv2_axis)
            if a_rv2_axis_len != 0.:
                a_rv2_axis /= a_rv2_axis_len
                final_delta_theta_a = (-1) * self.cal_angleByDot(g_parent_pos, end_pos, final_end_pos)
                a_rv2 = final_delta_theta_a * a_rv2_axis
            else:
                a_rv2 = np.zeros(3)
            
            a_rv2_temp = np.array([0., 0., 0., 0.])
            a_rv2_temp[:-1] = np.array(a_rv2)
            a_rv2 = np.linalg.inv(g_parent_framebuffer1) @ a_rv2_temp
            a_rm2 = self.exp(a_rv2[:-1])
            # print("final_delta_theta_a: ")
            # print(final_delta_theta_a)
            # print("a_rv2_temp: ")
            # print(a_rv2_temp)
            # print("a_rv2: ")
            # print(a_rv2)
            # print("a_rm2: ")
            # print(a_rm2)
            # a_rm2 = self.exp(a_rv2)
            data.Limb_IK_posture.Rmatrix[g_parent.bufferIndex] = data.Limb_IK_posture.Rmatrix[g_parent.bufferIndex] @ a_rm2
            # g_parent_framebuffer2 = g_parent_framebuffer1 @ a_rm2

            # g_parent_framebuffer2 = a_rm2 @ g_parent_framebuffer1


            # Link 그려내기
            objectColor = (.8, .4, .2, 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)

            data.Limb_IK_posture.freeFramebuffer()
            data.Limb_IK_posture.make_framebuffer(motion.skeleton.root)
            self.drawModel(motion.skeleton.root, data.Limb_IK_posture)


            # temp_offset = np.identity(4)
            # temp_offset[:-1,3] = np.array(parent.offset)
            # final_parent_pos = g_parent_framebuffer2 @ temp_offset @ origin
            # parent_new_framebuffer = np.array(parent_new_orientation)
            # parent_new_framebuffer[:,3] = final_parent_pos

            # L_posture = Posture()
            # for item in posture.Rmatrix:
            #     L_posture.Rmatrix.append(np.array(item))
            # L_posture.framebuffer = [None] * (motion.skeleton.joint_num)
            # node = g_parent
            # L_framebuffer = [g_parent_framebuffer2, parent_new_framebuffer]
            
            
            # calculated_end_pos = parent_new_framebuffer @ temp_N @ origin
            
            # self.make_framebuffer_v2(node, L_posture, [node.bufferIndex,0], L_framebuffer, data.Limb_Is_drawn_nodeList)
            # self.draw_Model_v2(node, L_posture, [0])

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

            temp_N = np.identity(4)
            temp_N[:-1,3] = end.offset
            calculated_end_pos = data.Limb_IK_posture.framebuffer[parent.bufferIndex] @ temp_N @ origin
            glPushMatrix()
            # glTranslatef(final_end_pos[0],final_end_pos[1],final_end_pos[2])
            glTranslatef(calculated_end_pos[0], calculated_end_pos[1], calculated_end_pos[2])
            glScalef(ratio, ratio, ratio)
            self.drawCube_glDrawElements()
            glPopMatrix()

            # print("IK posture Rmatrix:")
            # for R in data.Limb_IK_posture.Rmatrix:
            #     print(R)
            # print("----------------------------------------")

            # data.Limb_IK_framebuffer[0] = g_parent_framebuffer2
            # data.Limb_IK_framebuffer[1] = parent_new_framebuffer
            

    def Jacobian_IK_Draw(self):
        data = self.opengl_data
        motion = self.motion
        if not data.Jacobian_IK_first_check:
            return
            
        if data.Is_Endeffector_Selected:
            J_framebuffer = data.Jacobian_IK_framebuffer
            J_nodeList = data.Jacobian_nodeList
            end = data.selected_endEffector
            posture = motion.postures[data.timeline]
            joint_num = len(data.Jacobian_IK_framebuffer)
            origin = np.array([0., 0., 0., 1.])
            M = np.identity(4)
            M[:-1,3] = end.offset

            current_end_pos = J_framebuffer[joint_num-1] @ M @ origin
            
            init_end_pos = posture.framebuffer[end.parent.bufferIndex] @ M @ origin
            final_end_pos = np.array([0.,0.,0.,1.])
            final_end_pos[:-1] = np.array(init_end_pos[:-1]) + data.endEffector_trans[:-1]
            
            delta_joint = None
            for num in range(100):
                # current_end_pos = J_framebuffer[joint_num-1] @ M @ origin
                J = np.zeros((3,joint_num*3))
                
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
                    R = None
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
            
            # Link 그려내기
            objectColor = (1., 1., 1., 1.)
            specularObjectColor = (1.,1.,1.,1.)
            glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
            glMaterialfv(GL_FRONT,GL_SHININESS,100)
            glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
                  
            # all joint draw
            J_posture = Posture(None, [])
            for item in posture.Rmatrix:
                J_posture.Rmatrix.append(np.array(item))
            J_posture.framebuffer = [None] * (motion.skeleton.joint_num)
            node = J_nodeList[0]
            self.make_framebuffer_v2(node, J_posture, [node.bufferIndex,0], J_framebuffer, data.Jacobian_Is_drawn_nodeList)
            self.draw_Model_v2(node, J_posture, [0])
            
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
        
        threshold = 0.05
        if sum < threshold:
            return True
        else:
            return False
    
    def make_framebuffer_v2(self, node, posture, index, J_framebuffer, Is_drawn_nodeList):
        # data = self.opengl_data
        
        if node.name == "__END__":
            return
        if Is_drawn_nodeList[index[0]] == 1:
            posture.framebuffer[index[0]] = np.array(J_framebuffer[index[1]])
            index[1] += 1
        else:
            M = posture.framebuffer[node.parent.bufferIndex]
            N = np.array(posture.Rmatrix[node.bufferIndex])
            N[:-1,3] = node.offset    
            posture.framebuffer[index[0]] = M @ N
        index[0] += 1
        for child in node.child:
            self.make_framebuffer_v2(child, posture, index, J_framebuffer, Is_drawn_nodeList)
    
    def draw_Model_v2(self, node, posture, index):
        if index[0] != 0:
            glPushMatrix()
            M = posture.framebuffer[node.parent.bufferIndex]
            glMultMatrixf(M.T)
            self.draw_proper_cube(node.offset)
            glPopMatrix()
       
        if node.name != "__END__":
            index[0] += 1
            for child in node.child:
                self.draw_Model_v2(child, posture, index)

                


            



            