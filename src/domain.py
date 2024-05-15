from __future__ import annotations
import usb.core
import usb.util

from datetime import datetime
from enum import Enum

resolution_dict = {
    0: "2304x1296 30fps",
    1: "1920x1080 30fps",
    3: "1280x720 60fps",
    4: "1280x720 30fps"
}

class CommandData():

    command_text: list[int]
    data_len: int

    def __init__(self, command_text, data_len):
        self.command_text = command_text
        self.data_len = data_len

class Command(Enum):

    READ_BATTERY = CommandData([0xe1, 0x00, 0x70], 1)
    SYNC_TIME = CommandData([0xe1, 0x00, 0x41], 7)
    READ_VIDEO_RESOLUTION = CommandData([0xe1, 0x00, 0x60], 1)

    SWITCH_TO_STORAGE_MODE = CommandData([0xe1, 0x00, 0x51], 0)
    DEVICE_PING = CommandData([0xe1, 0x00, 0x20], 5)

    READ_WIFI_MODE = CommandData([0xe2, 0x00, 0x11], 1)
    WRITE_WIFI_MODE = CommandData([0xe2, 0x00, 0x10], 1)

    READ_WIFI_SSID = CommandData([0xe2, 0x00, 0x21], 32)
    WRITE_WIFI_SSID = CommandData([0xe2, 0x00, 0x20], 32)

    READ_WIFI_PASSWORD = CommandData([0xe2, 0x00, 0x31], 32)
    WRITE_WIFI_PASSWORD = CommandData([0xe2, 0x00, 0x30], 32)

    READ_CAM_ID = CommandData([0xe1, 0x00, 0x30], 100)
    WRITE_CAM_ID = CommandData([0xe1, 0x00, 0x31], 100)

    READ_SIM_APN = CommandData([0xe2, 0x00, 0x41], 32)
    WRITE_SIM_APN = CommandData([0xe2, 0x00, 0x40], 32)

    READ_SIM_PIN = CommandData([0xe2, 0x00, 0x51], 8)
    WRITE_SIM_PIN = CommandData([0xe2, 0x00, 0x50], 8)

    READ_SERVER_IP = CommandData([0xe2, 0x00, 0x61], 30)
    WRITE_SERVER_IP = CommandData([0xe2, 0x00, 0x60], 30)

    READ_SERVER_PORT = CommandData([0xe2, 0x00, 0x71], 10)
    WRITE_SERVER_PORT = CommandData([0xe2, 0x00, 0x70], 10)

    USER_LOGIN = CommandData([0xe1, 0x00, 0x11], 6)
    SET_USER_PASSWORD = CommandData([0xe1, 0x00, 0xa1], 6)

    ADMIN_LOGIN = CommandData([0xe1, 0x00, 0x10], 6)
    SET_ADMIN_PASSWORD = CommandData([0xe1, 0x00, 0xa2], 6)

class MainViewModel():

    dev = usb.core.find(idVendor=0x4255, idProduct=0x0001)

    def get_devices(self):
        
        devices = []

        for device in usb.core.find(idVendor=0x4255, find_all=True):
            devices.append(device)

        return devices

    def set_device(self, dev):
        self.dev = dev

    def non_zero_filter(self, num):
        return num != 0x00

    def read_battery(self):
        return self.send_command(Command.READ_BATTERY)[0]
    
    def sync_time(self):

        date = datetime.now()
        payload = list(date.year.to_bytes(2, 'big'))
        payload += list(date.month.to_bytes(1, 'big'))
        payload += list(date.day.to_bytes(1, 'big'))
        payload += list(date.hour.to_bytes(1, 'big'))
        payload += list(date.minute.to_bytes(1, 'big'))
        payload += list(date.second.to_bytes(1, 'big'))

        result = self.send_command(Command.SYNC_TIME, payload)
        if result != None:
            year = int.from_bytes(result[:2], 'big')
            month = int.from_bytes(result[2:3], 'big')
            day = int.from_bytes(result[3:4], 'big')
            hour = int.from_bytes(result[4:5], 'big')
            minute = int.from_bytes(result[5:6], 'big')
            second = int.from_bytes(result[6:7], 'big')
            return datetime(year, month, day, hour, minute, second)
        else:
            return None
    
    def switch_to_storage_mode(self):
        result = self.send_command(Command.SWITCH_TO_STORAGE_MODE)
        return result != None

    def read_wifi_mode(self):
        return self.send_command(Command.READ_WIFI_MODE)[0]

    def read_wifi_ssid(self):
        result = filter(self.non_zero_filter, self.send_command(Command.READ_WIFI_SSID))
        result = ''.join([chr(x) for x in result])
        return result[:-1]
    
    def write_wifi_ssid(self, ssid):
        result = self.send_command(Command.WRITE_WIFI_SSID, [ord(x) for x in ssid])
        return result != None
    
    def read_wifi_password(self):
        result = filter(self.non_zero_filter, self.send_command(Command.READ_WIFI_PASSWORD))
        result = ''.join([chr(x) for x in result])
        return result[:-1]
    
    def write_wifi_password(self, password):
        result = self.send_command(Command.WRITE_WIFI_PASSWORD, [ord(x) for x in password])
        return result != None
    
    def read_video_resolution(self):
        return resolution_dict[self.send_command(Command.READ_VIDEO_RESOLUTION)[-1]]

    def read_cam_id(self):
        ret = self.send_command(Command.READ_CAM_ID)

        camera_sn_raw = filter(self.non_zero_filter, ret[0:7])
        camera_sn = ''.join([chr(x) for x in camera_sn_raw])

        user_id_raw = filter(self.non_zero_filter, ret[9:16])
        user_id = ''.join([chr(x) for x in user_id_raw])

        user_name_raw = filter(self.non_zero_filter, ret[17:33])
        user_name = ''.join([chr(x) for x in user_name_raw])

        dep_id_raw = filter(self.non_zero_filter, ret[52:65])
        dep_id = ''.join([chr(x) for x in dep_id_raw])

        dep_name_raw = filter(self.non_zero_filter, ret[68:86])
        dep_name = ''.join([chr(x) for x in dep_name_raw])
        
        return [camera_sn, user_id, user_name, dep_id, dep_name]
    
    def write_cam_id(self, camera_serial, user_id, user_name, dep_id, dep_name):
        msg = [ord(x) for x in camera_serial] + [0x00] * (9 - len(camera_serial))
        msg += [ord(x) for x in user_id] + [0x00] * (8 - len(user_id))
        msg += [ord(x) for x in user_name] + [0x00] * (35 - len(user_name))
        msg += [ord(x) for x in dep_id] + [0x00] * (16 - len(dep_id))
        msg += [ord(x) for x in dep_name] + [0x00] * (32 - len(dep_name))

        result = self.send_command(Command.WRITE_CAM_ID, msg)
        return result != None
    
    def read_server_ip(self):
        ret = filter(self.non_zero_filter, self.send_command(Command.READ_SERVER_IP))
        result = ''.join([chr(x) for x in ret])
        return result
    
    def write_server_ip(self, ip):
        result = self.send_command(Command.WRITE_SERVER_IP, [ord(x) for x in ip])
        return result != None
    
    def read_server_port(self):
        result = filter(self.non_zero_filter, self.send_command(Command.READ_SERVER_PORT))
        result = ''.join([chr(x) for x in result])
        return result
    
    def write_server_port(self, port):
        result = self.send_command(Command.WRITE_SERVER_PORT, [ord(x) for x in port])
        return result != None
    
    def read_apn(self):
        result = filter(self.non_zero_filter, self.send_command(Command.READ_SIM_APN))
        result = ''.join([chr(x) for x in result])
        return result[:-1]

    def write_sim_apn(self, apn):
        result = self.send_command(Command.WRITE_SIM_APN, [ord(x) for x in apn])
        return result != None

    def read_sim_pin(self):
        result = filter(self.non_zero_filter, self.send_command(Command.READ_SIM_PIN))
        result = ''.join([chr(x) for x in result])
        return result[:-1]
    
    def write_sim_pin(self, pin):
        result = self.send_command(Command.WRITE_SIM_PIN, [ord(x) for x in pin])
        return result != None
    
    def write_wifi_mode(self, mode):
        result = self.send_command(Command.WRITE_WIFI_MODE, [mode])
        return result != None

    def login(self, password, user_type):
        password_payload = [ord(x) for x in password]
        
        if user_type == 0x10:
            result = self.send_command(Command.ADMIN_LOGIN, password_payload)
        else:
            result = self.send_command(Command.USER_LOGIN, password_payload)

        return result != None
    
    def set_admin_password(self, password):
        result = self.send_command(Command.SET_ADMIN_PASSWORD, [ord(x) for x in password])
        return result != None
    
    def set_user_password(self, password):
        result = self.send_command(Command.SET_USER_PASSWORD, [ord(x) for x in password])
        return result != None

    def ping_device(self):
        result = self.send_command(Command.DEVICE_PING)
        return result != None and ''.join([chr(x) for x in result]) == 'ABCDE'
    
    def send_command(self, command: Command, payload: list[int] = []) -> list[int] | None:
        try:

            msg = [0xa1, 0xb2, 0xc3, 0xd4, 0x00] + command.value.command_text + [0x00] + payload + [0x00] * (command.value.data_len - len(payload))
            assert self.dev.ctrl_transfer(0x40, 85, 0x00aa, 0, msg) == len(msg)
            ret = self.dev.ctrl_transfer(0xC0, 85, 0, 0, len(msg))

            print(command.name, ret[6] == 0x80)

            if ret[6] == 0x80:
                return ret[9:]
            else:
                return None
            
        except:
            return None
    