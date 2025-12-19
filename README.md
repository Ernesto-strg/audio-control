# Windows Audio Control

![Windows](https://img.shields.io/badge/Platform-Windows-0078d7.svg?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.13-3776ab.svg?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

<p align="center">
  <img src="assets/win-audio-control.png" alt="WinAudioControl Logo" width="300">
</p>

Control your Windows master, app-specific, and foreground process volumes with your own microcontroller and rotary encoders.

## ✨ Features
- **Channel Mixing**: Control Master, specific Apps, and the currently focused window.
- **Mute Function**: Push the encoder to toggle mute for the assigned channel.
- **Intelligent Foreground Control**: Automatically targets the active window's volume, but stays locked to the last audio-producing app until a new, unmapped sound source is detected.
- **EarTrumpet Integration**: Triggers the EarTrumpet flyout for visual feedback.
- **Auto-Reconnect**: Automatically restores connection if the Arduino is unplugged.

## 🚀 Installation & Setup
1. **Hardware:** Connect your rotary encoders to the microcontroller.
<p align="center">
  <img src="assets/wiring.jpg" alt="Hardware Wiring" width="500">
  <br>
  <em>Aktueller Prototyp-Aufbau auf dem Breadboard</em>
</p>
3. **Firmware:** Upload the `sketch_dec17b.ino` from the `/sketch_dec17b` folder. Ensure the pin assignments in the code match your wiring and adjust the number of encoders if necessary.
4. **Configuration:** Run the `.exe` or `audio-control.py`. Make sure to edit the `config.json` in the same directory.
   - Set the `com_port` (if left empty, the app will auto-connect to the first available COM device).
   - Configure your channels using these three options:

| Channel Option | Description |
| :--- | :--- |
| **master** | Adjusts the global Windows system volume. |
| **foreground** | Adjusts the volume of the application currently in focus. |
| **app.exe** | Adjusts the volume of a specific app (e.g., `spotify.exe`). |

   - `flyout_hotkey`: Must match your EarTrumpet "Settings > Shortcuts" hotkey.

4. **Autostart (Optional):** Create a shortcut of the `.exe` and place it in the Windows Startup folder (`shell:startup`) to launch it automatically on boot.
5. **Run:** Start `audio-control.exe` or run `python audio-control.py`.
