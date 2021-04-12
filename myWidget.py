import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt

import numpy as np
from draw import *

class myopenGL(QOpenGLWidget):
    def __init__(self, parent=None):
        super(myopenGL, self).__init__(parent)
        self.Left_pressed = False
        self.Right_pressed = False
        self.degree1 = 0.
        self.degree2 = 0.
        self.init_pos = np.array([0,0])
        self.eye = np.array([0.,0.,.1])
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
        self.Is_Joint_Selected = False
        self.selected_joint = -1
        # self.motion_scale_ratio = 0.005
        self.motion_scale_ratio = 1.

        self.Is_Endeffector_Selected = False
        self.selected_endEffector = None
        self.endEffector_trans = np.array([0., 0., 0., 0.])
        self.Limb_IK_framebuffer = []

        self.textList = []
        self.mySlider = None
        self.scrollArea = None
        self.scrollArea_Endeffector = None
        self.setAcceptDrops(True)
    
    def setDraw(self, draw):
        self.draw = draw
    
    def addTextObj(self, text):
        self.textList.append(text)
    
    def setSlider(self, myslider):
        self.mySlider = myslider
    
    def setScroll(self, scroll):
        self.scrollArea = scroll
    
    def setScroll_Endeffector(self, scroll):
        self.scrollArea_Endeffector = scroll
        
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        file_path = [unicode(u.toLocalFile()) for u in e.mimeData().urls()]
        self.ENABLE_FLAG = True
        self.START_FLAG = False
        self.timeline_changed = True
        self.timeline = 0
        file_name = ''.join(file_path)
        file = open(file_name,'r')
        
        # Make "motion" object
        parsing = Parsing()
        self.full_list = file.readlines()
        
        line_num = [0]
        channel_list = []
        postures = []
        root = parsing.make_tree(self.full_list, Node(), line_num, channel_list, [0])
        postures = parsing.make_postures(self.full_list, line_num[0], channel_list)
        skeleton = Skeleton(root, parsing.joint_num)
        self.motion = Motion(skeleton, postures, parsing.frames, parsing.frame_rate)

        # Joint scroll area 만들기
        self.motion.skeleton.make_jointList(self.motion.skeleton.root, "")
        widget = QWidget()
        vbox = QVBoxLayout()

        def radioButton_cb():
            self.Is_Joint_Selected = True
            for i in range(parsing.joint_num):
                if vbox.itemAt(i).widget().isChecked():
                    # print(i)
                    self.selected_joint = i
            self.update()
        
        for name in self.motion.skeleton.joint_list:
            obj = QRadioButton(name, self.scrollArea)
            obj.clicked.connect(radioButton_cb) 
            vbox.addWidget(obj)
        widget.setLayout(vbox)
        self.scrollArea.setWidget(widget)

        # End Effector scroll area 만들기
        end_list, end_name_list = self.motion.skeleton.make_endEffectorList(self.motion.skeleton.root, [], [])
        widget2 = QWidget()
        vbox2 = QVBoxLayout()

        for i in range(len(end_list)):
            name = end_name_list[i]
            obj = MyRadioButton(name)
            obj.setNode(end_list[i])
            obj.setOpenGL(self)
            obj.clicked.connect(obj.click_cb)
            vbox2.addWidget(obj)
        widget2.setLayout(vbox2)
        self.scrollArea_Endeffector.setWidget(widget2)

        print("File name: %s"%(file_name))
        print("###########################################################")
        file.close()
        self.update()

    def mouseButtonKind(self, button):
        if button & Qt.LeftButton:
            return 'LEFT'
        elif button & Qt.RightButton:
            return 'RIGHT'
        elif button & Qt.MidButton:
            return 'MID'
        
    def mousePressEvent(self, e):
        button = self.mouseButtonKind(e.button())
        self.init_pos[0] = e.x()
        self.init_pos[1] = e.y()

        if button == 'LEFT':
            self.Left_pressed = True
        elif button == 'RIGHT':
            self.Right_pressed = True
    
    def mouseReleaseEvent(self, e):
        button = self.mouseButtonKind(e.button())
        if button == 'RIGHT':  
            self.Right_pressed = False
        elif button == 'LEFT':
            self.Left_pressed = False

    def mouseMoveEvent(self, e):
        xpos = e.x()
        ypos = e.y()
        if self.Left_pressed:
            ratio = 0.02
            self.degree1 += (self.init_pos[0] - xpos) * ratio
            self.degree2 += (-self.init_pos[1] + ypos) * ratio
            if self.degree2 >= 0.:
                self.degree2 %= 360.
            else:
                self.degree2 %= -360.
            
            if 90. <= self.degree2 and self.degree2 <= 270.:
                self.cameraUp[1] = -1.
            elif -90. >= self.degree2 and self.degree2 >= -270.:
                self.cameraUp[1] = -1.
            else:
                self.cameraUp[1] = 1.
            # radius = 0.1
            radius = 20
            self.eye[0] = radius * np.cos(np.radians(self.degree2)) * np.sin(np.radians(self.degree1))
            self.eye[1] = radius * np.sin(np.radians(self.degree2))
            self.eye[2] = radius * np.cos(np.radians(self.degree2)) * np.cos(np.radians(self.degree1))
            
        elif self.Right_pressed:
            ratio = 0.01
            cameraFront = self.eye - self.at
            temp1 = np.cross(cameraFront, self.cameraUp)
            u = temp1/np.sqrt(np.dot(temp1,temp1))
            temp2 = np.cross(u,cameraFront)
            w = temp2/np.sqrt(np.dot(temp2,temp2))
            self.trans += u *(-self.init_pos[0]+xpos)*ratio
            self.trans += w *(-self.init_pos[1]+ypos)*ratio
        self.update()
    
    def wheelEvent(self, e):
        ratio = 0.15
        yoffset = e.angleDelta().y() * ratio
        if self.scale <= 1. and yoffset > 0:
            self.scale = 1.
            return
        self.scale -= yoffset
        self.update()
    
    def paintGL(self):
        self.draw.render()
        if self.motion != None:
            text1 = "Total frames: " + str(self.motion.frames)
            text2 = "Current frame: " + str(self.timeline)
            origin = np.array(self.motion.postures[self.timeline].origin)
            for i in range(3):
                    origin[i] *= self.motion_scale_ratio
            text3 = "Origin: " + str(origin)
            # text3 = "Origin: " + str(self.motion_scale_ratio * self.motion.postures[self.timeline].origin)
            self.textList[0].setText(text1)
            self.textList[1].setText(text2)
            self.textList[2].setText(text3)
            self.mySlider.value_decision(self.timeline)

class MyRadioButton(QRadioButton):
    def __init__(self, parent=None):
        super(MyRadioButton, self).__init__(parent)
        self.end_node = None
        self.opengl = None

    def setNode(self, node):
        self.end_node = node
    
    def setOpenGL(self, opengl):
        self.opengl = opengl
    
    def click_cb(self):
        print("click_callback")
        self.opengl.Is_Endeffector_Selected = True
        self.opengl.selected_endEffector = self.end_node
        self.opengl.endEffector_trans = np.array([0., 0., 0., 0.])
        self.opengl.Limb_IK_framebuffer = []
        end = self.opengl.selected_endEffector
        posture = self.opengl.motion.postures[self.opengl.timeline]
        parent = end.parent
        g_parent = parent.parent
        self.opengl.Limb_IK_framebuffer.append(posture.framebuffer[g_parent.bufferIndex])
        self.opengl.Limb_IK_framebuffer.append(posture.framebuffer[parent.bufferIndex])

        self.opengl.update()
    
class mySlider(QSlider):
    def __init__(self, parent=None):
        super(mySlider, self).__init__(parent)
        self.myopengl = None
        self._is_drag = False
    
    def setOpenGL(self, myopengl):
        self.myopengl = myopengl
    
    def mouseButtonKind(self, buttons):
        if buttons & Qt.LeftButton:
            return 'LEFT'
        elif buttons & Qt.RightButton:
            return 'RIGHT'
        elif buttons & Qt.MidButton:
            return 'MID'
    
    def value_decision(self, frame):
        bar_len = self.maximum() - self.minimum()
        self.setValue(bar_len * frame / self.myopengl.motion.frames)
    
    def frame_decision(self, x):
        value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        if value < self.minimum():
            value = self.minimum()
        elif value > self.maximum():
            value = self.maximum()
        bar_len = self.maximum() - self.minimum()
        self.myopengl.timeline = int(self.myopengl.motion.frames * value / bar_len)
        self.setValue(int(value))
        self.myopengl.update()
    
    def mousePressEvent(self, e):
        button = self.mouseButtonKind(e.buttons())
        if button == 'LEFT':
            e.accept()
            x = e.pos().x()
            self.frame_decision(x)
        
    def mouseMoveEvent(self, e):
        button = self.mouseButtonKind(e.buttons())
        if button == 'LEFT':
            e.accept()
            x = e.pos().x()
            self.frame_decision(x)
            
            if not self._is_drag:
                self._is_drag = True

    def mouseReleaseEvent(self, e):
        button = self.mouseButtonKind(e.buttons())
        if button == 'LEFT' and self._is_drag:
            e.accept()
            self._is_drag = False

# class myEdit(QTextEdit):
#     def __init__(self, parent=None):
#         super(myEdit, self).__init__(parent)
#         self.myopengl = None
#         # self.setStyleSheet('color:red;font-size:45px;')
#         self.setStyleSheet('font-size:17px;')
    
#     def setOpenGL(self, myopengl):
#         self.myopengl = myopengl
    
#     def keyPressEvent(self, e):
#         if e.key() & Qt.Key_Return:
#             print("NICE")
#         else:
#             self.keyPressEvent(e)

            
