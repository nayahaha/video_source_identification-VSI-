import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QLabel, QTableWidget

from tool import main

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('.\\ui\\main.ui', self)

        # for Debugging
        DEBUG = False

        # UI 요소 연결
        self.selectButton = self.findChild(QtWidgets.QPushButton, 'pushButton_select')
        self.analyzeButton = self.findChild(QtWidgets.QPushButton, 'pushButton_analyze')
        self.folderLineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.resultsTable = self.findChild(QtWidgets.QTableWidget, 'tableWidget')
        self.resultsTable.setColumnCount(3)
        self.resultsTable.setHorizontalHeaderLabels(['Filename', 'Application', 'Icon'])

        # 컬럼 비율 설정 (5:1:1)
        self.resultsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.resultsTable.setColumnWidth(1, 100)
        self.resultsTable.setColumnWidth(2, 30)

        # 행 높이 설정
        self.resultsTable.verticalHeader().setDefaultSectionSize(30)

        # self.setFixedSize(500, 700)  # 원하는 고정 크기로 설정
        if DEBUG == True:
            self.folderLineEdit.setText("F:\\dataset")

        # 버튼 클릭 시 함수 연결
        self.selectButton.clicked.connect(self.select)
        self.analyzeButton.clicked.connect(self.analyze_folder)

    def select(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            self.folderLineEdit.setText(folder_path)

    def analyze_folder(self):
        folder_path = self.folderLineEdit.text()

        result_list = list()
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)

                if file.lower().endswith(('.mov', '.mp4')):
                    result_list.append((full_path, main(full_path)))


        # 예시로 텍스트 파일과 이미지 파일을 표시하는 코드입니다

        self.resultsTable.setRowCount(0)  # 기존 테이블 초기화

        for result in result_list:
            file_name = result[0]
            app_name = result[1]
            self.add_table_row(file_name, app_name.lower())


    def add_table_row(self, filename, text):
        row_position = self.resultsTable.rowCount()
        self.resultsTable.insertRow(row_position)

        filename_item = QTableWidgetItem(filename)
        filename_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.resultsTable.setItem(row_position, 0, filename_item)


        text_item = QTableWidgetItem(text)
        text_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.resultsTable.setItem(row_position, 1, text_item)


        label = QLabel()
        pixmap = QPixmap('.\\icon\\{}.png'.format(text))
        label.setPixmap(pixmap.scaled(30, 30, QtCore.Qt.KeepAspectRatio))
        self.resultsTable.setCellWidget(row_position, 2, label)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())