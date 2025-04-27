from controllers.option_controller import OptionController
from views.componenets.textEditorComponenets.menuBar.line_height_changer import LineHeightChangerComponent
from views.componenets.textEditorComponenets.zeusEditor.Menus.main_drop_down_menu_component import MainPopUMenu
from views.componenets.textEditorComponenets.menuBar.font_size_changer import FontSizeView
from views.componenets.textEditorComponenets.menuBar.list_style_changer import ListStyleChanger
from views.componenets.textEditorComponenets.menuBar.text_alignment_changer import TextAlignmentChanger
from views.componenets.textEditorComponenets.menuBar.text_style_changer import TextStyleChanger
from views.editorViews.template.main_template_editor_view import MainTemplateEditorView

from PyQt6.QtGui import QTextCursor, QTextCharFormat, QKeyEvent
from PyQt6.QtWidgets import QTextEdit, QComboBox, QPushButton, QFontComboBox
from typing import Optional, Any, List
from PyQt6.QtCore import pyqtSignal


class ZeusTextBox(QTextEdit):
    selectionCompleted : pyqtSignal()
    parent: Optional[MainTemplateEditorView]
    menu_bar_reference: Optional[MainTemplateEditorView]
    text_type_changer: Optional[QComboBox]
    font_size_changer = Optional[FontSizeView]
    text_style_changers: Optional[TextStyleChanger]
    text_alignment_changer: Optional[TextAlignmentChanger]
    line_height_changer: Optional[LineHeightChangerComponent]
    font_color_changer: Optional[QPushButton]
    background_color_changer: Optional[QPushButton]
    list_style_changer: Optional[ListStyleChanger]
    font_family_changer: Optional[QFontComboBox]

    options_list: Optional[List[Any]]
    option_controller: OptionController
    drop_down: MainPopUMenu
    cursor: QTextCursor
    main_editor_char_format:QTextCharFormat
    count_font_size_emptiness: int
    count_font_family_emptiness: int
    count_text_type_emptiness: int
    bold: bool


    def __init__(self, parent: object = None) -> None:
        self.onSelectionChanged = None
        self.onCurrentCharFormatChanged = None
        self.editor_font = None
        ...

    def applySelectionChanges(self) -> None: ...

    def selection_is_completed(self) -> None: ...
    def on_current_char_format_changed(self) -> None: ...
    def on_selection_changed(self) -> None: ...

    def enableMenuBarComponents(self)  -> None: ...

    def disableMenuBarComponents(self)  -> None: ...

    def on_text_changed(self) -> None: ...

    def update_options_list(self, options_list) -> None: ...

    def insertFromMimeData(self, source) -> None: ...

    def mousePressEvent(self, event) -> None: ...

    def keyPressEvent(self, event: QKeyEvent) -> None: ...

    def is_protected_word_effected(self, event: QKeyEvent) -> bool: ...

    def update_font_size(self, state, word=None) -> None: ...




