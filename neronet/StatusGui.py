import sys
from PyQt4 import QtGui
import design
import neronet.neroman
import os.path

class ExampleApp(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        default = os.path.expanduser("~/.neronet/default.yaml")
        pref = os.path.expanduser("~/.neronet/preferences.yaml")
        clust = os.path.expanduser("~/.neronet/clusters.yaml")
        self.nero = neronet.neroman.Neroman()
	self.init_clusters()
 
    def init_clusters(self):
	print self.nero.clusters


def main():
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
	main()
