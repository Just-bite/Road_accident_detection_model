import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QHBoxLayout, QMessageBox,
    QMenuBar, QFileDialog, QAction,
    QListWidget, QLineEdit, QTextEdit,
    QListWidgetItem, QDialog, QPlainTextEdit
)
from PyQt5.QtCore import Qt
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QTextDocument

class ReportsArchiveScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.root_path = r"E:\WTS\wts_dataset_zip\reports\val"
        self.current_path = self.root_path
        self.current_doc_path = None
        self.search_matches = []
        self.current_match_index = -1

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # === Верхнее меню ===
        menu_bar = QMenuBar()

        # --- File ---
        file_menu = menu_bar.addMenu("File")
        export_action = QAction("Export (Ctrl+E)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_action)

        # Опция удаления — только для admin / analyst
        cur = self.parent.conn.cursor()
        cur.execute("SELECT role FROM users WHERE username = %s", (self.parent.current_username,))
        role = cur.fetchone()[0]
        cur.close()
        self.user_role = role

        if role in ("admin", "analyst"):
            delete_action = QAction("Delete Report", self)
            delete_action.triggered.connect(self.delete_report)
            file_menu.addAction(delete_action)

        # --- Help ---
        help_menu = menu_bar.addMenu("Help")
        help_action = QAction("How this works", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        self.layout.setMenuBar(menu_bar)

        # === Основная область ===
        main_area = QHBoxLayout()

        # --- Левая панель ---
        left_panel = QVBoxLayout()
        self.path_label = QLabel(self.current_path)
        self.path_label.setStyleSheet("font-weight: bold; color: gray;")
        left_panel.addWidget(self.path_label)

        self.folder_list = QListWidget()
        self.folder_list.itemClicked.connect(self.on_item_clicked)
        left_panel.addWidget(self.folder_list)
        main_area.addLayout(left_panel, 2)

        # --- Правая панель ---
        right_panel = QVBoxLayout()

        # Поисковая строка + кнопки Next/Prev
        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search in document...")
        self.search_field.textChanged.connect(self.highlight_text)
        search_layout.addWidget(self.search_field)

        self.btn_prev = QPushButton("⬆️ Prev")
        self.btn_prev.clicked.connect(self.goto_prev_match)
        self.btn_next = QPushButton("⬇️ Next")
        self.btn_next.clicked.connect(self.goto_next_match)
        search_layout.addWidget(self.btn_prev)
        search_layout.addWidget(self.btn_next)

        right_panel.addLayout(search_layout)

        # Текстовое окно
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(False)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                font-family: Consolas, monospace;
                font-size: 14px;
                border: 1px solid #008000;
                padding: 8px;
            }
        """)
        right_panel.addWidget(self.text_edit, 6)

        main_area.addLayout(right_panel, 5)
        self.layout.addLayout(main_area)

        # === Нижняя панель ===
        bottom_bar = QHBoxLayout()
        self.up_btn = QPushButton("⬆️ Up")
        self.up_btn.clicked.connect(self.go_up)
        bottom_bar.addWidget(self.up_btn, alignment=Qt.AlignLeft)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.back_to_menu)
        bottom_bar.addWidget(back_btn, alignment=Qt.AlignLeft)
        self.layout.addLayout(bottom_bar)

        # === Загрузка начальной папки ===
        self.load_folder(self.root_path)

    # --- Загрузка папки ---
    def load_folder(self, path):
        self.folder_list.clear()
        self.current_path = path
        self.path_label.setText(path)

        try:
            items = os.listdir(path)
        except PermissionError:
            QMessageBox.warning(self, "Access Denied", f"Cannot access {path}")
            return

        folders = [f for f in items if os.path.isdir(os.path.join(path, f))]
        docs = [f for f in items if f.lower().endswith((".docx", ".txt"))]

        for folder in folders:
            item = QListWidgetItem(f"📁 {folder}")
            item.setData(Qt.UserRole, os.path.join(path, folder))
            item.setData(Qt.UserRole + 1, "folder")
            self.folder_list.addItem(item)

        for doc in docs:
            item = QListWidgetItem(f"📄 {doc}")
            item.setData(Qt.UserRole, os.path.join(path, doc))
            item.setData(Qt.UserRole + 1, "doc")
            self.folder_list.addItem(item)

    # --- Клик по элементу ---
    def on_item_clicked(self, item):
        path = item.data(Qt.UserRole)
        item_type = item.data(Qt.UserRole + 1)
        if item_type == "folder":
            self.load_folder(path)
        elif item_type == "doc":
            self.load_document(path)

    # --- Загрузка документа ---
    def load_document(self, path):
        self.current_doc_path = path
        text = ""
        if path.lower().endswith(".docx"):
            try:
                doc = Document(path)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                text = "\n".join(paragraphs) if paragraphs else "⚠️ The document has no readable text."
            except Exception as e:
                text = f"⚠️ Error reading DOCX file:\n{e}"
        elif path.lower().endswith(".txt"):
            try:
                with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
                    text = f.read()
            except Exception as e:
                text = f"⚠️ Error reading TXT file:\n{e}"

        self.text_edit.setPlainText(text)
        self.search_field.clear()
        self.search_matches.clear()
        self.current_match_index = -1

    # --- Навигация вверх ---
    def go_up(self):
        if self.current_path != self.root_path:
            parent_path = os.path.dirname(self.current_path)
            self.load_folder(parent_path)

    # --- Подсветка поиска ---
    def highlight_text(self):
        text_to_find = self.search_field.text().strip()
        doc = self.text_edit.document()

        # Очистка предыдущих выделений
        cursor = QTextCursor(doc)
        cursor.beginEditBlock()
        fmt_clear = QTextCharFormat()
        fmt_clear.setBackground(Qt.transparent)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(fmt_clear)
        cursor.endEditBlock()

        self.search_matches.clear()
        self.current_match_index = -1

        if not text_to_find:
            return

        # Поиск всех совпадений (регистронечувствительный)
        cursor = QTextCursor(doc)
        fmt_highlight = QTextCharFormat()
        fmt_highlight.setBackground(QColor(144, 238, 144, 150))  # бледно-зелёная подсветка

        while not cursor.isNull() and not cursor.atEnd():
            found_cursor = doc.find(text_to_find, cursor, QTextDocument.FindCaseSensitively)
            if found_cursor.isNull():
                break
            if found_cursor.selectedText().lower() == text_to_find.lower():
                found_cursor.mergeCharFormat(fmt_highlight)
                self.search_matches.append(QTextCursor(found_cursor))
            cursor = found_cursor

        if self.search_matches:
            self.current_match_index = 0
            self.text_edit.setTextCursor(self.search_matches[0])

    # --- Переход к следующему совпадению ---
    def goto_next_match(self):
        if not self.search_matches:
            return
        self.current_match_index = (self.current_match_index + 1) % len(self.search_matches)
        self.text_edit.setTextCursor(self.search_matches[self.current_match_index])

    # --- Переход к предыдущему совпадению ---
    def goto_prev_match(self):
        if not self.search_matches:
            return
        self.current_match_index = (self.current_match_index - 1) % len(self.search_matches)
        self.text_edit.setTextCursor(self.search_matches[self.current_match_index])

    # --- Экспорт PDF ---
    def export_pdf(self):
        if not self.text_edit.toPlainText().strip():
            QMessageBox.warning(self, "Export Error", "No document loaded to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        c = canvas.Canvas(path, pagesize=A4)
        text_obj = c.beginText(40, 800)
        text_obj.setFont("Courier", 10)
        for line in self.text_edit.toPlainText().splitlines():
            text_obj.textLine(line)
        c.drawText(text_obj)
        c.save()
        QMessageBox.information(self, "Export Complete", f"Report saved as:\n{path}")

    # --- Удаление отчёта ---
    def delete_report(self):
        if not self.current_doc_path:
            QMessageBox.warning(self, "No file", "Open a report first.")
            return
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete:\n{os.path.basename(self.current_doc_path)}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            os.remove(self.current_doc_path)
            QMessageBox.information(self, "Deleted", "Report deleted successfully.")
            self.load_folder(self.current_path)

    # --- Окно помощи ---
    def show_help(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Help - Reports Archive")
        dlg.resize(700, 500)

        layout = QVBoxLayout()
        txt = QPlainTextEdit()
        txt.setReadOnly(True)
        txt.setStyleSheet("background-color: #000; color: #00FF00; font-family: Consolas; font-size: 13px;")
        txt.setPlainText("""
🟩 HOW REPORTS ARCHIVE WORKS

• Left side — folder and document list.
• Click a folder to open it.
• Click a document (.docx or .txt) to view it on the right.
• Use the search field to find text (case-insensitive, green highlight).
• File → Export (Ctrl+E): Save current report to PDF.
• Admins/Analysts can delete reports via File → Delete Report.
• Use ⬆️ Up to return to the previous folder.
• Click Back to return to main menu.

🟩 COLOR SCHEME
Black background with green text for comfort and readability.
""")
        layout.addWidget(txt)
        dlg.setLayout(layout)
        dlg.exec_()

    # --- Назад в главное меню ---
    def back_to_menu(self):
        cur = self.parent.conn.cursor()
        cur.execute("SELECT role FROM users WHERE username = %s", (self.parent.current_username,))
        role = cur.fetchone()[0]
        cur.close()
        self.parent.show_main_menu(self.parent.current_username, role)