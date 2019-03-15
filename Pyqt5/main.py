import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from dest.mainWindow import *
from dest.childWindow import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #實例化主窗口 
    main = QMainWindow()
    main_ui = Ui_MainWindow()
    main_ui.setupUi(main)
    #實例化子窗口 
    child = QDialog()
    child_ui = Ui_Dialog()
    child_ui.setupUi(child)
    
    #按鈕綁定事件
    btn = main_ui.pushButton
    btn.clicked.connect( child.show )

    #顯示
    main.show()
    sys.exit(app.exec_())
