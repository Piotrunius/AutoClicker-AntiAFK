# ==================================================================================================
#                                         IMPORTS
# ==================================================================================================
import json
import os
import random
import re
import sys
import threading
import time
from dataclasses import dataclass, field

# --- Dependency Check ---
# Ensures that the required pygetwindow library is installed before proceeding.
try:
    import pygetwindow
except ImportError:
    print("Error: The pygetwindow library is not installed.")
    print("Please install it using the command: pip install pygetwindow")
    sys.exit(1)

# --- Core Libraries ---
# PyQt6 for the graphical user interface.
# pynput for listening to and controlling mouse and keyboard inputs globally.
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QStyle
from pynput.mouse import Controller as MouseController, Button as MouseButton, Listener as MouseListener
from pynput.keyboard import Controller as KeyboardController, Listener as KeyboardListener, Key, KeyCode

# ==================================================================================================
#                                     CONSTANTS & CONFIGURATION
# ==================================================================================================

# --- Translation System ---
# A dictionary holding all UI text for both English and Polish languages.
TRANSLATIONS = {
    'en': {
        # General
        'window_title': "Piotrunius AutoClicker & More",
        'close_button': "Close",
        # Tabs
        'tab_autoclicker': "AutoClicker",
        'tab_antiafk': "Anti-AFK",
        'tab_settings': "Settings",
        # Status
        'status_stopped': "Status: STOPPED",
        'status_armed': "Status: <font color='orange'>ARMED</font>",
        'status_clicking': "Status: <font color='{color}'>CLICKING</font>",
        'status_antiafk': "Status: <font color='{color}'>ANTI-AFK ACTIVE</font>",
        # Autoclicker Tab
        'lmb_box_title': "Left Mouse Button (LMB)",
        'rmb_box_title': "Right Mouse Button (RMB)",
        'cps_label': "CPS:",
        'variation_check': "Random Variation",
        'jitter_label': "Jitter (± ms):",
        'global_settings_title': "AutoClicker Global Settings",
        'activation_mode_label': "Activation Mode:",
        'hold_mode_radio': "Hold Mode",
        'toggle_mode_radio': "Toggle Mode",
        'burst_mode_radio': "Burst Mode",
        'click_with_label': "Click with (Toggle/Burst):",
        'left_button_radio': "Left Button",
        'right_button_radio': "Right Button",
        'burst_clicks_label': "Clicks in burst:",
        'burst_delay_label': "Delay in burst:",
        'fixed_pos_check': "Click at fixed position",
        'capture_pos_button': "Capture Position",
        'capture_pos_button_countdown': "Capturing in {count}...",
        'click_limit_label': "Click Limit (Toggle):",
        'hotkeys_title': "Hotkeys",
        'activation_key_label': "Activation Key:",
        'autoclicker_info_title': "💡 How to Use (Click to Expand)",
        'autoclicker_info_text': (
            "• <b>Hold Mode:</b> Press the Activation Key to ARM. Then, hold down your physical mouse button (LMB/RMB) to start clicking.<br>"
            "• <b>Toggle/Burst Mode:</b> Press the Activation Key to start or stop clicking.<br>"
            "• <b>Emergency STOP:</b> Press the <b>ESC</b> key at any time to immediately stop all actions (both AutoClicker and Anti-AFK)."
        ),
        # Anti-AFK Tab
        'antiafk_settings_title': "Anti-AFK Actions",
        'enable_antiafk_check': "Enable Anti-AFK Module",
        'perform_actions_every_label': "Perform actions every:",
        'interval_min_label': "Min:",
        'interval_max_label': "Max:",
        'move_mouse_check': "Slight mouse movement",
        'movement_range_label': "Movement range (±):",
        'return_to_start_check': "Return to start position",
        'click_mouse_check': "Random mouse click",
        'scroll_mouse_check': "Random mouse scroll",
        'press_keys_check': "Press keys",
        'presets_label': "Presets:",
        'custom_keys_label': "Custom keys:",
        'custom_keys_placeholder': "e.g. efq",
        'start_antiafk_button': "Start Anti-AFK",
        'stop_antiafk_button': "Stop Anti-AFK",
        'antiafk_hotkey_label': "Anti-AFK Hotkey:",
        'antiafk_info_title': "💡 How to Use (Click to Expand)",
        'antiafk_info_text': "Configure the desired actions and time intervals above. Then, press the <b>Start Anti-AFK</b> button or use the <b>Anti-AFK Hotkey</b> to begin. The module will run until you stop it or use the emergency ESC key.",
        # Settings Tab
        'app_settings_title': "Application Settings",
        'language_label': "Language:",
        'theme_label': "Theme:",
        'theme_dark': "Dark",
        'theme_light': "Light",
        'opacity_label': "Window Opacity:",
        'start_delay_label': "Global Start Delay:",
        'limit_window_check': "Restrict actions to game window",
        'window_title_placeholder': "Window title (e.g. Minecraft)",
        'always_on_top_check': "Always on Top",
        'accent_color_label': "Accent Color:",
        'change_color_button': "Change",
        'reset_settings_label': "Reset all settings:",
        'reset_settings_button': "Reset to Defaults",
        'reset_confirm_title': "Confirm Reset",
        'reset_confirm_text': "Are you sure you want to reset all settings to their default values? The application will need to be restarted.",
    },
    'pl': {
        # General
        'window_title': "Piotrunius AutoClicker & Więcej",
        'close_button': "Zamknij",
        # Tabs
        'tab_autoclicker': "AutoClicker",
        'tab_antiafk': "Anty-AFK",
        'tab_settings': "Ustawienia",
        # Status
        'status_stopped': "Status: ZATRZYMANY",
        'status_armed': "Status: <font color='orange'>UZBROJONY</font>",
        'status_clicking': "Status: <font color='{color}'>KLIKANIE</font>",
        'status_antiafk': "Status: <font color='{color}'>ANTY-AFK AKTYWNY</font>",
        # Autoclicker Tab
        'lmb_box_title': "Lewy Przycisk Myszy (LPM)",
        'rmb_box_title': "Prawy Przycisk Myszy (PPM)",
        'cps_label': "CPS:",
        'variation_check': "Losowa Zmienność",
        'jitter_label': "Zmienność (± ms):",
        'global_settings_title': "Globalne Ustawienia AutoClickera",
        'activation_mode_label': "Tryb Aktywacji:",
        'hold_mode_radio': "Tryb Przytrzymania",
        'toggle_mode_radio': "Tryb Przełączania",
        'burst_mode_radio': "Tryb Serii",
        'click_with_label': "Klikaj (Przełącz/Seria):",
        'left_button_radio': "Lewy Przycisk",
        'right_button_radio': "Prawy Przycisk",
        'burst_clicks_label': "Kliknięć w serii:",
        'burst_delay_label': "Odstęp w serii:",
        'fixed_pos_check': "Klikaj w stałej pozycji",
        'capture_pos_button': "Złap Pozycję",
        'capture_pos_button_countdown': "Łapanie za {count}...",
        'click_limit_label': "Limit Kliknięć (Przełącz):",
        'hotkeys_title': "Skróty Klawiszowe",
        'activation_key_label': "Klawisz Aktywacji:",
        'autoclicker_info_title': "💡 Jak Używać (Kliknij, by rozwinąć)",
        'autoclicker_info_text': (
            "• <b>Tryb Przytrzymania:</b> Wciśnij Klawisz Aktywacji, aby UZBROIĆ. Następnie przytrzymaj fizyczny przycisk myszy (LPM/PPM), aby zacząć klikać.<br>"
            "• <b>Tryb Przełączania/Serii:</b> Wciśnij Klawisz Aktywacji, aby włączyć lub wyłączyć klikanie.<br>"
            "• <b>STOP Awaryjny:</b> Wciśnij klawisz <b>ESC</b> w dowolnym momencie, aby natychmiast zatrzymać wszystkie akcje (AutoClicker i Anty-AFK)."
        ),
        # Anti-AFK Tab
        'antiafk_settings_title': "Akcje Anty-AFK",
        'enable_antiafk_check': "Włącz Moduł Anty-AFK",
        'perform_actions_every_label': "Wykonuj akcje co:",
        'interval_min_label': "Min:",
        'interval_max_label': "Max:",
        'move_mouse_check': "Lekki ruch myszą",
        'movement_range_label': "Zasięg ruchu (±):",
        'return_to_start_check': "Powrót do pozycji startowej",
        'click_mouse_check': "Losowe kliknięcie myszą",
        'scroll_mouse_check': "Losowe przewijanie rolką",
        'press_keys_check': "Wciskaj klawisze",
        'presets_label': "Predefiniowane:",
        'custom_keys_label': "Własne klawisze:",
        'custom_keys_placeholder': "np. efq",
        'start_antiafk_button': "Start Anty-AFK",
        'stop_antiafk_button': "Stop Anty-AFK",
        'antiafk_hotkey_label': "Klawisz Anty-AFK:",
        'antiafk_info_title': "💡 Jak Używać (Kliknij, by rozwinąć)",
        'antiafk_info_text': "Skonfiguruj pożądane akcje i interwały czasowe powyżej. Następnie wciśnij przycisk <b>Start Anty-AFK</b> lub użyj <b>Klawisza Anty-AFK</b>, aby rozpocząć. Moduł będzie działał, dopóki go nie zatrzymasz lub nie użyjesz awaryjnego klawisza ESC.",
        # Settings Tab
        'app_settings_title': "Ustawienia Aplikacji",
        'language_label': "Język:",
        'theme_label': "Motyw:",
        'theme_dark': "Ciemny",
        'theme_light': "Jasny",
        'opacity_label': "Przezroczystość okna:",
        'start_delay_label': "Globalne Opóźnienie Startu:",
        'limit_window_check': "Ogranicz akcje do okna gry",
        'window_title_placeholder': "Tytuł okna (np. Minecraft)",
        'always_on_top_check': "Zawsze na wierzchu",
        'accent_color_label': "Kolor Akcentu:",
        'change_color_button': "Zmień",
        'reset_settings_label': "Zresetuj ustawienia:",
        'reset_settings_button': "Resetuj do domyślnych",
        'reset_confirm_title': "Potwierdź Reset",
        'reset_confirm_text': "Czy na pewno chcesz przywrócić wszystkie ustawienia do wartości domyślnych? Aplikacja będzie wymagała ponownego uruchomienia.",
    }
}

# --- Global Constants ---
# Defines the path for the settings file, the copyright text, and the default UI color.
SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".autoclicker_piotrunius.json")
COPYRIGHT_TEXT = f'Made with love by <a href="https://e-z.bio/piotrunius" style="color: {{ACCENT_COLOR}}; text-decoration:none;">Piotrunius</a> © 2025'
DEFAULT_ACCENT_COLOR = "#42a5f5"

# ==================================================================================================
#                                     SETTINGS HELPER FUNCTIONS
# ==================================================================================================

# --- Load Settings ---
# Reads the configuration from the JSON file in the user's home directory.
# Returns an empty dictionary if the file doesn't exist or is corrupted.
def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {}
    return {}

# --- Save Settings ---
# Writes the current application settings to the JSON file.
def save_settings(data: dict):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception: pass

# ==================================================================================================
#                                         DATA CLASSES
# ==================================================================================================

# --- Clicker Configuration ---
# A data class to hold all settings related to the autoclicker's operation.
@dataclass
class ClickConfig:
    cps: float = 12.0
    use_random_variation: bool = True
    jitter_ms: int = 8
    click_button: MouseButton = MouseButton.left
    limit_to_window: bool = False
    window_title: str = "Minecraft"
    start_delay_s: float = 0.0
    click_limit: int = 0
    use_fixed_position: bool = False
    fixed_x: int = 0
    fixed_y: int = 0
    is_burst_mode: bool = False
    burst_clicks: int = 3
    burst_delay_ms: int = 50

# --- Anti-AFK Configuration ---
# A data class to hold all settings for the Anti-AFK module.
@dataclass
class AntiAfkConfig:
    enabled: bool = False
    min_interval_s: int = 10
    max_interval_s: int = 15
    move_mouse: bool = True
    mouse_range: int = 5
    return_to_start: bool = False
    click_mouse: bool = False
    scroll_mouse: bool = False
    press_keys: bool = False
    keys_to_press: list[str] = field(default_factory=list)

# ==================================================================================================
#                                         WORKER THREADS
# ==================================================================================================

# --- ClickWorker Class ---
# This QThread performs the actual clicking actions in the background to prevent the UI from freezing.
class ClickWorker(QtCore.QThread):
    sig_finished = QtCore.pyqtSignal() # Signal emitted when the worker is done.
    def __init__(self, cfg: ClickConfig, main_window, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.main_window = main_window
        self._stop_event = threading.Event()
        self.mouse = MouseController()

    # Gracefully stops the worker thread.
    def stop(self): self._stop_event.set()

    # Main entry point for the thread's execution.
    def run(self):
        if self.cfg.start_delay_s > 0: self._sleep_interruptible(self.cfg.start_delay_s)
        if self.cfg.is_burst_mode: self._run_burst_mode()
        else: self._run_continuous_mode()
        self.sig_finished.emit()

    # Logic for executing a fixed number of clicks (Burst Mode).
    def _run_burst_mode(self):
        burst_interval_s = self.cfg.burst_delay_ms / 1000.0
        for _ in range(self.cfg.burst_clicks):
            if self._stop_event.is_set(): break
            self._do_single_click()
            self._sleep_interruptible(burst_interval_s)

    # Logic for continuous clicking until stopped (Hold/Toggle Mode).
    def _run_continuous_mode(self):
        click_count = 0
        while not self._stop_event.is_set():
            self._do_single_click()
            click_count += 1
            if self.cfg.click_limit > 0 and click_count >= self.cfg.click_limit: break
            base_interval = 1.0 / max(0.1, self.cfg.cps)
            interval = base_interval
            if self.cfg.use_random_variation:
                jitter = self.cfg.jitter_ms / 1000.0
                delta = random.uniform(-jitter, jitter)
                interval = max(0.001, base_interval + delta)
            self._sleep_interruptible(interval)

    # Performs a single, validated mouse click.
    def _do_single_click(self):
        # Check if clicking should be restricted to a specific window.
        if self.cfg.limit_to_window and self.cfg.window_title:
            try:
                active_window = pygetwindow.getActiveWindow()
                if active_window is None or not re.search(self.cfg.window_title, active_window.title, re.IGNORECASE): return
            except Exception: return
        # Move mouse to a fixed position if enabled.
        if self.cfg.use_fixed_position:
            self.mouse.position = (self.cfg.fixed_x, self.cfg.fixed_y)
            self._sleep_interruptible(0.01)
        # Perform the click.
        self.main_window.programmatic_click = True
        self.mouse.click(self.cfg.click_button, 1)

    # A sleep implementation that can be interrupted by the stop event.
    def _sleep_interruptible(self, seconds: float):
        end_time = time.perf_counter() + seconds
        while time.perf_counter() < end_time:
            if self._stop_event.is_set(): break
            time.sleep(0.001)

# --- AntiAfkWorker Class ---
# This QThread performs Anti-AFK actions at random intervals in the background.
class AntiAfkWorker(QtCore.QThread):
    sig_finished = QtCore.pyqtSignal()
    def __init__(self, cfg: AntiAfkConfig, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self._stop_event = threading.Event()
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

    # Gracefully stops the worker thread.
    def stop(self): self._stop_event.set()

    # Main entry point for the thread's execution.
    def run(self):
        while not self._stop_event.is_set():
            # Wait for a random interval.
            wait_time = random.uniform(self.cfg.min_interval_s, self.cfg.max_interval_s)
            if self._stop_event.wait(wait_time):
                break
            
            start_pos = self.mouse.position

            # Perform enabled actions.
            if self.cfg.move_mouse:
                offset_x = random.randint(-self.cfg.mouse_range, self.cfg.mouse_range)
                offset_y = random.randint(-self.cfg.mouse_range, self.cfg.mouse_range)
                self.mouse.move(offset_x, offset_y)
                self._sleep_interruptible(0.1)

            if self.cfg.click_mouse:
                button_to_click = random.choice([MouseButton.left, MouseButton.right])
                self.mouse.click(button_to_click, 1)
                self._sleep_interruptible(0.1)

            if self.cfg.scroll_mouse:
                scroll_dir = random.choice([-1, 1])
                self.mouse.scroll(0, scroll_dir)
                self._sleep_interruptible(0.1)

            if self.cfg.press_keys and self.cfg.keys_to_press:
                key_to_press = random.choice(self.cfg.keys_to_press)
                self.keyboard.press(key_to_press)
                self._sleep_interruptible(0.1)
                self.keyboard.release(key_to_press)
            
            # Return mouse to its original position if enabled.
            if self.cfg.return_to_start:
                self.mouse.position = start_pos

        self.sig_finished.emit()
    
    # An interruptible sleep implementation.
    def _sleep_interruptible(self, seconds: float):
        end_time = time.perf_counter() + seconds
        while time.perf_counter() < end_time:
            if self._stop_event.is_set(): break
            time.sleep(0.001)

# ==================================================================================================
#                                         MAIN WINDOW
# ==================================================================================================
class MainWindow(QtWidgets.QMainWindow):
    # --- Custom Signals ---
    # Signals for thread-safe communication between listeners and the main UI thread.
    sig_start_clicking = QtCore.pyqtSignal(MouseButton)
    sig_stop_clicking = QtCore.pyqtSignal()
    sig_toggle_armed = QtCore.pyqtSignal()
    sig_trigger_action = QtCore.pyqtSignal()
    sig_toggle_afk = QtCore.pyqtSignal() # <<< FIX 1: ADDED SIGNAL
    
    # --- Initialization ---
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 650)
        
        # --- State Variables ---
        self.worker: ClickWorker | None = None
        self.afk_worker: AntiAfkWorker | None = None
        self.is_armed = False # Used for "Hold Mode"
        self.programmatic_click = False # Flag to ignore clicks generated by the app
        self.capture_timer = None
        self.capture_countdown = 0
        
        # --- Load Settings & Theming ---
        self.settings = load_settings()
        self.accent_color = QtGui.QColor(self.settings.get("accent_color", DEFAULT_ACCENT_COLOR))
        self.current_language = self.settings.get("language", "en")
        self.current_theme = self.settings.get("theme", "dark")

        # --- UI and Listener Setup ---
        self._build_ui()
        self._load_settings_to_ui()
        self._update_theme() 
        self._retranslate_ui()
        self._verify_integrity()
        
        # --- Connect Signals to Slots ---
        self.sig_start_clicking.connect(self.on_start_clicking)
        self.sig_stop_clicking.connect(self.on_stop_clicking)
        self.sig_toggle_armed.connect(self.on_toggle_armed)
        self.sig_trigger_action.connect(self.on_trigger_action)
        self.sig_toggle_afk.connect(self.on_toggle_afk_worker) # <<< FIX 2: CONNECTED SIGNAL
        
        self._start_listeners()

    # --- Translation Helper ---
    # Fetches the translated string for a given key.
    def _tr(self, key):
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS['en']).get(key, f"_{key}_")

    # =====================================================================
    # UI Building
    # =====================================================================

    # --- Main UI Structure ---
    # Builds the main window layout, tabs, status bar, and close button.
    def _build_ui(self):
        main_widget = QtWidgets.QWidget()
        main_widget.setObjectName("mainWidget")
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        self.tab_widget = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        autoclicker_tab = QtWidgets.QWidget()
        antiafk_tab = QtWidgets.QWidget()
        settings_tab = QtWidgets.QWidget()
        
        self.tab_widget.addTab(autoclicker_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon), "")
        self.tab_widget.addTab(antiafk_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_DialogYesButton), "")
        self.tab_widget.addTab(settings_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "")

        # Populate each tab with its specific widgets.
        self._populate_autoclicker_tab(autoclicker_tab)
        self._populate_antiafk_tab(antiafk_tab)
        self._populate_settings_tab(settings_tab)

        # Status label at the bottom.
        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Main close button.
        self.close_button = QtWidgets.QPushButton()
        self.close_button.clicked.connect(self.close)
        main_layout.addWidget(self.close_button)

    # --- Autoclicker Tab UI ---
    # Creates and arranges all widgets for the Autoclicker tab.
    def _populate_autoclicker_tab(self, tab):
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # --- Left and Right Mouse Button Settings ---
        mouse_buttons_layout = QtWidgets.QHBoxLayout()
        self.lmb_box = self._create_mouse_button_group(self._tr('lmb_box_title'))
        self.rmb_box = self._create_mouse_button_group(self._tr('rmb_box_title'))
        mouse_buttons_layout.addWidget(self.lmb_box)
        mouse_buttons_layout.addWidget(self.rmb_box)
        layout.addLayout(mouse_buttons_layout)
        
        # --- Global AutoClicker Settings (Mode, Limits, etc.) ---
        self.global_settings_box = QtWidgets.QGroupBox()
        global_settings_layout = QtWidgets.QFormLayout(self.global_settings_box)
        
        self.hold_mode_radio = QtWidgets.QRadioButton()
        self.toggle_mode_radio = QtWidgets.QRadioButton()
        self.burst_mode_radio = QtWidgets.QRadioButton()
        mode_layout = QtWidgets.QHBoxLayout()
        mode_layout.addWidget(self.hold_mode_radio); mode_layout.addWidget(self.toggle_mode_radio); mode_layout.addWidget(self.burst_mode_radio)
        self.activation_mode_label = QtWidgets.QLabel()
        global_settings_layout.addRow(self.activation_mode_label, mode_layout)

        # Create composite widgets for specific options.
        self.button_choice_widget = self._create_button_choice_widget()
        global_settings_layout.addRow(self.button_choice_widget)
        self.burst_options_widget = self._create_burst_options_widget()
        global_settings_layout.addRow(self.burst_options_widget)
        self.fixed_pos_widget = self._create_fixed_pos_widget()
        global_settings_layout.addRow(self.fixed_pos_widget)

        self.click_limit_spin = QtWidgets.QSpinBox(); self.click_limit_spin.setRange(0, 1000000)
        self.click_limit_label = QtWidgets.QLabel()
        global_settings_layout.addRow(self.click_limit_label, self.click_limit_spin)
        
        layout.addWidget(self.global_settings_box)
        
        # --- Hotkeys ---
        self.hotkey_box = QtWidgets.QGroupBox()
        hotkey_layout = QtWidgets.QFormLayout(self.hotkey_box)
        self.activation_key_edit = QtWidgets.QLineEdit()
        self.activation_key_edit.setMaxLength(1)
        self.activation_key_edit.setFixedWidth(40)
        self.activation_key_label = QtWidgets.QLabel()
        hotkey_layout.addRow(self.activation_key_label, self.activation_key_edit)
        layout.addWidget(self.hotkey_box)

        # --- Info Box ---
        self.autoclicker_info_box = QtWidgets.QGroupBox()
        self.autoclicker_info_box.setCheckable(True)
        self.autoclicker_info_box.setChecked(False)
        self.autoclicker_info_label = QtWidgets.QLabel()
        self.autoclicker_info_label.setWordWrap(True)
        self.autoclicker_info_label.setVisible(False)
        info_layout = QtWidgets.QVBoxLayout(self.autoclicker_info_box)
        info_layout.addWidget(self.autoclicker_info_label)
        self.autoclicker_info_box.toggled.connect(self.autoclicker_info_label.setVisible)
        layout.addWidget(self.autoclicker_info_box)

        layout.addStretch()

    # --- Anti-AFK Tab UI ---
    # Creates and arranges all widgets for the Anti-AFK tab.
    def _populate_antiafk_tab(self, tab):
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.afk_box = QtWidgets.QGroupBox()
        afk_layout = QtWidgets.QFormLayout(self.afk_box)

        self.afk_enabled_check = QtWidgets.QCheckBox()
        afk_layout.addRow(self.afk_enabled_check)

        # --- Interval Settings ---
        interval_layout = QtWidgets.QHBoxLayout()
        self.afk_min_interval_spin = QtWidgets.QSpinBox(); self.afk_min_interval_spin.setRange(1, 300); self.afk_min_interval_spin.setSuffix(" s")
        self.afk_max_interval_spin = QtWidgets.QSpinBox(); self.afk_max_interval_spin.setRange(1, 300); self.afk_max_interval_spin.setSuffix(" s")
        self.interval_min_label = QtWidgets.QLabel(); self.interval_max_label = QtWidgets.QLabel()
        interval_layout.addWidget(self.interval_min_label); interval_layout.addWidget(self.afk_min_interval_spin)
        interval_layout.addSpacing(10)
        interval_layout.addWidget(self.interval_max_label); interval_layout.addWidget(self.afk_max_interval_spin)
        self.perform_actions_every_label = QtWidgets.QLabel()
        afk_layout.addRow(self.perform_actions_every_label, interval_layout)
        
        # --- Mouse Action Settings ---
        self.afk_move_mouse_check = QtWidgets.QCheckBox()
        self.afk_mouse_range_spin = QtWidgets.QSpinBox(); self.afk_mouse_range_spin.setRange(1, 100); self.afk_mouse_range_spin.setSuffix(" px")
        self.movement_range_label = QtWidgets.QLabel()
        afk_layout.addRow(self.afk_move_mouse_check)
        afk_layout.addRow(self.movement_range_label, self.afk_mouse_range_spin)
        self.afk_return_to_start_check = QtWidgets.QCheckBox()
        afk_layout.addRow(self.afk_return_to_start_check)
        self.afk_click_mouse_check = QtWidgets.QCheckBox()
        self.afk_scroll_mouse_check = QtWidgets.QCheckBox()
        afk_layout.addRow(self.afk_click_mouse_check)
        afk_layout.addRow(self.afk_scroll_mouse_check)
        
        self.afk_move_mouse_check.toggled.connect(lambda checked: [self.afk_mouse_range_spin.setEnabled(checked), self.afk_return_to_start_check.setEnabled(checked)])

        # --- Keyboard Action Settings ---
        self.afk_press_keys_check = QtWidgets.QCheckBox()
        afk_layout.addRow(self.afk_press_keys_check)
        keys_widget = QtWidgets.QWidget()
        keys_layout = QtWidgets.QHBoxLayout(keys_widget); keys_layout.setContentsMargins(0,0,0,0)
        self.afk_key_w = QtWidgets.QCheckBox("W"); self.afk_key_a = QtWidgets.QCheckBox("A"); self.afk_key_s = QtWidgets.QCheckBox("S"); self.afk_key_d = QtWidgets.QCheckBox("D"); self.afk_key_space = QtWidgets.QCheckBox("Space")
        keys_layout.addStretch(); keys_layout.addWidget(self.afk_key_w); keys_layout.addWidget(self.afk_key_a); keys_layout.addWidget(self.afk_key_s); keys_layout.addWidget(self.afk_key_d); keys_layout.addWidget(self.afk_key_space); keys_layout.addStretch()
        self.presets_label = QtWidgets.QLabel()
        afk_layout.addRow(self.presets_label, keys_widget)
        self.afk_custom_keys_edit = QtWidgets.QLineEdit()
        self.custom_keys_label = QtWidgets.QLabel()
        afk_layout.addRow(self.custom_keys_label, self.afk_custom_keys_edit)

        # --- Anti-AFK Hotkey ---
        self.afk_hotkey_edit = QtWidgets.QLineEdit()
        self.afk_hotkey_edit.setMaxLength(1)
        self.afk_hotkey_edit.setFixedWidth(40)
        self.afk_hotkey_label = QtWidgets.QLabel()
        afk_layout.addRow(self.afk_hotkey_label, self.afk_hotkey_edit)

        # --- Logic to enable/disable child widgets ---
        key_widgets = [keys_widget, self.afk_custom_keys_edit]
        self.afk_press_keys_check.toggled.connect(lambda checked: [w.setEnabled(checked) for w in key_widgets])
        all_afk_widgets = [self.afk_min_interval_spin, self.afk_max_interval_spin, self.afk_move_mouse_check, self.afk_mouse_range_spin, self.afk_return_to_start_check, self.afk_click_mouse_check, self.afk_scroll_mouse_check, self.afk_press_keys_check, self.afk_hotkey_edit] + key_widgets
        self.afk_enabled_check.toggled.connect(lambda checked: [w.setEnabled(checked) for w in all_afk_widgets])
        layout.addWidget(self.afk_box)

        # --- Start/Stop Button ---
        self.afk_toggle_button = QtWidgets.QPushButton()
        self.afk_toggle_button.clicked.connect(self.on_toggle_afk_worker)
        layout.addWidget(self.afk_toggle_button)
        
        # --- Info Box ---
        self.antiafk_info_box = QtWidgets.QGroupBox()
        self.antiafk_info_box.setCheckable(True)
        self.antiafk_info_box.setChecked(False)
        self.antiafk_info_label = QtWidgets.QLabel()
        self.antiafk_info_label.setWordWrap(True)
        self.antiafk_info_label.setVisible(False)
        info_layout_afk = QtWidgets.QVBoxLayout(self.antiafk_info_box)
        info_layout_afk.addWidget(self.antiafk_info_label)
        self.antiafk_info_box.toggled.connect(self.antiafk_info_label.setVisible)
        layout.addWidget(self.antiafk_info_box)

        layout.addStretch()
    
    # --- Settings Tab UI ---
    # Creates and arranges all widgets for the Settings tab.
    def _populate_settings_tab(self, tab):
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        self.settings_box = QtWidgets.QGroupBox()
        settings_layout = QtWidgets.QFormLayout(self.settings_box)

        # --- Language Selection ---
        self.language_combo = QtWidgets.QComboBox(); self.language_combo.addItems(["English", "Polski"])
        self.language_label = QtWidgets.QLabel()
        settings_layout.addRow(self.language_label, self.language_combo)
        self.language_combo.currentIndexChanged.connect(self._change_language)
        
        # --- Theme Selection ---
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_label = QtWidgets.QLabel()
        settings_layout.addRow(self.theme_label, self.theme_combo)
        self.theme_combo.currentIndexChanged.connect(self._change_theme)
        
        # --- Window Opacity ---
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.opacity_slider.setRange(20, 100)
        self.opacity_label = QtWidgets.QLabel()
        self.opacity_slider.valueChanged.connect(self._change_opacity)
        settings_layout.addRow(self.opacity_label, self.opacity_slider)
        
        # --- Global Start Delay ---
        self.start_delay_spin = QtWidgets.QDoubleSpinBox(); self.start_delay_spin.setRange(0.0, 60.0); self.start_delay_spin.setSingleStep(0.1); self.start_delay_spin.setSuffix(" s")
        self.start_delay_label = QtWidgets.QLabel()
        settings_layout.addRow(self.start_delay_label, self.start_delay_spin)
        
        # --- Limit to Window ---
        self.limit_window_check = QtWidgets.QCheckBox()
        self.window_title_edit = QtWidgets.QLineEdit()
        self.limit_window_check.toggled.connect(self.window_title_edit.setEnabled)
        settings_layout.addRow(self.limit_window_check)
        settings_layout.addRow(self.window_title_edit)

        # --- Always on Top ---
        self.always_on_top_checkbox = QtWidgets.QCheckBox()
        self.always_on_top_checkbox.toggled.connect(self._set_always_on_top)
        settings_layout.addRow(self.always_on_top_checkbox)

        # --- Accent Color Picker ---
        color_layout = QtWidgets.QHBoxLayout()
        self.color_swatch = QtWidgets.QLabel(); self.color_swatch.setFixedSize(24, 24)
        self.change_color_button = QtWidgets.QPushButton()
        self.change_color_button.clicked.connect(self._open_color_picker)
        color_layout.addWidget(self.color_swatch)
        color_layout.addWidget(self.change_color_button)
        self.accent_color_label = QtWidgets.QLabel()
        settings_layout.addRow(self.accent_color_label, color_layout)

        # --- Reset Settings Button ---
        self.reset_settings_button = QtWidgets.QPushButton()
        self.reset_settings_button.clicked.connect(self._reset_settings)
        self.reset_settings_label = QtWidgets.QLabel()
        settings_layout.addRow(self.reset_settings_label, self.reset_settings_button)
        layout.addWidget(self.settings_box)
        
        # --- Copyright Label ---
        self.copyright_label = QtWidgets.QLabel()
        self.copyright_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.copyright_label.setOpenExternalLinks(True)
        self.copyright_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.copyright_label)
    
    # --- UI Widget Factory Methods ---
    # These methods create reusable, complex groups of widgets to keep the main UI methods clean.

    # Creates a group box for either LMB or RMB settings (CPS, Jitter).
    def _create_mouse_button_group(self, title):
        box = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QFormLayout(box)
        cps_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); cps_slider.setRange(10, 300)
        cps_value_label = QtWidgets.QLabel("12.0"); cps_value_label.setMinimumWidth(40)
        cps_layout = QtWidgets.QHBoxLayout(); cps_layout.addWidget(cps_slider); cps_layout.addWidget(cps_value_label)
        cps_label_widget = QtWidgets.QLabel(self._tr('cps_label'))
        layout.addRow(cps_label_widget, cps_layout)
        variation_check = QtWidgets.QCheckBox(self._tr('variation_check'))
        jitter_spin = QtWidgets.QSpinBox(); jitter_spin.setRange(0, 100)
        layout.addRow(variation_check)
        jitter_label_widget = QtWidgets.QLabel(self._tr('jitter_label'))
        layout.addRow(jitter_label_widget, jitter_spin)
        variation_check.toggled.connect(jitter_spin.setEnabled)
        box.widgets = {'slider': cps_slider, 'label': cps_value_label, 'variation': variation_check, 'jitter': jitter_spin, 'cps_label': cps_label_widget, 'jitter_label': jitter_label_widget}
        cps_slider.valueChanged.connect(lambda val, label=cps_value_label: label.setText(f"{val/10.0:.1f}"))
        return box
    
    # Creates the radio buttons for choosing the click button in Toggle/Burst mode.
    def _create_button_choice_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget); layout.setContentsMargins(0,0,0,0)
        self.toggle_lmb_radio = QtWidgets.QRadioButton()
        self.toggle_rmb_radio = QtWidgets.QRadioButton()
        button_layout = QtWidgets.QHBoxLayout(); button_layout.addWidget(self.toggle_lmb_radio); button_layout.addWidget(self.toggle_rmb_radio)
        self.click_with_label = QtWidgets.QLabel()
        layout.addRow(self.click_with_label, button_layout)
        return widget

    # Creates the spin boxes for Burst mode specific settings.
    def _create_burst_options_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget); layout.setContentsMargins(0,0,0,0)
        self.burst_clicks_spin = QtWidgets.QSpinBox(); self.burst_clicks_spin.setRange(1, 100)
        self.burst_delay_spin = QtWidgets.QSpinBox(); self.burst_delay_spin.setRange(1, 1000); self.burst_delay_spin.setSuffix(" ms")
        self.burst_clicks_label = QtWidgets.QLabel()
        self.burst_delay_label = QtWidgets.QLabel()
        layout.addRow(self.burst_clicks_label, self.burst_clicks_spin)
        layout.addRow(self.burst_delay_label, self.burst_delay_spin)
        return widget

    # Creates the widgets for the "Click at fixed position" feature.
    def _create_fixed_pos_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget); layout.setContentsMargins(0,0,0,0)
        self.fixed_pos_check = QtWidgets.QCheckBox()
        pos_layout = QtWidgets.QHBoxLayout()
        self.fixed_pos_x_spin = QtWidgets.QSpinBox(); self.fixed_pos_x_spin.setRange(0, 10000)
        self.fixed_pos_y_spin = QtWidgets.QSpinBox(); self.fixed_pos_y_spin.setRange(0, 10000)
        self.capture_pos_button = QtWidgets.QPushButton()
        pos_layout.addWidget(QtWidgets.QLabel("X:")); pos_layout.addWidget(self.fixed_pos_x_spin)
        pos_layout.addWidget(QtWidgets.QLabel("Y:")); pos_layout.addWidget(self.fixed_pos_y_spin)
        pos_layout.addWidget(self.capture_pos_button)
        layout.addRow(self.fixed_pos_check)
        layout.addRow(pos_layout)
        self.fixed_pos_check.toggled.connect(lambda checked: [w.setEnabled(checked) for w in [self.fixed_pos_x_spin, self.fixed_pos_y_spin, self.capture_pos_button]])
        self.capture_pos_button.clicked.connect(self._capture_mouse_position)
        return widget

    # =====================================================================
    # Settings Persistence
    # =====================================================================

    # Connects all relevant UI widget signals to the save function.
    def _connect_signals_for_saving(self):
        autoclicker_widgets = [self.lmb_box.widgets['slider'], self.lmb_box.widgets['variation'], self.lmb_box.widgets['jitter'], self.rmb_box.widgets['slider'], self.rmb_box.widgets['variation'], self.rmb_box.widgets['jitter'], self.activation_key_edit, self.start_delay_spin, self.click_limit_spin, self.limit_window_check, self.window_title_edit, self.always_on_top_checkbox, self.hold_mode_radio, self.toggle_mode_radio, self.burst_mode_radio, self.toggle_lmb_radio, self.toggle_rmb_radio, self.burst_clicks_spin, self.burst_delay_spin, self.fixed_pos_check, self.fixed_pos_x_spin, self.fixed_pos_y_spin]
        antiafk_widgets = [self.afk_enabled_check, self.afk_min_interval_spin, self.afk_max_interval_spin, self.afk_move_mouse_check, self.afk_mouse_range_spin, self.afk_return_to_start_check, self.afk_click_mouse_check, self.afk_scroll_mouse_check, self.afk_press_keys_check, self.afk_key_w, self.afk_key_a, self.afk_key_s, self.afk_key_d, self.afk_key_space, self.afk_custom_keys_edit, self.afk_hotkey_edit]
        settings_widgets = [self.opacity_slider]
        all_widgets = autoclicker_widgets + antiafk_widgets + settings_widgets
        for widget in all_widgets:
            if isinstance(widget, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox, QtWidgets.QSlider)): widget.valueChanged.connect(self._save_settings_from_ui)
            elif isinstance(widget, (QtWidgets.QCheckBox, QtWidgets.QRadioButton)): widget.toggled.connect(self._save_settings_from_ui)
            elif isinstance(widget, QtWidgets.QLineEdit): widget.textChanged.connect(self._save_settings_from_ui)
    
    # Gathers all current settings from the UI and saves them to the JSON file.
    def _save_settings_from_ui(self, *args):
        settings = {
            "lmb_cps": self.lmb_box.widgets['slider'].value()/10.0, "lmb_variation": self.lmb_box.widgets['variation'].isChecked(), "lmb_jitter": self.lmb_box.widgets['jitter'].value(),
            "rmb_cps": self.rmb_box.widgets['slider'].value()/10.0, "rmb_variation": self.rmb_box.widgets['variation'].isChecked(), "rmb_jitter": self.rmb_box.widgets['jitter'].value(),
            "activation_mode": "toggle" if self.toggle_mode_radio.isChecked() else "burst" if self.burst_mode_radio.isChecked() else "hold",
            "toggle_button": "right" if self.toggle_rmb_radio.isChecked() else "left",
            "burst_clicks": self.burst_clicks_spin.value(), "burst_delay": self.burst_delay_spin.value(),
            "use_fixed_pos": self.fixed_pos_check.isChecked(), "fixed_x": self.fixed_pos_x_spin.value(), "fixed_y": self.fixed_pos_y_spin.value(),
            "click_limit": self.click_limit_spin.value(),
            "limit_window": self.limit_window_check.isChecked(), "window_title": self.window_title_edit.text(), "activation_key": self.activation_key_edit.text(),
            "start_delay": self.start_delay_spin.value(), "always_on_top": self.always_on_top_checkbox.isChecked(),
            "accent_color": self.accent_color.name(),
            "language": self.current_language,
            "theme": self.current_theme,
            "opacity": self.opacity_slider.value(),
            "afk_enabled": self.afk_enabled_check.isChecked(),
            "afk_min_interval": self.afk_min_interval_spin.value(), "afk_max_interval": self.afk_max_interval_spin.value(),
            "afk_move_mouse": self.afk_move_mouse_check.isChecked(), "afk_mouse_range": self.afk_mouse_range_spin.value(),
            "afk_return_to_start": self.afk_return_to_start_check.isChecked(),
            "afk_click_mouse": self.afk_click_mouse_check.isChecked(),
            "afk_scroll_mouse": self.afk_scroll_mouse_check.isChecked(),
            "afk_press_keys": self.afk_press_keys_check.isChecked(),
            "afk_key_w": self.afk_key_w.isChecked(), "afk_key_a": self.afk_key_a.isChecked(), "afk_key_s": self.afk_key_s.isChecked(), "afk_key_d": self.afk_key_d.isChecked(), "afk_key_space": self.afk_key_space.isChecked(),
            "afk_custom_keys": self.afk_custom_keys_edit.text(),
            "afk_hotkey": self.afk_hotkey_edit.text()
        }
        save_settings(settings)

    # Loads settings from the file and applies them to the UI widgets on startup.
    def _load_settings_to_ui(self):
        s = self.settings
        # --- Load AutoClicker Settings ---
        self.lmb_box.widgets['slider'].setValue(int(s.get("lmb_cps", 12.0) * 10)); self.lmb_box.widgets['variation'].setChecked(s.get("lmb_variation", True)); self.lmb_box.widgets['jitter'].setValue(s.get("lmb_jitter", 8))
        self.rmb_box.widgets['slider'].setValue(int(s.get("rmb_cps", 8.0) * 10)); self.rmb_box.widgets['variation'].setChecked(s.get("rmb_variation", True)); self.rmb_box.widgets['jitter'].setValue(s.get("rmb_jitter", 12))
        mode = s.get("activation_mode", "hold"); self.toggle_mode_radio.setChecked(mode=="toggle"); self.burst_mode_radio.setChecked(mode=="burst"); self.hold_mode_radio.setChecked(mode=="hold")
        self.toggle_rmb_radio.setChecked(s.get("toggle_button", "left") == "right"); self.toggle_lmb_radio.setChecked(s.get("toggle_button", "left") != "right")
        self.burst_clicks_spin.setValue(s.get("burst_clicks", 3)); self.burst_delay_spin.setValue(s.get("burst_delay", 50))
        self.fixed_pos_check.setChecked(s.get("use_fixed_pos", False)); self.fixed_pos_x_spin.setValue(s.get("fixed_x", 0)); self.fixed_pos_y_spin.setValue(s.get("fixed_y", 0))
        self.click_limit_spin.setValue(s.get("click_limit", 0))
        self.limit_window_check.setChecked(s.get("limit_window", False)); self.window_title_edit.setText(s.get("window_title", "Minecraft"))
        self.activation_key_edit.setText(s.get("activation_key", "r")); self.start_delay_spin.setValue(s.get("start_delay", 0.0)); self.always_on_top_checkbox.setChecked(s.get("always_on_top", False))
        
        # --- Load General Settings ---
        lang_index = 1 if s.get("language", "en") == "pl" else 0
        self.language_combo.setCurrentIndex(lang_index)
        theme_index = 1 if s.get("theme", "dark") == "light" else 0
        self.theme_combo.setCurrentIndex(theme_index)
        opacity = s.get("opacity", 100)
        self.opacity_slider.setValue(opacity)
        self.setWindowOpacity(opacity / 100.0)

        # --- Load Anti-AFK Settings ---
        self.afk_enabled_check.setChecked(s.get("afk_enabled", False)); self.afk_min_interval_spin.setValue(s.get("afk_min_interval", 10)); self.afk_max_interval_spin.setValue(s.get("afk_max_interval", 15))
        self.afk_move_mouse_check.setChecked(s.get("afk_move_mouse", True)); self.afk_mouse_range_spin.setValue(s.get("afk_mouse_range", 5))
        self.afk_return_to_start_check.setChecked(s.get("afk_return_to_start", False))
        self.afk_click_mouse_check.setChecked(s.get("afk_click_mouse", False))
        self.afk_scroll_mouse_check.setChecked(s.get("afk_scroll_mouse", False))
        self.afk_press_keys_check.setChecked(s.get("afk_press_keys", False))
        self.afk_key_w.setChecked(s.get("afk_key_w", False)); self.afk_key_a.setChecked(s.get("afk_key_a", False)); self.afk_key_s.setChecked(s.get("afk_key_s", False)); self.afk_key_d.setChecked(s.get("afk_key_d", False)); self.afk_key_space.setChecked(s.get("afk_key_space", False))
        self.afk_custom_keys_edit.setText(s.get("afk_custom_keys", ""))
        self.afk_hotkey_edit.setText(s.get("afk_hotkey", "p"))

        # --- Post-load UI adjustments ---
        self._on_mode_changed()
        self.lmb_box.widgets['jitter'].setEnabled(self.lmb_box.widgets['variation'].isChecked())
        self.rmb_box.widgets['jitter'].setEnabled(self.rmb_box.widgets['variation'].isChecked())
        self.window_title_edit.setEnabled(self.limit_window_check.isChecked())
        self._connect_signals_for_saving()

    # =====================================================================
    # Event Handling & Logic
    # =====================================================================
    
    # --- Listener Setup ---
    # Starts the global mouse and keyboard listeners from pynput.
    def _start_listeners(self):
        # Connect mode change signals to update the UI visibility.
        self.hold_mode_radio.toggled.connect(self._on_mode_changed)
        self.toggle_mode_radio.toggled.connect(self._on_mode_changed)
        self.burst_mode_radio.toggled.connect(self._on_mode_changed)
        # Start pynput listeners in separate threads.
        self.keyboard_listener = KeyboardListener(on_press=self._on_key_press); self.keyboard_listener.start()
        self.mouse_listener = MouseListener(on_click=self._on_mouse_click); self.mouse_listener.start()

    # --- Anti-AFK Worker Management ---
    # Toggles the Anti-AFK worker thread on or off.
    def on_toggle_afk_worker(self):
        # If worker is running, stop it.
        if self.afk_worker and self.afk_worker.isRunning():
            self.afk_worker.stop()
            return
        
        # Collect keys to be pressed from the UI.
        keys = []
        if self.afk_key_w.isChecked(): keys.append('w')
        if self.afk_key_a.isChecked(): keys.append('a')
        if self.afk_key_s.isChecked(): keys.append('s')
        if self.afk_key_d.isChecked(): keys.append('d')
        if self.afk_key_space.isChecked(): keys.append(Key.space)
        if self.afk_custom_keys_edit.text(): keys.extend(list(self.afk_custom_keys_edit.text().lower()))

        # Create config and start the worker.
        cfg = AntiAfkConfig(
            enabled=self.afk_enabled_check.isChecked(), 
            min_interval_s=self.afk_min_interval_spin.value(), max_interval_s=self.afk_max_interval_spin.value(), 
            move_mouse=self.afk_move_mouse_check.isChecked(), mouse_range=self.afk_mouse_range_spin.value(),
            return_to_start=self.afk_return_to_start_check.isChecked(),
            click_mouse=self.afk_click_mouse_check.isChecked(),
            scroll_mouse=self.afk_scroll_mouse_check.isChecked(),
            press_keys=self.afk_press_keys_check.isChecked(), keys_to_press=keys
        )
        self.afk_worker = AntiAfkWorker(cfg)
        self.afk_worker.sig_finished.connect(self.on_afk_worker_finished)
        self.afk_worker.start()

        # Update UI to reflect the active state.
        self.status_label.setText(self._tr('status_antiafk').format(color=self.accent_color.name()))
        self.afk_toggle_button.setText(self._tr('stop_antiafk_button'))
        self.tab_widget.setTabEnabled(0, False) # Disable other tabs
        self.tab_widget.setTabEnabled(2, False)

    # Slot that cleans up after the Anti-AFK worker has finished.
    def on_afk_worker_finished(self):
        self.status_label.setText(self._tr('status_stopped'))
        self.afk_toggle_button.setText(self._tr('start_antiafk_button'))
        self.afk_worker = None
        self.tab_widget.setTabEnabled(0, True) # Re-enable other tabs
        self.tab_widget.setTabEnabled(2, True)

    # --- AutoClicker Worker Management ---
    # Creates and starts the ClickWorker thread based on current UI settings.
    @QtCore.pyqtSlot(MouseButton)
    def on_start_clicking(self, button):
        if self.worker is not None: return
        is_burst = self.burst_mode_radio.isChecked()
        is_toggle = self.toggle_mode_radio.isChecked()
        cfg = ClickConfig(is_burst_mode=is_burst)
        
        # Load settings based on which mouse button is being used.
        if button == MouseButton.left: cfg.cps=self.lmb_box.widgets['slider'].value()/10.0; cfg.use_random_variation=self.lmb_box.widgets['variation'].isChecked(); cfg.jitter_ms=self.lmb_box.widgets['jitter'].value()
        else: cfg.cps=self.rmb_box.widgets['slider'].value()/10.0; cfg.use_random_variation=self.rmb_box.widgets['variation'].isChecked(); cfg.jitter_ms=self.rmb_box.widgets['jitter'].value()
        
        # Load global and mode-specific settings.
        cfg.click_button = button
        cfg.limit_to_window=self.limit_window_check.isChecked(); cfg.window_title=self.window_title_edit.text()
        cfg.start_delay_s=self.start_delay_spin.value()
        if is_toggle: cfg.click_limit=self.click_limit_spin.value(); cfg.use_fixed_position=self.fixed_pos_check.isChecked(); cfg.fixed_x=self.fixed_pos_x_spin.value(); cfg.fixed_y=self.fixed_pos_y_spin.value()
        if is_burst: cfg.burst_clicks=self.burst_clicks_spin.value(); cfg.burst_delay_ms=self.burst_delay_spin.value()
        
        # Create and start the worker.
        self.worker = ClickWorker(cfg, main_window=self)
        self.worker.sig_finished.connect(self.on_stop_clicking)
        self.worker.start()
        
        # Update UI state.
        self.status_label.setText(self._tr('status_clicking').format(color=self.accent_color.name()))
        self.tab_widget.setTabEnabled(1, False) # Disable Anti-AFK tab

    # Stops the ClickWorker thread and updates the UI.
    @QtCore.pyqtSlot()
    def on_stop_clicking(self):
        if self.worker:
            self.worker.stop(); self.worker.wait(200); self.worker = None
        
        # Update status based on the current mode.
        if self.hold_mode_radio.isChecked() and self.is_armed:
            self.status_label.setText(self._tr('status_armed'))
        else:
            self.status_label.setText(self._tr('status_stopped'))
            self.is_armed = False
        self.tab_widget.setTabEnabled(1, True) # Re-enable Anti-AFK tab

    # --- Global Input Handlers ---
    # Callback function for the pynput keyboard listener.
    def _on_key_press(self, key):
        # Emergency stop key.
        if key == Key.esc:
            if self.is_armed: self.is_armed = False
            if self.worker: self.worker.stop()
            if self.afk_worker: self.afk_worker.stop()
            return

        # Prevent hotkeys from firing when typing in an input field.
        if isinstance(QtWidgets.QApplication.focusWidget(), QtWidgets.QLineEdit):
            return

        try:
            pressed_char = key.char.lower()
        except AttributeError:
            return # It's a special key like Ctrl, not a character.

        # Check for Anti-AFK hotkey press.
        afk_hotkey = (self.afk_hotkey_edit.text() or "p").lower()
        if pressed_char == afk_hotkey:
            if not (self.worker and self.worker.isRunning()):
                self.sig_toggle_afk.emit() # <<< FIX 3: EMIT SIGNAL INSTEAD OF DIRECT CALL
            return

        # Check for AutoClicker hotkey press.
        activation_key = (self.activation_key_edit.text() or "r").lower()
        if pressed_char == activation_key:
            if not (self.afk_worker and self.afk_worker.isRunning()):
                self.sig_trigger_action.emit()
            return
    
    # Toggles the 'armed' state for Hold Mode.
    def on_toggle_armed(self):
        self.is_armed = not self.is_armed
        if self.is_armed: self.status_label.setText(self._tr('status_armed'))
        else:
            self.status_label.setText(self._tr('status_stopped'))
            if self.worker and self.worker.isRunning(): self.sig_stop_clicking.emit()
            
    # Main action handler triggered by the autoclicker hotkey.
    def on_trigger_action(self):
        if self.hold_mode_radio.isChecked(): self.on_toggle_armed()
        else: # Toggle or Burst mode
            if self.worker and self.worker.isRunning(): self.sig_stop_clicking.emit()
            else:
                button = MouseButton.right if self.toggle_rmb_radio.isChecked() else MouseButton.left
                self.sig_start_clicking.emit(button)
                
    # Callback function for the pynput mouse listener.
    def _on_mouse_click(self, x, y, button, pressed):
        if self.afk_worker and self.afk_worker.isRunning(): return
        if not self.hold_mode_radio.isChecked(): return
        
        # Ignore clicks generated by this program.
        if self.programmatic_click:
            if not pressed: self.programmatic_click = False
            return
            
        # Logic for Hold Mode: start/stop clicking when the physical mouse button is pressed/released.
        is_worker_running = self.worker is not None and self.worker.isRunning()
        if not self.is_armed: return
        if pressed and not is_worker_running:
            if button in [MouseButton.left, MouseButton.right]: self.sig_start_clicking.emit(button)
        elif not pressed and is_worker_running:
            self.sig_stop_clicking.emit()

    # --- UI Logic Handlers ---
    # Shows or hides UI elements based on the selected activation mode.
    def _on_mode_changed(self, *args):
        is_toggle = self.toggle_mode_radio.isChecked()
        is_burst = self.burst_mode_radio.isChecked()
        self.button_choice_widget.setVisible(is_toggle or is_burst)
        self.burst_options_widget.setVisible(is_burst)
        self.fixed_pos_widget.setVisible(is_toggle)
        self.click_limit_label.setVisible(is_toggle)
        self.click_limit_spin.setVisible(is_toggle)

    # Starts the countdown to capture the mouse's current screen position.
    def _capture_mouse_position(self):
        self.capture_pos_button.setEnabled(False)
        self.capture_countdown = 3
        self.capture_timer = QtCore.QTimer(self); self.capture_timer.timeout.connect(self._update_capture_countdown); self.capture_timer.start(1000)
        self._update_capture_countdown()
        
    # Updates the countdown timer on the capture button.
    def _update_capture_countdown(self):
        if self.capture_countdown > 0:
            self.capture_pos_button.setText(self._tr('capture_pos_button_countdown').format(count=self.capture_countdown))
            self.capture_countdown -= 1
        else:
            self.capture_timer.stop()
            self._perform_capture()
            
    # Actually captures and sets the mouse position in the UI.
    def _perform_capture(self):
        pos = MouseController().position
        self.fixed_pos_x_spin.setValue(pos[0]); self.fixed_pos_y_spin.setValue(pos[1])
        self.capture_pos_button.setText(self._tr('capture_pos_button')); self.capture_pos_button.setEnabled(True)
    
    # Toggles the "Always on Top" window flag.
    @QtCore.pyqtSlot(bool)
    def _set_always_on_top(self, checked):
        flags = self.windowFlags()
        if checked: self.setWindowFlags(flags | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        else: self.setWindowFlags(flags & ~QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    # Opens the system's color picker dialog to choose a new accent color.
    def _open_color_picker(self):
        color = QtWidgets.QColorDialog.getColor(self.accent_color, self, "Select Accent Color")
        if color.isValid():
            self.accent_color = color
            self._update_theme()
            self._save_settings_from_ui()

    # =====================================================================
    # Theming, Styling, and Internationalization
    # =====================================================================

    # --- Theme and Style Update ---
    # Applies the full visual style (dark/light theme, colors, CSS) to the application.
    def _update_theme(self):
        QtWidgets.QApplication.setStyle("Fusion")
        
        is_dark = self.current_theme == "dark"
        
        # Define color palettes for dark and light themes.
        if is_dark:
            base_color = QtGui.QColor(45, 45, 45); alt_color = QtGui.QColor(35, 35, 35); text_color = QtGui.QColor(220, 220, 220)
            border_color = QtGui.QColor("#3c3c3c"); button_color = QtGui.QColor("#555"); button_hover_color = QtGui.QColor("#666")
            button_pressed_color = QtGui.QColor("#444"); tab_bg_color = QtGui.QColor("#2d2d2d"); tab_selected_bg_color = QtGui.QColor("#454545")
        else:
            base_color = QtGui.QColor(240, 240, 240); alt_color = QtGui.QColor(255, 255, 255); text_color = QtGui.QColor(0, 0, 0)
            border_color = QtGui.QColor("#c0c0c0"); button_color = QtGui.QColor("#e1e1e1"); button_hover_color = QtGui.QColor("#f0f0f0")
            button_pressed_color = QtGui.QColor("#c8c8c8"); tab_bg_color = QtGui.QColor("#d4d4d4"); tab_selected_bg_color = QtGui.QColor("#f0f0f0")

        # Apply the chosen palette.
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, base_color); palette.setColor(QtGui.QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QtGui.QPalette.ColorRole.Base, alt_color); palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, base_color)
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, text_color); palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, text_color)
        palette.setColor(QtGui.QPalette.ColorRole.Text, text_color); palette.setColor(QtGui.QPalette.ColorRole.Button, base_color)
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, text_color); palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(255, 0, 0))
        palette.setColor(QtGui.QPalette.ColorRole.Link, self.accent_color); palette.setColor(QtGui.QPalette.ColorRole.Highlight, self.accent_color)
        palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(0, 0, 0))
        self.setPalette(palette)

        # Update accent color specific widgets.
        accent_color_str = self.accent_color.name()
        self.color_swatch.setStyleSheet(f"background-color: {accent_color_str}; border: 1px solid {border_color.name()}; border-radius: 4px;")
        self.copyright_label.setText(COPYRIGHT_TEXT.format(ACCENT_COLOR=accent_color_str))

        # Apply global stylesheet (CSS).
        self.setStyleSheet(f"""
            QWidget {{ font-size: 10pt; }}
            #mainWidget {{ padding: 5px; }}
            QGroupBox {{ font-weight: bold; border: 1px solid {border_color.name()}; border-radius: 8px; margin-top: 1ex; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; }}
            QGroupBox:checkable::indicator {{ width: 13px; height: 13px; }}
            QPushButton {{ background-color: {button_color.name()}; border: 1px solid {border_color.name()}; padding: 8px; border-radius: 6px; }}
            QPushButton:hover {{ background-color: {button_hover_color.name()}; }}
            QPushButton:pressed {{ background-color: {button_pressed_color.name()}; }}
            QTabWidget::pane {{ border-top: 2px solid {border_color.name()}; }}
            QTabBar::tab {{ background: {tab_bg_color.name()}; border: 1px solid {border_color.name()}; border-bottom: none; padding: 8px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px; }}
            QTabBar::tab:selected, QTabBar::tab:hover {{ background: {tab_selected_bg_color.name()}; color: {accent_color_str}; }}
            QSlider::groove:horizontal {{ border: 1px solid {border_color.name()}; background: {border_color.name()}; height: 4px; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {accent_color_str}; border: 1px solid {accent_color_str}; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }}
            QCheckBox::indicator, QRadioButton::indicator {{ border: 1px solid #777; width: 14px; height: 14px; border-radius: 8px; }}
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{ background-color: {accent_color_str}; border-color: {accent_color_str}; }}
        """)

    # --- Settings Change Handlers ---
    # Triggered when the language is changed in the settings.
    def _change_language(self, index):
        self.current_language = 'en' if index == 0 else 'pl'
        self._retranslate_ui()
        self._save_settings_from_ui()

    # Triggered when the theme is changed in the settings.
    def _change_theme(self, index):
        self.current_theme = 'dark' if index == 0 else 'light'
        self._update_theme()
        self._save_settings_from_ui()

    # Triggered when the opacity slider value is changed.
    def _change_opacity(self, value):
        self.setWindowOpacity(value / 100.0)
    
    # Resets all settings to their default values by deleting the settings file.
    def _reset_settings(self):
        reply = QtWidgets.QMessageBox.question(self, self._tr('reset_confirm_title'), self._tr('reset_confirm_text'),
                                               QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                                               QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if os.path.exists(SETTINGS_PATH):
                os.remove(SETTINGS_PATH)
            QtWidgets.QMessageBox.information(self, "Restart Required", "Settings have been reset. Please restart the application.")
            self.close()

    # --- UI Retranslation ---
    # Updates all text in the UI to the currently selected language.
    def _retranslate_ui(self):
        self.setWindowTitle(self._tr('window_title'))
        self.tab_widget.setTabText(0, self._tr('tab_autoclicker')); self.tab_widget.setTabIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tab_widget.setTabText(1, self._tr('tab_antiafk')); self.tab_widget.setTabIcon(1, self.style().standardIcon(QStyle.StandardPixmap.SP_DialogYesButton))
        self.tab_widget.setTabText(2, self._tr('tab_settings')); self.tab_widget.setTabIcon(2, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        
        # Update status label based on current state.
        if self.worker and self.worker.isRunning():
            self.status_label.setText(self._tr('status_clicking').format(color=self.accent_color.name()))
        elif self.afk_worker and self.afk_worker.isRunning():
            self.status_label.setText(self._tr('status_antiafk').format(color=self.accent_color.name()))
        elif self.hold_mode_radio.isChecked() and self.is_armed:
            self.status_label.setText(self._tr('status_armed'))
        else:
            self.status_label.setText(self._tr('status_stopped'))
            
        self.close_button.setText(self._tr('close_button'))

        # Retranslate Autoclicker Tab
        self.lmb_box.setTitle(self._tr('lmb_box_title')); self.lmb_box.widgets['cps_label'].setText(self._tr('cps_label')); self.lmb_box.widgets['variation'].setText(self._tr('variation_check')); self.lmb_box.widgets['jitter_label'].setText(self._tr('jitter_label'))
        self.rmb_box.setTitle(self._tr('rmb_box_title')); self.rmb_box.widgets['cps_label'].setText(self._tr('cps_label')); self.rmb_box.widgets['variation'].setText(self._tr('variation_check')); self.rmb_box.widgets['jitter_label'].setText(self._tr('jitter_label'))
        self.global_settings_box.setTitle(self._tr('global_settings_title'))
        self.activation_mode_label.setText(self._tr('activation_mode_label'))
        self.hold_mode_radio.setText(self._tr('hold_mode_radio')); self.toggle_mode_radio.setText(self._tr('toggle_mode_radio')); self.burst_mode_radio.setText(self._tr('burst_mode_radio'))
        self.click_with_label.setText(self._tr('click_with_label')); self.toggle_lmb_radio.setText(self._tr('left_button_radio')); self.toggle_rmb_radio.setText(self._tr('right_button_radio'))
        self.burst_clicks_label.setText(self._tr('burst_clicks_label')); self.burst_delay_label.setText(self._tr('burst_delay_label'))
        self.fixed_pos_check.setText(self._tr('fixed_pos_check')); self.capture_pos_button.setText(self._tr('capture_pos_button'))
        self.click_limit_label.setText(self._tr('click_limit_label'))
        self.hotkey_box.setTitle(self._tr('hotkeys_title'))
        self.activation_key_label.setText(self._tr('activation_key_label'))
        self.autoclicker_info_box.setTitle(self._tr('autoclicker_info_title'))
        self.autoclicker_info_label.setText(self._tr('autoclicker_info_text'))
        
        # Retranslate Anti-AFK Tab
        self.afk_box.setTitle(self._tr('antiafk_settings_title')); self.afk_enabled_check.setText(self._tr('enable_antiafk_check'))
        self.perform_actions_every_label.setText(self._tr('perform_actions_every_label')); self.interval_min_label.setText(self._tr('interval_min_label')); self.interval_max_label.setText(self._tr('interval_max_label'))
        self.afk_move_mouse_check.setText(self._tr('move_mouse_check')); self.movement_range_label.setText(self._tr('movement_range_label'))
        self.afk_return_to_start_check.setText(self._tr('return_to_start_check'))
        self.afk_click_mouse_check.setText(self._tr('click_mouse_check'))
        self.afk_scroll_mouse_check.setText(self._tr('scroll_mouse_check'))
        self.afk_press_keys_check.setText(self._tr('press_keys_check')); self.presets_label.setText(self._tr('presets_label'))
        self.custom_keys_label.setText(self._tr('custom_keys_label')); self.afk_custom_keys_edit.setPlaceholderText(self._tr('custom_keys_placeholder'))
        self.afk_toggle_button.setText(self._tr('start_antiafk_button'))
        self.afk_hotkey_label.setText(self._tr('antiafk_hotkey_label'))
        self.antiafk_info_box.setTitle(self._tr('antiafk_info_title'))
        self.antiafk_info_label.setText(self._tr('antiafk_info_text'))
        
        # Retranslate Settings Tab
        self.settings_box.setTitle(self._tr('app_settings_title'))
        self.language_label.setText(self._tr('language_label'))
        self.theme_label.setText(self._tr('theme_label')); self.theme_combo.setItemText(0, self._tr('theme_dark')); self.theme_combo.setItemText(1, self._tr('theme_light'))
        self.opacity_label.setText(self._tr('opacity_label'))
        self.start_delay_label.setText(self._tr('start_delay_label'))
        self.limit_window_check.setText(self._tr('limit_window_check')); self.window_title_edit.setPlaceholderText(self._tr('window_title_placeholder'))
        self.always_on_top_checkbox.setText(self._tr('always_on_top_check'))
        self.accent_color_label.setText(self._tr('accent_color_label')); self.change_color_button.setText(self._tr('change_color_button'))
        self.reset_settings_label.setText(self._tr('reset_settings_label'))
        self.reset_settings_button.setText(self._tr('reset_settings_button'))

    # =====================================================================
    # Application Lifecycle
    # =====================================================================

    # Handles the window closing event to ensure all threads are stopped safely.
    def closeEvent(self, event):
        if self.worker: self.worker.stop()
        if self.afk_worker: self.afk_worker.stop()
        self.mouse_listener.stop(); self.keyboard_listener.stop()
        event.accept()
        
    # A simple check to ensure the copyright notice has not been removed.
    def _verify_integrity(self):
        if "Piotrunius" not in self.copyright_label.text():
            msg_box = QtWidgets.QMessageBox(self); msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg_box.setText("Application Integrity Error."); msg_box.setInformativeText("The author's attribution has been modified or removed. The application will now close.")
            msg_box.setWindowTitle("Error"); msg_box.exec(); sys.exit(1)

# ==================================================================================================
#                                         APPLICATION ENTRY POINT
# ==================================================================================================

# --- Main Function ---
# Initializes the QApplication and the MainWindow, then starts the event loop.
def main():
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())

# --- Script Execution ---
# Ensures the main function is called only when the script is executed directly.
if __name__ == "__main__":
    main()
