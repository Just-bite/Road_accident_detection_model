from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QLineEdit,
    QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from functools import partial

class ManageUsersScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.all_users = []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by username...")
        self.search_input.textChanged.connect(self.filter_users)
        top_bar.addWidget(self.search_input)

        self.add_btn = QPushButton("Add User")
        self.add_btn.setStyleSheet("""
            QPushButton { color: white; border: 2px solid #00FF00; background-color: #2d2d2d; padding: 3px 8px; }
            QPushButton:hover { background-color: #3a3a3a; }
        """)
        self.add_btn.clicked.connect(self.add_user)
        top_bar.addWidget(self.add_btn)

        user_role = getattr(self.parent, "user_role", None)
        if user_role in ("admin", "analyst"):
            self.add_btn.setEnabled(True)
        else:
            self.add_btn.setDisabled(True)

        self.layout.addLayout(top_bar)

        self.users_container = QFrame()
        self.users_container.setStyleSheet("background-color: #2d2d2d;")
        self.users_layout = QVBoxLayout()
        self.users_layout.setContentsMargins(5,5,5,5)
        self.users_layout.setSpacing(5)
        self.users_container.setLayout(self.users_layout)
        self.layout.addWidget(self.users_container)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.back_to_menu)
        self.layout.addWidget(back_btn, alignment=Qt.AlignRight)

        self.refresh_users()

    def clear_users_layout(self):
        while self.users_layout.count():
            child = self.users_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def refresh_users(self):
        try:
            cur = self.parent.conn.cursor()
            cur.execute("SELECT id, username, role, activator_id FROM users ORDER BY id")
            self.all_users = cur.fetchall()
            cur.close()
            self.display_users(self.all_users)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def display_users(self, users):
        self.clear_users_layout()
        current_user = getattr(self.parent, "current_username", None)

        for user_id, username, role, activator_id in users:
            if username == current_user:
                continue

            hbox = QHBoxLayout()
            label = QLabel(f"{username} ({role})")
            label.setStyleSheet("color: white;")
            hbox.addWidget(label)

            change_btn = QPushButton("Change Role")
            del_btn = QPushButton("Delete")
            for btn in [change_btn, del_btn]:
                btn.setStyleSheet("""
                    QPushButton {
                        color: white; border: 2px solid #00FF00; background-color: #2d2d2d; padding: 3px 8px;
                    }
                    QPushButton:hover { background-color: #3a3a3a; }
                """)
            change_btn.clicked.connect(partial(self.change_role, user_id, role))
            del_btn.clicked.connect(partial(self.delete_user, user_id))

            hbox.addWidget(change_btn)
            hbox.addWidget(del_btn)
            self.users_layout.addLayout(hbox)

    def filter_users(self):
        text = self.search_input.text().strip().lower()
        if not text:
            self.display_users(self.all_users)
            return

        matched = [u for u in self.all_users if text in u[1].lower()]
        unmatched = [u for u in self.all_users if text not in u[1].lower()]
        self.display_users(matched + unmatched)

    def add_user(self):
        print("Add user button clicked")
        try:
            username, ok = QInputDialog.getText(self, "Add User", "Enter new username:")
            if not ok or not username.strip():
                print("Add user cancelled or empty")
                return
            username = username.strip()

            cur = self.parent.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            if cur.fetchone()[0] > 0:
                QMessageBox.warning(self, "Error", f"Username '{username}' already exists.")
                cur.close()
                return

            activator, ok2 = QInputDialog.getText(
                self, "Activator (optional)",
                "Enter activator code for analyst (or leave empty):"
            )
            activator = activator.strip() if ok2 else ""

            default_password = "default_pass"  # обязательно для NOT NULL

            if activator:
                cur.execute(
                    "INSERT INTO users (username, password, role, activator_id, created_at) "
                    "VALUES (%s, %s, 'analyst', NULL, NOW()) RETURNING id",
                    (username, default_password)
                )
                cur.execute(
                    "INSERT INTO activators (activator_code, role, is_used, created_by, created_at) "
                    "VALUES (%s, 'analyst', TRUE, 1, NOW())",
                    (activator,)
                )
            else:
                cur.execute(
                    "INSERT INTO users (username, password, role, activator_id, created_at) "
                    "VALUES (%s, %s, 'observer', NULL, NOW())",
                    (username, default_password)
                )

            self.parent.conn.commit()
            cur.close()
            print(f"User '{username}' added successfully")
            self.clear_users_layout() ###
            self.refresh_users()

        except Exception as e:
            print("Database error in add_user:", e)
            QMessageBox.critical(self, "Database Error", str(e))

    def change_role(self, user_id, current_role):
        try:
            cur = self.parent.conn.cursor()
            if current_role == "analyst":
                cur.execute("SELECT activator_id FROM users WHERE id = %s", (user_id,))
                act_id = cur.fetchone()[0]
                cur.execute("UPDATE users SET role = 'observer', activator_id = NULL WHERE id = %s", (user_id,))
                if act_id:
                    cur.execute("UPDATE activators SET is_used = FALSE WHERE id = %s", (act_id,))
            else:
                cur.execute("SELECT id FROM activators WHERE role = 'analyst' AND is_used = FALSE LIMIT 1")
                act = cur.fetchone()
                if not act:
                    QMessageBox.warning(self, "Error", "No free analyst activators available.")
                    cur.close()
                    return
                activator_id = act[0]
                cur.execute("UPDATE users SET role = 'analyst', activator_id = %s WHERE id = %s", (activator_id, user_id))
                cur.execute("UPDATE activators SET is_used = TRUE WHERE id = %s", (activator_id,))

            self.parent.conn.commit()
            cur.close()
            self.refresh_users()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def delete_user(self, user_id):
        try:
            cur = self.parent.conn.cursor()
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.parent.conn.commit()
            cur.close()
            self.refresh_users()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def back_to_menu(self):
        try:
            cur = self.parent.conn.cursor()
            cur.execute("SELECT role FROM users WHERE username = %s", (self.parent.current_username,))
            role = cur.fetchone()[0]
            cur.close()
            self.parent.user_role = role  # <- сохраняем роль родителю
            self.parent.show_main_menu(self.parent.current_username, role)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))