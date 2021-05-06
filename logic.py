from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import copy

from data import *
from draw import Draw
from parsing import *
from myWidget import *
from view import *
from presenter import *
from utility import Utility as uti

class MainWindowLogic(MainWindowPresenter):
    def __init__(self, opengl, opengl_data, motion):
        self.opengl = opengl
        self.opengl_data = opengl_data
        self.motion = motion
    
    # User interface for IK
    def keyPressCB(self, key):
        # step = 1.5 * 2
        step = 1. 
        if key == "A":
            self.opengl_data.endEffector_trans[0] -= step
        elif key == "D":
            self.opengl_data.endEffector_trans[0] += step
        elif key == "W":
            self.opengl_data.endEffector_trans[1] += step
        elif key == "S":
            self.opengl_data.endEffector_trans[1] -= step
        elif key == "Z":
            self.opengl_data.endEffector_trans[2] -= step
        elif key == "X":
            self.opengl_data.endEffector_trans[2] += step
        self.opengl.viewUpdate()

class OpenGL_Logic(OpenGL_Presenter):
    def __init__(self,  opengl, opengl_data, motion, mainWindow, draw):
        self.opengl = opengl
        self.opengl_data = opengl_data
        self.motion = motion
        self.mainWindow = mainWindow
        self.draw = draw

    def IsMotionEmpty(self):
        if self.motion.frames == 0:
            return True
        else:
            return False

    def dropCB(self, file_path):
        data = self.opengl_data
        data.ENABLE_FLAG = True
        data.START_FLAG = False
        data.timeline_changed = True
        data.timeline = 0
        file_name = ''.join(file_path)
        file = open(file_name,'r')
        
        # Make "motion" object
        parsing = BVH_Parsing()
        full_list = file.readlines()
        line_num = [0]
        channel_list = []
        postures = []
        root = parsing.make_tree(full_list, None, line_num, channel_list, [0])
        postures = parsing.make_postures(full_list, line_num[0], channel_list)
        for posture in postures:
            posture.make_framebuffer(root)
       
        skeleton = Skeleton(parsing.joint_num, parsing.total_joint_num, list(parsing.jointList), root)
    
        # self.motion = Motion(skeleton, postures, parsing.frames, parsing.frame_rate)
        self.motion.skeleton = skeleton
        self.motion.postures = postures
        self.motion.frames = parsing.frames
        self.motion.frame_rate = parsing.frame_rate
        

        self.motion.skeleton.makeJointList_FK(self.motion.skeleton.root, "")
        self.motion.skeleton.makeJointList_IK(self.motion.skeleton.root, "")
        
        self.mainWindow.makeScroll(skeleton.jointListStr_FK, skeleton.jointListStr_IK, skeleton.jointList)

        # print("joint_nun: %d"%parsing.joint_num)
        print("File name: %s"%(file_name))
        print("###########################################################")
        file.close()

        # print(self.motion.postures[40].framebuffer)
        self.opengl.viewUpdate()
    
    def mousePressCB(self, pos, button):
        self.opengl_data.init_pos = pos
        if button == 'LEFT':
            self.opengl_data.Left_pressed = True
        elif button == 'RIGHT':
            self.opengl_data.Right_pressed = True
    
    def mouseReleaseCB(self, button):
        if button == 'LEFT':
            self.opengl_data.Left_pressed = False
        elif button == 'RIGHT':
            self.opengl_data.Right_pressed = False

    def mouseMoveCB(self, pos):
        xpos = pos[0]
        ypos = pos[1]
        data = self.opengl_data
        if data.Left_pressed:
            ratio = 0.02
            data.degree1 += (data.init_pos[0] - xpos) * ratio
            data.degree2 += (-data.init_pos[1] + ypos) * ratio
            if data.degree2 >= 0.:
                data.degree2 %= 360.
            else:
                data.degree2 %= -360.
            
            if 90. <= data.degree2 and data.degree2 <= 270.:
                data.cameraUp[1] = -1.
            elif -90. >= data.degree2 and data.degree2 >= -270.:
                data.cameraUp[1] = -1.
            else:
                data.cameraUp[1] = 1.
            radius = 1.
            
            data.eye[0] = radius * np.cos(np.radians(data.degree2)) * np.sin(np.radians(data.degree1))
            data.eye[1] = radius * np.sin(np.radians(data.degree2))
            data.eye[2] = radius * np.cos(np.radians(data.degree2)) * np.cos(np.radians(data.degree1))
            
        elif data.Right_pressed:
            ratio = 0.01
            cameraFront = data.eye - data.at
            temp1 = np.cross(cameraFront, data.cameraUp)
            u = temp1/np.sqrt(np.dot(temp1,temp1))
            temp2 = np.cross(u,cameraFront)
            w = temp2/np.sqrt(np.dot(temp2,temp2))
            data.trans += u *(-data.init_pos[0]+xpos)*ratio
            data.trans += w *(-data.init_pos[1]+ypos)*ratio
        
        self.opengl.viewUpdate()

    def wheelCB(self, yoffset):
        ratio = 0.15
        yoffset *= ratio
        data = self.opengl_data
        if data.scale <= 1. and yoffset > 0:
            data.scale = 1.
            self.opengl.viewUpdate()
            return
        data.scale -= yoffset
        
        self.opengl.viewUpdate()

    def IsKeepGoing(self):
        if self.opengl_data.START_FLAG:
            return True
        else:
            return False

    def paintCB(self):
        self.draw.render()
        # if self.opengl_data.START_FLAG or self.opengl_data.TIME_WARPING_FLAG:
        if self.opengl_data.START_FLAG or self.opengl_data.MOTION_WARPING_FLAG:
            self.opengl.viewUpdate()

class RadioButtonLogic(RadioPresenter):
    def __init__(self, opengl, opengl_data, motion, radioButton=None):
        self.opengl = opengl
        self.opengl_data = opengl_data
        self.motion = motion
        # self.radioButton = radioButton
    
    def FKPressCB(self, joint_index):
        
        self.opengl_data.Is_Joint_Selected = True
        self.opengl_data.selected_joint = joint_index
        self.opengl.viewUpdate()
    
    def IKPressCB(self, joint):
        data = self.opengl_data
        posture = self.motion.postures[data.timeline]
        data.Is_Endeffector_Selected = True
        data.selected_endEffector = joint
        data.endEffector_trans = np.array([0., 0., 0., 0.])
        data.Limb_IK_framebuffer = []
        end = data.selected_endEffector
        posture = self.motion.postures[data.timeline]
        parent = end.parent
        g_parent = parent.parent
        joint_num = self.motion.skeleton.joint_num
        # initialize Limb IK posture
        data.Limb_IK_posture = Posture(np.array(posture.origin), list(posture.Rmatrix))
        data.Limb_IK_posture.make_framebuffer(self.motion.skeleton.root)

        # initialize Jacobian IK framebuffer
        temp_framebuffer, temp_nodeList = self.makeTempFramebuffer(end,posture,[],[])
        data.Jacobian_IK_framebuffer = []
        data.Jacobian_nodeList = []
        data.Jacobian_Is_drawn_nodeList = np.zeros(joint_num)
        for i in range(len(temp_framebuffer)-1,-1,-1):
            data.Jacobian_IK_framebuffer.append(temp_framebuffer[i])
            data.Jacobian_nodeList.append(temp_nodeList[i])
            data.Jacobian_Is_drawn_nodeList[temp_nodeList[i].bufferIndex] = 1
            # print(temp_nodeList[i].name)

        self.opengl.viewUpdate()
    
    def makeTempFramebuffer(self,end,posture,temp_buffer,temp_nodeList):
        parent = end.parent
        # root 빼주기
        if parent.bufferIndex == 0:
            return 
        temp_buffer.append(posture.framebuffer[parent.bufferIndex])
        temp_nodeList.append(parent)
        self.makeTempFramebuffer(parent,posture,temp_buffer,temp_nodeList)
        return temp_buffer, temp_nodeList

class CheckBoxLogic(CheckBoxPresenter):
    def __init__(self, opengl, opengl_data, motion):
        self.opengl = opengl
        self.opengl_data = opengl_data
        self.motion = motion
    
    def FK_CheckBoxCB(self, IsChecked):
        if IsChecked:
            self.opengl_data.fk_first_check = True
        else:
            self.opengl_data.fk_first_check = False
        self.opengl.viewUpdate()
    
    def LimbIK_CheckBoxCB(self, IsChecked):
        if IsChecked:
            self.opengl_data.Limb_IK_first_check = True
        else:
            self.opengl_data.Limb_IK_first_check = False
        self.opengl.viewUpdate()
    
    def JacobianIK_CheckBoxCB(self, IsChecked):
        if IsChecked:
            self.opengl_data.Jacobian_IK_first_check = True
        else:
            self.opengl_data.Jacobian_IK_first_check = False
        self.opengl.viewUpdate()

class PushButtonLogic(PushButtonPresenter):
    def __init__(self, opengl, opengl_data, motion, draw):
        self.opengl = opengl
        self.opengl_data = opengl_data
        self.motion = motion
        self.draw = draw

    def startPressCB(self):
        self.opengl_data.START_FLAG = not self.opengl_data.START_FLAG
        self.opengl.viewUpdate()

    
    def fplusPressCB(self):
        self.opengl_data.timeline_changed = True
        self.opengl_data.timeline += 1
        self.opengl.viewUpdate()
    
    
    def fminusPressCB(self):
        self.opengl_data.timeline_changed = True
        self.opengl_data.timeline -= 1
        self.opengl.viewUpdate()
    
    def initPressCB(self):
        self.opengl_data.timeline_changed = True
        self.opengl_data.timeline = 0
        self.opengl.viewUpdate()
    
    def pointDrawCB(self, position):
        self.opengl_data.point = np.array(position)
        self.opengl_data.POINT_FLAG = True
        self.opengl.viewUpdate()
    
    def lineDrawCB(self, positions):
        self.opengl_data.line = np.array(positions)
        self.opengl_data.LINE_FLAG = True
        self.opengl.viewUpdate()
    
    def timeWarpingCB(self, funcType, coeff):
        func = None
        if funcType == 0:
            func = uti.linearFunc
        elif funcType == 1:
            func = uti.sinFunc
        self.draw.setTimeWarpingMotion(self.motion.timeWarping(func, coeff))
        self.opengl_data.TIME_WARPING_FLAG = True
        self.opengl_data.TW_timeline = 0

        self.opengl_data.START_FLAG = True
        self.opengl_data.timeline = 1
        self.opengl.viewUpdate()
    
    def motionWarpingCB(self, funcType, startF, endF):
        self.draw.setMotionWarpingMotion(self.motion.motionWarping(self.opengl_data.timeline, self.opengl_data.Limb_IK_posture, startF, endF, funcType))
        self.opengl_data.MOTION_WARPING_FLAG = True
        self.opengl_data.MW_timeline = 1
        
        # self.opengl_data.START_FLAG = True
        # self.opengl_data.timeline = 1
        self.opengl.viewUpdate()

            

class SliderLogic(SliderPresenter):
    def __init__(self, opengl, opengl_data, motion, sliderView=None):
        self.opengl = opengl
        self.opengl_data = opengl_data
        self.motion = motion
        self.sliderView = sliderView
        self.value = None
    
    def getTotalFrames(self):
        return self.motion.frames
    
    def getCurrentFrame(self):
        return self.opengl_data.timeline

    def frameDecision(self, value, bar_len):
        self.opengl_data.timeline = int(self.motion.frames * value / bar_len)
        self.opengl.viewUpdate()
    

class LabelLogic(LabelPresenter):
    def __init__(self, opengl, opengl_data, motion):
        self.opengl = opengl
        self.opengl_data = opengl_data
        self.motion = motion
    
    def getTotalFrames(self):
        return self.motion.frames
    
    def getTimeLine(self):
        return self.opengl_data.timeline
    
    def getOriginPos(self):
        return self.motion.postures[self.opengl_data.timeline].origin
    
    def getJointPos(self):
        return self.opengl_data.current_joint_pos

class LineEditLogic(LineEditPresenter):
    def __init__(self, opengl, opengl_data, motion):
        self.opengl = opengl
        self.opengl_data = opengl_data
        self.motion = motion

    def frameNumCB(self, new_frame):
        self.opengl_data.timeline_changed = True
        self.opengl_data.timeline = new_frame
        self.opengl.viewUpdate()


# class FK_RadioLogic(RadioPresenter):
#     def __init__(self, opengl_data, opengl, radioButton=None):
#         self.opengl_data = opengl_data
#         self.opengl = opengl
#         self.radioButton = radioButton

#     def mousePressCB(self, joint_index):
#         self.opengl_data.Is_Joint_Selected = True
#         self.opengl_data.selected_joint = joint_index
#         self.opengl.viewUpdate()

# class IK_RadioLogic(RadioPresenter):
#     def __init__(self, opengl_data, motion, opengl, radioButton=None):
#         self.opengl_data = opengl_data
#         self.motion = motion
#         self.opengl = opengl
#         self.radioButton = radioButton
    
#     def mousePressCB(self, joint):
#         data = self.opengl_data
#         data.Is_Endeffector_Selected = True
#         data.selected_endEffector = joint
#         data.endEffector_trans = np.array([0., 0., 0., 0.])
#         data.Limb_IK_framebuffer = []
#         end = data.selected_endEffector
#         posture = self.motion.postures[data.timeline]
#         parent = end.parent
#         g_parent = parent.parent
#         # initialize Limb IK framebuffer
#         data.Limb_IK_framebuffer.append(posture.framebuffer[g_parent.bufferIndex])
#         data.Limb_IK_framebuffer.append(posture.framebuffer[parent.bufferIndex])
#         # initialize Jacobian IK framebuffer
#         temp_framebuffer, temp_nodeList = self.makeTempFramebuffer(end,posture,[],[])
#         data.Jacobian_IK_framebuffer = []
#         data.Jacobian_nodeList = []
#         joint_num = len(self.motion.skeleton.joint_num)
#         data.Jacobian_Is_drawn_nodeList = np.zeros(joint_num)
#         for i in range(len(temp_framebuffer)-1,-1,-1):
#             self.opengl.Jacobian_IK_framebuffer.append(temp_framebuffer[i])
#             self.opengl.Jacobian_nodeList.append(temp_nodeList[i])
#             self.opengl.Jacobian_Is_drawn_nodeList[temp_nodeList[i].bufferIndex] = 1
#             print(temp_nodeList[i].name)

#         self.opengl.viewUpdate()
    
#     def makeTempFramebuffer(self,end,posture,temp_buffer,temp_nodeList):
#         parent = end.parent
#         # root 빼주기
#         if parent.bufferIndex == 0:
#             return 
#         temp_buffer.append(posture.framebuffer[parent.bufferIndex])
#         temp_nodeList.append(parent)
#         self.makeTempFramebuffer(parent,posture,temp_buffer,temp_nodeList)
#         return temp_buffer, temp_nodeList