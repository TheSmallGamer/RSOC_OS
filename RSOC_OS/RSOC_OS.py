import sys
import os
import configparser
import getpass
import threading
import keyboard
from functools import partial

from PySide6.QtWidgets import (
    QApplication, QGraphicsOpacityEffect, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QMenu, QMessageBox, QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import QEvent, Qt, QSize, QPropertyAnimation, QRect, QEasingCurve, QTimer

from lib.utils import QIcon, QPixmap, tint_icon
import lib.settings_window as settings_window
from lib import sitreps_menu, websites
from lib.bulletin_form import BulletinForm # type: ignore
from lib.elt_details import get_elt_details_widget # type: ignore
from lib.contact_directory import get_contact_directory_widget # type: ignore
from lib.bolo_generator import get_bolo_generator_widget # type: ignore
from lib.documents_widget import get_documents_widget # type: ignore
from lib.folders_widget import FoldersWidget #type: ignore
from lib.email_formats_widget import EmailFormatsWidget #type: ignore

CUSTOM_EXIT_EVENT = QEvent.Type(QEvent.registerEventType())

class RSOC_Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSOC-OS")
        self.setWindowIcon(QIcon('images/rsoc-os logo.png'))
        self.setGeometry(100, 100, 800, 500)

        self.current_user = getpass.getuser()
        self.config = configparser.ConfigParser()
        self.config.read('./config/settings.ini')

        self.buttons_info = [
            ("home.png", "Home"),
            ("clipboard.png", "Clipboard"),
            ("notes.png", "QuickNotes"),
            ("alert.png", "Alerts"),
            ("question.png", "UserGuide"),
            ("settings.png", "Settings")
        ]

        self.load_theme()
        self.setup_ui()

    def load_theme(self):
        theme = self.config.get(self.current_user, 'theme', fallback='dark')
        theme_file = f'./themes/{theme}.qss'
        if os.path.exists(theme_file):
            with open(theme_file, "r") as file:
                self.setStyleSheet(file.read())

    def setup_ui(self):
        outer_layout = QVBoxLayout()   # This will hold TitleBox + MainContent

        # ===== Sidebar =====
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_buttons = []

        theme = self.config.get(self.current_user, 'theme', fallback='dark')
        icon_color = "#FFFFFF" if theme == "dark" else "#000000"

        tooltip_names = {
            "Home": "Dashboard",
            "QuickNotes": "Quick Notes",
            "Alerts": "Alerts Center",
            "UserGuide": "User Guide",
            "Settings": "Settings"
        }

        for icon_file, action_name in self.buttons_info:
            btn = QPushButton()
            btn.setIcon(tint_icon(f'images/{icon_file}', icon_color))
            btn.setIconSize(QSize(32, 32))
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("border: none;")
            btn.setToolTip(tooltip_names.get(action_name, action_name))
            btn.clicked.connect(partial(self.handle_button_action, action_name))
            self.sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        self.sidebar_layout.addStretch()

        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(68)               # Lock Sidebar Width
        sidebar_widget.setLayout(self.sidebar_layout)
        sidebar_widget.setObjectName("SidebarBox")

        # ===== TitleBox =====
        title_layout = QHBoxLayout()
        title_layout.setObjectName("TitleBox")

        icon_label = settings_window.QLabel()
        icon_pixmap = QPixmap('images/rsoc-os logo.png').scaled(62, 62, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)

        self.title_label = settings_window.QLabel("RSOC OPERATING SYSTEM")
        self.title_label.setObjectName("TitleLabel")

        title_layout.addWidget(icon_label)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Wrap the layout in a QWidget to add it properly
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        title_widget.setFixedHeight(60)   # Lock TitleBox Height

        # ===== Grid Content =====
        grid_layout = QGridLayout()
        self.grid_buttons_info = [
        ("Cameras", "OpenCameras"),
        ("Sitreps", "OpenSitreps"),
        ("Bulletin", "OpenBulletin"),
        ("BOLO", "OpenBOLO"),
        ("Folders", "OpenFolders"),
        ("Documents", "OpenDocuments"),
        ("Contact Directory", "OpenContacts"),
        ("Email Formats", "OpenEmailFormats"),
        ("Websites", "OpenWebsites"),
        ("ELT Details", "OpenELTDetails")
    ]

        # ===== Outer vertical layout (Title + Main Content) =====
        outer_layout = QVBoxLayout()

        # Add the wrapped title widget
        outer_layout.addWidget(title_widget)

        # ===== Main horizontal layout (Sidebar + Content) =====
        main_content_layout = QHBoxLayout()
        main_content_layout.addWidget(sidebar_widget)

        # Create a container for dynamic content (grid + future features)
        self.dynamic_content = QWidget()
        self.dynamic_layout = QGridLayout()
        self.dynamic_content.setLayout(self.dynamic_layout)

        self.build_grid_buttons()

        main_content_layout.addWidget(self.dynamic_content)

        # Lock sidebar, allow dynamic_content to stretch
        main_content_layout.setStretch(0, 0)   # Sidebar fixed
        main_content_layout.setStretch(1, 1)   # Content resizes

        # Add main content layout under the title
        outer_layout.addLayout(main_content_layout)

        self.setLayout(outer_layout)
        self.adjustSize()

    def refresh_icons(self):
        theme = self.config.get(self.current_user, 'theme', fallback='dark')
        icon_color = "#FFFFFF" if theme == "dark" else "#000000"

        for btn, (icon_file, _) in zip(self.sidebar_buttons, self.buttons_info):
            btn.setIcon(tint_icon(f'images/{icon_file}', icon_color))

    # ==== BUTTON HANDLER ====
    def handle_button_action(self, action_name):
        if action_name == "Settings":
            settings_window.open_settings(self)
        elif action_name == "Home":
            self.load_dashboard()
        elif action_name == "QuickNotes":
            self.load_quick_notes()
        elif action_name == "Clipboard":
            self.load_clipboard()
        elif action_name == "Alerts":
            self.load_alerts_center()
        elif action_name == "OpenCameras":
            self.load_camera_selector()
        elif action_name == "OpenSitreps":
            self.load_sitreps_menu()
        elif action_name == "OpenBulletin":
            self.show_bulletin_form()
        elif action_name == "OpenWebsites":
            self.load_websites()
        elif action_name == "OpenELTDetails":
            self.load_elt_details()
        elif action_name == "OpenContacts":
            self.load_contact_directory()
        elif action_name == "OpenBOLO":
            self.load_bolo_generator()
        elif action_name == "OpenDocuments":
            self.load_documents()
        elif action_name == "OpenFolders":
            self.load_folders()
        elif action_name == "OpenEmailFormats":
            self.load_email_formats()
        else:
            print(f"Action triggered: {action_name}")

    # Add new Load Module functions below this line 
     
    def load_email_formats(self):
        self.clear_content_area()
        widget = EmailFormatsWidget()  
        self.dynamic_layout.addWidget(widget)
        self.animate_window_resize(QSize(400, 400))
        self.animate_fade_in(widget)

    def load_folders(self):
        self.clear_content_area()
        widget = FoldersWidget()
        self.dynamic_layout.addWidget(widget)
        self.animate_window_resize(QSize(740, 500))
        self.animate_fade_in(widget)

    def load_documents(self):
        self.clear_content_area()
        widget = get_documents_widget()
        self.dynamic_layout.addWidget(widget)
        self.animate_window_resize(QSize(600, 400))
        self.animate_fade_in(widget)

    def load_bolo_generator(self):
        self.clear_content_area()
        widget = get_bolo_generator_widget()
        self.dynamic_layout.addWidget(widget)
        self.animate_window_resize(QSize(900, 500))
        self.animate_fade_in(widget)

    def load_contact_directory(self):
        self.clear_content_area()
        widget = get_contact_directory_widget()
        self.dynamic_layout.addWidget(widget)
        self.animate_window_resize(QSize(1400, 500))  # adjust if needed
        self.animate_fade_in(widget)

    def load_elt_details(self):
        self.clear_content_area()
        from lib.elt_details import get_elt_details_widget  # type: ignore
        widget = get_elt_details_widget(parent=self)
        self.dynamic_layout.addWidget(widget)
        self.animate_window_resize(QSize(1470, 800))
        self.animate_fade_in(widget)

    def show_bulletin_form(self):
        self.clear_content_area()
        from lib.bulletin_form import get_bulletin_form_widget  # type: ignore
        widget = get_bulletin_form_widget()
        self.dynamic_layout.addWidget(widget)
        self.animate_window_resize(QSize(400, 300))   # tweak size as you like
        self.animate_fade_in(widget)

    def load_camera_selector(self):
        self.clear_content_area()
        from lib.milestone_launcher import get_milestone_launcher_widget # type: ignore
        widget = get_milestone_launcher_widget()
        self.dynamic_layout.addWidget(widget)
        self.animate_window_resize(QSize(400, 400))
        self.animate_fade_in(widget)

    def load_websites(self):
        self.clear_content_area()
        selector = websites.get_website_selector_widget(parent=self)
        self.dynamic_layout.addWidget(selector)
        self.animate_window_resize(QSize(400, 400))
        self.animate_fade_in(selector)

    def load_embedded_browser(self, url):
        self.clear_content_area()
        browser_widget = websites.get_webview_widget(url, back_callback=self.load_websites)
        self.dynamic_layout.addWidget(browser_widget)
        self.animate_window_resize(QSize(1600, 900))
        self.animate_fade_in(browser_widget)


    def load_sitreps_menu(self):
        self.clear_content_area()
        from lib import sitreps_menu
        sitreps_widget = sitreps_menu.get_sitreps_menu_widget(self)
        self.dynamic_layout.addWidget(sitreps_widget)
        self.resize_with_animation(400, 400)
        self.animate_fade_in(sitreps_widget)

    def resize_with_animation(self, target_width, target_height):
        from PySide6.QtCore import QPropertyAnimation, QRect, QEasingCurve

        current_geometry = self.geometry()
        target_geometry = QRect(
            current_geometry.x(),
            current_geometry.y(),
            target_width,
            target_height
        )

        self.resize_anim = QPropertyAnimation(self, b"geometry")
        self.resize_anim.setDuration(500)
        self.resize_anim.setStartValue(current_geometry)
        self.resize_anim.setEndValue(target_geometry)
        self.resize_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.resize_anim.start()


    def load_alerts_center(self):
        self.clear_content_area()
        from lib import alerts_center
        alerts_widget = alerts_center.get_alerts_widget(self)
        self.dynamic_layout.addWidget(alerts_widget)
        self.animate_window_resize(QSize(950, 600))
        self.animate_fade_in(alerts_widget)

    def load_clipboard(self):
        self.clear_content_area()
        from lib import clipboard_manager
        clipboard_widget = clipboard_manager.get_clipboard_widget(self)
        self.dynamic_layout.addWidget(clipboard_widget)
        self.animate_window_resize(QSize(950, 600))
        self.animate_fade_in(clipboard_widget)

    def load_quick_notes(self):
        self.clear_content_area()
        from lib import quick_notes
        notes_widget = quick_notes.get_quick_notes_widget(self)
        self.dynamic_layout.addWidget(notes_widget)
        self.animate_window_resize(QSize(900, 600))
        self.animate_fade_in(notes_widget)

    def animate_fade_in(self, widget, duration=500):
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        from PySide6.QtCore import QPropertyAnimation

        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)

        self.fade_anim = QPropertyAnimation(effect, b"opacity")
        self.fade_anim.setDuration(duration)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.resize_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_anim.start()

    def animate_window_resize(self, target_size, duration=500):
        from PySide6.QtCore import QRect, QEasingCurve, QPropertyAnimation

        current_geometry = self.geometry()

        self.resize_anim = QPropertyAnimation(self, b"geometry")
        self.resize_anim.setDuration(duration)
        self.resize_anim.setStartValue(current_geometry)
        self.resize_anim.setEndValue(QRect(
            current_geometry.x(),
            current_geometry.y(),
            target_size.width(),
            target_size.height()
        ))
        self.resize_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.resize_anim.start()

    def animate_dashboard_transition(self):
        # --- Fade-in Effect for Content Area ---
        effect = QGraphicsOpacityEffect()
        self.dynamic_content.setGraphicsEffect(effect)

        self.fade_anim = QPropertyAnimation(effect, b"opacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.start()

        # --- Smooth Window Resize ---
        current_geometry = self.geometry()
        self.layout().activate()
        target_size = self.dynamic_content.sizeHint()

        self.resize_anim = QPropertyAnimation(self, b"geometry")
        self.resize_anim.setDuration(500)
        self.resize_anim.setStartValue(current_geometry)
        self.resize_anim.setEndValue(QRect(
            current_geometry.x(),
            current_geometry.y(),
            target_size.width(),
            target_size.height()
        ))
        self.resize_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.resize_anim.start()

    def load_dashboard(self):
        self.clear_content_area()
        self.build_grid_buttons()
        self.animate_dashboard_transition()

    def clear_content_area(self):
        for i in reversed(range(self.dynamic_layout.count())):
            widget_to_remove = self.dynamic_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

    def build_grid_buttons(self):
        positions = [(i,j) for i in range(4) for j in range(3)]
        for position, (label, action_name) in zip(positions, self.grid_buttons_info):
            btn = QPushButton(label)
            btn.setFixedSize(150, 80)
            btn.clicked.connect(partial(self.handle_button_action, action_name))
            self.dynamic_layout.addWidget(btn, *position)

    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def event(self, event):
        if event.type() == QEvent.User:
            self.toggle_window()
            return True
        elif event.type() == CUSTOM_EXIT_EVENT:
            QApplication.quit()
            return True
        return super().event(event)


    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RSOC_Dashboard()
    window.hide()  # Start hidden on launch

    def handle_f7():
        app = QApplication.instance()
        if app:
            app.postEvent(window, QEvent(QEvent.User))  # Thread-safe toggle

    def handle_close():
        app = QApplication.instance()
        if app:
            app.postEvent(window, QEvent(CUSTOM_EXIT_EVENT))

    # Register F7 hotkey in background thread
    threading.Thread(target=lambda: keyboard.add_hotkey('F7', handle_f7), daemon=True).start()
    threading.Thread(target=lambda: keyboard.add_hotkey('ctrl+shift+alt+q', handle_close), daemon=True).start()

    sys.exit(app.exec())



