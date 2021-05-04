from abc import *

class MainWindowPresenter(metaclass=ABCMeta):
    @abstractmethod
    def keyPressCB(self, key):
        pass
    
class OpenGL_Presenter(metaclass=ABCMeta):
    @abstractmethod
    def IsMotionEmpty(self):
        pass
    @abstractmethod
    def dropCB(self, file_path):
        pass
    @abstractmethod
    def mousePressCB(self, pos, button):
        pass
    @abstractmethod
    def mouseReleaseCB(self, button):
        pass
    @abstractmethod
    def mouseMoveCB(self, pos):
        pass
    @abstractmethod
    def wheelCB(self, yoffset):
        pass    
    @abstractmethod
    def paintCB(self):
        pass
    @abstractmethod
    def IsKeepGoing(self):
        pass

# class RadioPresenter(metaclass=ABCMeta):
#     @abstractmethod
#     def mousePressCB(self):
#         pass

class RadioPresenter(metaclass=ABCMeta):
    @abstractmethod
    def FKPressCB(self, joint_index):
        pass
    @abstractmethod
    def IKPressCB(self, joint):
        pass

class CheckBoxPresenter(metaclass=ABCMeta):
    @abstractmethod
    def FK_CheckBoxCB(self, IsChecked):
        pass
    @abstractmethod
    def LimbIK_CheckBoxCB(self, IsChecked):
        pass
    @abstractmethod
    def JacobianIK_CheckBoxCB(self, IsChecked):
        pass

class PushButtonPresenter(metaclass=ABCMeta):
    @abstractmethod
    def startPressCB(self):
        pass
    @abstractmethod
    def fplusPressCB(self):
        pass
    @abstractmethod
    def fminusPressCB(self):
        pass
    @abstractmethod
    def initPressCB(self):
        pass
    @abstractmethod
    def pointDrawCB(self, position):
        pass
    @abstractmethod
    def lineDrawCB(self, positions):
        pass

class SliderPresenter(metaclass=ABCMeta):
    @abstractmethod
    def getTotalFrames(self):
        pass
    @abstractmethod
    def getCurrentFrame(self):
        pass
    @abstractmethod
    def frameDecision(self, value, bar_len):
        pass

class LabelPresenter(metaclass=ABCMeta):
    @abstractmethod
    def getTotalFrames(self):
        pass
    @abstractmethod
    def getTimeLine(self):
        pass
    @abstractmethod
    def getOriginPos(self):
        pass
    @abstractmethod
    def getJointPos(self):
        pass

class LineEditPresenter(metaclass=ABCMeta):
    @abstractmethod
    def frameNumCB(self, new_frame):
        pass