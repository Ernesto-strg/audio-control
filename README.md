![Windows](https://img.shields.io/badge/Platform-Windows-0078d7.svg?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.13-3776ab.svg?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

### Installation & Setup

1. **Hardware:** Connect your rotary encoders to the microcontroller.
2. **Firmware:** Upload the `sketch_dec17b.ino` from the `/sketch_dec17b` folder. Ensure the pin assignments in the code match your wiring and adjust the number of encoders if necessary.
3. **Configuration:** Run the `.exe` or `audio-control.py`. Make sure to edit the `config.json` in the same directory.
   - Set the `com_port` (if left empty, the app will auto-connect to the first available COM device).
   - Configure your channels using these three options:

| Channel Option | Description |
| :--- | :--- |
| **master** | Adjusts the global Windows system volume. |
| **foreground** | Adjusts the volume of the application currently in focus. |
| **app.exe** | Adjusts the volume of a specific app (e.g., `spotify.exe`). |

4. **Autostart (Optional):** Create a shortcut of the `.exe` and place it in the Windows Startup folder (`shell:startup`) to launch it automatically on boot.

Features
- **Visual Feedback**: Compatible with EarTrumpet (triggers the flyout via shortcut for a modern UI experience).
