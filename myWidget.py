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
        self.scale = 1.
        self.trans = np.array([0.,0.,0.])
        self.full_list = []
        self.START_FLAG = False
        self.ENABLE_FLAG = False
        self.timeline_changed = False
        self.timeline = 0
        self.motion = None
        self.draw = None

        self.textList = []
        self.mySlider = None
        self.setAcceptDrops(True)
    
    def setDraw(self, draw):
        self.draw = draw
    
    def addTextObj(self, text):
        self.textList.append(text)
    
    def setSlider(self, myslider):
        self.mySlider = myslider
        
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
        root = parsing.make_tree(self.full_list, Node(), line_num, channel_list)
        postures = parsing.make_postures(self.full_list, line_num[0], channel_list)
        skeleton = Skeleton(root, parsing.joint_num)
        
        # for i in range(parsing.joint_num):
        #     print(postures[1].Rmatrix[i], end=' ')
        # print()

        self.motion = Motion(skeleton, postures, parsing.frames)
        

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
        else:
            return 'what?'
        
    def mousePressEvent(self, e):
        button = self.mouseButtonKind(e.button())
        self.init_pos[0] = e.x()
        self.init_pos[1] = e.y()

        if button == 'LEFT':
            print("LEFT")
            self.Left_pressed = True
        elif button == 'RIGHT':
            print("RIGHT")
            self.Right_pressed = True
    
    def mouseReleaseEvent(self, e):
        button = self.mouseButtonKind(e.button())
        print("released")
        print(button)
        if button == 'RIGHT':
            print("RIGHT RELEASE")
            self.Right_pressed = False
        elif button == 'LEFT':
            print("LEFT RELEASE")
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
            self.eye[0] = 0.1 * np.cos(np.radians(self.degree2)) * np.sin(np.radians(self.degree1))
            self.eye[1] = 0.1 * np.sin(np.radians(self.degree2))
            self.eye[2] = 0.1 * np.cos(np.radians(self.degree2)) * np.cos(np.radians(self.degree1))
            
        elif self.Right_pressed:
            ratio = 0.0001
            cameraFront = self.eye - self.at
            temp1 = np.cross(cameraFront, self.cameraUp)
            u = temp1/np.sqrt(np.dot(temp1,temp1))
            temp2 = np.cross(u,cameraFront)
            w = temp2/np.sqrt(np.dot(temp2,temp2))
            self.trans += u *(-self.init_pos[0]+xpos)*ratio
            self.trans += w *(-self.init_pos[1]+ypos)*ratio
        self.update()
    
    def wheelEvent(self, e):
        ratio = 0.03
        yoffset = e.angleDelta().y() * ratio
        if self.scale <= 0.1 and yoffset == 1:
            self.scale = 0.1
            return
        self.scale -= 0.1 * yoffset
        self.update()
    
    def paintGL(self):
        self.draw.render()
        if self.motion != None:
            text1 = "Total frames: " + str(self.motion.frames)
            text2 = "Current frame: " + str(self.timeline)
            text3 = "Origin: " + str(self.motion.postures[self.timeline].origin)
            self.textList[0].setText(text1)
            self.textList[1].setText(text2)
            self.textList[2].setText(text3)
            self.mySlider.value_decision(self.timeline)

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

            
