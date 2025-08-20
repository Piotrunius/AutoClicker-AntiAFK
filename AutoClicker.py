# ==================================================================================================
#                                         IMPORTS
# ==================================================================================================
import json
import math
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
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QStyle, QMenu, QScrollArea, QPlainTextEdit
from pynput.mouse import Controller as MouseController, Button as MouseButton, Listener as MouseListener
from pynput.keyboard import Controller as KeyboardController, Listener as KeyboardListener, Key, KeyCode

# ==================================================================================================
#                                 CONSTANTS & CONFIGURATION
# ==================================================================================================

# --- Translation System ---
# A dictionary holding all UI text for both English and Polish languages.
TRANSLATIONS = {
    'en': {
        # General
        'window_title': "Piotrunius AutoClicker & More",
        'close_button': "Close",
        'module_disabled_info': "<h1>Module Disabled</h1><p>Enable it in the <b>Settings</b> tab under <b>Module Activation</b>.</p>",
        # Tabs
        'tab_autoclicker': "AutoClicker",
        'tab_antiafk': "Anti-AFK",
        'tab_logs': "Logs",
        'tab_settings': "Settings",
        # Logs Tab
        'clear_logs_button': "Clear Logs",
        # Status
        'status_stopped': "Status: STOPPED",
        'status_armed': "Status: <font color='orange'>ARMED</font>",
        'status_clicking': "Status: <font color='{color}'>CLICKING</font>",
        'status_antiafk': "Status: <font color='{color}'>ANTI-AFK ACTIVE</font>",
        'status_playback': "Status: <font color='{color}'>PLAYBACK ACTIVE</font>",
        'status_recording': "Status: <font color='red'>RECORDING...</font>",
        # Autoclicker Tab
        'lmb_box_title': "Left Mouse Button (LMB)",
        'rmb_box_title': "Right Mouse Button (RMB)",
        'cps_label': "CPS:",
        'click_type_label': "Click Type:",
        'click_type_single': "Single",
        'click_type_double': "Double",
        'click_type_triple': "Triple",
        'variation_check': "Random Variation",
        'jitter_label': "Jitter (± ms):",
        'global_settings_title': "AutoClicker Mode Settings",
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
        'activation_key_placeholder': "e.g. r",
        'record_playback_title': "Record & Playback",
        'record_button': "Record Sequence",
        'stop_record_button': "Stop Recording (ESC)",
        'playback_button': "Play Sequence",
        'playback_reps_label': "Repetitions (0=inf):",
        'recorded_clicks_label': "Recorded Clicks: {count}",
        'autoclicker_summary_title': "Action Summary (Click to Expand)",
        'autoclicker_info_title': "💡 How to Use (Click to Expand)",
        'autoclicker_info_text': (
            "<b><u>Activation</u></b><br>"
            "• First, enable the module in <b>Settings -> Module Activation</b>. The hotkey <b><font color='{accent_color}'>{activation_key}</font></b> will only work if this is enabled.<br>"
            "• <b>Emergency STOP:</b> Press <b><font color='{accent_color}'>{emergency_key}</font></b> at any time to immediately stop all actions.<br><br>"
            "<b><u>Click Settings (per button)</u></b><br>"
            "• <b>CPS (Clicks Per Second):</b> Sets the base speed of clicking.<br>"
            "• <b>Click Type:</b> Choose between single, double, or triple clicks at each interval.<br>"
            "• <b>Random Variation:</b> Makes clicks less robotic. <b>Jitter</b> adds a small, random delay (in milliseconds) between clicks.<br><br>"
            "<b><u>Activation Modes</u></b><br>"
            "• <b>Hold Mode:</b> Press <b><font color='{accent_color}'>{activation_key}</font></b> to ARM the clicker. Then, hold your physical mouse button to start clicking. Releasing stops it.<br>"
            "• <b>Toggle Mode:</b> Press <b><font color='{accent_color}'>{activation_key}</font></b> once to start continuous clicking, and press it again to stop.<br>"
            "• <b>Burst Mode:</b> Press <b><font color='{accent_color}'>{activation_key}</font></b> to perform a quick burst of a set number of clicks.<br><br>"
            "<b><u>Record & Playback</u></b><br>"
            "• Click 'Record' to capture a sequence of clicks, including their position and the delay between them. Press <b><font color='{accent_color}'>{emergency_key}</font></b> to stop recording. Then, use 'Play' to repeat the recorded actions."
        ),
        # Anti-AFK Tab
        'antiafk_actions_title': "Actions & Interval", # ### ZMIANA ###
        'mouse_movement_title': "Mouse Movement Settings", # ### ZMIANA ###
        'key_press_title': "Key Press Settings", # ### ZMIANA ###
        'perform_actions_every_label': "Perform actions every:",
        'interval_min_label': "Min:",
        'interval_max_label': "Max:",
        'move_mouse_check': "Slight mouse movement",
        'use_human_moves_check': "Use human-like movements",
        'human_move_mode_label': "Movement Mode:",
        'human_move_mode_bezier1': "Simple Bezier Curve",
        'human_move_mode_bezier2': "Complex Bezier Curve",
        'human_move_mode_gravity': "Gravity Simulation",
        'human_move_duration_label': "Movement Duration (s):",
        'movement_range_label': "Movement range (± px):",
        'return_to_start_check': "Return to start position",
        'click_mouse_check': "Random mouse click",
        'scroll_mouse_check': "Random mouse scroll",
        'press_keys_check': "Press keys",
        'presets_label': "Presets:",
        'custom_keys_label': "Custom keys:",
        'custom_keys_placeholder': "e.g. efq",
        'antiafk_hotkey_label': "Anti-AFK Hotkey:",
        'afk_hotkey_placeholder': "e.g. p",
        'antiafk_summary_title': "Action Summary (Click to Expand)",
        'antiafk_info_title': "💡 How to Use (Click to Expand)",
        'antiafk_info_text': (
            "<b><u>Activation</u></b><br>"
            "• First, enable the module in <b>Settings -> Module Activation</b>. The hotkey <b><font color='{accent_color}'>{afk_hotkey}</font></b> will only work if this is enabled.<br>"
            "• Use the <b><font color='{accent_color}'>{afk_hotkey}</font></b> key to start or stop the Anti-AFK actions.<br>"
            "• <b>Emergency STOP:</b> Press <b><font color='{accent_color}'>{emergency_key}</font></b> at any time to immediately stop all actions.<br><br>"
            "<b><u>Action Settings</u></b><br>"
            "• <b>Perform actions every:</b> Sets a random time range (Min-Max seconds) to wait before performing the next set of actions.<br>"
            "• <b>Slight mouse movement:</b> Moves the cursor by a random amount within the specified <b>Movement range</b>.<br>"
            "  - <b>Use human-like movements:</b> Simulates a more natural, curved mouse path instead of an instant jump.<br>"
            "• <b>Return to start position:</b> After moving, the cursor will return to where it was before the action.<br>"
            "• <b>Random mouse click/scroll:</b> Performs a random click (left or right) or scrolls the mouse wheel up or down.<br>"
            "• <b>Press keys:</b> Presses random keys from the selected presets (WASD, Space) or your own custom keys."
        ),
        # Settings Tab
        'module_activation_title': "Module Activation",
        'enable_autoclicker_check': "Enable AutoClicker Module",
        'enable_antiafk_check': "Enable Anti-AFK Module",
        'app_settings_title': "Application Settings",
        'language_label': "Language:",
        'theme_label': "Theme:",
        'theme_dark': "Dark",
        'theme_light': "Light",
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
        'emergency_key_label': "Emergency STOP Key:",
        'emergency_key_placeholder': "e.g. esc, f12",
        'profiles_title': "Profiles",
        'profile_name_label': "Profile Name:",
        'save_profile_button': "Save as New",
        'delete_profile_button': "Delete Selected",
        'import_profile_button': "Import",
        'export_profile_button': "Export",
        'profile_import_success_title': "Import Successful",
        'profile_import_success_text': "Profile '{name}' has been successfully imported.",
        'profile_import_error_title': "Import Error",
        'profile_import_error_text': "The selected file is not a valid profile file.",
    },
    'pl': {
        # General
        'window_title': "Piotrunius AutoClicker & Więcej",
        'close_button': "Zamknij",
        'module_disabled_info': "<h1>Moduł Wyłączony</h1><p>Włącz go w zakładce <b>Ustawienia</b> w sekcji <b>Aktywacja Modułów</b>.</p>",
        # Tabs
        'tab_autoclicker': "AutoClicker",
        'tab_antiafk': "Anty-AFK",
        'tab_logs': "Dziennik",
        'tab_settings': "Ustawienia",
        # Logs Tab
        'clear_logs_button': "Wyczyść Dziennik",
        # Status
        'status_stopped': "Status: ZATRZYMANY",
        'status_armed': "Status: <font color='orange'>UZBROJONY</font>",
        'status_clicking': "Status: <font color='{color}'>KLIKANIE</font>",
        'status_antiafk': "Status: <font color='{color}'>ANTY-AFK AKTYWNY</font>",
        'status_playback': "Status: <font color='{color}'>ODTWARZANIE</font>",
        'status_recording': "Status: <font color='red'>NAGRYWANIE...</font>",
        # Autoclicker Tab
        'lmb_box_title': "Lewy Przycisk Myszy (LPM)",
        'rmb_box_title': "Prawy Przycisk Myszy (PPM)",
        'cps_label': "CPS:",
        'click_type_label': "Typ Kliknięcia:",
        'click_type_single': "Pojedyncze",
        'click_type_double': "Podwójne",
        'click_type_triple': "Potrójne",
        'variation_check': "Losowa Zmienność",
        'jitter_label': "Zmienność (± ms):",
        'global_settings_title': "Ustawienia Trybu AutoClickera",
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
        'activation_key_placeholder': "np. r",
        'record_playback_title': "Nagrywanie i Odtwarzanie",
        'record_button': "Nagraj Sekwencję",
        'stop_record_button': "Zatrzymaj Nagrywanie (ESC)",
        'playback_button': "Odtwórz Sekwencję",
        'playback_reps_label': "Powtórzenia (0=niesk.):",
        'recorded_clicks_label': "Nagrane kliknięcia: {count}",
        'autoclicker_summary_title': "Podsumowanie Akcji (Kliknij, by rozwinąć)",
        'autoclicker_info_title': "💡 Jak Używać (Kliknij, by rozwinąć)",
        'autoclicker_info_text': (
            "<b><u>Aktywacja</u></b><br>"
            "• Najpierw włącz moduł w <b>Ustawienia -> Aktywacja Modułów</b>. Skrót klawiszowy <b><font color='{accent_color}'>{activation_key}</font></b> zadziała tylko wtedy.<br>"
            "• <b>STOP Awaryjny:</b> Naciśnij <b><font color='{accent_color}'>{emergency_key}</font></b> w dowolnym momencie, aby natychmiast zatrzymać wszystkie akcje.<br><br>"
            "<b><u>Ustawienia Kliknięć (dla każdego przycisku)</u></b><br>"
            "• <b>CPS (Kliknięcia na Sekundę):</b> Ustawia bazową prędkość klikania.<br>"
            "• <b>Typ Kliknięcia:</b> Wybierz pomiędzy pojedynczym, podwójnym lub potrójnym kliknięciem w każdym interwale.<br>"
            "• <b>Losowa Zmienność:</b> Sprawia, że kliknięcia są mniej mechaniczne. <b>Zmienność</b> dodaje małe, losowe opóźnienie (w milisekundach) między kliknięciami.<br><br>"
            "<b><u>Tryby Aktywacji</u></b><br>"
            "• <b>Tryb Przytrzymania:</b> Naciśnij <b><font color='{accent_color}'>{activation_key}</font></b>, aby UZBROIĆ clicker. Następnie przytrzymaj fizyczny przycisk myszy, aby zacząć klikać. Puszczenie go zatrzymuje klikanie.<br>"
            "• <b>Tryb Przełączania:</b> Naciśnij <b><font color='{accent_color}'>{activation_key}</font></b> raz, aby włączyć ciągłe klikanie, i naciśnij go ponownie, aby wyłączyć.<br>"
            "• <b>Tryb Serii:</b> Naciśnij <b><font color='{accent_color}'>{activation_key}</font></b>, aby wykonać szybką serię określonej liczby kliknięć.<br><br>"
            "<b><u>Nagrywanie i Odtwarzanie</u></b><br>"
            "• Kliknij 'Nagraj', by zapisać sekwencję kliknięć, ich pozycję i opóźnienia między nimi. Naciśnij <b><font color='{accent_color}'>{emergency_key}</font></b>, aby zakończyć nagrywanie. Następnie użyj przycisku 'Odtwórz', aby powtórzyć nagrane akcje."
        ),
        # Anti-AFK Tab
        'antiafk_actions_title': "Akcje i Interwał", # ### ZMIANA ###
        'mouse_movement_title': "Ustawienia Ruchu Myszy", # ### ZMIANA ###
        'key_press_title': "Ustawienia Wciskania Klawiszy", # ### ZMIANA ###
        'perform_actions_every_label': "Wykonuj akcje co:",
        'interval_min_label': "Min:",
        'interval_max_label': "Max:",
        'move_mouse_check': "Lekki ruch myszą",
        'use_human_moves_check': "Użyj ludzkich ruchów",
        'human_move_mode_label': "Tryb ruchu:",
        'human_move_mode_bezier1': "Krzywa Beziera (Prosta)",
        'human_move_mode_bezier2': "Krzywa Beziera (Złożona)",
        'human_move_mode_gravity': "Symulacja Grawitacji",
        'human_move_duration_label': "Czas trwania ruchu (s):",
        'movement_range_label': "Zasięg ruchu (± px):",
        'return_to_start_check': "Powrót do pozycji startowej",
        'click_mouse_check': "Losowe kliknięcie myszą",
        'scroll_mouse_check': "Losowe przewijanie rolką",
        'press_keys_check': "Wciskaj klawisze",
        'presets_label': "Predefiniowane:",
        'custom_keys_label': "Własne klawisze:",
        'custom_keys_placeholder': "np. efq",
        'antiafk_hotkey_label': "Klawisz Anty-AFK:",
        'afk_hotkey_placeholder': "np. p",
        'antiafk_summary_title': "Podsumowanie Akcji (Kliknij, by rozwinąć)",
        'antiafk_info_title': "💡 Jak Używać (Kliknij, by rozwinąć)",
        'antiafk_info_text': (
            "<b><u>Aktywacja</u></b><br>"
            "• Najpierw włącz moduł w <b>Ustawienia -> Aktywacja Modułów</b>. Skrót klawiszowy <b><font color='{accent_color}'>{afk_hotkey}</font></b> zadziała tylko wtedy.<br>"
            "• Użyj klawisza <b><font color='{accent_color}'>{afk_hotkey}</font></b>, aby włączyć lub wyłączyć akcje Anty-AFK.<br>"
            "• <b>STOP Awaryjny:</b> Naciśnij <b><font color='{accent_color}'>{emergency_key}</font></b> w dowolnym momencie, aby natychmiast zatrzymać wszystkie akcje.<br><br>"
            "<b><u>Ustawienia Akcji</u></b><br>"
            "• <b>Wykonuj akcje co:</b> Ustawia losowy przedział czasowy (Min-Max sekund), po którym wykonany zostanie kolejny zestaw akcji.<br>"
            "• <b>Lekki ruch myszą:</b> Przesuwa kursor o losową odległość w ramach podanego <b>Zasięgu ruchu</b>.<br>"
            "  - <b>Użyj ludzkich ruchów:</b> Symuluje bardziej naturalną, zakrzywioną ścieżkę myszy zamiast natychmiastowego skoku.<br>"
            "• <b>Powrót do pozycji startowej:</b> Po wykonaniu ruchu, kursor wróci na swoje pierwotne miejsce.<br>"
            "• <b>Losowe kliknięcie/przewinięcie:</b> Wykonuje losowe kliknięcie (lewe lub prawe) lub przewija kółkiem myszy w górę lub w dół.<br>"
            "• <b>Wciskaj klawisze:</b> Wciska losowe klawisze z wybranych presetów (WASD, Spacja) lub Twoich własnych."
        ),
        # Settings Tab
        'module_activation_title': "Aktywacja Modułów",
        'enable_autoclicker_check': "Włącz Moduł AutoClickera",
        'enable_antiafk_check': "Włącz Moduł Anty-AFK",
        'app_settings_title': "Ustawienia Aplikacji",
        'language_label': "Język:",
        'theme_label': "Motyw:",
        'theme_dark': "Ciemny",
        'theme_light': "Jasny",
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
        'emergency_key_label': "Klawisz STOPu Awaryjnego:",
        'emergency_key_placeholder': "np. esc, f12",
        'profiles_title': "Profile",
        'profile_name_label': "Nazwa profilu:",
        'save_profile_button': "Zapisz jako nowy",
        'delete_profile_button': "Usuń zaznaczony",
        'import_profile_button': "Importuj",
        'export_profile_button': "Eksportuj",
        'profile_import_success_title': "Import Udany",
        'profile_import_success_text': "Profil '{name}' został pomyślnie zaimportowany.",
        'profile_import_error_title': "Błąd Importu",
        'profile_import_error_text': "Wybrany plik nie jest prawidłowym plikiem profilu.",
    }
}


# --- Global Constants ---
# Defines the path for the settings file, the copyright text, and the default UI color.
SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".autoclicker_piotrunius.json")
COPYRIGHT_TEXT = f'Made with love by <a href="https://e-z.bio/piotrunius" style="color: {{ACCENT_COLOR}}; text-decoration:none;">Piotrunius</a> © {time.strftime("%Y")}'
DEFAULT_ACCENT_COLOR = "#42a5f5"

# ==================================================================================================
#                                 SETTINGS HELPER FUNCTIONS
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
    click_type: int = 1 # 1=single, 2=double, 3=triple
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
    use_human_like_move: bool = False
    human_move_mode_index: int = 0 # 0=bezier1, 1=bezier2, 2=gravity
    human_move_duration: float = 0.3

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

        # Check for click type (single, double, triple)
        for i in range(self.cfg.click_type):
            self.mouse.click(self.cfg.click_button, 1)
            if i < self.cfg.click_type - 1:
                self._sleep_interruptible(0.05) # Short delay between multi-clicks


    # A sleep implementation that can be interrupted by the stop event.
    def _sleep_interruptible(self, seconds: float):
        end_time = time.perf_counter() + seconds
        while time.perf_counter() < end_time:
            if self._stop_event.is_set(): break
            time.sleep(0.001)

# --- PlaybackWorker Class ---
# This QThread plays back a recorded sequence of mouse clicks.
class PlaybackWorker(QtCore.QThread):
    sig_finished = QtCore.pyqtSignal()
    sig_update_status = QtCore.pyqtSignal(str)

    def __init__(self, sequence: list, repetitions: int, parent=None):
        super().__init__(parent)
        self.sequence = sequence
        self.repetitions = repetitions
        self._stop_event = threading.Event()
        self.mouse = MouseController()

    def stop(self):
        self._stop_event.set()

    def run(self):
        if not self.sequence:
            self.sig_finished.emit()
            return

        rep_count = 0
        while not self._stop_event.is_set():
            for event in self.sequence:
                if self._stop_event.is_set(): break

                # Wait for the recorded delay
                delay = event.get('delay', 0.1)
                self._sleep_interruptible(delay)
                if self._stop_event.is_set(): break

                # Perform the click
                self.mouse.position = (event['x'], event['y'])
                self._sleep_interruptible(0.01) # Small delay to ensure position is set
                button = MouseButton.left if event['button'] == 'left' else MouseButton.right
                self.mouse.click(button, 1)

            rep_count += 1
            if self.repetitions > 0 and rep_count >= self.repetitions:
                break

        self.sig_finished.emit()

    def _sleep_interruptible(self, seconds: float):
        self._stop_event.wait(seconds)


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

    def _perform_human_like_move(self, start_pos, end_pos):
        """Moves the mouse from start_pos to end_pos using a selected algorithm."""
        duration = self.cfg.human_move_duration
        steps = int(duration / 0.01) # Number of steps based on 10ms interval
        if steps == 0: return

        # Bezier curve control points
        c1x, c1y, c2x, c2y = 0, 0, 0, 0
        if self.cfg.human_move_mode_index in [0, 1]: # 0=bezier1, 1=bezier2
            c1x = start_pos[0] + random.uniform(-50, 50)
            c1y = start_pos[1] + random.uniform(-50, 50)
            if self.cfg.human_move_mode_index == 1: # 1=bezier2
                c2x = end_pos[0] + random.uniform(-50, 50)
                c2y = end_pos[1] + random.uniform(-50, 50)

        for i in range(steps + 1):
            if self._stop_event.is_set(): return
            t = i / steps
            x, y = end_pos[0], end_pos[1] # Default to end position

            if self.cfg.human_move_mode_index == 2: # 2=gravity
                # Ease-in-quad for a gravity effect
                ease_t = t * t
                x = start_pos[0] + (end_pos[0] - start_pos[0]) * ease_t
                y = start_pos[1] + (end_pos[1] - start_pos[1]) * ease_t
            elif self.cfg.human_move_mode_index == 0: # 0=bezier1
                # Quadratic Bezier
                x = (1-t)**2 * start_pos[0] + 2*(1-t)*t*c1x + t**2 * end_pos[0]
                y = (1-t)**2 * start_pos[1] + 2*(1-t)*t*c1y + t**2 * end_pos[1]
            elif self.cfg.human_move_mode_index == 1: # 1=bezier2
                # Cubic Bezier
                x = (1-t)**3*start_pos[0] + 3*(1-t)**2*t*c1x + 3*(1-t)*t**2*c2x + t**3*end_pos[0]
                y = (1-t)**3*start_pos[1] + 3*(1-t)**2*t*c1y + 3*(1-t)*t**2*c2y + t**3*end_pos[1]

            self.mouse.position = (int(x), int(y))
            time.sleep(0.01)

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

                if self.cfg.use_human_like_move:
                    end_pos = (start_pos[0] + offset_x, start_pos[1] + offset_y)
                    self._perform_human_like_move(start_pos, end_pos)
                else:
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
                if self.cfg.use_human_like_move:
                    current_pos = self.mouse.position
                    self._perform_human_like_move(current_pos, start_pos)
                else:
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
    sig_start_clicking = QtCore.pyqtSignal(MouseButton)
    sig_stop_clicking = QtCore.pyqtSignal()
    sig_toggle_armed = QtCore.pyqtSignal()
    sig_trigger_action = QtCore.pyqtSignal()
    sig_toggle_afk = QtCore.pyqtSignal()
    sig_log_message = QtCore.pyqtSignal(str)

    # --- Initialization ---
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 780)

        # --- State Variables ---
        self.worker: ClickWorker | None = None
        self.afk_worker: AntiAfkWorker | None = None
        self.playback_worker: PlaybackWorker | None = None
        self.is_armed = False
        self.programmatic_click = False
        self.capture_timer = None
        self.capture_countdown = 0
        self.is_recording = False
        self.recorded_sequence = []
        self.last_click_time = 0

        # --- Load Settings & Theming ---
        self.settings = load_settings()
        self.accent_color = QtGui.QColor(self.settings.get("accent_color", DEFAULT_ACCENT_COLOR))
        self.current_language = self.settings.get("language", "en")
        self.current_theme = self.settings.get("theme", "dark")

        # --- UI and Listener Setup ---
        self._build_ui()
        self._load_profiles_to_ui()
        self._load_active_profile_to_ui()
        self._update_theme()
        self._retranslate_ui()
        self._verify_integrity()

        # --- Connect Signals to Slots ---
        self.sig_start_clicking.connect(self.on_start_clicking)
        self.sig_stop_clicking.connect(self.on_stop_clicking)
        self.sig_toggle_armed.connect(self.on_toggle_armed)
        self.sig_trigger_action.connect(self.on_trigger_action)
        self.sig_toggle_afk.connect(self.on_toggle_afk_worker)
        self.sig_log_message.connect(self._on_log_message)

        self._start_listeners()
        self.sig_log_message.emit("Application started.")

    # --- Translation Helper ---
    def _tr(self, key):
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS['en']).get(key, f"_{key}_")

    # =====================================================================
    # UI Building
    # =====================================================================

    # --- Main UI Structure ---
    def _build_ui(self):
        main_widget = QtWidgets.QWidget()
        main_widget.setObjectName("mainWidget")
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        self.tab_widget = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tab_widget)

        autoclicker_tab = QtWidgets.QWidget()
        antiafk_tab = QtWidgets.QWidget()
        log_tab = QtWidgets.QWidget()
        settings_tab = QtWidgets.QWidget()

        self.tab_widget.addTab(autoclicker_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon), "")
        self.tab_widget.addTab(antiafk_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_DialogYesButton), "")
        self.tab_widget.addTab(log_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView), "")
        self.tab_widget.addTab(settings_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "")

        # Populate each tab with its specific widgets.
        self._populate_autoclicker_tab(autoclicker_tab)
        self._populate_antiafk_tab(antiafk_tab)
        self._populate_log_tab(log_tab)
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
    def _populate_autoclicker_tab(self, tab):
        layout = QtWidgets.QVBoxLayout(tab)

        self.autoclicker_controls_widget = QtWidgets.QWidget()
        controls_layout = QtWidgets.QVBoxLayout(self.autoclicker_controls_widget)
        controls_layout.setContentsMargins(15, 15, 15, 15)

        mouse_buttons_layout = QtWidgets.QHBoxLayout()
        self.lmb_box = self._create_mouse_button_group(self._tr('lmb_box_title'))
        self.rmb_box = self._create_mouse_button_group(self._tr('rmb_box_title'))
        mouse_buttons_layout.addWidget(self.lmb_box)
        mouse_buttons_layout.addWidget(self.rmb_box)
        controls_layout.addLayout(mouse_buttons_layout)

        self.global_settings_box = QtWidgets.QGroupBox()
        global_settings_layout = QtWidgets.QFormLayout(self.global_settings_box)

        self.hold_mode_radio = QtWidgets.QRadioButton()
        self.toggle_mode_radio = QtWidgets.QRadioButton()
        self.burst_mode_radio = QtWidgets.QRadioButton()
        mode_layout = QtWidgets.QHBoxLayout()
        mode_layout.addWidget(self.hold_mode_radio); mode_layout.addWidget(self.toggle_mode_radio); mode_layout.addWidget(self.burst_mode_radio)
        self.activation_mode_label = QtWidgets.QLabel()
        global_settings_layout.addRow(self.activation_mode_label, mode_layout)

        self.button_choice_widget = self._create_button_choice_widget()
        global_settings_layout.addRow(self.button_choice_widget)
        self.burst_options_widget = self._create_burst_options_widget()
        global_settings_layout.addRow(self.burst_options_widget)
        self.fixed_pos_widget = self._create_fixed_pos_widget()
        global_settings_layout.addRow(self.fixed_pos_widget)

        self.click_limit_spin = QtWidgets.QSpinBox(); self.click_limit_spin.setRange(0, 1000000)
        self.click_limit_label = QtWidgets.QLabel()
        global_settings_layout.addRow(self.click_limit_label, self.click_limit_spin)

        controls_layout.addWidget(self.global_settings_box)

        self.record_playback_box = QtWidgets.QGroupBox()
        record_layout = QtWidgets.QFormLayout(self.record_playback_box)
        self.record_button = QtWidgets.QPushButton()
        self.record_button.clicked.connect(self._toggle_recording)
        self.playback_button = QtWidgets.QPushButton()
        self.playback_button.clicked.connect(self._toggle_playback)
        self.recorded_clicks_count_label = QtWidgets.QLabel()
        self.playback_reps_spin = QtWidgets.QSpinBox(); self.playback_reps_spin.setRange(0, 1000)
        self.playback_reps_label = QtWidgets.QLabel()

        record_buttons_layout = QtWidgets.QHBoxLayout()
        record_buttons_layout.addWidget(self.record_button)
        record_buttons_layout.addWidget(self.playback_button)
        record_layout.addRow(record_buttons_layout)
        record_layout.addRow(self.recorded_clicks_count_label)
        record_layout.addRow(self.playback_reps_label, self.playback_reps_spin)
        controls_layout.addWidget(self.record_playback_box)

        self.hotkey_box = QtWidgets.QGroupBox()
        hotkey_layout = QtWidgets.QFormLayout(self.hotkey_box)
        self.activation_key_edit = QtWidgets.QLineEdit()
        self.activation_key_edit.setMaxLength(1)
        self.activation_key_edit.setFixedWidth(40)
        self.activation_key_label = QtWidgets.QLabel()
        hotkey_layout.addRow(self.activation_key_label, self.activation_key_edit)
        controls_layout.addWidget(self.hotkey_box)
        controls_layout.addStretch()

        # ### ZMIANA: Panel podsumowania jest teraz składany ###
        self.autoclicker_summary_box = QtWidgets.QGroupBox()
        self.autoclicker_summary_box.setCheckable(True)
        self.autoclicker_summary_box.setChecked(True)
        summary_layout_ac = QtWidgets.QVBoxLayout(self.autoclicker_summary_box)
        summary_layout_ac.setContentsMargins(10, 10, 10, 10)
        self.autoclicker_summary_label = QtWidgets.QLabel()
        self.autoclicker_summary_label.setWordWrap(True)
        summary_layout_ac.addWidget(self.autoclicker_summary_label)
        controls_layout.addWidget(self.autoclicker_summary_box)
        self.autoclicker_summary_box.toggled.connect(self.autoclicker_summary_label.setVisible)

        self.autoclicker_info_box = QtWidgets.QGroupBox()
        self.autoclicker_info_box.setCheckable(True)
        self.autoclicker_info_box.setChecked(False)
        info_layout = QtWidgets.QVBoxLayout(self.autoclicker_info_box)

        info_scroll_area = QScrollArea()
        info_scroll_area.setWidgetResizable(True)
        info_scroll_area.setVisible(False)
        info_scroll_area.setMaximumHeight(220)

        self.autoclicker_info_label = QtWidgets.QLabel()
        self.autoclicker_info_label.setWordWrap(True)
        self.autoclicker_info_label.setOpenExternalLinks(True)

        info_scroll_area.setWidget(self.autoclicker_info_label)
        info_layout.addWidget(info_scroll_area)
        self.autoclicker_info_box.toggled.connect(info_scroll_area.setVisible)

        controls_layout.addWidget(self.autoclicker_info_box)

        self.autoclicker_disabled_label = QtWidgets.QLabel()
        self.autoclicker_disabled_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.autoclicker_disabled_label.setWordWrap(True)
        self.autoclicker_disabled_label.setObjectName("disabledLabel")

        layout.addWidget(self.autoclicker_controls_widget)
        layout.addWidget(self.autoclicker_disabled_label)

    # ### ZMIANA: Całkowita przebudowa tej metody w celu zapewnienia spójności ###
    def _populate_antiafk_tab(self, tab):
        layout = QtWidgets.QVBoxLayout(tab)

        self.afk_controls_widget = QtWidgets.QWidget()
        controls_layout = QtWidgets.QVBoxLayout(self.afk_controls_widget)
        controls_layout.setContentsMargins(15, 15, 15, 15)

        # Panel 1: Akcje i Interwał
        self.antiafk_actions_box = QtWidgets.QGroupBox()
        afk_actions_layout = QtWidgets.QFormLayout(self.antiafk_actions_box)

        interval_layout = QtWidgets.QHBoxLayout()
        self.afk_min_interval_spin = QtWidgets.QSpinBox(); self.afk_min_interval_spin.setRange(1, 300); self.afk_min_interval_spin.setSuffix(" s")
        self.afk_max_interval_spin = QtWidgets.QSpinBox(); self.afk_max_interval_spin.setRange(1, 300); self.afk_max_interval_spin.setSuffix(" s")
        self.interval_min_label = QtWidgets.QLabel(); self.interval_max_label = QtWidgets.QLabel()
        interval_layout.addWidget(self.interval_min_label); interval_layout.addWidget(self.afk_min_interval_spin)
        interval_layout.addSpacing(10)
        interval_layout.addWidget(self.interval_max_label); interval_layout.addWidget(self.afk_max_interval_spin)
        self.perform_actions_every_label = QtWidgets.QLabel()
        afk_actions_layout.addRow(self.perform_actions_every_label, interval_layout)
        afk_actions_layout.addRow(QtWidgets.QLabel()) # Spacer

        self.afk_move_mouse_check = QtWidgets.QCheckBox()
        self.afk_click_mouse_check = QtWidgets.QCheckBox()
        self.afk_scroll_mouse_check = QtWidgets.QCheckBox()
        self.afk_press_keys_check = QtWidgets.QCheckBox()
        afk_actions_layout.addRow(self.afk_move_mouse_check)
        afk_actions_layout.addRow(self.afk_click_mouse_check)
        afk_actions_layout.addRow(self.afk_scroll_mouse_check)
        afk_actions_layout.addRow(self.afk_press_keys_check)
        controls_layout.addWidget(self.antiafk_actions_box)

        # Panel 2: Ustawienia Ruchu Myszy
        self.mouse_movement_box = QtWidgets.QGroupBox()
        mouse_movement_layout = QtWidgets.QFormLayout(self.mouse_movement_box)

        self.afk_mouse_range_spin = QtWidgets.QSpinBox(); self.afk_mouse_range_spin.setRange(1, 100); self.afk_mouse_range_spin.setSuffix(" px")
        self.movement_range_label = QtWidgets.QLabel()
        mouse_movement_layout.addRow(self.movement_range_label, self.afk_mouse_range_spin)
        self.afk_return_to_start_check = QtWidgets.QCheckBox()
        mouse_movement_layout.addRow(self.afk_return_to_start_check)

        self.human_move_widget = QtWidgets.QWidget()
        human_move_layout = QtWidgets.QFormLayout(self.human_move_widget)
        human_move_layout.setContentsMargins(0, 5, 0, 5)
        self.afk_use_human_moves_check = QtWidgets.QCheckBox()
        self.afk_human_move_mode_combo = QtWidgets.QComboBox()
        self.afk_human_move_mode_combo.addItems(["bezier1", "bezier2", "gravity"])
        self.afk_human_move_duration_spin = QtWidgets.QDoubleSpinBox(); self.afk_human_move_duration_spin.setRange(0.1, 2.0); self.afk_human_move_duration_spin.setSingleStep(0.1); self.afk_human_move_duration_spin.setSuffix(" s")
        self.human_move_mode_label = QtWidgets.QLabel()
        self.human_move_duration_label = QtWidgets.QLabel()
        human_move_layout.addRow(self.afk_use_human_moves_check)
        human_move_layout.addRow(self.human_move_mode_label, self.afk_human_move_mode_combo)
        human_move_layout.addRow(self.human_move_duration_label, self.afk_human_move_duration_spin)
        mouse_movement_layout.addRow(self.human_move_widget)
        controls_layout.addWidget(self.mouse_movement_box)

        # Panel 3: Ustawienia Klawiszy
        self.key_press_box = QtWidgets.QGroupBox()
        key_press_layout = QtWidgets.QFormLayout(self.key_press_box)
        self.afk_key_w = QtWidgets.QCheckBox("W"); self.afk_key_a = QtWidgets.QCheckBox("A"); self.afk_key_s = QtWidgets.QCheckBox("S"); self.afk_key_d = QtWidgets.QCheckBox("D"); self.afk_key_space = QtWidgets.QCheckBox("Space")
        presets_widget = QtWidgets.QWidget()
        presets_layout = QtWidgets.QHBoxLayout(presets_widget); presets_layout.setContentsMargins(0,0,0,0)
        presets_layout.addStretch(); presets_layout.addWidget(self.afk_key_w); presets_layout.addWidget(self.afk_key_a); presets_layout.addWidget(self.afk_key_s); presets_layout.addWidget(self.afk_key_d); presets_layout.addWidget(self.afk_key_space); presets_layout.addStretch()
        self.presets_label = QtWidgets.QLabel()
        key_press_layout.addRow(self.presets_label, presets_widget)
        self.afk_custom_keys_edit = QtWidgets.QLineEdit()
        self.custom_keys_label = QtWidgets.QLabel()
        key_press_layout.addRow(self.custom_keys_label, self.afk_custom_keys_edit)
        controls_layout.addWidget(self.key_press_box)

        # Panel 4: Skróty klawiszowe
        self.hotkey_box_afk = QtWidgets.QGroupBox()
        hotkey_afk_layout = QtWidgets.QFormLayout(self.hotkey_box_afk)
        self.afk_hotkey_edit = QtWidgets.QLineEdit()
        self.afk_hotkey_edit.setMaxLength(1)
        self.afk_hotkey_edit.setFixedWidth(40)
        self.afk_hotkey_label = QtWidgets.QLabel()
        hotkey_afk_layout.addRow(self.afk_hotkey_label, self.afk_hotkey_edit)
        controls_layout.addWidget(self.hotkey_box_afk)

        # Połączenia sygnałów dla nowej struktury
        self.afk_move_mouse_check.toggled.connect(self.mouse_movement_box.setEnabled)
        self.afk_press_keys_check.toggled.connect(self.key_press_box.setEnabled)
        self.afk_use_human_moves_check.toggled.connect(self._on_afk_use_human_move_toggled)

        controls_layout.addStretch()

        # Panel Podsumowania
        self.antiafk_summary_box = QtWidgets.QGroupBox()
        self.antiafk_summary_box.setCheckable(True)
        self.antiafk_summary_box.setChecked(True)
        summary_layout_afk = QtWidgets.QVBoxLayout(self.antiafk_summary_box)
        summary_layout_afk.setContentsMargins(10, 10, 10, 10)
        self.antiafk_summary_label = QtWidgets.QLabel()
        self.antiafk_summary_label.setWordWrap(True)
        summary_layout_afk.addWidget(self.antiafk_summary_label)
        controls_layout.addWidget(self.antiafk_summary_box)
        self.antiafk_summary_box.toggled.connect(self.antiafk_summary_label.setVisible)

        # Panel Informacyjny
        self.antiafk_info_box = QtWidgets.QGroupBox()
        self.antiafk_info_box.setCheckable(True)
        self.antiafk_info_box.setChecked(False)
        info_layout_afk = QtWidgets.QVBoxLayout(self.antiafk_info_box)
        info_scroll_area_afk = QScrollArea()
        info_scroll_area_afk.setWidgetResizable(True)
        info_scroll_area_afk.setVisible(False)
        info_scroll_area_afk.setMaximumHeight(220)
        self.antiafk_info_label = QtWidgets.QLabel()
        self.antiafk_info_label.setWordWrap(True)
        self.antiafk_info_label.setOpenExternalLinks(True)
        info_scroll_area_afk.setWidget(self.antiafk_info_label)
        info_layout_afk.addWidget(info_scroll_area_afk)
        self.antiafk_info_box.toggled.connect(info_scroll_area_afk.setVisible)
        controls_layout.addWidget(self.antiafk_info_box)

        # Etykieta Wyłączonego Modułu
        self.afk_disabled_label = QtWidgets.QLabel()
        self.afk_disabled_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.afk_disabled_label.setWordWrap(True)
        self.afk_disabled_label.setObjectName("disabledLabel")

        layout.addWidget(self.afk_controls_widget)
        layout.addWidget(self.afk_disabled_label)


    def _populate_log_tab(self, tab):
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        self.log_widget = QPlainTextEdit()
        self.log_widget.setReadOnly(True)

        self.clear_logs_button = QtWidgets.QPushButton()
        self.clear_logs_button.clicked.connect(self._clear_logs)

        layout.addWidget(self.log_widget)
        layout.addWidget(self.clear_logs_button)


    # --- Settings Tab UI ---
    def _populate_settings_tab(self, tab):
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)

        self.profiles_box = QtWidgets.QGroupBox()
        profiles_layout = QtWidgets.QFormLayout(self.profiles_box)
        self.profiles_combo = QtWidgets.QComboBox()
        self.profiles_combo.currentIndexChanged.connect(self._on_profile_selected)
        self.profile_name_edit = QtWidgets.QLineEdit()
        self.save_profile_button = QtWidgets.QPushButton()
        self.save_profile_button.clicked.connect(self._save_new_profile)
        self.delete_profile_button = QtWidgets.QPushButton()
        self.delete_profile_button.clicked.connect(self._delete_profile)
        self.import_profile_button = QtWidgets.QPushButton()
        self.import_profile_button.clicked.connect(self._import_profile)
        self.export_profile_button = QtWidgets.QPushButton()
        self.export_profile_button.clicked.connect(self._export_profile)
        self.profile_name_label = QtWidgets.QLabel()

        profile_buttons1 = QtWidgets.QHBoxLayout()
        profile_buttons1.addWidget(self.save_profile_button)
        profile_buttons1.addWidget(self.delete_profile_button)
        profile_buttons2 = QtWidgets.QHBoxLayout()
        profile_buttons2.addWidget(self.import_profile_button)
        profile_buttons2.addWidget(self.export_profile_button)

        profiles_layout.addRow(self.profiles_combo)
        profiles_layout.addRow(self.profile_name_label, self.profile_name_edit)
        profiles_layout.addRow(profile_buttons1)
        profiles_layout.addRow(profile_buttons2)
        layout.addWidget(self.profiles_box)

        self.module_activation_box = QtWidgets.QGroupBox()
        module_activation_layout = QtWidgets.QVBoxLayout(self.module_activation_box)
        self.autoclicker_enabled_check = QtWidgets.QCheckBox()
        self.afk_enabled_check = QtWidgets.QCheckBox()
        module_activation_layout.addWidget(self.autoclicker_enabled_check)
        module_activation_layout.addWidget(self.afk_enabled_check)
        layout.addWidget(self.module_activation_box)

        self.autoclicker_enabled_check.toggled.connect(self._on_autoclicker_enabled_toggled)
        self.afk_enabled_check.toggled.connect(self._on_afk_enabled_toggled)

        self.settings_box = QtWidgets.QGroupBox()
        settings_layout = QtWidgets.QFormLayout(self.settings_box)

        self.language_combo = QtWidgets.QComboBox(); self.language_combo.addItems(["English", "Polski"])
        self.language_label = QtWidgets.QLabel()
        settings_layout.addRow(self.language_label, self.language_combo)
        self.language_combo.currentIndexChanged.connect(self._change_language)

        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_label = QtWidgets.QLabel()
        settings_layout.addRow(self.theme_label, self.theme_combo)
        self.theme_combo.currentIndexChanged.connect(self._change_theme)

        self.start_delay_spin = QtWidgets.QDoubleSpinBox(); self.start_delay_spin.setRange(0.0, 60.0); self.start_delay_spin.setSingleStep(0.1); self.start_delay_spin.setSuffix(" s")
        self.start_delay_label = QtWidgets.QLabel()
        settings_layout.addRow(self.start_delay_label, self.start_delay_spin)

        self.emergency_key_edit = QtWidgets.QLineEdit()
        self.emergency_key_edit.setFixedWidth(60)
        self.emergency_key_label = QtWidgets.QLabel()
        settings_layout.addRow(self.emergency_key_label, self.emergency_key_edit)

        self.limit_window_check = QtWidgets.QCheckBox()
        self.window_title_edit = QtWidgets.QLineEdit()
        self.limit_window_check.toggled.connect(self.window_title_edit.setEnabled)
        settings_layout.addRow(self.limit_window_check)
        settings_layout.addRow(self.window_title_edit)

        self.always_on_top_checkbox = QtWidgets.QCheckBox()
        self.always_on_top_checkbox.toggled.connect(self._set_always_on_top)
        settings_layout.addRow(self.always_on_top_checkbox)

        color_layout = QtWidgets.QHBoxLayout()
        self.color_swatch = QtWidgets.QLabel(); self.color_swatch.setFixedSize(24, 24)
        self.change_color_button = QtWidgets.QPushButton()
        self.change_color_button.clicked.connect(self._open_color_picker)
        color_layout.addWidget(self.color_swatch)
        color_layout.addWidget(self.change_color_button)
        self.accent_color_label = QtWidgets.QLabel()
        settings_layout.addRow(self.accent_color_label, color_layout)

        self.reset_settings_button = QtWidgets.QPushButton()
        self.reset_settings_button.clicked.connect(self._reset_settings)
        self.reset_settings_label = QtWidgets.QLabel()
        settings_layout.addRow(self.reset_settings_label, self.reset_settings_button)
        layout.addWidget(self.settings_box)

        layout.addStretch()
        self.copyright_label = QtWidgets.QLabel()
        self.copyright_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.copyright_label.setOpenExternalLinks(True)
        self.copyright_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.copyright_label)

    # --- UI Widget Factory Methods ---
    def _create_mouse_button_group(self, title):
        box = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QFormLayout(box)
        cps_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); cps_slider.setRange(10, 300)
        cps_value_label = QtWidgets.QLabel("12.0"); cps_value_label.setMinimumWidth(40)
        cps_layout = QtWidgets.QHBoxLayout(); cps_layout.addWidget(cps_slider); cps_layout.addWidget(cps_value_label)
        cps_label_widget = QtWidgets.QLabel(self._tr('cps_label'))
        layout.addRow(cps_label_widget, cps_layout)

        click_type_combo = QtWidgets.QComboBox()
        click_type_combo.addItems([self._tr('click_type_single'), self._tr('click_type_double'), self._tr('click_type_triple')])
        click_type_label_widget = QtWidgets.QLabel(self._tr('click_type_label'))
        layout.addRow(click_type_label_widget, click_type_combo)

        variation_check = QtWidgets.QCheckBox(self._tr('variation_check'))
        jitter_spin = QtWidgets.QSpinBox(); jitter_spin.setRange(0, 100)
        layout.addRow(variation_check)
        jitter_label_widget = QtWidgets.QLabel(self._tr('jitter_label'))
        layout.addRow(jitter_label_widget, jitter_spin)
        variation_check.toggled.connect(jitter_spin.setEnabled)
        box.widgets = {'slider': cps_slider, 'label': cps_value_label, 'variation': variation_check, 'jitter': jitter_spin, 'cps_label': cps_label_widget, 'jitter_label': jitter_label_widget, 'click_type': click_type_combo, 'click_type_label': click_type_label_widget}
        cps_slider.valueChanged.connect(lambda val, label=cps_value_label: label.setText(f"{val/10.0:.1f}"))
        return box

    def _create_button_choice_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget); layout.setContentsMargins(0,0,0,0)
        self.toggle_lmb_radio = QtWidgets.QRadioButton()
        self.toggle_rmb_radio = QtWidgets.QRadioButton()
        button_layout = QtWidgets.QHBoxLayout(); button_layout.addWidget(self.toggle_lmb_radio); button_layout.addWidget(self.toggle_rmb_radio)
        self.click_with_label = QtWidgets.QLabel()
        layout.addRow(self.click_with_label, button_layout)
        return widget

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
        autoclicker_widgets = [self.lmb_box.widgets['slider'], self.lmb_box.widgets['variation'], self.lmb_box.widgets['jitter'], self.lmb_box.widgets['click_type'], self.rmb_box.widgets['slider'], self.rmb_box.widgets['variation'], self.rmb_box.widgets['jitter'], self.rmb_box.widgets['click_type'], self.activation_key_edit, self.start_delay_spin, self.click_limit_spin, self.limit_window_check, self.window_title_edit, self.always_on_top_checkbox, self.hold_mode_radio, self.toggle_mode_radio, self.burst_mode_radio, self.toggle_lmb_radio, self.toggle_rmb_radio, self.burst_clicks_spin, self.burst_delay_spin, self.fixed_pos_check, self.fixed_pos_x_spin, self.fixed_pos_y_spin, self.playback_reps_spin]
        antiafk_widgets = [self.afk_min_interval_spin, self.afk_max_interval_spin, self.afk_move_mouse_check, self.afk_use_human_moves_check, self.afk_human_move_mode_combo, self.afk_human_move_duration_spin, self.afk_mouse_range_spin, self.afk_return_to_start_check, self.afk_click_mouse_check, self.afk_scroll_mouse_check, self.afk_press_keys_check, self.afk_key_w, self.afk_key_a, self.afk_key_s, self.afk_key_d, self.afk_key_space, self.afk_custom_keys_edit, self.afk_hotkey_edit]
        settings_widgets = [self.emergency_key_edit, self.autoclicker_enabled_check, self.afk_enabled_check]
        all_widgets = autoclicker_widgets + antiafk_widgets + settings_widgets
        for widget in all_widgets:
            if isinstance(widget, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox, QtWidgets.QSlider)):
                widget.valueChanged.connect(self._save_active_profile_from_ui)
                widget.valueChanged.connect(self._update_summaries)
            elif isinstance(widget, (QtWidgets.QCheckBox, QtWidgets.QRadioButton)):
                widget.toggled.connect(self._save_active_profile_from_ui)
                widget.toggled.connect(self._update_summaries)
            elif isinstance(widget, QtWidgets.QLineEdit):
                widget.textChanged.connect(self._save_active_profile_from_ui)
                widget.textChanged.connect(self._update_summaries)
            elif isinstance(widget, QtWidgets.QComboBox):
                widget.currentIndexChanged.connect(self._save_active_profile_from_ui)
                widget.currentIndexChanged.connect(self._update_summaries)

    # Saves current settings to the active profile.
    def _save_active_profile_from_ui(self, *args):
        if self.profiles_combo.blockSignals(True):
            self.profiles_combo.blockSignals(False)
            return

        current_profile_name = self.profiles_combo.currentText()
        if not current_profile_name: return

        profile_data = self._get_settings_from_ui()

        if "profiles" not in self.settings: self.settings["profiles"] = {}
        self.settings["profiles"][current_profile_name] = profile_data

        save_settings(self.settings)

    # Gathers all current settings from the UI.
    def _get_settings_from_ui(self):
        return {
            "lmb_cps": self.lmb_box.widgets['slider'].value()/10.0, "lmb_variation": self.lmb_box.widgets['variation'].isChecked(), "lmb_jitter": self.lmb_box.widgets['jitter'].value(), "lmb_click_type": self.lmb_box.widgets['click_type'].currentIndex() + 1,
            "rmb_cps": self.rmb_box.widgets['slider'].value()/10.0, "rmb_variation": self.rmb_box.widgets['variation'].isChecked(), "rmb_jitter": self.rmb_box.widgets['jitter'].value(), "rmb_click_type": self.rmb_box.widgets['click_type'].currentIndex() + 1,
            "autoclicker_enabled": self.autoclicker_enabled_check.isChecked(),
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
            "emergency_key": self.emergency_key_edit.text(),
            "playback_reps": self.playback_reps_spin.value(),
            "afk_enabled": self.afk_enabled_check.isChecked(),
            "afk_min_interval": self.afk_min_interval_spin.value(), "afk_max_interval": self.afk_max_interval_spin.value(),
            "afk_move_mouse": self.afk_move_mouse_check.isChecked(), "afk_mouse_range": self.afk_mouse_range_spin.value(),
            "afk_return_to_start": self.afk_return_to_start_check.isChecked(),
            "afk_click_mouse": self.afk_click_mouse_check.isChecked(),
            "afk_scroll_mouse": self.afk_scroll_mouse_check.isChecked(),
            "afk_press_keys": self.afk_press_keys_check.isChecked(),
            "afk_key_w": self.afk_key_w.isChecked(), "afk_key_a": self.afk_key_a.isChecked(), "afk_key_s": self.afk_key_s.isChecked(), "afk_key_d": self.afk_key_d.isChecked(), "afk_key_space": self.afk_key_space.isChecked(),
            "afk_custom_keys": self.afk_custom_keys_edit.text(),
            "afk_hotkey": self.afk_hotkey_edit.text(),
            "afk_use_human_moves": self.afk_use_human_moves_check.isChecked(),
            "afk_human_move_mode_index": self.afk_human_move_mode_combo.currentIndex(),
            "afk_human_move_duration": self.afk_human_move_duration_spin.value()
        }

    # Loads settings from a profile dict and applies them to the UI widgets.
    def _load_settings_to_ui(self, s: dict):
        for widget in self.findChildren(QtWidgets.QWidget): widget.blockSignals(True)

        # --- Load AutoClicker Settings ---
        self.lmb_box.widgets['slider'].setValue(int(s.get("lmb_cps", 12.0) * 10)); self.lmb_box.widgets['variation'].setChecked(s.get("lmb_variation", True)); self.lmb_box.widgets['jitter'].setValue(s.get("lmb_jitter", 8)); self.lmb_box.widgets['click_type'].setCurrentIndex(s.get("lmb_click_type", 1) - 1)
        self.rmb_box.widgets['slider'].setValue(int(s.get("rmb_cps", 8.0) * 10)); self.rmb_box.widgets['variation'].setChecked(s.get("rmb_variation", True)); self.rmb_box.widgets['jitter'].setValue(s.get("rmb_jitter", 12)); self.rmb_box.widgets['click_type'].setCurrentIndex(s.get("rmb_click_type", 1) - 1)
        mode = s.get("activation_mode", "hold"); self.toggle_mode_radio.setChecked(mode=="toggle"); self.burst_mode_radio.setChecked(mode=="burst"); self.hold_mode_radio.setChecked(mode=="hold")
        self.toggle_rmb_radio.setChecked(s.get("toggle_button", "left") == "right"); self.toggle_lmb_radio.setChecked(s.get("toggle_button", "left") != "right")
        self.burst_clicks_spin.setValue(s.get("burst_clicks", 3)); self.burst_delay_spin.setValue(s.get("burst_delay", 50))
        self.fixed_pos_check.setChecked(s.get("use_fixed_pos", False)); self.fixed_pos_x_spin.setValue(s.get("fixed_x", 0)); self.fixed_pos_y_spin.setValue(s.get("fixed_y", 0))
        self.click_limit_spin.setValue(s.get("click_limit", 0))
        self.limit_window_check.setChecked(s.get("limit_window", False)); self.window_title_edit.setText(s.get("window_title", "Minecraft"))
        self.activation_key_edit.setText(s.get("activation_key") or "r"); self.start_delay_spin.setValue(s.get("start_delay", 0.0)); self.always_on_top_checkbox.setChecked(s.get("always_on_top", False));
        self.playback_reps_spin.setValue(s.get("playback_reps", 0))

        # --- Load General Settings ---
        self.autoclicker_enabled_check.setChecked(s.get("autoclicker_enabled", False))
        self.afk_enabled_check.setChecked(s.get("afk_enabled", False))
        self.current_language = s.get("language", "en")
        self.language_combo.setCurrentIndex(1 if self.current_language == "pl" else 0)
        self.current_theme = s.get("theme", "dark")
        self.theme_combo.setCurrentIndex(1 if self.current_theme == "light" else 0)
        self.emergency_key_edit.setText(s.get("emergency_key") or "esc")
        self.accent_color = QtGui.QColor(s.get("accent_color", DEFAULT_ACCENT_COLOR))

        # --- Load Anti-AFK Settings ---
        self.afk_min_interval_spin.setValue(s.get("afk_min_interval", 10)); self.afk_max_interval_spin.setValue(s.get("afk_max_interval", 15))
        self.afk_move_mouse_check.setChecked(s.get("afk_move_mouse", True)); self.afk_mouse_range_spin.setValue(s.get("afk_mouse_range", 5))
        self.afk_return_to_start_check.setChecked(s.get("afk_return_to_start", False))
        self.afk_click_mouse_check.setChecked(s.get("afk_click_mouse", False))
        self.afk_scroll_mouse_check.setChecked(s.get("afk_scroll_mouse", False))
        self.afk_press_keys_check.setChecked(s.get("afk_press_keys", False))
        self.afk_key_w.setChecked(s.get("afk_key_w", False)); self.afk_key_a.setChecked(s.get("afk_key_a", False)); self.afk_key_s.setChecked(s.get("afk_key_s", False)); self.afk_key_d.setChecked(s.get("afk_key_d", False)); self.afk_key_space.setChecked(s.get("afk_key_space", False))
        self.afk_custom_keys_edit.setText(s.get("afk_custom_keys", ""))
        self.afk_hotkey_edit.setText(s.get("afk_hotkey") or "p")
        self.afk_use_human_moves_check.setChecked(s.get("afk_use_human_moves", False))
        self.afk_human_move_mode_combo.setCurrentIndex(s.get("afk_human_move_mode_index", 0))
        self.afk_human_move_duration_spin.setValue(s.get("afk_human_move_duration", 0.3))

        # --- Post-load UI adjustments ---
        self._on_mode_changed()
        self.lmb_box.widgets['jitter'].setEnabled(self.lmb_box.widgets['variation'].isChecked())
        self.rmb_box.widgets['jitter'].setEnabled(self.rmb_box.widgets['variation'].isChecked())
        self.window_title_edit.setEnabled(self.limit_window_check.isChecked())
        self.mouse_movement_box.setEnabled(self.afk_move_mouse_check.isChecked())
        self.key_press_box.setEnabled(self.afk_press_keys_check.isChecked())
        self._on_afk_use_human_move_toggled(self.afk_use_human_moves_check.isChecked())
        self._on_autoclicker_enabled_toggled(self.autoclicker_enabled_check.isChecked())
        self._on_afk_enabled_toggled(self.afk_enabled_check.isChecked())

        self._update_theme()
        self._retranslate_ui()
        self._update_summaries()

        for widget in self.findChildren(QtWidgets.QWidget): widget.blockSignals(False)

    # =====================================================================
    # Event Handling & Logic
    # =====================================================================

    # --- Listener Setup ---
    def _start_listeners(self):
        self.hold_mode_radio.toggled.connect(self._on_mode_changed)
        self.toggle_mode_radio.toggled.connect(self._on_mode_changed)
        self.burst_mode_radio.toggled.connect(self._on_mode_changed)

        self.activation_key_edit.textChanged.connect(self._update_info_texts)
        self.afk_hotkey_edit.textChanged.connect(self._update_info_texts)
        self.emergency_key_edit.textChanged.connect(self._update_info_texts)

        self.keyboard_listener = KeyboardListener(on_press=self._on_key_press); self.keyboard_listener.start()
        self.mouse_listener = MouseListener(on_click=self._on_mouse_click); self.mouse_listener.start()

    # --- Anti-AFK Worker Management ---
    def on_toggle_afk_worker(self):
        if not self.afk_enabled_check.isChecked():
            return

        if self.afk_worker and self.afk_worker.isRunning():
            self.sig_log_message.emit("Anti-AFK stopping...")
            self.afk_worker.stop()
            return

        self.sig_log_message.emit("Anti-AFK starting...")
        keys = []
        if self.afk_key_w.isChecked(): keys.append('w')
        if self.afk_key_a.isChecked(): keys.append('a')
        if self.afk_key_s.isChecked(): keys.append('s')
        if self.afk_key_d.isChecked(): keys.append('d')
        if self.afk_key_space.isChecked(): keys.append(Key.space)
        if self.afk_custom_keys_edit.text(): keys.extend(list(self.afk_custom_keys_edit.text().lower()))

        cfg = AntiAfkConfig(
            enabled=self.afk_enabled_check.isChecked(),
            min_interval_s=self.afk_min_interval_spin.value(), max_interval_s=self.afk_max_interval_spin.value(),
            move_mouse=self.afk_move_mouse_check.isChecked(), mouse_range=self.afk_mouse_range_spin.value(),
            return_to_start=self.afk_return_to_start_check.isChecked(),
            click_mouse=self.afk_click_mouse_check.isChecked(),
            scroll_mouse=self.afk_scroll_mouse_check.isChecked(),
            press_keys=self.afk_press_keys_check.isChecked(), keys_to_press=keys,
            use_human_like_move=self.afk_use_human_moves_check.isChecked(),
            human_move_mode_index=self.afk_human_move_mode_combo.currentIndex(),
            human_move_duration=self.afk_human_move_duration_spin.value()
        )
        self.afk_worker = AntiAfkWorker(cfg)
        self.afk_worker.sig_finished.connect(self.on_afk_worker_finished)
        self.afk_worker.start()

        self.status_label.setText(self._tr('status_antiafk').format(color=self.accent_color.name()))
        self.tab_widget.setTabEnabled(0, False) # Disable Autoclicker Tab
        self.tab_widget.setTabEnabled(3, False) # Disable Settings Tab

    def on_afk_worker_finished(self):
        self.sig_log_message.emit("Anti-AFK stopped.")
        self.status_label.setText(self._tr('status_stopped'))
        self.afk_worker = None
        self.tab_widget.setTabEnabled(0, True)
        self.tab_widget.setTabEnabled(3, True)

    # --- AutoClicker Worker Management ---
    @QtCore.pyqtSlot(MouseButton)
    def on_start_clicking(self, button):
        if self.worker is not None: return
        self.sig_log_message.emit("AutoClicker started.")
        is_burst = self.burst_mode_radio.isChecked()
        is_toggle = self.toggle_mode_radio.isChecked()
        cfg = ClickConfig(is_burst_mode=is_burst)

        if button == MouseButton.left:
            cfg.cps=self.lmb_box.widgets['slider'].value()/10.0; cfg.use_random_variation=self.lmb_box.widgets['variation'].isChecked(); cfg.jitter_ms=self.lmb_box.widgets['jitter'].value(); cfg.click_type=self.lmb_box.widgets['click_type'].currentIndex() + 1
        else:
            cfg.cps=self.rmb_box.widgets['slider'].value()/10.0; cfg.use_random_variation=self.rmb_box.widgets['variation'].isChecked(); cfg.jitter_ms=self.rmb_box.widgets['jitter'].value(); cfg.click_type=self.rmb_box.widgets['click_type'].currentIndex() + 1

        cfg.click_button = button
        cfg.limit_to_window=self.limit_window_check.isChecked(); cfg.window_title=self.window_title_edit.text()
        cfg.start_delay_s=self.start_delay_spin.value()
        if is_toggle: cfg.click_limit=self.click_limit_spin.value(); cfg.use_fixed_position=self.fixed_pos_check.isChecked(); cfg.fixed_x=self.fixed_pos_x_spin.value(); cfg.fixed_y=self.fixed_pos_y_spin.value()
        if is_burst: cfg.burst_clicks=self.burst_clicks_spin.value(); cfg.burst_delay_ms=self.burst_delay_spin.value()

        self.worker = ClickWorker(cfg, main_window=self)
        self.worker.sig_finished.connect(self.on_stop_clicking)
        self.worker.start()

        self.status_label.setText(self._tr('status_clicking').format(color=self.accent_color.name()))
        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(3, False)

    @QtCore.pyqtSlot()
    def on_stop_clicking(self):
        if self.worker:
            self.sig_log_message.emit("AutoClicker stopped.")
            self.worker.stop(); self.worker.wait(200); self.worker = None

        if self.hold_mode_radio.isChecked() and self.is_armed:
            self.status_label.setText(self._tr('status_armed'))
        else:
            self.status_label.setText(self._tr('status_stopped'))
            self.is_armed = False
        self.tab_widget.setTabEnabled(1, True)
        self.tab_widget.setTabEnabled(3, True)


    # --- Record & Playback ---
    def _toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.sig_log_message.emit("Recording started...")
            self.recorded_sequence = []
            self.last_click_time = time.perf_counter()
            self.status_label.setText(self._tr('status_recording'))
            self.record_button.setText(self._tr('stop_record_button'))
            self.tab_widget.setTabEnabled(1, False)
            self.tab_widget.setTabEnabled(3, False)
        else:
            self.sig_log_message.emit(f"Recording stopped. Clicks captured: {len(self.recorded_sequence)}.")
            self.status_label.setText(self._tr('status_stopped'))
            self.record_button.setText(self._tr('record_button'))
            self.recorded_clicks_count_label.setText(self._tr('recorded_clicks_label').format(count=len(self.recorded_sequence)))
            self.tab_widget.setTabEnabled(1, True)
            self.tab_widget.setTabEnabled(3, True)

    def _toggle_playback(self):
        if self.playback_worker and self.playback_worker.isRunning():
            self.sig_log_message.emit("Playback stopping...")
            self.playback_worker.stop()
        else:
            if not self.recorded_sequence:
                self.sig_log_message.emit("Playback failed: No sequence recorded.")
                return
            self.sig_log_message.emit("Playback started.")
            reps = self.playback_reps_spin.value()
            self.playback_worker = PlaybackWorker(self.recorded_sequence, reps)
            self.playback_worker.sig_finished.connect(self._on_playback_finished)
            self.playback_worker.start()
            self.status_label.setText(self._tr('status_playback').format(color=self.accent_color.name()))
            self.playback_button.setText(self._tr('stop_record_button'))
            self.tab_widget.setTabEnabled(1, False)
            self.tab_widget.setTabEnabled(3, False)

    def _on_playback_finished(self):
        self.sig_log_message.emit("Playback finished.")
        self.playback_worker = None
        self.status_label.setText(self._tr('status_stopped'))
        self.playback_button.setText(self._tr('playback_button'))
        self.tab_widget.setTabEnabled(1, True)
        self.tab_widget.setTabEnabled(3, True)

    # --- Global Input Handlers ---
    def _on_key_press(self, key):
        emergency_key_str = (self.emergency_key_edit.text() or "esc").lower()
        key_matched = False

        if hasattr(key, 'char') and key.char is not None:
            if key.char.lower() == emergency_key_str: key_matched = True
        elif hasattr(key, 'name') and key.name is not None:
            if key.name.lower() == emergency_key_str: key_matched = True

        if key_matched:
            self.sig_log_message.emit("Emergency STOP triggered!")
            if self.is_recording: self._toggle_recording()
            if self.is_armed: self.is_armed = False
            if self.worker: self.worker.stop()
            if self.afk_worker: self.afk_worker.stop()
            if self.playback_worker: self.playback_worker.stop()
            return

        if isinstance(QtWidgets.QApplication.focusWidget(), (QtWidgets.QLineEdit, QPlainTextEdit)):
            return

        try:
            pressed_char = key.char.lower()
        except AttributeError:
            return

        afk_hotkey = (self.afk_hotkey_edit.text() or "p").lower()
        if pressed_char == afk_hotkey:
            if self.afk_enabled_check.isChecked() and not (self.worker and self.worker.isRunning()):
                self.sig_toggle_afk.emit()
            return

        activation_key = (self.activation_key_edit.text() or "r").lower()
        if pressed_char == activation_key:
            if self.autoclicker_enabled_check.isChecked() and not (self.afk_worker and self.afk_worker.isRunning()):
                self.sig_trigger_action.emit()
            return

    def on_toggle_armed(self):
        self.is_armed = not self.is_armed
        if self.is_armed:
            self.sig_log_message.emit("Hold mode armed.")
            self.status_label.setText(self._tr('status_armed'))
        else:
            self.sig_log_message.emit("Hold mode disarmed.")
            self.status_label.setText(self._tr('status_stopped'))
            if self.worker and self.worker.isRunning(): self.sig_stop_clicking.emit()

    def on_trigger_action(self):
        if self.hold_mode_radio.isChecked(): self.on_toggle_armed()
        else:
            if self.worker and self.worker.isRunning(): self.sig_stop_clicking.emit()
            else:
                button = MouseButton.right if self.toggle_rmb_radio.isChecked() else MouseButton.left
                self.sig_start_clicking.emit(button)

    def _on_mouse_click(self, x, y, button, pressed):
        if self.is_recording and pressed:
            current_time = time.perf_counter()
            delay = current_time - self.last_click_time
            self.last_click_time = current_time

            button_name = 'left' if button == MouseButton.left else 'right'
            self.recorded_sequence.append({'x': x, 'y': y, 'delay': delay, 'button': button_name})
            self.recorded_clicks_count_label.setText(self._tr('recorded_clicks_label').format(count=len(self.recorded_sequence)))
            return

        if self.afk_worker and self.afk_worker.isRunning(): return
        if not self.hold_mode_radio.isChecked(): return

        if self.programmatic_click:
            if not pressed: self.programmatic_click = False
            return

        is_worker_running = self.worker is not None and self.worker.isRunning()
        if not self.is_armed: return
        if pressed and not is_worker_running:
            if button in [MouseButton.left, MouseButton.right]: self.sig_start_clicking.emit(button)
        elif not pressed and is_worker_running:
            self.sig_stop_clicking.emit()

    # --- UI Logic Handlers ---
    def _on_mode_changed(self, *args):
        is_toggle = self.toggle_mode_radio.isChecked()
        is_burst = self.burst_mode_radio.isChecked()
        self.button_choice_widget.setVisible(is_toggle or is_burst)
        self.burst_options_widget.setVisible(is_burst)
        self.fixed_pos_widget.setVisible(is_toggle)
        self.click_limit_label.setVisible(is_toggle)
        self.click_limit_spin.setVisible(is_toggle)

    def _on_autoclicker_enabled_toggled(self, checked):
        self.autoclicker_controls_widget.setVisible(checked)
        self.autoclicker_disabled_label.setVisible(not checked)

    def _on_afk_enabled_toggled(self, checked):
        self.afk_controls_widget.setVisible(checked)
        self.afk_disabled_label.setVisible(not checked)

    def _on_afk_use_human_move_toggled(self, checked):
        self.afk_human_move_mode_combo.setEnabled(checked)
        self.afk_human_move_duration_spin.setEnabled(checked)

    def _capture_mouse_position(self):
        self.capture_pos_button.setEnabled(False)
        self.capture_countdown = 3
        self.capture_timer = QtCore.QTimer(self); self.capture_timer.timeout.connect(self._update_capture_countdown); self.capture_timer.start(1000)
        self._update_capture_countdown()

    def _update_capture_countdown(self):
        if self.capture_countdown > 0:
            self.capture_pos_button.setText(self._tr('capture_pos_button_countdown').format(count=self.capture_countdown))
            self.capture_countdown -= 1
        else:
            self.capture_timer.stop()
            self._perform_capture()

    def _perform_capture(self):
        pos = MouseController().position
        self.fixed_pos_x_spin.setValue(pos[0]); self.fixed_pos_y_spin.setValue(pos[1])
        self.capture_pos_button.setText(self._tr('capture_pos_button')); self.capture_pos_button.setEnabled(True)

    @QtCore.pyqtSlot(bool)
    def _set_always_on_top(self, checked):
        flags = self.windowFlags()
        if checked: self.setWindowFlags(flags | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        else: self.setWindowFlags(flags & ~QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def _open_color_picker(self):
        color = QtWidgets.QColorDialog.getColor(self.accent_color, self, "Select Accent Color")
        if color.isValid():
            self.accent_color = color
            self._update_theme()
            self._save_active_profile_from_ui()

    @QtCore.pyqtSlot(str)
    def _on_log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_widget.appendPlainText(log_entry)

    def _clear_logs(self):
        self.log_widget.clear()
        self.sig_log_message.emit("Logs cleared.")


    # =====================================================================
    # Profile Management
    # =====================================================================
    def _load_profiles_to_ui(self):
        self.profiles_combo.blockSignals(True)
        self.profiles_combo.clear()

        profiles = self.settings.get("profiles", {})
        if not profiles:
            default_profile = self._get_settings_from_ui()
            self.settings["profiles"] = {"Default": default_profile}
            self.settings["active_profile"] = "Default"

        profile_names = list(self.settings.get("profiles", {}).keys())
        self.profiles_combo.addItems(profile_names)

        active_profile = self.settings.get("active_profile", "Default")
        if active_profile in profile_names:
            self.profiles_combo.setCurrentText(active_profile)

        self.profiles_combo.blockSignals(False)

    def _load_active_profile_to_ui(self):
        active_profile_name = self.settings.get("active_profile", "Default")
        self.sig_log_message.emit(f"Profile '{active_profile_name}' loaded.")
        profile_data = self.settings.get("profiles", {}).get(active_profile_name, {})
        if profile_data:
            self._load_settings_to_ui(profile_data)
        self._connect_signals_for_saving()

    def _on_profile_selected(self, index):
        profile_name = self.profiles_combo.itemText(index)
        if not profile_name: return

        self.settings["active_profile"] = profile_name
        save_settings(self.settings)
        self._load_active_profile_to_ui()

    def _save_new_profile(self):
        profile_name = self.profile_name_edit.text().strip()
        if not profile_name: return

        self.sig_log_message.emit(f"Profile '{profile_name}' saved.")
        profile_data = self._get_settings_from_ui()

        if "profiles" not in self.settings: self.settings["profiles"] = {}

        self.settings["profiles"][profile_name] = profile_data
        self.settings["active_profile"] = profile_name
        save_settings(self.settings)

        self._load_profiles_to_ui()
        self.profile_name_edit.clear()

    def _delete_profile(self):
        if self.profiles_combo.count() <= 1:
            self.sig_log_message.emit("Cannot delete the last profile.")
            return

        profile_name = self.profiles_combo.currentText()
        if profile_name in self.settings.get("profiles", {}):
            self.sig_log_message.emit(f"Profile '{profile_name}' deleted.")
            del self.settings["profiles"][profile_name]
            self.settings["active_profile"] = self.profiles_combo.itemText(0)
            save_settings(self.settings)
            self._load_profiles_to_ui()
            self._load_active_profile_to_ui()

    def _import_profile(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Profile", "", "JSON Files (*.json)")
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f: profile_data = json.load(f)
            if "lmb_cps" not in profile_data or "activation_mode" not in profile_data: raise ValueError("Invalid profile structure")
            profile_name = os.path.basename(file_path).replace(".json", "")
            base_name = profile_name
            count = 1
            while profile_name in self.settings.get("profiles", {}):
                profile_name = f"{base_name}_{count}"
                count += 1
            self.settings["profiles"][profile_name] = profile_data
            self.settings["active_profile"] = profile_name
            save_settings(self.settings)
            self._load_profiles_to_ui()
            self._load_active_profile_to_ui()
            QtWidgets.QMessageBox.information(self, self._tr('profile_import_success_title'), self._tr('profile_import_success_text').format(name=profile_name))
            self.sig_log_message.emit(f"Profile '{profile_name}' imported.")
        except Exception:
            QtWidgets.QMessageBox.warning(self, self._tr('profile_import_error_title'), self._tr('profile_import_error_text'))
            self.sig_log_message.emit("Profile import failed.")

    def _export_profile(self):
        profile_name = self.profiles_combo.currentText()
        if not profile_name: return
        profile_data = self.settings.get("profiles", {}).get(profile_name)
        if not profile_data: return
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Profile", f"{profile_name}.json", "JSON Files (*.json)")
        if not file_path: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            self.sig_log_message.emit(f"Profile '{profile_name}' exported.")
        except Exception:
            self.sig_log_message.emit("Profile export failed.")

    # =====================================================================
    # Theming, Styling, and Internationalization
    # =====================================================================
    def _update_theme(self):
        QtWidgets.QApplication.setStyle("Fusion")
        is_dark = self.current_theme == "dark"
        if is_dark:
            base_color = QtGui.QColor(45, 45, 45); alt_color = QtGui.QColor(35, 35, 35); text_color = QtGui.QColor(220, 220, 220)
            border_color = QtGui.QColor("#3c3c3c"); button_color = QtGui.QColor("#555"); button_hover_color = QtGui.QColor("#666")
            button_pressed_color = QtGui.QColor("#444"); tab_bg_color = QtGui.QColor("#2d2d2d"); tab_selected_bg_color = QtGui.QColor("#454545")
        else:
            base_color = QtGui.QColor(240, 240, 240); alt_color = QtGui.QColor(255, 255, 255); text_color = QtGui.QColor(0, 0, 0)
            border_color = QtGui.QColor("#c0c0c0"); button_color = QtGui.QColor("#e1e1e1"); button_hover_color = QtGui.QColor("#f0f0f0")
            button_pressed_color = QtGui.QColor("#c8c8c8"); tab_bg_color = QtGui.QColor("#d4d4d4"); tab_selected_bg_color = QtGui.QColor("#f0f0f0")

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, base_color); palette.setColor(QtGui.QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QtGui.QPalette.ColorRole.Base, alt_color); palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, base_color)
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, text_color); palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, text_color)
        palette.setColor(QtGui.QPalette.ColorRole.Text, text_color); palette.setColor(QtGui.QPalette.ColorRole.Button, base_color)
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, text_color); palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(255, 0, 0))
        palette.setColor(QtGui.QPalette.ColorRole.Link, self.accent_color); palette.setColor(QtGui.QPalette.ColorRole.Highlight, self.accent_color)
        palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(0, 0, 0))
        self.setPalette(palette)

        accent_color_str = self.accent_color.name()
        self.color_swatch.setStyleSheet(f"background-color: {accent_color_str}; border: 1px solid {border_color.name()}; border-radius: 4px;")
        self.copyright_label.setText(COPYRIGHT_TEXT.format(ACCENT_COLOR=accent_color_str))
        self._update_info_texts()

        self.setStyleSheet(f"""
            QWidget {{ font-size: 10pt; }} #mainWidget {{ padding: 5px; }}
            QGroupBox {{ font-weight: bold; border: 1px solid {border_color.name()}; border-radius: 8px; margin-top: 1ex; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; }}
            QGroupBox:checkable::indicator {{ width: 13px; height: 13px; }}
            QPushButton {{ background-color: {button_color.name()}; border: 1px solid {border_color.name()}; padding: 8px; border-radius: 6px; }}
            QPushButton:hover {{ background-color: {button_hover_color.name()}; }} QPushButton:pressed {{ background-color: {button_pressed_color.name()}; }}
            QTabWidget::pane {{ border-top: 2px solid {border_color.name()}; }}
            QTabBar::tab {{ background: {tab_bg_color.name()}; border: 1px solid {border_color.name()}; border-bottom: none; padding: 8px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px; }}
            QTabBar::tab:selected, QTabBar::tab:hover {{ background: {tab_selected_bg_color.name()}; color: {accent_color_str}; }}
            QSlider::groove:horizontal {{ border: 1px solid {border_color.name()}; background: {border_color.name()}; height: 4px; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {accent_color_str}; border: 1px solid {accent_color_str}; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }}
            QCheckBox::indicator, QRadioButton::indicator {{ border: 1px solid #777; width: 14px; height: 14px; border-radius: 8px; }}
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{ background-color: {accent_color_str}; border-color: {accent_color_str}; }}
            #disabledLabel {{ color: #888; }}
            QPlainTextEdit {{ border: 1px solid {border_color.name()}; border-radius: 6px; }}
        """)

    # --- Settings Change Handlers ---
    def _change_language(self, index):
        self.current_language = 'en' if index == 0 else 'pl'
        self._retranslate_ui()
        self._save_active_profile_from_ui()

    def _change_theme(self, index):
        self.current_theme = 'dark' if index == 0 else 'light'
        self._update_theme()
        self._save_active_profile_from_ui()

    def _reset_settings(self):
        reply = QtWidgets.QMessageBox.question(self, self._tr('reset_confirm_title'), self._tr('reset_confirm_text'), QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.sig_log_message.emit("All settings have been reset.")
            if os.path.exists(SETTINGS_PATH): os.remove(SETTINGS_PATH)
            QtWidgets.QMessageBox.information(self, "Restart Required", "Settings have been reset. Please restart the application.")
            self.close()

    def _update_info_texts(self):
        hotkeys = {
            'activation_key': (self.activation_key_edit.text() or 'r').upper(),
            'afk_hotkey': (self.afk_hotkey_edit.text() or 'p').upper(),
            'emergency_key': (self.emergency_key_edit.text() or 'esc').upper(),
            'accent_color': self.accent_color.name()
        }
        self.autoclicker_info_label.setText(self._tr('autoclicker_info_text').format(**hotkeys))
        self.antiafk_info_label.setText(self._tr('antiafk_info_text').format(**hotkeys))

    # --- UI Retranslation ---
    def _retranslate_ui(self):
        self.setWindowTitle(self._tr('window_title'))
        self.tab_widget.setTabText(0, self._tr('tab_autoclicker')); self.tab_widget.setTabIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tab_widget.setTabText(1, self._tr('tab_antiafk')); self.tab_widget.setTabIcon(1, self.style().standardIcon(QStyle.StandardPixmap.SP_DialogYesButton))
        self.tab_widget.setTabText(2, self._tr('tab_logs')); self.tab_widget.setTabIcon(2, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView))
        self.tab_widget.setTabText(3, self._tr('tab_settings')); self.tab_widget.setTabIcon(3, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))

        self.close_button.setText(self._tr('close_button'))
        self.clear_logs_button.setText(self._tr('clear_logs_button'))

        # Autoclicker Tab
        self.lmb_box.setTitle(self._tr('lmb_box_title'))
        self.rmb_box.setTitle(self._tr('rmb_box_title'))
        self.global_settings_box.setTitle(self._tr('global_settings_title'))
        self.activation_mode_label.setText(self._tr('activation_mode_label'))
        self.hold_mode_radio.setText(self._tr('hold_mode_radio')); self.toggle_mode_radio.setText(self._tr('toggle_mode_radio')); self.burst_mode_radio.setText(self._tr('burst_mode_radio'))
        self.click_with_label.setText(self._tr('click_with_label')); self.toggle_lmb_radio.setText(self._tr('left_button_radio')); self.toggle_rmb_radio.setText(self._tr('right_button_radio'))
        self.burst_clicks_label.setText(self._tr('burst_clicks_label')); self.burst_delay_label.setText(self._tr('burst_delay_label'))
        self.fixed_pos_check.setText(self._tr('fixed_pos_check')); self.capture_pos_button.setText(self._tr('capture_pos_button'))
        self.click_limit_label.setText(self._tr('click_limit_label'))
        self.hotkey_box.setTitle(self._tr('hotkeys_title'))
        self.activation_key_label.setText(self._tr('activation_key_label'))
        self.activation_key_edit.setPlaceholderText(self._tr('activation_key_placeholder'))
        self.record_playback_box.setTitle(self._tr('record_playback_title'))
        self.record_button.setText(self._tr('stop_record_button') if self.is_recording else self._tr('record_button'))
        self.playback_button.setText(self._tr('stop_record_button') if self.playback_worker and self.playback_worker.isRunning() else self._tr('playback_button'))
        self.playback_reps_label.setText(self._tr('playback_reps_label'))
        self.recorded_clicks_count_label.setText(self._tr('recorded_clicks_label').format(count=len(self.recorded_sequence)))
        self.autoclicker_summary_box.setTitle(self._tr('autoclicker_summary_title'))
        self.autoclicker_info_box.setTitle(self._tr('autoclicker_info_title'))

        # Anti-AFK Tab
        self.antiafk_actions_box.setTitle(self._tr('antiafk_actions_title'))
        self.mouse_movement_box.setTitle(self._tr('mouse_movement_title'))
        self.key_press_box.setTitle(self._tr('key_press_title'))
        self.hotkey_box_afk.setTitle(self._tr('hotkeys_title'))
        self.perform_actions_every_label.setText(self._tr('perform_actions_every_label')); self.interval_min_label.setText(self._tr('interval_min_label')); self.interval_max_label.setText(self._tr('interval_max_label'))
        self.afk_move_mouse_check.setText(self._tr('move_mouse_check')); self.movement_range_label.setText(self._tr('movement_range_label'))
        self.afk_use_human_moves_check.setText(self._tr('use_human_moves_check'))
        self.human_move_mode_label.setText(self._tr('human_move_mode_label'))
        self.afk_human_move_mode_combo.setItemText(0, self._tr('human_move_mode_bezier1')); self.afk_human_move_mode_combo.setItemText(1, self._tr('human_move_mode_bezier2')); self.afk_human_move_mode_combo.setItemText(2, self._tr('human_move_mode_gravity'))
        self.human_move_duration_label.setText(self._tr('human_move_duration_label'))
        self.afk_return_to_start_check.setText(self._tr('return_to_start_check'))
        self.afk_click_mouse_check.setText(self._tr('click_mouse_check'))
        self.afk_scroll_mouse_check.setText(self._tr('scroll_mouse_check'))
        self.afk_press_keys_check.setText(self._tr('press_keys_check')); self.presets_label.setText(self._tr('presets_label'))
        self.custom_keys_label.setText(self._tr('custom_keys_label')); self.afk_custom_keys_edit.setPlaceholderText(self._tr('custom_keys_placeholder'))
        self.afk_hotkey_label.setText(self._tr('antiafk_hotkey_label'))
        self.afk_hotkey_edit.setPlaceholderText(self._tr('afk_hotkey_placeholder'))
        self.antiafk_summary_box.setTitle(self._tr('antiafk_summary_title'))
        self.antiafk_info_box.setTitle(self._tr('antiafk_info_title'))

        # Settings Tab
        self.module_activation_box.setTitle(self._tr('module_activation_title'))
        self.autoclicker_enabled_check.setText(self._tr('enable_autoclicker_check'))
        self.afk_enabled_check.setText(self._tr('enable_antiafk_check'))
        self.settings_box.setTitle(self._tr('app_settings_title'))
        self.profiles_box.setTitle(self._tr('profiles_title'))
        self.profile_name_label.setText(self._tr('profile_name_label'))
        self.save_profile_button.setText(self._tr('save_profile_button'))
        self.delete_profile_button.setText(self._tr('delete_profile_button'))
        self.import_profile_button.setText(self._tr('import_profile_button'))
        self.export_profile_button.setText(self._tr('export_profile_button'))
        self.language_label.setText(self._tr('language_label'))
        self.theme_label.setText(self._tr('theme_label')); self.theme_combo.setItemText(0, self._tr('theme_dark')); self.theme_combo.setItemText(1, self._tr('theme_light'))
        self.start_delay_label.setText(self._tr('start_delay_label'))
        self.emergency_key_label.setText(self._tr('emergency_key_label'))
        self.emergency_key_edit.setPlaceholderText(self._tr('emergency_key_placeholder'))
        self.limit_window_check.setText(self._tr('limit_window_check')); self.window_title_edit.setPlaceholderText(self._tr('window_title_placeholder'))
        self.always_on_top_checkbox.setText(self._tr('always_on_top_check'))
        self.accent_color_label.setText(self._tr('accent_color_label')); self.change_color_button.setText(self._tr('change_color_button'))
        self.reset_settings_label.setText(self._tr('reset_settings_label'))
        self.reset_settings_button.setText(self._tr('reset_settings_button'))

        self.autoclicker_disabled_label.setText(self._tr('module_disabled_info'))
        self.afk_disabled_label.setText(self._tr('module_disabled_info'))

        self._update_info_texts()

    def _update_summaries(self, *args):
        self._update_autoclicker_summary()
        self._update_antiafk_summary()

    def _update_autoclicker_summary(self):
        summary_parts = []
        mode = "Hold"
        if self.toggle_mode_radio.isChecked(): mode = "Toggle"
        if self.burst_mode_radio.isChecked(): mode = "Burst"
        summary_parts.append(f"• Mode: <b>{mode}</b>")

        if mode in ["Toggle", "Burst"]:
            button = "Left" if self.toggle_lmb_radio.isChecked() else "Right"
            summary_parts.append(f"• Clicking with: <b>{button} Button</b>")

        lmb_cps = self.lmb_box.widgets['slider'].value() / 10.0
        rmb_cps = self.rmb_box.widgets['slider'].value() / 10.0
        summary_parts.append(f"• CPS: <b>LMB: {lmb_cps:.1f} / RMB: {rmb_cps:.1f}</b>")

        if mode == "Toggle":
            limit = self.click_limit_spin.value()
            limit_text = f"{limit if limit > 0 else 'Unlimited'}"
            summary_parts.append(f"• Click Limit: <b>{limit_text}</b>")

        if mode == "Burst":
            clicks = self.burst_clicks_spin.value()
            delay = self.burst_delay_spin.value()
            summary_parts.append(f"• Burst clicks: <b>{clicks}</b> (delay: {delay}ms)")

        self.autoclicker_summary_label.setText("<br>".join(summary_parts))

    def _update_antiafk_summary(self):
        summary_parts = []
        min_t = self.afk_min_interval_spin.value()
        max_t = self.afk_max_interval_spin.value()
        summary_parts.append(f"• Interval: <b>{min_t} - {max_t}s</b>")

        if self.afk_move_mouse_check.isChecked():
            rng = self.afk_mouse_range_spin.value()
            human = " (Human-like)" if self.afk_use_human_moves_check.isChecked() else ""
            summary_parts.append(f"• Mouse Move: <b>Yes (±{rng}px){human}</b>")

        if self.afk_click_mouse_check.isChecked():
            summary_parts.append("• Mouse Click: <b>Yes</b>")

        if self.afk_scroll_mouse_check.isChecked():
            summary_parts.append("• Mouse Scroll: <b>Yes</b>")

        if self.afk_press_keys_check.isChecked():
            keys = []
            if self.afk_key_w.isChecked(): keys.append('W')
            if self.afk_key_a.isChecked(): keys.append('A')
            if self.afk_key_s.isChecked(): keys.append('S')
            if self.afk_key_d.isChecked(): keys.append('D')
            if self.afk_key_space.isChecked(): keys.append('Space')
            custom = self.afk_custom_keys_edit.text()
            if custom:
                keys.append(f"Custom({custom})")

            if keys:
                summary_parts.append(f"• Key Press: <b>{', '.join(keys)}</b>")
            else:
                summary_parts.append("• Key Press: <b>Yes (No keys selected)</b>")


        if len(summary_parts) == 1:
            summary_text = "<b>No actions enabled.</b> Only the interval is set."
        else:
            summary_text = "<br>".join(summary_parts)

        self.antiafk_summary_label.setText(summary_text)

    # =====================================================================
    # Application Lifecycle
    # =====================================================================

    def closeEvent(self, event):
        if self.worker: self.worker.stop()
        if self.afk_worker: self.afk_worker.stop()
        if self.playback_worker: self.playback_worker.stop()
        self.mouse_listener.stop(); self.keyboard_listener.stop()
        event.accept()
        QtWidgets.QApplication.quit() # Ensure the application exits cleanly

    def _verify_integrity(self):
        if "Piotrunius" not in self.copyright_label.text():
            msg_box = QtWidgets.QMessageBox(self); msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg_box.setText("Application Integrity Error."); msg_box.setInformativeText("The author's attribution has been modified or removed. The application will now close.")
            msg_box.setWindowTitle("Error"); msg_box.exec(); sys.exit(1)

# ==================================================================================================
#                                 APPLICATION ENTRY POINT
# ==================================================================================================
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
