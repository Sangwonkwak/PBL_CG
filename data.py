from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import copy

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
        a = np.zeros(3)
        b = np.zeros(3)
        for i in range(3):
            a[i] = (1-t) * posture1.origin[i]
            b[i] = t * posture2.origin[i]
        new_origin = a + b
        #orientation interpolation
        new_Rmatrix = []
        for R1, R2 in zip(posture1.Rmatrix,posture2.Rmatrix):
            new_R = np.identity(4)
            new_R[:-1,:-1] = uti.slerp(R1[:-1,:-1], R2[:-1,:-1], t)
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
            new_R[:-1,:-1] = R1[:-1,:-1].T @ R2[:-1,:-1]
            ori_dif.append(np.array(new_R))
            
        
        new_posture = Posture(pos_dif, ori_dif)
        return new_posture
    
    @staticmethod
    def postureDifference_v2(posture1, posture2):
        pos_dif = np.array(posture1.origin) - np.array(posture2.origin)
        ori_dif = []
        
        for R1, R2 in zip(posture1.Rmatrix,posture2.Rmatrix):
            new_R = np.identity(4)
            new_R[:-1,:-1] = R1[:-1,:-1] @ R2[:-1,:-1].T
            ori_dif.append(np.array(new_R))
            
        
        new_posture = Posture(pos_dif, ori_dif)
        return new_posture

class Motion:
    def __init__(self, skeleton=None, postures=None, frames=0, frame_rate=0):
        self.skeleton = skeleton
        self.postures = postures
        self.frames = frames
        self.frame_rate = frame_rate
    
    def timeWarping(self, func, coeff):
        new_postures = []
        i = 1
        while(True):
            new_frame = None
            if func == uti.linearFunc:
                new_frame = func(coeff, i)
            elif func == uti.sinFunc:
                new_frame = func(self.frames, i)
            else:
                print("Not yet implemented!!")

            if new_frame == self.frames:
                new_posture = copy.deepcopy(self.postures[self.frames])
                new_postures.append(new_posture)
                break
            if new_frame > self.frames:
                i -= 1
                break
            a = int(new_frame) 
            t = new_frame - a
            
            new_posture = Posture.postureInterpolation(self.postures[a], self.postures[a+1], t)
            new_postures.append(new_posture)
            i += 1

        for posture in new_postures:
            posture.make_framebuffer(self.skeleton.root)

        return Motion(self.skeleton, new_postures, i, self.frame_rate)
    
    def motionWarping(self, frame, new_posture, startF, endF, funcType):
        posture_dif = Posture.postureDifference(self.postures[frame], new_posture)
        
        new_postures = []
        
        for posture in self.postures:
            new_postures.append(Posture(np.array(posture.origin),list(posture.Rmatrix)))
        
        first_slice = frame - startF
        second_slice = endF - frame
        first_func = None
        second_func = None
        firstArg = None
        secondArg = None
        if funcType == 0:
            first_func = uti.linearFunc_t
            second_func = uti.linearFunc2_t
            firstArg = 1. / first_slice
            secondArg = 1. / second_slice
        elif funcType == 1:
            first_func = uti.sinFunc_t
            second_func = uti.cosFunc_t
            firstArg = first_slice
            secondArg = second_slice

        for i in range(startF, frame+1):
            t = first_func(firstArg, i-startF)
            b = np.zeros(3)
            for j in range(3):
                b[j] = t * posture_dif.origin[j]
            new_origin = self.postures[i].origin + b
            
            new_Rmatrix = []
            for R1,R2 in zip(self.postures[i].Rmatrix, posture_dif.Rmatrix):
                new_R = np.identity(4)
                new_R[:-1,:-1] = uti.addByT(R1[:-1,:-1],R2[:-1,:-1],t)
                new_Rmatrix.append(new_R)
            new_postures[i] = Posture(new_origin, new_Rmatrix)
            
        
        for i in range(frame+1, endF+1):
            t = second_func(secondArg, i-frame)
            b = np.zeros(3)
            for j in range(3):
                b[j] = t * posture_dif.origin[j]
            new_origin = self.postures[i].origin + b
            
            new_Rmatrix = []
            for R1,R2 in zip(self.postures[i].Rmatrix, posture_dif.Rmatrix):
                new_R = np.identity(4)
                new_R[:-1,:-1] = uti.addByT(R1[:-1,:-1],R2[:-1,:-1],t)
                new_Rmatrix.append(new_R)
            new_postures[i] = Posture(new_origin, new_Rmatrix)
            
            
        for posture in new_postures:
            posture.Rmatrix[0][:-1,3] = posture.origin
            posture.make_framebuffer(self.skeleton.root)
        
        return Motion(self.skeleton, new_postures, self.frames, self.frame_rate)
    
    @staticmethod
    def motionStitching(M1, M2, slice, funcType):
        A_endPos = M1.postures[M1.frames]
        B_startPos = M2.postures[1]
        pos_dif = Posture.postureDifference_v2(A_endPos,B_startPos)
        # project to y-axis
        for i in range(len(pos_dif.Rmatrix)):
            new_R = np.identity(4)
            new_R[:-1,:-1] = uti.projection_y(pos_dif.Rmatrix[i][:-1,:-1])
            pos_dif.Rmatrix[i] = new_R
            
        newB_postures = []
        for i in range(1, M2.frames+1):
            newB_postures.append(Posture(np.array(M2.postures[i].origin),list(M2.postures[i].Rmatrix)))
        
        # Alignment
        for posture in newB_postures:
            posture.origin = A_endPos.origin + pos_dif.Rmatrix[0][:-1,:-1] @ (posture.origin - B_startPos.origin)
            posture.Rmatrix[0][:-1,:-1] = pos_dif.Rmatrix[0][:-1,:-1] @ posture.Rmatrix[0][:-1,:-1]
            posture.Rmatrix[0][:-1,3] = posture.origin
        
        # Motion Warping
        # pos_dif = Posture.postureDifference_v2(A_endPos,newB_postures[0])
        pos_dif = Posture.postureDifference(newB_postures[0],A_endPos)
        # project to y-axis
        for i in range(len(pos_dif.Rmatrix)):
            new_R = np.identity(4)
            new_R[:-1,:-1] = uti.projection_y(pos_dif.Rmatrix[i][:-1,:-1])
            pos_dif.Rmatrix[i] = new_R
            
        func = None
        arg = None
        if funcType == 0:
            func = uti.linearFunc2_t
            arg = 1. / slice
        elif funcType == 1:
            func = uti.cosFunc_t
            arg = slice

        for i in range(1, slice+1):
            t = func(arg, i)
            b = np.zeros(3)
            for j in range(3):
                b[j] = t * pos_dif.origin[j]
            new_origin = newB_postures[i].origin + b

            new_Rmatrix = []
            # for R1,R2 in zip(pos_dif.Rmatrix, newB_postures[i].Rmatrix):
            for R1,R2 in zip(newB_postures[i].Rmatrix, pos_dif.Rmatrix):
                new_R = np.identity(4)
                # new_R[:-1,:-1] = uti.addByT_v2(R1[:-1,:-1],R2[:-1,:-1],t)
                new_R[:-1,:-1] = uti.addByT(R1[:-1,:-1],R2[:-1,:-1],t)
                new_Rmatrix.append(new_R)
            new_Rmatrix[0][:-1,3] = new_origin
            newB_postures[i] = Posture(new_origin, new_Rmatrix)
        
        # Concatenate
        for i in range(1, M2.frames):
            newB_postures[i].make_framebuffer(M1.skeleton.root)
            M1.postures.append(newB_postures[i])
        M1.frames = M1.frames + (M2.frames-1)

        return M1


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
        self.Limb_IK_posture = None



        self.Jacobian_IK_framebuffer = []
        self.Jacobian_nodeList = []
        self.Jacobian_Is_drawn_nodeList = None

        self.TIME_WARPING_FLAG = False
        self.TW_timeline = 0
        self.MOTION_WARPING_FLAG = False
        self.MW_timeline = 0

