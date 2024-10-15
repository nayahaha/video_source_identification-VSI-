import os
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QLabel

from tool import main

class AnalysisThread(QtCore.QThread):
    progressUpdated = pyqtSignal(int)
    tableUpdated = pyqtSignal(list)
    def __init__(self, folder_path):
        super(AnalysisThread, self).__init__()
        self.folder_path = folder_path

    def run(self):
        total_files = 0
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith(('.mov', '.mp4')):
                    total_files += 1

        count = 0
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith(('.mov', '.mp4')):
                    count += 1
                    self.progressUpdated.emit(int(count / total_files * 100))
                    full_path = os.path.join(root, file).replace('/', os.sep)
                    try:
                        result_class, percent = main(full_path)
                        percent = str(float(percent) * float(100)) + '%'
                    except Exception as e:
                        print(str(e))
                        continue

                    app_name = result_class.lower()
                    emit_data = list()
                    emit_data.append(full_path)
                    emit_data.append(app_name)
                    emit_data.append(percent)

                    self.tableUpdated.emit(emit_data)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(f'{BASE_DIR+os.sep}ui{os.sep}main.ui', self)


        self.selectButton = self.findChild(QtWidgets.QPushButton, 'pushButton_select')
        self.analyzeButton = self.findChild(QtWidgets.QPushButton, 'pushButton_analyze')
        self.folderLineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.progressBar = self.findChild(QtWidgets.QProgressBar, 'progressBar')
        self.progressBar.setValue(0)
        self.resultsTable = self.findChild(QtWidgets.QTableWidget, 'tableWidget')
        self.resultsTable.setColumnCount(4)
        self.resultsTable.setHorizontalHeaderLabels(['Filename', 'Application', 'Icon', 'Probability'])

        self.resultsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.resultsTable.setColumnWidth(1, 100)
        self.resultsTable.setColumnWidth(2, 30)
        self.resultsTable.setColumnWidth(4, 20)

        self.resultsTable.verticalHeader().setDefaultSectionSize(30)

        self.selectButton.clicked.connect(self.select)
        self.analyzeButton.clicked.connect(self.analyze_folder)

    def select(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            self.folderLineEdit.setText(folder_path)

    def analyze_folder(self):
        folder_path = self.folderLineEdit.text()
        self.progressBar.setValue(0)

        self.thread = AnalysisThread(folder_path)
        self.thread.progressUpdated.connect(self.update_progress)
        self.thread.tableUpdated.connect(self.add_table_row)
        self.thread.start()

    def update_progress(self, value):
        self.progressBar.setValue(value)

    def add_table_row(self, emit_data):
        filename = emit_data[0]
        text = emit_data[1]
        probability = emit_data[2]

        row_position = self.resultsTable.rowCount()
        self.resultsTable.insertRow(row_position)

        filename_item = QTableWidgetItem(filename)
        filename_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.resultsTable.setItem(row_position, 0, filename_item)

        text_item = QTableWidgetItem(text)
        text_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.resultsTable.setItem(row_position, 1, text_item)

        label = QLabel()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        pixmap = QPixmap(f'{BASE_DIR + os.sep}icon{os.sep+text}.png'.format(text))
        label.setPixmap(pixmap.scaled(30, 30, QtCore.Qt.KeepAspectRatio))
        self.resultsTable.setCellWidget(row_position, 2, label)

        percent_item = QTableWidgetItem(probability)
        percent_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.resultsTable.setItem(row_position, 3, percent_item)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())