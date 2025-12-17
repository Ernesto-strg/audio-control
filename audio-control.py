import pywintypes
import win32gui
import win32process
import win32con
import psutil
import time
import serial
import pyautogui
import json
import sys
import os
import serial.tools.list_ports
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume


def find_port():
    ports = serial.tools.list_ports.comports()
    return ports[0].device

def load_config():
    config_name = 'config.json'
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(base_path, config_name)

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der {config_name}: {e}")
        detected_port = find_port()
        return {
            "connection": {"port": detected_port, "baud_rate": 9600},
            "settings": {"step": 0.02, "flyout_time": 1.5, "flyout_hotkey": ["winleft", "alt", "o"], "sleep_time": 0.02},
            "channels": [ {"id": 1, "type": "master"}, {"id": 2, "type": "app", "target": "firefox.exe"}, {"id": 3, "type": "foreground"}, {"id": 4, "type": "app", "target": "discord.exe"} ]
        }

config = load_config()

COM_PORT = config['connection']['port']
BAUD_RATE = config['connection']['baud_rate']
VOL_STEP = config['settings']['step']
FLYOUT_TIME = config['settings']['flyout_time']
FLYOUT_HOTKEY = config['settings']['flyout_hotkey']
SLEEP_TIME = config['settings']['sleep_time']

CHANNELS: dict = {str(ch.get('id')): ch for ch in config.get('channels', [])}
MAPPED_APPS = [ch['target'].lower() for ch in CHANNELS.values() if ch.get('type') == 'app']

print(f"Konfiguration geladen. Aktive Kanäle: {list(CHANNELS.keys())}")


last_valid_foreground_exe = None
prev_hwnd = 0
flyout_busy = False
last_change = time.time()


def get_device():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return interface.QueryInterface(IAudioEndpointVolume)


def vol_change(direction):
    volume = get_device()
    current = volume.GetMasterVolumeLevelScalar()
    new_vol = min(current + VOL_STEP, 1.0) if direction == "UP" else max(current - VOL_STEP, 0.0)
    volume.SetMasterVolumeLevelScalar(new_vol, None)

    global flyout_busy
    flyout_busy = True


def app_vol_change(app_name, direction):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == app_name.lower():
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            current = volume.GetMasterVolume()
            new_vol = min(current + VOL_STEP, 1.0) if direction == "UP" else max(current - VOL_STEP, 0.0)
            volume.SetMasterVolume(new_vol, None)

            global flyout_busy
            flyout_busy = True


def toggle_mute(app_name=None):
    if app_name:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() == app_name.lower():
                vol = session._ctl.QueryInterface(ISimpleAudioVolume)
                vol.SetMute(not vol.GetMute(), None)

                global flyout_busy
                flyout_busy = True
    else:
        vol = get_device()
        vol.SetMute(not vol.GetMute(), None)

        flyout_busy = True


def is_app_volume_controllable(exe_name):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == exe_name:
            return True
    return False


def get_foreground_exe():
    global last_valid_foreground_exe
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return last_valid_foreground_exe
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        proc = psutil.Process(pid)
        exe_name = proc.name().lower()
        if exe_name in MAPPED_APPS:
            return last_valid_foreground_exe
        elif is_app_volume_controllable(exe_name):
            last_valid_foreground_exe = exe_name
            return exe_name
        else:
            return last_valid_foreground_exe
    except psutil.NoSuchProcess:
        return last_valid_foreground_exe


def flyout():
    global flyout_busy, prev_hwnd
    if not flyout_busy:
        flyout_busy = True
        prev_hwnd = win32gui.GetForegroundWindow()
        pyautogui.hotkey(*FLYOUT_HOTKEY)


try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
except serial.SerialException:
    ser = None
    print(f"Konnte {COM_PORT} nicht öffnen.")


while True:
    line = ""
    try:
        line = ser.readline().decode('utf-8').strip()
    except serial.SerialException:
        if ser and ser.is_open:
            ser.close()

        while True:
            try:
                ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
                break
            except serial.SerialException:
                time.sleep(2)

    if not line:
        if flyout_busy and time.time() - last_change > FLYOUT_TIME:
            if win32gui.IsWindow(prev_hwnd):
                win32gui.ShowWindow(prev_hwnd, win32con.SW_SHOW)
                try:
                    win32gui.SetForegroundWindow(prev_hwnd)
                except pywintypes.error:
                    pass
            flyout_busy = False
        continue

    parts = line.split('_')
    if len(parts) >= 2:
        cmd_type = parts[0]
        ch_id = parts[-1]

        if ch_id in CHANNELS:
            ch = CHANNELS[ch_id]

            if ch['type'] == 'foreground':
                target_app = get_foreground_exe()
            else:
                target_app = ch.get('target')

            last_change = time.time()
            flyout()

            if cmd_type == "VOL":
                direction = parts[1]
                if ch['type'] == 'master':
                    vol_change(direction)
                elif target_app:
                    app_vol_change(target_app, direction)
            elif cmd_type == "BUTTON":
                if ch['type'] == 'master':
                    toggle_mute()
                elif target_app:
                    toggle_mute(target_app)

    time.sleep(SLEEP_TIME)