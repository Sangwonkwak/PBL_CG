from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from utility import Utility as uti

class Node:
    def __init__(self, name=None):
        self.name = name
        self.offset = np.zeros(3)
        self.child = []
        self.parent = None
        self.bufferIndex = None

class Skeleton:
    def __init__(self, joint_num, total_joint_num, jointList, root):
        self.root = root
        self.joint_num = joint_num
        self.total_joint_num = total_joint_num
        self.jointListStr_FK = []
        self.jointListStr_IK = []
        self.jointList = jointList

    def makeJointList_FK(self, node, str=None):
        if node.name != "__END__":
            self.jointListStr_FK.append(str+node.name)
            temp_str = str + "-"
            for child in node.child:
                self.makeJointList_FK(child, temp_str)
    
    def makeJointList_IK(self, node, str=None):
        self.jointListStr_IK.append(str+node.name)
        temp_str = str + "-"
        for child in node.child:
            self.makeJointList_IK(child, temp_str)
    
class Posture:
    def __init__(self, origin, Rmatrix):
        self.origin = origin
        self.Rmatrix = Rmatrix
        self.framebuffer = []
    
    def freeFramebuffer(self):
        self.framebuffer = []

    def make_framebuffer(self, node):
        if node.name != "__END__":
            index = node.bufferIndex
            M = np.array(self.Rmatrix[index])
            if index == 0:
                self.framebuffer.append(M)
            else:
                M[:-1,3] = np.array(node.offset)
                N = np.array(self.framebuffer[node.parent.bufferIndex])
                N = N @ M
                self.framebuffer.append(N)
            for child in node.child:
                self.make_framebuffer(child)
    
    @staticmethod
    def postureInterpolation(posture1, posture2, t):
        #postion interpolation
        new_origin = (1.-t) * posture1.origin + t * posture2.origin
        #orientation interpolation
        new_Rmatrix = []
        for R1, R2 in zip(posture1.Rmatrix,posture2.Rmatrix):
            new_R = np.identity(4)
            new_R[:-1,:-1] = uti.slerp(R1, R2, t)
            new_Rmatrix.append(new_R)
        new_Rmatrix[0][:-1,3] = new_origin
        new_posture = Posture(new_origin, new_Rmatrix)
        
        return new_posture
    
    @staticmethod
    def postureDifference(posture1, posture2):
        pos_dif = posture2.origin - posture1.origin
        ori_dif = []
        for R1, R2 in zip(posture1.Rmatrix,posture2.Rmatrix):
            new_R = np.identity(4)
            new_R[:-1,:-1] = R1[:-1,:-1].T @ R2[:-1,-1]
            ori_dif.append(new_R)
        # ori_dif[0][:-1,3] = pos_dif
        new_posture = Posture(pos_dif, ori_dif)
        return new_posture

class Motion:
    def __init__(self, skeleton=None, postures=None, frames=0, frame_rate=0):
        self.skeleton = skeleton
        self.postures = postures
        self.frames = frames
        self.frame_rate = frame_rate
    
    # def timeWarping(self, funct):
    def timeWarping(self):
        new_postures = []
        i = 1
        while(True):
            new_frame = 1.4 * i
            if new_frame > self.frames:
                i -= 1
                break
            a = int(new_frame) 
            t = new_frame - a
            new_posture = Posture.postureInterpolation(self.postures[a], self.postures[a+1], t)
            new_postures.append(new_posture)
            i += 1
        return Motion(self.skeleton, new_postures, i, self.frame_rate)
    
    def motionWarping(self, frame, new_posture):
        posture_dif = Posture.postureDifference(self.postures[frame], new_posture)
        
        new_postures = []
        temp_Rmatrix = []
        for i in range(self.skeleton.joint_num):
            M = np.identity(4)
            temp_Rmatrix.append(M)
        posture0 = Posture(np.zeros(3),temp_Rmatrix)
        new_postures.append(posture0)

        t1 = 1. / frame
        for i in range(1, frame+1):
            new_Rmatrix = []
            for R1,R2 in zip(self.postures[i].Rmatrix, new_posture.Rmatrix):
                new_R = np.identity(4)
                new_R[:-1,:-1] = uti.addByT(R1,R2,i*t1)
                new_Rmatrix.append(new_R)
            new_posture = Posture(self.postures[i].origin, new_Rmatrix)
            new_postures.append(new_posture)
        
        t2 = 1. / (self.frames - frame)
        for i in range(frame+1, self.frames+1):
            k = 1. - (i-frame/(self.frames-frame))
            new_Rmatrix = []
            for R1,R2 in zip(self.postures[i].Rmatrix, new_posture.Rmatrix):
                new_R = np.identity(4)
                new_R[:-1,:-1] = uti.addByT(R1,R2,k*t2)
                new_Rmatrix.append(new_R)
            new_posture = Posture(self.postures[i].origin, new_Rmatrix)
            new_postures.append(new_posture)
        
        return Motion(self.skeleton, new_postures, self.frames, self.frame_rate)
        
class OpenGL_Data():
    def __init__(self):
        self.Left_pressed = False
        self.Right_pressed = False
        self.degree1 = 0.
        self.degree2 = 0.
        self.init_pos = np.array([0,0])
        self.eye = np.array([0.,0.,1.])
        self.at = np.array([0.,0.,0.])
        self.cameraUp = np.array([0.,1.,0.])
        # self.scale = 1.
        self.scale = 100.
        self.trans = np.array([0.,0.,0.])
        self.full_list = []
        self.START_FLAG = False
        self.ENABLE_FLAG = False
        self.timeline_changed = False
        self.timeline = 0
        self.motion = None
        self.draw = None
        self.POINT_FLAG = False
        self.point = np.zeros(3)
        self.LINE_FLAG = False
        self.line = np.zeros((2,3))
        
        self.fk_first_check = False
        self.Is_Joint_Selected = False
        self.selected_joint = -1
        self.motion_scale_ratio = 1.
        self.current_joint_pos = None

        self.Limb_IK_first_check = False
        self.Jacobian_IK_first_check = False
        self.Is_Endeffector_Selected = False
        self.selected_endEffector = None
        self.endEffector_trans = np.array([0., 0., 0., 0.])


        # self.Limb_IK_framebuffer = []
        # self.Limb_Is_drawn_nodeList = None
        self.Limb_IK_posture = None



        self.Jacobian_IK_framebuffer = []
        self.Jacobian_nodeList = []
        self.Jacobian_Is_drawn_nodeList = None
