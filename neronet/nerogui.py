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
	self.init_experiments()
	self.cluster_add_btn.clicked.connect(self.add_cluster)
	self.clusters.itemSelectionChanged.connect(self.update_cluster_fields)
	self.exp_add_btn.clicked.connect(self.add_file)
	self.submit_btn.clicked.connect(self.submit_exp)	

    def init_clusters(self):
	self.clusters.clear()
	for cluster in self.nero.clusters["clusters"]:
		self.clusters.addItem(cluster)

    def init_experiments(self):
	self.experiments.clear()
	for exp_name in self.nero.database.keys():
	    self.experiments.addItem(exp_name)
	
    def add_cluster(self):
	addr = str(self.cluster_address_field.text())
	nm = str(self.cluster_name_field.text())
	port = str(self.cluster_port_field.text())
	self.nero.specify_cluster(nm, addr, "unmanaged", port)
	self.init_clusters()

    def update_cluster_fields(self):
	cluster = str(self.clusters.currentItem().text())
	self.cluster_name_field.setText(cluster)
	self.cluster_address_field.setText(self.nero.clusters["clusters"][cluster]["ssh_address"])
	self.cluster_port_field.setText(self.nero.clusters["clusters"][cluster]["port"])

    def add_file(self):
	file_path = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
	self.nero.specify_experiments(file_path)
	self.init_experiments()

    def submit_exp(self):
	exp = str(self.experiments.currentItem().text())
	cluster = str(self.clusters.currentItem().text())
	self.nero.submit(exp, cluster)


def main():
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
	main()
