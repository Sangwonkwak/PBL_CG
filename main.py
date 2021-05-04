import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
# from PyQt5.QtCore import Qt

from presenter import *
from view import *
from logic import *
from myWidget import *
from draw import *

form_class = uic.loadUiType("MotionViewer.ui")[0]

class WindowClass(QDialog, form_class):
    def __init__(self):
        super().__init__()
        self.setUi()

        # event handle
        self.startButton.clicked.connect(self.start_click_cb)
        self.fplusButton.pressed.connect(self.fplus_press_cb)
        self.fminusButton.pressed.connect(self.fminus_press_cb)
        self.initButton.clicked.connect(self.init_click_cb)
        self.frameNumEdit.returnPressed.connect(self.frameNum_change_cb)
        self.pointDraw_button.clicked.connect(self.pointDraw_cb)
        self.lineDraw_button.clicked.connect(self.lineDraw_cb)
        self.FK_Checkbox.stateChanged.connect(self.FK_Checkbox_cb)
        self.Limb_IK_Checkbox.stateChanged.connect(self.Limb_IK_Checkbox_cb)
        self.Jacobian_IK_Checkbox.stateChanged.connect(self.Jacobian_IK_Checkbox_cb)
    
    def setUi(self):
        self.setupUi(self)
        self.fplusButton.setAutoRepeat(True)
        self.fminusButton.setAutoRepeat(True)
        self.startButton.setAutoDefault(False)
        self.fplusButton.setAutoDefault(False)
        self.fminusButton.setAutoDefault(False)
        self.initButton.setAutoDefault(False)

        self.setWindowTitle("MotionViewer")
        self.setStyleSheet("background-color: #DFDFDF") 
        self.frame.setStyleSheet("background-color: #83DCB7;")

        self.openGLWidget.setMainWindowView(self)
        self.openGLWidget.addLabel(self.totalFrame)
        self.openGLWidget.addLabel(self.currentFrame)
        self.openGLWidget.addLabel(self.origin)
        self.openGLWidget.addLabel(self.jointLabel)
        self.jointLabel.setStyleSheet("background-color: #f89b00;")
        self.openGLWidget.setSlider(self.timeLine)
        

    def getOpenGL(self):
        return self.openGLWidget

    def setPresenter(self, presenter):
        self.presenter = presenter

    def setOpenGL_Presenter(self, presenter):
        self.openGLWidget.setPresenter(presenter)

    def setRadioButtonPresenter(self, presenter):
        self.RadioButtonPresenter = presenter

    def setCheckBoxPresenter(self, presenter):
        self.CheckBoxPresenter = presenter
    
    def setPushButtonPresenter(self, presenter):
        self.PushButtonPresenter = presenter
    
    def setSliderPresenter(self, presenter):
        self.timeLine.setPresenter(presenter)

    def setLabelPresenter(self, presenter):
        self.totalFrame.setPresenter(presenter)
        self.currentFrame.setPresenter(presenter)
        self.origin.setPresenter(presenter)
        self.jointLabel.setPresenter(presenter)
    
    def setLineEditPresenter(self, presenter):
        self.LineEditPresenter = presenter
    
    def makeScroll(self, jointList_FK, jointList_IK, jointList):
        # Joint scroll area 만들기
        widget = QWidget()
        vbox = QVBoxLayout()
        bufferIndex = 0
        
        for name in jointList_FK:
            
            obj = FK_RadioButton(name, bufferIndex)
            obj.setPresenter(self.RadioButtonPresenter)
            vbox.addWidget(obj)
            bufferIndex += 1
        widget.setLayout(vbox)
        self.jointList.setWidget(widget)

        # End Effector scroll area 만들기
        widget2 = QWidget()
        vbox2 = QVBoxLayout()
        for i in range(len(jointList)):
            name = jointList_IK[i]
            obj = IK_RadioButton(name, jointList[i])
            obj.setPresenter(self.RadioButtonPresenter)
            vbox2.addWidget(obj)
        widget2.setLayout(vbox2)
        self.endEffectorList.setWidget(widget2)

    def FK_Checkbox_cb(self):
        self.CheckBoxPresenter.FK_CheckBoxCB(self.FK_Checkbox.isChecked())
        
    def Limb_IK_Checkbox_cb(self):
        self.CheckBoxPresenter.LimbIK_CheckBoxCB(self.Limb_IK_Checkbox.isChecked())
        
    def Jacobian_IK_Checkbox_cb(self):
        self.CheckBoxPresenter.JacobianIK_CheckBoxCB(self.Jacobian_IK_Checkbox.isChecked())
        
    def keyPressEvent(self, e):
        # Z키는 z축 -, X키는 z축 +
        if e.key() == Qt.Key_A:
            self.presenter.keyPressCB("A")
        elif e.key() == Qt.Key_D:
            self.presenter.keyPressCB("D")
        elif e.key() == Qt.Key_W:
            self.presenter.keyPressCB("W")
        elif e.key() == Qt.Key_S:
            self.presenter.keyPressCB("S")
        elif e.key() == Qt.Key_Z:
            self.presenter.keyPressCB("Z")
        elif e.key() == Qt.Key_X:
            self.presenter.keyPressCB("X")

    def start_click_cb(self):
        self.PushButtonPresenter.startPressCB()

    def fplus_press_cb(self):
        self.PushButtonPresenter.fplusPressCB()
         
    def fminus_press_cb(self):
        self.PushButtonPresenter.fminusPressCB()

    def init_click_cb(self):
        self.PushButtonPresenter.initPressCB()
    
    def frameNum_change_cb(self):
        new_frame = int(self.frameNumEdit.text())
        self.frameNumEdit.setText("")
        self.LineEditPresenter.frameNumCB(new_frame)
    
    def pointDraw_cb(self):
        position = [float(self.point_x.text()), float(self.point_y.text()), float(self.point_z.text())]
        self.PushButtonPresenter.pointDrawCB(position)
    
    def lineDraw_cb(self):
        positions = np.array([[float(self.line_x1.text()), float(self.line_y1.text()), float(self.line_z1.text())], [float(self.line_x2.text()), float(self.line_y2.text()), float(self.line_z2.text())]])
        self.PushButtonPresenter.lineDrawCB(positions)

def main():
    app = QApplication(sys.argv)
    # mainWindow 생성 및 get opengl
    myWindow = WindowClass()
    opengl = myWindow.getOpenGL()

    # data 생성
    opengl_data = OpenGL_Data()
    motion = Motion()

    # draw 생성
    draw = Draw(opengl_data, motion)
    draw.createVertexAndIndexArrayIndexed()

    # presenter(logic class) 생성
    mainWindowPresenter = MainWindowLogic(opengl, opengl_data, motion)
    openglPresenter = OpenGL_Logic(opengl, opengl_data, motion, myWindow, draw)
    radioButtonPresenter = RadioButtonLogic(opengl, opengl_data, motion)
    checkBoxPresenter = CheckBoxLogic(opengl, opengl_data, motion)
    pushButtonPresenter = PushButtonLogic(opengl, opengl_data, motion)
    sliderPresenter = SliderLogic(opengl, opengl_data, motion)
    labelPresenter = LabelLogic(opengl, opengl_data, motion)
    lineEditPresenter = LineEditLogic(opengl, opengl_data, motion)
    
    # presenter 등록
    myWindow.setPresenter(mainWindowPresenter)
    myWindow.setOpenGL_Presenter(openglPresenter)
    myWindow.setRadioButtonPresenter(radioButtonPresenter)
    myWindow.setCheckBoxPresenter(checkBoxPresenter)
    myWindow.setPushButtonPresenter(pushButtonPresenter)
    myWindow.setSliderPresenter(sliderPresenter)
    myWindow.setLabelPresenter(labelPresenter)
    myWindow.setLineEditPresenter(lineEditPresenter)

    
    myWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__" :
    main()