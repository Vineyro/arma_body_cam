import usb.core
import usb.util
import domain
import form
import threading
import time
import sys, os

from PyQt6 import QtGui
from PyQt6.QtCore import QSize, Qt, QRunnable, QThreadPool, QMetaObject, Q_ARG
from PyQt6.QtWidgets import *

basedir = os.path.dirname(__file__)
viewModel = domain.MainViewModel()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.app_icon = QtGui.QIcon(os.path.join(basedir, 'res', 'favicon.ico'))

        self.setWindowIcon(self.app_icon)

        self.setFixedSize(QSize(860, 580))
        self.setWindowTitle("АРМАФОН S3.5")

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.login_widget = LoginWindow()
        self.login_widget.login_button.clicked.connect(self.login_click)
        self.central_widget.addWidget(self.login_widget)

    def login(self, password, user_type):
        result = viewModel.login(password, user_type)
        return result

    def login_click(self):

        user_type = 0

        if self.login_widget.login_type.currentIndex() == 0:
            user_type = 0x10
        else:
            user_type = 0x11

        if self.login(self.login_widget.password_text.text(), user_type):
            self.logged_in_widget = form.FormWindow(viewModel)
            self.logged_in_widget.logout_button.clicked.connect(self.logout_click)
            self.central_widget.addWidget(self.logged_in_widget)
            self.central_widget.setCurrentWidget(self.logged_in_widget)
        else:
            msg = QMessageBox()
            msg.setWindowIcon(self.app_icon)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Wrong password")
            msg.setWindowTitle("Sign in failed")
            msg.exec()

    def logout_click(self):
        self.central_widget.removeWidget(self.logged_in_widget)
        self.central_widget.setCurrentWidget(self.login_widget)

class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)

def run_device_serching(window):

    while True:
        time.sleep(2)
        try:
            window.update_devices()
        except:
            break

class LoginWindow(QWidget):

    logined = None

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        self.login_form = QFormLayout()

        self.device = QComboBox()
        self.device.setMinimumHeight(32)
        self.device.currentIndexChanged.connect(self.device_selected)
        
        self.login_form.addRow('Device', self.device)
        self.login_form.addItem(QSpacerItem(0, 32))

        self.login_type = QComboBox()
        self.login_type.setMinimumHeight(32)
        self.login_type.addItems([" Administrator", " User"])

        self.login_form.addRow('User type', self.login_type)

        self.password_text = QLineEdit()
        self.password_text.setMinimumHeight(32)
        self.password_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_text.setMaxLength(6)

        self.login_form.addRow('Password', self.password_text)
        
        self.login_button = QPushButton("Sign in")
        self.login_button.setMinimumHeight(32)

        self.login_form.addWidget(self.login_button)

        self.connect_button = QPushButton("Connect")
        self.connect_button.setMinimumHeight(32)
        self.connect_button.clicked.connect(self.try_device_conect)

        layout.addStretch()
        layout.addLayout(self.login_form)
        
        layout.addSpacerItem(QSpacerItem(0, 32))

        row = QHBoxLayout()

        layout.addStretch()

        row.addWidget(QWidget(), 1)
        row.addLayout(layout, 1)
        row.addWidget(QWidget(), 1)

        self.update_devices()

        self.p = ProcessRunnable(target=run_device_serching, args=(self))
        self.p.start()

        self.setLayout(row)

    def device_selected(self):
        viewModel.set_device(self.device.itemData(self.device.currentIndex()))

    def update_devices(self):
        
        current_device = self.device.itemData(self.device.currentIndex())
        self.device.clear()

        devices = viewModel.get_devices()

        for idx, device in enumerate(devices):

            self.device.addItem(f" {device.address:03d}", device)

            if current_device != None and device.address == current_device.address:
                self.device.setCurrentIndex(idx)

    def try_device_conect(self):
        return viewModel.ping_device
    

app = QApplication([])

main_widget = MainWindow()
main_widget.show()

app.exec()