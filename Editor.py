import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QMenuBar, QMenu, QFileDialog
from PyQt6.QtGui import QAction


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和初始大小
        self.setWindowTitle('PyQt6 Text Editor')
        self.setGeometry(100, 100, 800, 600)

        # 创建文本编辑器控件
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        # 创建菜单栏和文件菜单
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QMenu('File', self)
        self.menu_bar.addMenu(file_menu)

        # 创建动作并添加到文件菜单
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '', "Text Files (*.txt *.py)")
        if file_name:
            with open(file_name, 'r') as file:
                self.text_edit.setPlainText(file.read())

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', "Text Files (*.txt *.py)")
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_edit.toPlainText())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())
