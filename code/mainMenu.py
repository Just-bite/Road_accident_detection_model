from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class MainMenuScreen(QWidget):
    def __init__(self, parent, username, role):
        super().__init__()
        self.parent = parent
        self.username = username
        self.role = role
        self.layout_main = QVBoxLayout()
        self.setLayout(self.layout_main)
        self.setup_ui()

    def setup_ui(self):

        content_layout = QHBoxLayout()
        self.layout_main.addLayout(content_layout)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(5)

        btn_reports = QPushButton("Reports Archive")
        btn_datasets = QPushButton("Datasets")
        btn_reports.clicked.connect(self.show_reports_archive)
        btn_datasets.clicked.connect(self.show_datasets)
        left_panel.addWidget(btn_reports)
        left_panel.addWidget(btn_datasets)

        if self.role in ("admin", "analyst"):
            btn_settings = QPushButton("Model Settings")
            btn_settings.clicked.connect(self.show_model_settings)
            left_panel.addWidget(btn_settings)
            left_panel.addSpacing(btn_settings.sizeHint().height())
            btn_start = QPushButton("Start Analysis")
            btn_start.clicked.connect(self.show_start_analysis)
            left_panel.addWidget(btn_start)

        content_layout.addLayout(left_panel, stretch=1)

        right_panel = QVBoxLayout()
        right_panel.addStretch(2)

        font_label = QFont()
        font_label.setPointSize(12)
        font_label.setBold(True)

        # Username
        hl_user = QHBoxLayout()
        lbl_user_text = QLabel("Username:")
        lbl_user_text.setFont(font_label)
        lbl_user_text.setStyleSheet("color: white;")
        lbl_username = QLabel(self.username)
        lbl_username.setFont(font_label)
        lbl_username.setStyleSheet("color: white;")

        btn_logout = QPushButton("Logout")
        btn_logout.clicked.connect(self.logout)

        hl_user.addWidget(lbl_user_text)
        hl_user.addWidget(lbl_username)
        hl_user.addStretch(1)
        hl_user.addWidget(btn_logout)
        right_panel.addLayout(hl_user)

        # Role строка
        hl_role = QHBoxLayout()
        lbl_role_text = QLabel("Role:")
        lbl_role_text.setFont(font_label)
        lbl_role_text.setStyleSheet("color: white;")
        lbl_role = QLabel(self.role)
        lbl_role.setFont(font_label)
        lbl_role.setStyleSheet("color: white;")
        hl_role.addWidget(lbl_role_text)
        hl_role.addWidget(lbl_role)
        hl_role.addStretch(1)

        if self.role == "admin":
            btn_manage = QPushButton("Manage Users")
            btn_manage.clicked.connect(self.show_manage_users)
            hl_role.addWidget(btn_manage)

        right_panel.addLayout(hl_role)
        right_panel.addSpacing(40)

        banner = QLabel()
        pix = QPixmap("banner_green.png")
        banner.setPixmap(pix)
        banner.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(banner)
        right_panel.addStretch(3)

        content_layout.addLayout(right_panel, stretch=2)

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