# Piotrunius AutoClicker & More

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)

An advanced and fully customizable AutoClicker and Anti-AFK tool, designed for gamers and task automation. The application features a modern and intuitive user interface with extensive personalization options.


*I suggest inserting a screenshot of the main application window here.*

## 📜 Features

The application consists of three main modules: AutoClicker, Anti-AFK, and Settings.

### 🖱️ AutoClicker
- **Independent LMB & RMB Settings**: Configure Clicks Per Second (CPS), random variation, and jitter separately for the left and right mouse buttons.
- **Three Activation Modes**:
    - **Hold**: Clicking is active while you hold down the physical mouse button (after arming with a hotkey).
    - **Toggle**: Start and stop clicking with a single hotkey press.
    - **Burst**: Execute a defined number of clicks in a burst after pressing the hotkey.
- **Click Customization**:
    - Set a click limit in Toggle mode.
    - Option to click at a fixed, predefined screen position.
    - Option to restrict actions to a specific game window (e.g., Minecraft).
- **Customizable Hotkey** for activation/deactivation.
- **Emergency STOP**: The `ESC` key immediately stops all actions.

### ☕ Anti-AFK
- **Flexible Intervals**: Set the minimum and maximum time after which the program should perform an action.
- **Diverse Actions**:
    - **Mouse Movement**: A slight cursor movement within a given range.
    - **Mouse Click**: A random left or right mouse click.
    - **Scroll**: A random mouse wheel scroll up or down.
    - **Key Presses**: Emulate key presses from predefined sets (e.g., WASD) or custom keys.
- **Return to Start Position**: Option to return the cursor to its original position after performing an action.
- **Dedicated Hotkey** to enable and disable the module.

### ⚙️ General Settings
- **Multi-Language Support**: The interface is available in English and Polish.
- **Appearance Customization**:
    - Two themes: Dark and Light.
    - Ability to change the UI's accent color.
    - Adjustable window opacity.
- **Always on Top**: Option to pin the application window so it's always visible.
- **Global Start Delay**: Set a delay in seconds before the program starts its action after activation.
- **Auto-Save**: All settings are automatically saved to a `.json` file in the user's home directory.

## 🚀 Installation

The program requires **Python 3** to be installed.
1.  **Install the required libraries:**
    It is recommended to create a virtual environment. Then, install the packages using `pip`:
    ```bash
    pip install PyQt6 pynput pygetwindow
    ```

## ▶️ How to Use

After installing the dependencies, run the main script file:

```bash
python AutoClicker.py
```

1.  Navigate to the desired tab (AutoClicker or Anti-AFK).
2.  Configure the options to your liking (CPS, activation mode, hotkeys, etc.).
3.  Use your defined hotkey to activate the function.
4.  **To immediately stop all program actions, press the `ESC` key**.

## ⚖️ License

This project is licensed under the **MIT License**. This means you are free to use, copy, modify, and distribute this code, provided that the original copyright notice is retained.

---

Made with ❤️ by [Piotrunius](https://e-z.bio/piotrunius) © 2025
