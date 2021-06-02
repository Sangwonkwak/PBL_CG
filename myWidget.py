# import sys
from PyQt5.QtWidgets import *
# from PyQt5 import uic
from PyQt5.QtCore import Qt

import numpy as np
from draw import *
from view import *

class MyOpenGL(QOpenGLWidget):
    def __init__(self, parent=None):
        super(MyOpenGL, self).__init__(parent)
        self.setAcceptDrops(True)
        self.sliderView = None
        self.BVHLabelView = []
        self.physicsLabelView = []
        self.mainWindowView = None
        self.presenter = None

    def setPresenter(self, presenter):
        self.presenter = presenter

    def setMainWindowView(self, window):
        self.mainWindowView = window

    def setSlider(self, slider):
        self.sliderView = slider
    
    def addBVHLabel(self, label):
        self.BVHLabelView.append(label)
    
    def addPhysicsLabel(self, label):
        self.physicsLabelView.append(label)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        file_path = [unicode(u.toLocalFile()) for u in e.mimeData().urls()]
        self.presenter.dropCB(file_path)

    def mouseButtonKind(self, button):
        if button & Qt.LeftButton:
            return 'LEFT'
        elif button & Qt.RightButton:
            return 'RIGHT'
        elif button & Qt.MidButton:
            return 'MID'
        
    def mousePressEvent(self, e):
        
        button = self.mouseButtonKind(e.button())
        self.presenter.mousePressCB([e.x(),e.y()], button)
    
    def mouseReleaseEvent(self, e):
        button = self.mouseButtonKind(e.button())
        self.presenter.mouseReleaseCB(button)

    def mouseMoveEvent(self, e):

        self.presenter.mouseMoveCB([e.x(),e.y()])
    
    def wheelEvent(self, e):
        self.presenter.wheelCB(e.angleDelta().y())
    
    def paintGL(self):
        # print("4.paintGL")
        self.presenter.paintCB()
        if not self.presenter.IsMotionEmpty():
            for item in self.BVHLabelView:
                item.viewUpdate()
            self.sliderView.viewUpdate()
        if not self.presenter.IsPhysicsEmpty():
            for item in self.physicsLabelView:
                item.viewUpdate()
    
    def viewUpdate(self):
        # print("3.openglViewUpdate")
        self.update()
        # if self.presenter.IsKeepGoing():
        #     self.viewUpdate
        # print("3.5.dasd")
        # if not self.presenter.IsMotionEmpty():
        #     for item in self.labelView:
        #         item.viewUpdate()
        #     self.sliderView.viewUpdate()
        

class FK_RadioButton(QRadioButton):
    def __init__(self, name, index):
        super(FK_RadioButton, self).__init__(name)
        # super().__init__()
        self.index = index
        self.clicked.connect(self.clickEvent)

    def setPresenter(self, presenter):
        self.presenter = presenter

    # def mousePressEvent(self, e):
    #     print(self.text())
    #     self.presenter.FKPressCB(self.index)

    def clickEvent(self):
        # print("1.clickEvent")
        self.presenter.FKPressCB(self.index)

class IK_RadioButton(QRadioButton):
    def __init__(self, name, joint):
        super(IK_RadioButton, self).__init__(name)
        # super().__init__()
        self.joint = joint
        self.clicked.connect(self.clickEvent)

    def setPresenter(self, presenter):
        self.presenter = presenter

    # def mousePressEvent(self, e):
    #     print(self.text())
    #     self.presenter.IKPressCB(self.joint)
    
    def clickEvent(self):
        self.presenter.IKPressCB(self.joint)
     
class MySlider(QSlider):
    def __init__(self, parent=None):
        super(MySlider, self).__init__(parent)
        # super().__init__()
        self.bar_len = self.maximum() - self.minimum()
    
    def setPresenter(self, presenter):
        self.presenter = presenter

    def mouseButtonKind(self, buttons):
        if buttons & Qt.LeftButton:
            return 'LEFT'
        elif buttons & Qt.RightButton:
            return 'RIGHT'
        elif buttons & Qt.MidButton:
            return 'MID'
    
    def viewUpdate(self):
        frame = self.presenter.getCurrentFrame()
        frames = self.presenter.getTotalFrames()
        self.setValue(self.bar_len * frame / frames)
    
    def frameDecision(self, x):
        value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        if value < self.minimum():
            value = self.minimum()
        elif value > self.maximum():
            value = self.maximum()
        self.setValue(int(value))
        self.presenter.frameDecision(value, self.bar_len)
    
    def mousePressEvent(self, e):
        button = self.mouseButtonKind(e.buttons())
        if button == 'LEFT':
            e.accept()
            x = e.pos().x()
            self.frameDecision(x)
        
    def mouseMoveEvent(self, e):
        button = self.mouseButtonKind(e.buttons())
        if button == 'LEFT':
            e.accept()
            x = e.pos().x()
            self.frameDecision(x)

class TotalFrameLabel(QLabel):
    def __init__(self,parent=None):
        super(TotalFrameLabel,self).__init__(parent)

    def setPresenter(self, presenter):
        self.presenter = presenter

    def viewUpdate(self):
        text = "Total frames: " + str(self.presenter.getTotalFrames())
        self.setText(text)

class CurrentFrameLabel(QLabel):
    def __init__(self,parent=None):
        super(CurrentFrameLabel, self).__init__(parent)

    def setPresenter(self, presenter):
        self.presenter = presenter

    def viewUpdate(self):
        text = "Current frame: " + str(self.presenter.getTimeLine())
        self.setText(text)

class OriginPosLabel(QLabel):
    def __init__(self,parent=None):
        super(OriginPosLabel,self).__init__(parent)

    def setPresenter(self, presenter):
        self.presenter = presenter

    def viewUpdate(self):
        text = "Origin: " + str(self.presenter.getOriginPos())
        self.setText(text)

class JointPosLabel(QLabel):
    def __init__(self,parent=None):
        super(JointPosLabel,self).__init__(parent)

    def setPresenter(self, presenter):
        self.presenter = presenter

    def viewUpdate(self):
        text = "Current Joint: " + str(self.presenter.getJointPos())
        self.setText(text)

class TimeStepLabel(QLabel):
    def __init__(self,parent=None):
        super(TimeStepLabel,self).__init__(parent)

    def setPresenter(self, presenter):
        self.presenter = presenter

    def viewUpdate(self):
        text = "Time Step: " + str(self.presenter.getTimeStep())
        self.setText(text)

class KsLabel(QLabel):
    def __init__(self,parent=None):
        super(KsLabel,self).__init__(parent)

    def setPresenter(self, presenter):
        self.presenter = presenter

    def viewUpdate(self):
        text = "Spring Stiffness: " + str(self.presenter.getKs())
        self.setText(text)

class KdLabel(QLabel):
    def __init__(self,parent=None):
        super(KdLabel,self).__init__(parent)

    def setPresenter(self, presenter):
        self.presenter = presenter

    def viewUpdate(self):
        text = "Damping: " + str(self.presenter.getKd())
        self.setText(text)

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

            
