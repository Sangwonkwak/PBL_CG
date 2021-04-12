import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

from myWidget import *
from draw import *

form_class = uic.loadUiType("MotionViewer.ui")[0]

class WindowClass(QDialog, form_class) :
    def __init__(self, draw) :
        super().__init__()
        self.setUi(draw)
        self.fplusButton.setAutoRepeat(True)
        self.fminusButton.setAutoRepeat(True)
        self.startButton.setAutoDefault(False)
        self.fplusButton.setAutoDefault(False)
        self.fminusButton.setAutoDefault(False)
        self.initButton.setAutoDefault(False)

        # event handle
        self.startButton.clicked.connect(self.start_click_cb)
        self.fplusButton.pressed.connect(self.fplus_press_cb)
        self.fminusButton.pressed.connect(self.fminus_press_cb)
        self.initButton.clicked.connect(self.init_click_cb)
        self.frameNumEdit.returnPressed.connect(self.frameNum_change_cb)
        self.pointDraw_button.clicked.connect(self.pointDraw_cb)
        self.lineDraw_button.clicked.connect(self.lineDraw_cb)

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
        self.openGLWidget.setScroll(self.jointList)
        self.openGLWidget.setScroll_Endeffector(self.endEffectorList)

    def keyPressEvent(self, e):
        # Z키는 z축 -, X키는 z축 +
        step = 1.
        if e.key() == Qt.Key_A:
            self.openGLWidget.endEffector_trans[0] -= step
            self.openGLWidget.update()
        elif e.key() == Qt.Key_D:
            self.openGLWidget.endEffector_trans[0] += step
            self.openGLWidget.update()
        elif e.key() == Qt.Key_W:
            self.openGLWidget.endEffector_trans[1] += step
            self.openGLWidget.update()
        elif e.key() == Qt.Key_S:
            self.openGLWidget.endEffector_trans[1] -= step
            self.openGLWidget.update()
        elif e.key() == Qt.Key_Z:
            self.openGLWidget.endEffector_trans[2] -= step
            self.openGLWidget.update()
        elif e.key() == Qt.Key_X:
            self.openGLWidget.endEffector_trans[2] += step
            self.openGLWidget.update()

    def start_click_cb(self):
        self.openGLWidget.START_FLAG = not self.openGLWidget.START_FLAG
        self.openGLWidget.update()

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
    
    def pointDraw_cb(self):
        position = [float(self.point_x.text()), float(self.point_y.text()), float(self.point_z.text())]
        self.openGLWidget.point = np.array(position)
        self.openGLWidget.POINT_FLAG = True
        self.openGLWidget.update()
    
    def lineDraw_cb(self):
        position = np.array([[float(self.line_x1.text()), float(self.line_y1.text()), float(self.line_z1.text())], [float(self.line_x2.text()), float(self.line_y2.text()), float(self.line_z2.text())]])
        self.openGLWidget.line = np.array(position)
        self.openGLWidget.LINE_FLAG = True
        self.openGLWidget.update()
    
def main():
    app = QApplication(sys.argv)
    draw = Draw()
    draw.createVertexAndIndexArrayIndexed()
    myWindow = WindowClass(draw)
    myWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__" :
    main()