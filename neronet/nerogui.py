import sys
import webbrowser
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QApplication, QTableWidget, QTableWidgetItem
import design
import neronet.neroman
import os.path

class MyTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        if ( isinstance(other, QTableWidgetItem) ):
            my_value, my_ok = self.data(Qt.EditRole).toInt()
            other_value, other_ok = other.data(Qt.EditRole).toInt()

            if ( my_ok and other_ok ):
                return my_value < other_value

        return super(MyTableWidgetItem, self).__lt__(other)


class Nerogui(QtGui.QMainWindow, design.Ui_MainWindow):

    def __init__(self, parent=None):
        super(Nerogui, self).__init__(parent)
        self.setupUi(self)
        self.nero = neronet.neroman.Neroman()
        self.init_clusters()
        self.add_to_param_table()
        # bind signals and slots
        self.cluster_add_btn.clicked.connect(self.add_cluster)
        self.clusters.itemSelectionChanged.connect(self.update_cluster_fields)
        self.paramTable.itemSelectionChanged.connect(self.show_one_experiment)
        self.paramTable.verticalHeader().sectionDoubleClicked.connect(self.open_config)
        self.paramTable.doubleClicked.connect(self.open_config)
        self.exp_add_btn.clicked.connect(self.add_file)
        self.submit_btn.clicked.connect(self.submit_exp)
        self.refresh_btn.clicked.connect(self.fetch_exp)

    def init_clusters(self):
        """add each cluster to view"""
        self.clusters.clear()
        for cluster in self.nero.clusters["clusters"]:
            self.clusters.addItem(cluster)

    def add_cluster(self):
        """add cluster to neroman configs"""
        addr = str(self.cluster_address_field.text())
        nm = str(self.cluster_name_field.text())
        type = str(self.cluster_type_combo.currentText())
        self.nero.specify_cluster(nm, type, addr)
        self.init_clusters()

    def update_cluster_fields(self):
        """add clusters view"""
        cluster = str(self.clusters.currentItem().text())
        self.cluster_name_field.setText(cluster)
        self.cluster_address_field.setText(
            self.nero.clusters["clusters"][cluster].ssh_address)

    def add_file(self):
        """add folder to neroman database"""
        file_path = str(
            QtGui.QFileDialog.getExistingDirectory(
                self,
                "Select Directory"))
        self.nero.specify_experiments(file_path)
	self.add_to_param_table()

    def submit_exp(self):
        """submit button functionality"""
        cluster = str(self.clusters.currentItem().text())
        if cluster is None:
            return
        for exp in self.paramTable.selectionModel().selectedRows():
            name = str(self.paramTable.item(exp.row(), 0).text())
            self.nero.submit(name, cluster)

    def add_to_param_table(self):
        """inserts values from database to comparison table"""
        labels = set()
        names = []
        self.paramTable.setRowCount(0)
        self.paramTable.setColumnCount(0)
        for exp in self.nero.database.keys():
            labels |= set(
                self.nero.database[exp]._fields["parameters"].keys())
            names.append(exp)
        self.paramTable.setRowCount(len(names))
        self.paramTable.setColumnCount(len(labels)+1)
        self.paramTable.setHorizontalHeaderLabels(tuple(["Name",] + list(labels)))
        self.paramTable.setColumnWidth(0,200)
        #self.paramTable.setVerticalHeaderLabels(names)

        for idx1, name in enumerate(names):
            self.paramTable.setItem(
                idx1,
                0,
                MyTableWidgetItem(
                    QtCore.QString("%1").arg(name)))
            for idx2, param in enumerate(labels):
                try:
                    value = self.nero.database[
                        name]._fields["parameters"][param]
                    try:
                        value = int(value)
                    except:
                        pass
                    self.paramTable.setItem(
                        idx1,
                        idx2+1,
                        MyTableWidgetItem(
                            QtCore.QString("%1").arg(value)))
                except KeyError:
                    pass

    def show_one_experiment(self):
        """prints detailed info of one experiment"""
        self.experiment_log.clear()
        row = self.paramTable.currentRow()
	name = str(self.paramTable.item(row, 0).text())
        for line in self.nero.status_gen(name):
            self.experiment_log.insertPlainText(line)

    def open_config(self):
        """double clicking opens config file"""
        print "?"
        row = self.paramTable.currentRow()
	name = str(self.paramTable.item(row, 0).text())
        path = self.nero.database[name]._fields["path"]
        webbrowser.open(path + "/config.yaml")

    def fetch_exp(self):
        """fetches experiments statuses"""
        self.nero.fetch()


def main():
    app = QtGui.QApplication(sys.argv)
    form = Nerogui()
    form.show()
    app.exec_()
