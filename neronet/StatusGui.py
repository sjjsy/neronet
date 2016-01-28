import sys
from PyQt4 import QtGui
import design
import neronet.neroman
import os.path

class ExampleApp(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        self.nero = neronet.neroman.Neroman()
	self.init_clusters()
	self.cluster_add_btn.clicked.connect(self.add_cluster)
	self.clusters.itemSelectionChanged.connect(self.update_cluster_fields)
 
    def init_clusters(self):
	self.clusters.clear()
	for cluster in self.nero.clusters["clusters"]:
		self.clusters.addItem(cluster)
	
    def add_cluster(self):
	addr = self.cluster_address_field.text()
	nm = self.cluster_name_field.text()
	port = self.cluster_port_field.text()
	#type = 
	self.nero.specify_cluster(addr, nm, "unmanaged", port)
	self.init_clusters()

    def update_cluster_fields(self):
	cluster = self.clusters.currentItem().text()
	print self.nero.clusters
	self.cluster_name_field.setText(cluster)
	self.cluster_address_field.setText(self.nero.clusters["clusters"][cluster]["ssh_address"])
	self.cluster_port_field.setText(self.nero.clusters["clusters"][cluster]["port"])


def main():
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
	main()
