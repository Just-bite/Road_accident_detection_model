import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QMessageBox,
)
from authentication import AuthScreen
from dataSets import DatasetsScreen
from mainMenu import MainMenuScreen
from userManager import ManageUsersScreen
from analysis import StartAnalysisScreen
from reports import ReportsArchiveScreen
from modelSettings import ModelSettingsScreen

class RoadDetectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Road Detection Model")
        self.setGeometry(100, 100, 1000, 700)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.conn = self.connect_db()
        self.current_username = None
        self.apply_global_style()
        self.show_auth_screen()

    def apply_global_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;  /* серо-черный фон */
                color: white;                /* белый текст */
                font-size: 14px;
            }
            QLabel {
                color: white;
            }
            QLineEdit, QComboBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #00FF00;
                padding: 3px;
            }
            QPushButton {
                color: white;
                background-color: #2d2d2d;
                border: 2px solid #00FF00;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QScrollArea {
                background-color: #2d2d2d;
            }
            QCheckBox {
                color: white;
            }
        """)

    def connect_db(self):
        try:
            return psycopg2.connect(
                host="localhost",
                database="WTS_db",
                user="postgres",
                password="Sadccttyy88jjrrnn77228822"
            )
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            sys.exit(1)

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_auth_screen(self):
        self.clear_layout()
        self.layout.addWidget(AuthScreen(self))

    def show_main_menu(self, username, role):
        self.clear_layout()
        self.layout.addWidget(MainMenuScreen(self, username, role))

    def show_manage_users_screen(self):
        self.clear_layout()
        self.layout.addWidget(ManageUsersScreen(self))

    def show_model_settings_screen(self):
        self.clear_layout()
        self.layout.addWidget(ModelSettingsScreen(self))

    def show_datasets_screen(self):
        self.clear_layout()
        self.layout.addWidget(DatasetsScreen(self))

    def show_reports_archive_screen(self):
        self.clear_layout()
        self.layout.addWidget(ReportsArchiveScreen(self))

    def show_start_analysis_screen(self):
        self.clear_layout()
        self.layout.addWidget(StartAnalysisScreen(self))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoadDetectionApp()
    window.show()
    sys.exit(app.exec_())
