import sys
from PyQt4 import QtGui
import design
import neroman

class ExampleApp(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        tmp = neroman()
        #self.test.clicked.connect(self.showHello)

    #def showHello(self, event):
    	#self.test2.setPlainText("Hello World!")  


def main():
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
	main()
