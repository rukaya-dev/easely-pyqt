from PyQt6.QtCore import Qt, pyqtSlot, QSize, QSizeF
from PyQt6.QtWidgets import QTextEdit, QFrame, QApplication, QMessageBox, QAbstractScrollArea
from PyQt6.QtGui import QTextCursor, QKeyEvent, QFont, QTextCharFormat, QTextListFormat
from utils.editor import blockSignals


class ZeusTextBox(QTextEdit):
    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent
        self.menu_bar_reference = None
        self.text_type_changer = None
        self.font_size_changer = None
        self.font_size_changer = None
        self.font_family_changer = None
        self.text_style_changers = None
        self.text_alignment_changer = None
        self.line_height_changer = None
        self.font_color_changer = None
        self.background_color_changer = None
        self.list_style_changer = None
        self.undo_redo_buttons = None

        self.options_list = []
        self.heightMax = 1122

        # TextBox Configs
        self.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoAll)
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setStyleSheet("""
            QTextEdit {
                border: 0;
                background-color: white;
                color:black;
            }
            QScrollArea {
                    border:0;
            }
            QScrollBar:vertical {
                    background: transparent;
                    width: 8px; 
                    margin: 0px;
            }

            QScrollBar::handle:vertical {
                    background-color: rgba(0, 0, 0, 50); /* Semi-transparent handle */
                    min-height: 20px; /* Minimum height for the handle */
                    border-radius: 4px; /* Rounded corners for the handle */
            }
            QScrollBar::handle:vertical:hover {
                    background-color: rgba(0, 0, 0, 50); /* Slightly darker on hover */
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px; /* No buttons at the ends */
                    border: none;
                    background: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
            }

            QScrollBar:horizontal {
                    border: none;
                    background: transparent;
                    height: 8px; /* Thin horizontal scrollbar */
                    margin: 0px;
            }

            QScrollBar::handle:horizontal {
                    background-color: rgba(0, 0, 0, 140); /* Semi-transparent handle */
                    min-width: 20px; /* Minimum width for the handle */
                    border-radius: 4px; /* Rounded corners for the handle */
            }

            QScrollBar::handle:horizontal:hover {
                    background-color: rgba(0, 0, 0, 140); /* Slightly darker on hover */
            }

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px; /* No buttons at the ends */
                    border: none;
                    background: none;
            }

            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
            }
        """)

        self.document().setDocumentMargin(20)
        self.document().setPageSize(QSizeF(793, 1122))

        self.main_editor_char_format = self.currentCharFormat()

        self.editor_font = self.font()
        self.editor_font.setStyle(QFont.Style.StyleNormal)
        self.editor_font.setPointSize(12)

        self.main_editor_char_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.NoUnderline)
        self.main_editor_char_format.setFont(self.editor_font)

        self.setCurrentCharFormat(self.main_editor_char_format)

        self.setFixedSize(QSize(793, 1122))
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        # Signals
        self.textChanged.connect(self.on_text_changed)
        self.textChanged.connect(self.updateGeometry)
        self.selectionChanged.connect(self.on_selection_changed)
        self.undoAvailable.connect(self.update_undo_status)
        self.redoAvailable.connect(self.update_redo_status)

        self.document().documentLayout().documentSizeChanged.connect(self.sizeChange)

    def insertFromMimeData(self, source):
        cursor = self.textCursor()
        if source.hasHtml():
            html = source.html()
            # Call the function to manipulate HTML and change the font family
            new_font_family = self.font_family_changer.currentFont().family()  # Assume you have a way to get the current font family
            html = self.parent.format_bar.manipulate_html_font_family(html, new_font_family)

            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)

            # Insert the HTML at the cursor position
            cursor.insertHtml(html)
            # Ensure the cursor is at the end after insertion

            self.setTextCursor(cursor)
            cursor.movePosition(QTextCursor.MoveOperation.End)

            self.setFocus()

        elif source.hasText():
            # Fallback to plain text if no HTML is available
            text = source.text()
            self.textCursor().insertText(text)
        else:
            print("none")
            super().insertFromMimeData(source)

    def viewportSizeHint(self) -> QSize:
        return self.document().size().toSize()

    @pyqtSlot(bool)
    def update_undo_status(self, available):
        self.undo_redo_buttons.toggle_undo_status(available)

    @pyqtSlot(bool)
    def update_redo_status(self, available):
        self.undo_redo_buttons.toggle_redo_status(available)

    def sizeChange(self):
        current_height = self.document().documentLayout().documentSize().height()
        if current_height > self.heightMax:
            self.resize(793, 1122)
        return current_height > self.heightMax

    def update_options_list(self, options_list):
        """
         Updates the list of options used in the text editorViews.

         Args:
             options_list (list): The new list of options.
         """
        self.options_list = options_list

    def mousePressEvent(self, event):
        """
             Handles mouse press events, particularly for selecting words and interacting with custom features.

             Args:
                 event (QMouseEvent): The mouse event.
             """
        # super(ZeusTextBox, self).mousePressEvent(event)

        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)

        # Regular expression to extract the id attribute
        match = cursor.selectedText()
        if self.options_list:
            for option in self.options_list:
                if option == match:
                    # Check if the mouse was clicked to the left or right half of the word
                    cursor.clearSelection()
                    self.moveCursor(QTextCursor.MoveOperation.NextWord)
                    cursor.setPosition(cursor.selectionStart())
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handles key press events, with specific attention to protected words and custom shortcuts.

        Args:
            event (QKeyEvent): The key event.
        """
        try:
            if self.sizeChange():
                if event.key() == Qt.Key.Key_Backspace:
                    super().keyPressEvent(event)
                elif event.key() == Qt.Key.Key_V and event.modifiers() == Qt.Modifier.CTRL:
                    clipboard = QApplication.clipboard()
                    self.insertFromMimeData(clipboard.mimeData())
                else:
                    return

            elif self.is_protected_word_effected(event):
                if event.key() in [Qt.Key.Key_Backspace, Qt.Key.Key_Delete]:
                    QMessageBox.warning(self, "Title", "Please delete options first")
                    return

            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(e)

    def is_protected_word_effected(self, event: QKeyEvent):
        cursor = self.textCursor()
        cursor_pos = cursor.position()

        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            if self.options_list:
                for option in self.options_list:
                    if option in selected_text:
                        return True

        text = self.toPlainText()
        if self.options_list:
            for option in self.options_list:
                start_index = text.find(option)
                if start_index != -1:
                    end_index = start_index + len(option)
                    if start_index <= cursor_pos <= end_index:
                        return True
                    # To handle backspace or delete key
                    if event.key() in [Qt.Key.Key_Backspace, Qt.Key.Key_Delete]:
                        if cursor_pos - 1 == end_index or cursor_pos == start_index:
                            return True

            return False

    @pyqtSlot()
    def on_selection_changed(self):
        try:
            """
                Slot to handle changes in text selection. This method updates the format bar to reflect
                the formatting of the selected text.
                """
            blockSignals(self.parent.format_bar.format_actions, True)

            if self.textCursor().hasSelection():
                self.parent.format_bar.check_if_different_char_format(self.textCursor())
            else:
                current_char_format = self.currentCharFormat()

                self.font_size_changer.lineEditFontSize.setText(
                    str(int(self.currentCharFormat().fontPointSize())))

                self.font_family_changer.setCurrentFont(current_char_format.font())

                if current_char_format.fontWeight() <= 400:
                    self.parent.format_bar.set_active_bold_btn(False)

                elif current_char_format.fontWeight() >= 700:
                    self.parent.format_bar.set_active_bold_btn(True)

                if self.currentFont().style() == QFont.Style.StyleItalic:
                    self.parent.format_bar.set_active_italic_btn(True)
                else:
                    self.parent.format_bar.set_active_italic_btn(False)

                if current_char_format.fontUnderline():
                    self.parent.format_bar.set_active_underline_btn(True)
                else:
                    self.parent.format_bar.set_active_underline_btn(False)

                current_font_color = current_char_format.foreground().color().name()

                if current_font_color:
                    self.parent.format_bar.set_current_font_color(current_font_color)

                if self.alignment() == Qt.AlignmentFlag.AlignLeft:
                    self.text_alignment_changer.align_left_btn.setChecked(True)
                    self.text_alignment_changer.set_active_alignment(self.text_alignment_changer.align_left_btn)

                elif self.alignment() == Qt.AlignmentFlag.AlignHCenter:
                    self.text_alignment_changer.align_center_btn.setChecked(True)
                    self.text_alignment_changer.set_active_alignment(self.text_alignment_changer.align_center_btn)

                elif self.alignment() == Qt.AlignmentFlag.AlignRight:
                    self.text_alignment_changer.align_right_btn.setChecked(True)
                    self.text_alignment_changer.set_active_alignment(self.text_alignment_changer.align_right_btn)

                elif self.alignment() == Qt.AlignmentFlag.AlignJustify:
                    self.text_alignment_changer.align_justify_btn.setChecked(True)
                    self.text_alignment_changer.set_active_alignment(self.text_alignment_changer.align_justify_btn)

                if self.textCursor().currentList():
                    current_list_format = self.textCursor().currentList().format()
                    if current_list_format.style() == QTextListFormat.Style.ListDecimal:
                        self.list_style_changer.set_active_list_btn(self.list_style_changer.ordered_list_btn,
                                                                    checked=True)
                    elif current_list_format.style() == QTextListFormat.Style.ListDisc:
                        self.list_style_changer.set_active_list_btn(self.list_style_changer.un_ordered_list_btn,
                                                                    checked=True)
                else:
                    self.list_style_changer.set_active_list_btn(self.list_style_changer.ordered_list_btn, checked=False)
                    self.list_style_changer.set_active_list_btn(self.list_style_changer.un_ordered_list_btn,
                                                                checked=False)

                current_line_height = int(self.textCursor().blockFormat().lineHeight())
                if current_line_height == 100:
                    self.line_height_changer.single_action.setChecked(True)
                elif current_line_height == 115:
                    self.line_height_changer.one_point_15_action.setChecked(True)

                elif current_line_height == 150:
                    self.line_height_changer.one_point_5_action.setChecked(True)

                elif current_line_height == 200:
                    self.line_height_changer.double_action.setChecked(True)

            blockSignals(self.parent.format_bar.format_actions, False)
        except Exception as e:
            print(e)

    @pyqtSlot()
    def on_text_changed(self):
        if len(self.toPlainText()) == 0:
            self.setCurrentCharFormat(self.main_editor_char_format)

            # Setting Default Configs to MenuBar
            self.font_size_changer.lineEditFontSize.setText(str(int(self.currentCharFormat().fontPointSize())))
            self.font_family_changer.setCurrentText(self.currentCharFormat().fontFamily().format())
            self.parent.format_bar.set_active_bold_btn(False)
            self.parent.format_bar.set_active_italic_btn(False)
            self.parent.format_bar.set_active_underline_btn(False)
        else:
            if self.sizeChange():
                self.setFrameStyle(QFrame.Shape.HLine)
                self.setStyleSheet("""
                        QTextEdit {
                            border: 1px solid #ef4444;
                            background-color: white;
                            color:black;
                        }
                        QScrollBar:vertical {
                            /* retain default vertical scrollbar styles or customize as needed */
                        }
                        QScrollBar:horizontal {
                            /* retain default horizontal scrollbar styles or customize as needed */
                        }
                    """)
            else:
                self.setFrameStyle(QFrame.Shape.NoFrame)
                self.setStyleSheet("""
                         QTextEdit {
                             border:0;
                             background-color: white;
                             border-radius:7px;
                             color:black;
                         }
                         QScrollBar:vertical {
                             /* retain default vertical scrollbar styles or customize as needed */
                         }
                         QScrollBar:horizontal {
                             /* retain default horizontal scrollbar styles or customize as needed */
                         }
                     """)
