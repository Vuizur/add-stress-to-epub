import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt6 import QtCore
from PyQt6 import QtGui
from MainWindow import Ui_MainWindow
from edit_epub import convert_book
import os
import pathlib

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.environ["PYMORPHY2_DICT_PATH"] = str(pathlib.Path(sys._MEIPASS).joinpath('pymorphy2_dicts_ru/data'))

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which
    from shutil import which

    return which(name) is not None

class StressThread(QtCore.QThread):

    book_stressed = QtCore.pyqtSignal(object)

    def __init__(self, parent, input_path, output_path):
        QtCore.QThread.__init__(self, parent)
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        convert_book(self.input_path, self.output_path)
        self.book_stressed.emit("Stressing successful")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Stress Adder Tool")
        self.selectInputButton.clicked.connect(self.open)
        self.openOutputFolderButton.clicked.connect(self.openOutputFolder)
        self.stressMarkButton.clicked.connect(self.startStressMarking)

    def open(self):
        fileName = QFileDialog.getOpenFileName(self, 'OpenFile')
        print(fileName)
        self.lineEditInput.setText(fileName[0])
        if fileName[0] == "":
            return
        input_path_split = fileName[0].rsplit(".", 1)
        
        if input_path_split[1].lower() != "epub":
            if not is_tool("ebook-convert"):
                msgBox = QMessageBox()
                msgBox.setTextFormat(QtCore.Qt.TextFormat.RichText); 
                msgBox.setText("You want to add stress marks to a non-epub book. Please install Calibre from <a href='https://calibre-ebook.com/download'>https://calibre-ebook.com/download</a> first!")
                msgBox.exec()
        output_path = input_path_split[0] + "_stressed.epub"
        self.lineEditOutput.setText(output_path)

    def openOutputFolder(self):
        folder = self.lineEditInput.text().rsplit("/", 1)[0]
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(folder))

    def startStressMarking(self):
        self.stressMarkButton.setText("Stressing the book, please wait...")
        self.stressMarkButton.setEnabled(False)
        #convertBookThread = Thread(None, convert_book, args=(self.lineEditInput.text(), self.lineEditOutput.text()))
        stressThread = StressThread(self, self.lineEditInput.text(), self.lineEditOutput.text())
        stressThread.book_stressed.connect(self.stressMarkingFinished)
        stressThread.start()
        
        #self.lineEditOutput.setText(fileName[0].rfin)
    def stressMarkingFinished(self):
        self.stressMarkButton.setText("Start stress marking")
        self.stressMarkButton.setEnabled(True)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()