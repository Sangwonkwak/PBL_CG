# import sys
# from PyQt5.QtWidgets import *
# from PyQt5 import uic
# import glfw
# from OpenGL.GL import *
# from OpenGL.GLU import *
# import numpy as np
# import copy
import time
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
# from PyQt5.QtCore import Qt
from myWidget import *
from draw import Draw

form_class = uic.loadUiType("MotionViewer.ui")[0]

class WindowClass(QDialog, form_class) :
    def __init__(self, draw) :
        super().__init__()
        self.setUi(draw)
        self.fplusButton.setAutoRepeat(True)
        self.fminusButton.setAutoRepeat(True)
        self.startButton.setAutoDefault(False)
        # self.stopButton.setAutoDefault(False)
        self.fplusButton.setAutoDefault(False)
        self.fminusButton.setAutoDefault(False)
        self.initButton.setAutoDefault(False)

        # event handle
        self.startButton.clicked.connect(self.start_click_cb)
        # self.stopButton.clicked.connect(self.stop_click_cb)
        # self.fplusButton.clicked.connect(self.fplus_click_cb)
        self.fplusButton.pressed.connect(self.fplus_press_cb)
        # self.fminusButton.clicked.connect(self.fminus_click_cb)
        self.fminusButton.pressed.connect(self.fminus_press_cb)
        self.initButton.clicked.connect(self.init_click_cb)
        self.frameNumEdit.returnPressed.connect(self.frameNum_change_cb)
        
    def setUi(self, draw):
        self.setupUi(self)
        self.setWindowTitle("MotionViewer")
        self.setStyleSheet("background-color: #DFDFDF") 
        self.frame.setStyleSheet("background-color: #83DCB7;")
        self.openGLWidget.setDraw(draw)
        draw.setOpengl(self.openGLWidget)

        self.timeLine.setOpenGL(self.openGLWidget)
        self.openGLWidget.addTextObj(self.totalFrame)
        self.openGLWidget.addTextObj(self.currentFrame)
        self.openGLWidget.addTextObj(self.origin)
        self.openGLWidget.setSlider(self.timeLine)
        # self.frameNumEdit.setOpenGL(self.openGLWidget)

    def start_click_cb(self):
        self.openGLWidget.START_FLAG = not self.openGLWidget.START_FLAG
        self.openGLWidget.update()

    # def stop_click_cb(self):
    #     self.openGLWidget.START_FLAG = False
    #     self.openGLWidget.update()

    # def fplus_click_cb(self):
    #     self.openGLWidget.timeline_changed = True
    #     self.openGLWidget.timeline += 1
    #     self.openGLWidget.update()

    # def fminus_click_cb(self):
    #     self.openGLWidget.timeline_changed = True
    #     self.openGLWidget.timeline -= 1
    #     self.openGLWidget.update()

    def fplus_press_cb(self):
        self.openGLWidget.timeline_changed = True
        self.openGLWidget.timeline += 1
        self.openGLWidget.update()
         
    def fminus_press_cb(self):
        self.openGLWidget.timeline_changed = True
        self.openGLWidget.timeline -= 1
        self.openGLWidget.update()

    def init_click_cb(self):
        self.openGLWidget.timeline_changed = True
        self.openGLWidget.timeline = 0
        self.openGLWidget.update()
    
    def frameNum_change_cb(self):
        new_frame = int(self.frameNumEdit.text())
        self.openGLWidget.timeline_changed = True
        self.openGLWidget.timeline = new_frame
        self.openGLWidget.update()
        self.frameNumEdit.setText("")
    
def main():
    app = QApplication(sys.argv)
    draw = Draw()
    draw.createVertexAndIndexArrayIndexed()
    myWindow = WindowClass(draw)
    myWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__" :
    main()