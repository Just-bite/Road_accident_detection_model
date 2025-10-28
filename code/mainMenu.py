from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class MainMenuScreen(QWidget):
    def __init__(self, parent, username, role):
        super().__init__()
        self.parent = parent
        self.username = username
        self.role = role
        self.setStyleSheet("background-color: #121212; color: white;")
        self.layout_main = QHBoxLayout()
        self.setLayout(self.layout_main)
        self.setup_ui()

    def setup_ui(self):
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)
        left_panel.setContentsMargins(10, 10, 10, 10)

        left_panel.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        buttons_info = [
            ("Reports Archive", self.show_reports_archive),
            ("Datasets", self.show_datasets)
        ]

        if self.role in ("admin", "analyst"):
            buttons_info.extend([
                ("Model Settings", self.show_model_settings),
                ("Start Analysis", self.show_start_analysis)
            ])

        for text, func in buttons_info:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(50)
            btn.setFont(QFont("Courier New", 11, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                      stop:0 #1B1B1B, stop:1 #2D2D2D);
                    border: 2px solid #00FF00;
                    border-radius: 10px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #00FF00;
                    color: black;
                }
            """)
            btn.clicked.connect(func)
            left_panel.addWidget(btn)

        left_panel.addStretch()
        self.layout_main.addLayout(left_panel, stretch=1)

        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(20, 20, 20, 20)
        right_panel.setSpacing(15)

        right_panel.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        font_label = QFont("Courier New", 12, QFont.Bold)

        hl_user = QHBoxLayout()
        lbl_user_text = QLabel("Username:")
        lbl_user_text.setFont(font_label)
        lbl_user_text.setStyleSheet("color: #00FF00;")
        lbl_username = QLabel(self.username)
        lbl_username.setFont(font_label)
        lbl_username.setStyleSheet("color: white;")

        btn_logout = QPushButton("Logout")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #2D2D2D;
                border: 2px solid #FF0000;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover { background-color: #FF0000; color: white; }
        """)
        btn_logout.clicked.connect(self.logout)

        hl_user.addWidget(lbl_user_text)
        hl_user.addWidget(lbl_username)
        hl_user.addStretch(1)
        hl_user.addWidget(btn_logout)
        right_panel.addLayout(hl_user)

        hl_role = QHBoxLayout()
        lbl_role_text = QLabel("Role:")
        lbl_role_text.setFont(font_label)
        lbl_role_text.setStyleSheet("color: #00FF00;")
        lbl_role = QLabel(self.role)
        lbl_role.setFont(font_label)
        lbl_role.setStyleSheet("color: white;")

        hl_role.addWidget(lbl_role_text)
        hl_role.addWidget(lbl_role)
        hl_role.addStretch(1)

        if self.role == "admin":
            btn_manage = QPushButton("Manage Users")
            btn_manage.setCursor(Qt.PointingHandCursor)
            btn_manage.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #2D2D2D;
                    border: 2px solid #00FF00;
                    border-radius: 6px;
                    padding: 4px 10px;
                }
                QPushButton:hover { background-color: #00FF00; color: black; }
            """)
            btn_manage.clicked.connect(self.show_manage_users)
            hl_role.addWidget(btn_manage)

        right_panel.addLayout(hl_role)
        right_panel.addSpacing(40)

        banner_frame = QFrame()
        banner_frame.setStyleSheet("background-color: #1B1B1B; border-radius: 10px;")
        banner_layout = QVBoxLayout()
        banner = QLabel()
        pix = QPixmap("banner_green.png")
        banner.setPixmap(pix)
        banner.setAlignment(Qt.AlignCenter)
        banner_layout.addWidget(banner)
        banner_frame.setLayout(banner_layout)

        right_panel.addWidget(banner_frame)
        right_panel.addStretch(3)

        self.layout_main.addLayout(right_panel, stretch=3)

    def logout(self):
        self.parent.show_auth_screen()

    def show_manage_users(self):
        self.parent.show_manage_users_screen()

    def show_model_settings(self):
        self.parent.show_model_settings_screen()

    def show_datasets(self):
        self.parent.show_datasets_screen()

    def show_reports_archive(self):
        self.parent.show_reports_archive_screen()

    def show_start_analysis(self):
        self.parent.show_start_analysis_screen()