from abc import *
from PyQt5 import uic

from presenter import *

# form_class = uic.loadUiType("MotionViewer.ui")[0]
class MainWindowView:
    # def __init__(self):
    #     super(MainWindowView, self).__init__()
        # self.setupUi(self)
    def setPresenter(self, presenter):
        self.presenter = presenter
    @abstractmethod
    def makeScroll(self):
        pass

class OpenGL_View:
    # def __init__(self, parent=None):
    #     super(OpenGL_View, self).__init__(parent)
    def setPresenter(self, presenter):
        self.presenter = presenter
    @abstractmethod
    def viewUpdate(self):
        pass

class RadioButtonView:
    # def __init__(self, name, parent=None):
    #     super(RadioButtonView, self).__init__(name, parent)
    def setPresenter(self, presenter):
        self.presenter = presenter

class SliderView:
    # def __init__(self, parent=None):
    #     super(SliderView, self).__init__(parent)
    def setPresenter(self, presenter):
        self.presenter = presenter
    @abstractmethod
    def viewUpdate(self):
        pass

class LabelView:
    # def __init__(self, parent=None):
    #     super(LabelView, self).__init__(parent)
    def setPresenter(self, presenter):
        self.presenter = presenter
    @abstractmethod
    def viewUpdate(self):
        pass
