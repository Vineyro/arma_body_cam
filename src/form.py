
import usb.core
import usb.util
import domain
import threading
import time
import sys, os

from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, QRunnable, QThreadPool, QMetaObject, Q_ARG
from PyQt5.QtWidgets import *

basedir = os.path.dirname(__file__)

class FormWindow(QWidget):

    def __init__(self, viewModel: domain.MainViewModel):
        super().__init__()

        self.viewModel = viewModel
        self.app_icon = QtGui.QIcon(os.path.join(basedir, 'res', 'favicon.ico'))

        layout = QFormLayout()

        state_id_row = QHBoxLayout()

        state_group = QGroupBox('State')

        state_id_row.addWidget(state_group, 1)

        state_form = QFormLayout()
        state_group.setLayout(state_form)

        self.time_text = QLineEdit()
        self.time_text.setMinimumHeight(32)
        self.time_text.setReadOnly(True)

        self.video_resolution_text = QLineEdit()
        self.video_resolution_text.setMinimumHeight(32)
        self.video_resolution_text.setReadOnly(True)

        self.battery_text = QLineEdit()
        self.battery_text.setMinimumHeight(32)
        self.battery_text.setReadOnly(True)
        

        row = QHBoxLayout()

        self.sync_time_button = QPushButton('Sync time')
        self.sync_time_button.setMinimumHeight(32)
        self.sync_time_button.clicked.connect(self.sync_time)

        row.addWidget(self.sync_time_button)
        
        self.read_data_button = QPushButton('Read data')
        self.read_data_button.setMinimumHeight(32)

        row.addWidget(self.read_data_button)

        state_form.addRow('Time', self.time_text)
        state_form.addRow('Video resolution', self.video_resolution_text)
        state_form.addRow('Battery', self.battery_text)
        state_form.addRow('', row)

        id_group = QGroupBox('ID')
        id_row = QHBoxLayout()
        id_group.setLayout(id_row)
        state_id_row.addWidget(id_group, 2)

        serial_id_form = QFormLayout()
        id_row.addLayout(serial_id_form)

        self.camera_serial_text = QLineEdit()
        self.camera_serial_text.setMinimumHeight(32)
        self.camera_serial_text.setMaxLength(7)

        self.serial_text = QLineEdit()
        self.serial_text.setMinimumHeight(32)

        self.dep_id_text = QLineEdit()
        self.dep_id_text.setMinimumHeight(32)
        self.dep_id_text.setMaxLength(12)

        self.dep_name_text = QLineEdit()
        self.dep_name_text.setMinimumHeight(32)
        self.dep_name_text.setMaxLength(16)

        serial_id_form.addRow('Camera S/N', self.camera_serial_text)
        serial_id_form.addRow('Serial No', self.serial_text)
        serial_id_form.addRow('Deparatament ID', self.dep_id_text)
        serial_id_form.addRow('Deparatament Name', self.dep_name_text)

        user_id_form = QFormLayout()
        id_row.addLayout(user_id_form)

        self.user_id_text = QLineEdit()
        self.user_id_text.setMinimumHeight(32)
        self.user_id_text.setMaxLength(6)

        self.user_name_text = QLineEdit()
        self.user_name_text.setMinimumHeight(32)
        self.user_name_text.setMaxLength(16)

        self.read_user_button = QPushButton('Read')
        self.read_user_button.setMinimumHeight(32)
        self.read_user_button.clicked.connect(self.read_id)

        self.save_user_button = QPushButton('Save')
        self.save_user_button.setMinimumHeight(32)
        self.save_user_button.clicked.connect(self.set_id)

        user_id_form.addRow('User ID', self.user_id_text)
        user_id_form.addRow('User Name', self.user_name_text)
        user_id_form.addWidget(self.read_user_button)
        user_id_form.addWidget(self.save_user_button)
        
        network_row = QHBoxLayout()

        wifi_group = QGroupBox('WiFi')
        wifi_form = QFormLayout()
        wifi_group.setLayout(wifi_form)
        network_row.addWidget(wifi_group, 1)

        self.wifi_mode = QComboBox()
        self.wifi_mode.addItems([' AP', ' STA'])
        self.wifi_mode.setMinimumHeight(32)
        self.wifi_mode.currentIndexChanged.connect(self.set_wifi_mode)

        self.wifi_ssid_text = QLineEdit()
        self.wifi_ssid_text.setMinimumHeight(32)

        self.wifi_password_text = QLineEdit()
        self.wifi_password_text.setMinimumHeight(32)

        self.save_wifi_button = QPushButton('Save')
        self.save_wifi_button.setMinimumHeight(32)
        self.save_wifi_button.clicked.connect(self.save_wifi_settings)

        self.read_wifi_button = QPushButton('Read')
        self.read_wifi_button.setMinimumHeight(32)
        self.read_wifi_button.clicked.connect(self.read_wifi_state)

        wifi_form.addRow('Mode', self.wifi_mode)
        wifi_form.addRow('SSID', self.wifi_ssid_text)
        wifi_form.addRow('Password', self.wifi_password_text)

        row = QHBoxLayout()
        row.addWidget(self.read_wifi_button)
        row.addWidget(self.save_wifi_button)
        wifi_form.addRow('', row)

        server_group = QGroupBox('Server')
        server_form = QFormLayout()
        server_group.setLayout(server_form)

        self.server_ip_text = QLineEdit()
        self.server_ip_text.setMinimumHeight(32)
        self.server_ip_text.setMaxLength(20)

        self.server_port_text = QLineEdit()
        self.server_port_text.setMinimumHeight(32)
        self.server_port_text.setMaxLength(10)
        
        self.save_server_button = QPushButton('Save')
        self.save_server_button.setMinimumHeight(32)
        self.save_server_button.clicked.connect(self.set_server)

        self.read_server_button = QPushButton('Read')
        self.read_server_button.setMinimumHeight(32)
        self.read_server_button.clicked.connect(self.read_server)

        server_form.addRow('IP address', self.server_ip_text)
        server_form.addRow('Port', self.server_port_text)
        server_form.addItem(QSpacerItem(0, 32))

        row = QHBoxLayout()
        row.addWidget(self.read_server_button)
        row.addWidget(self.save_server_button)
        server_form.addRow('', row)

        sim_group = QGroupBox('SIM')
        sim_form = QFormLayout()
        sim_group.setLayout(sim_form)
        
        self.sim_apn_text = QLineEdit()
        self.sim_apn_text.setMinimumHeight(32)
        self.sim_apn_text.setMaxLength(31)

        self.sim_pin_text = QLineEdit()
        self.sim_pin_text.setMinimumHeight(32)
        self.sim_pin_text.setMaxLength(8)
       
        self.save_sim_button = QPushButton('Save')
        self.save_sim_button.setMinimumHeight(32)
        self.save_sim_button.clicked.connect(self.set_sim)

        self.read_sim_button = QPushButton('Read')
        self.read_sim_button.setMinimumHeight(32)
        self.read_sim_button.clicked.connect(self.read_sim)

        sim_form.addRow('APN', self.sim_apn_text)
        sim_form.addRow('PIN', self.sim_pin_text)
        sim_form.addItem(QSpacerItem(0, 32))

        row = QHBoxLayout()
        row.addWidget(self.read_sim_button)
        row.addWidget(self.save_sim_button)
        sim_form.addRow('', row)

        admin_password_group = QGroupBox('Admin password')
        admin_password_layout = QFormLayout()
        admin_password_group.setLayout(admin_password_layout)

        self.admin_password_text = QLineEdit()
        self.admin_password_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.admin_password_text.setMinimumHeight(32)
        self.admin_password_text.setMaxLength(6)

        self.admin_repeat_password_text = QLineEdit()
        self.admin_repeat_password_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.admin_repeat_password_text.setMinimumHeight(32)
        self.admin_repeat_password_text.setMaxLength(6)
                
        self.save_admin_password_button = QPushButton('Save')
        self.save_admin_password_button.setMinimumHeight(32)
        self.save_admin_password_button.clicked.connect(self.set_admin_password)

        admin_password_layout.addRow('New password', self.admin_password_text)
        admin_password_layout.addRow('Repeat password', self.admin_repeat_password_text)
        admin_password_layout.addWidget( self.save_admin_password_button)

        user_password_group = QGroupBox("User password")
        user_password_layout = QFormLayout()
        user_password_group.setLayout(user_password_layout)

        self.user_password_text = QLineEdit()
        self.user_password_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.user_password_text.setMinimumHeight(32)
        self.user_password_text.setMaxLength(6)

        self.user_repeat_password_text = QLineEdit()
        self.user_repeat_password_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.user_repeat_password_text.setMinimumHeight(32)
        self.user_repeat_password_text.setMaxLength(6)
                
        self.save_user_password_button = QPushButton('Save')
        self.save_user_password_button.setMinimumHeight(32)
        self.save_user_password_button.clicked.connect(self.set_user_password)

        user_password_layout.addRow('New password', self.user_password_text)
        user_password_layout.addRow('Repeat password', self.user_repeat_password_text)
        user_password_layout.addWidget(self.save_user_password_button)

        layout.addRow(state_id_row)

        network_row.addWidget(sim_group, 1)
        network_row.addWidget(server_group, 1)

        layout.addRow(network_row)

        password_row = QHBoxLayout()
        password_row.addWidget(admin_password_group)
        password_row.addWidget(user_password_group)
        
        layout.addRow(password_row)

        self.switch_mode_button = QPushButton('Switch to storage mode')
        self.switch_mode_button.setMinimumHeight(32)
        self.switch_mode_button.clicked.connect(self.switch_to_storage_mode)

        self.format_tf_button = QPushButton('Format TF Card')
        self.format_tf_button.setMinimumHeight(32)

        self.logout_button = QPushButton('Sign out')
        self.logout_button.setMinimumHeight(32)

        controls_row = QHBoxLayout()
        controls_row.addWidget(self.switch_mode_button)
        controls_row.addWidget(self.format_tf_button)
        controls_row.addWidget(self.logout_button)

        layout.addRow(controls_row)

        container = QWidget()
        container.setLayout(layout)

        self.read_wifi_state()
        self.read_sim()
        self.read_id()
        self.read_server()
        self.read_resolution()
        self.read_battery()
        self.sync_time()

        self.setLayout(layout)

    def sync_time(self):
        time = self.viewModel.sync_time()
        self.time_text.setText(str(time))
        return time

    def read_battery(self):
        battery = self.viewModel.read_battery()
        self.battery_text.setText('%i%%'%(self.viewModel.read_battery()))
        return battery

    def read_wifi_state(self):
        self.read_mode()
        self.read_sta_ssid()
        self.read_sta_password()

    def read_mode(self):
        result = self.viewModel.read_wifi_mode()
        self.wifi_mode.setCurrentIndex(result)
        return result

    def read_sta_ssid(self):
        result = self.viewModel.read_wifi_ssid()
        self.wifi_ssid_text.setText(result)
        return result
    
    def read_sta_password(self):
        result = self.viewModel.read_wifi_password()
        self.wifi_password_text.setText(result)
        return result
    
    def read_ip(self):
        result = self.viewModel.read_server_ip()
        self.server_ip_text.setText(result)
        return result
    
    def read_port(self):
        result = self.viewModel.read_server_port()
        self.server_port_text.setText(result)
        return result
    
    def read_apn(self):
        result = self.viewModel.read_apn()
        self.sim_apn_text.setText(result)
        return result

    def read_pin(self):
        result = self.viewModel.read_sim_pin()
        self.sim_pin_text.setText(result)
        return result
    
    def read_resolution(self):
        result = self.viewModel.read_video_resolution()
        self.video_resolution_text.setText(result)
        return result
    
    def read_id(self):

        result = self.viewModel.read_cam_id()

        self.camera_serial_text.setText(result[0])
        self.user_id_text.setText(result[1])
        self.user_name_text.setText(result[2])
        self.dep_id_text.setText(result[3])
        self.dep_name_text.setText(result[4])

        return result
    
    def set_id(self):
        self.viewModel.write_cam_id(
            self.camera_serial_text.text(),
            self.user_id_text.text(),
            self.user_name_text.text(),
            self.dep_id_text.text(),
            self.dep_name_text.text()
        )
        self.show_sucess("ID updated")
    
    def switch_to_storage_mode(self):
        if self.viewModel.switch_to_storage_mode() != None:
            self.show_sucess("Switched to storage mode")
            self.logout_button.click()
        else:
            self.show_sucess("Failed")

    def set_admin_password(self):
        if self.admin_password_text.text() != self.admin_repeat_password_text.text():
            self.show_error("Passwords must match")
        elif len(self.admin_password_text.text()) != 6:
            self.show_error("Password length must be 6")
        else:
            self.viewModel.set_admin_password(self.admin_password_text.text())
            self.show_sucess("Admin password updated")

    def set_user_password(self):
        if self.user_password_text.text() != self.user_repeat_password_text.text():
            self.show_error("Passwords must match")
        elif len(self.user_password_text.text()) != 6:
            self.show_error("Password length must be 6")
        else:
            self.viewModel.set_user_password(self.user_password_text.text())
            self.show_sucess("User password updated")

    def set_server(self):
        self.viewModel.write_server_ip(self.server_ip_text.text())
        self.viewModel.write_server_port(self.server_port_text.text())
        self.show_sucess("Server updated")

    def read_server(self):
        self.read_ip()
        self.read_port()
        
    def read_sim(self):
        self.read_apn()
        self.read_pin()

    def set_sim(self):
        self.viewModel.write_sim_apn(self.sim_apn_text.text())
        self.viewModel.write_sim_pin(self.sim_pin_text.text())
        self.show_sucess("SIM updated")

    def save_wifi_settings(self):
        self.viewModel.write_wifi_mode(self.wifi_mode.currentIndex())
        time.sleep(0.1)
        self.viewModel.write_wifi_ssid(self.wifi_ssid_text.text())
        self.viewModel.write_wifi_password(self.wifi_password_text.text())
        self.show_sucess("WIFI updated")

    def set_wifi_mode(self):
        self.viewModel.write_wifi_mode(self.wifi_mode.currentIndex())
        time.sleep(0.1)
        self.read_sta_ssid()
        self.read_sta_password()  

    def show_error(self, error):
        msg = QMessageBox()
        msg.setWindowIcon(self.app_icon)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(error)
        msg.setWindowTitle("Error")
        msg.exec()

    def show_sucess(self, error):
        msg = QMessageBox()
        msg.setWindowIcon(self.app_icon)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(error)
        msg.setWindowTitle("Succcess")
        msg.exec()