import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
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
        self.timeWarpingButton.clicked.connect(self.timeWarping_cb)
        self.motionWarpingButton.clicked.connect(self.motionWarping_cb)
        self.motion1FindButton.clicked.connect(self.showFile1)
        self.motion2FindButton.clicked.connect(self.showFile2)
        self.motionStitchingButton.clicked.connect(self.motionStitching_cb)
        self.makeParticleButton.clicked.connect(self.makeParticle_cb)


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
        # Label
        self.openGLWidget.addBVHLabel(self.totalFrame)
        self.openGLWidget.addBVHLabel(self.currentFrame)
        self.openGLWidget.addBVHLabel(self.origin)
        self.openGLWidget.addBVHLabel(self.jointLabel)
        self.openGLWidget.addPhysicsLabel(self.timestepLabel)
        self.openGLWidget.addPhysicsLabel(self.ksLabel)
        self.openGLWidget.addPhysicsLabel(self.kdLabel)
        ########
        self.jointLabel.setStyleSheet("background-color: #f89b00;")
        self.openGLWidget.setSlider(self.timeLine)
        
        # self.timer = QtCore.QTimer(self)
        # self.timer.setInterval(10)
        # self.timer.timeout.connect(self.openGLWidget.viewUpdate)

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
        self.timestepLabel.setPresenter(presenter)
        self.ksLabel.setPresenter(presenter)
        self.kdLabel.setPresenter(presenter)
    
    def setLineEditPresenter(self, presenter):
        self.LineEditPresenter = presenter
    
    def makeScroll(self, jointList_FK, jointList_IK, jointList):
        # Joint scroll area ?????????
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

        # End Effector scroll area ?????????
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
        # Z?????? z??? -, X?????? z??? +
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

    def timeWarping_cb(self):
        if self.linearRadioButton.isChecked():
            coeff = float(self.linearCoeff.text())
            print(coeff)
            self.PushButtonPresenter.timeWarpingCB(0, coeff)
        elif self.sinRadioButton.isChecked():
            self.PushButtonPresenter.timeWarpingCB(1, None)
            
    def motionWarping_cb(self):
        if self.linearRadioButton2.isChecked():
            funcType = 0
        elif self.sinRadioButton2.isChecked():
            funcType = 1
        self.PushButtonPresenter.motionWarpingCB(funcType, int(self.startFrame.text()), int(self.endFrame.text()))

    def showFile1(self):
        file_path = QFileDialog.getOpenFileName(self, 'Open File', './', "BVH(*.bvh)")
        file_name = ''.join(file_path[0])
        self.motion1Label.setText(file_name)
    
    def showFile2(self):
        file_path = QFileDialog.getOpenFileName(self, 'Open File', './', "BVH(*.bvh)")
        file_name = ''.join(file_path[0])
        self.motion2Label.setText(file_name)
    
    def motionStitching_cb(self):
        if self.linearRadioButton3.isChecked():
            funcType = 0
        elif self.sinRadioButton3.isChecked():
            funcType = 1
        self.PushButtonPresenter.motionStitchingCB(self.motion1Label.text(),self.motion2Label.text(),funcType,int(self.sliceEdit.text()))

    def makeParticle_cb(self):
        if self.twoDRadioButton.isChecked():
            modelType = 0
        elif self.threeDRadioButton.isChecked():
            modelType = 1
        timestep = None
        ks = None
        kd = None
        if self.timestepEdit.text():
            timestep = float(self.timestepEdit.text())
            self.timestepEdit.setText("")
            # self.timer.setInterval(timestep * 1000)   # period, in millisecond
        if self.ksEdit.text():
            ks = int(self.ksEdit.text())
            self.ksEdit.setText("")
        if self.kdEdit.text():
            kd = int(self.kdEdit.text())
            self.kdEdit.setText("")
        
        if self.timer.isActive():
            self.timer.stop()
        self.timer.start()
             
        self.PushButtonPresenter.makeParticleCB(modelType,timestep,ks,kd)


def main():
    app = QApplication(sys.argv)
    # mainWindow ?????? ??? get opengl
    myWindow = WindowClass()
    opengl = myWindow.getOpenGL()

    # data ??????
    opengl_data = OpenGL_Data()
    motion = Motion()

    # draw ??????
    draw = Draw(opengl_data, motion)
    draw.createVertexAndIndexArrayIndexed()

    # presenter(logic class) ??????
    mainWindowPresenter = MainWindowLogic(opengl, opengl_data, motion)
    openglPresenter = OpenGL_Logic(opengl, opengl_data, motion, myWindow, draw)
    radioButtonPresenter = RadioButtonLogic(opengl, opengl_data, motion)
    checkBoxPresenter = CheckBoxLogic(opengl, opengl_data, motion)
    pushButtonPresenter = PushButtonLogic(opengl, opengl_data, motion, draw, myWindow)
    sliderPresenter = SliderLogic(opengl, opengl_data, motion)
    labelPresenter = LabelLogic(opengl, opengl_data, motion)
    lineEditPresenter = LineEditLogic(opengl, opengl_data, motion)
    
    # presenter ??????
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