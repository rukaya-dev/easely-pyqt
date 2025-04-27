from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QTextCursor, QTextListFormat, QBrush, QTextBlockFormat

from PyQt6.QtWidgets import QFrame, QPushButton, QColorDialog, QDialog, QHBoxLayout, QWidget, QVBoxLayout
import re
import html5lib

from views.componenets.textEditorComponenets.menuBar.font_family_changer import FontFamilyChanger
# Components
from views.componenets.textEditorComponenets.menuBar.font_size_changer import FontSizeView
from views.componenets.textEditorComponenets.menuBar.background_color_changer import BackgroundColorChanger, ColorDialog
from views.componenets.textEditorComponenets.menuBar.line_height_changer import LineHeightChanger
from views.componenets.textEditorComponenets.menuBar.list_style_changer import ListStyleChanger
from views.componenets.textEditorComponenets.menuBar.text_style_changer import TextStyle
from views.componenets.textEditorComponenets.menuBar.text_style_changer import TextStyleChanger
from views.componenets.textEditorComponenets.menuBar.text_alignment_changer import TextAlignmentChanger
from views.componenets.textEditorComponenets.menuBar.undo_redo_buttons import UndoRedoButtons


class FormatBar(QWidget):
    """
     A custom widget for formatting text in a text editorViews. It provides a variety of formatting options
     such as font size, font family, text style (bold, italic, underline), text alignment,
     font color, background color, list style, and line height.

     Attributes:
         zeus_editor_text_box: The text box widget to which the formatting will be applied.
         font_size_changer: Widget to change font size.
         font_family_changer: Combo box for selecting font family.
         text_style_changers: Widget to change text style (bold, italic, underline).
         text_alignment_changers: Widget to change text alignment.
         font_color_changer: Button to change font color.
         background_color_changer: Widget to change text background color.
         list_style_changer: Widget to change list style (ordered, unordered).
         line_height_changer: Widget to change line height.
         format_actions: List of all the formatting actions for easy access and manipulation.
         base_color: Base color used for the widget's styling.
         btn_bg_color: Background color for buttons.
         separator_color: Color for separators in the widget.

     Args:
         :param zeus_editor (QWidget): The text editorViews widget where the formatting will be applied.
         :param: Parent (QWidget, optional): The parent widget. Defaults to None.

     Methods:
         init_format_bar: Initializes the format bar with all the formatting widgets.
         change_line_height: Changes the line height of the text.
         insert_ordered_list: Inserts an ordered list into the text.
         insert_unordered_list: Inserts an unordered list into the text.
         toggle_list: Toggles the list style of selected text.
         change_background_color: Opens a dialog to choose and set the text background color.
         change_font_color: Opens a dialog to choose and set the font color.
         set_current_font_color: Sets the current font color on the font color changer button.
         set_alignment: Sets the text alignment in the text editorViews.
         on_bold_toggled: Toggles the bold style of the text.
         set_active_bold_btn: Updates the bold button's style based on its state.
         on_italic_toggled: Toggles the italic style of the text.
         set_active_italic_btn: Updates the italic button's style based on its state.
         on_underline_toggled: Toggles the underline style of the text.
         set_active_underline_btn: Updates the underline button's style based on its state.
     """

    def __init__(self, zeus_editor, parent=None):
        """
              Constructor for FormatBar. Initializes the UI components and sets up the connections.
        """
        super().__init__()

        self.originalStyleSheet = None
        self.parent = parent
        self.zeus_editor_text_box = zeus_editor

        self.font_size_changer = FontSizeView(self)
        self.font_family_changer = FontFamilyChanger(self)
        self.text_style_changers = TextStyleChanger(self)
        self.text_alignment_changers = TextAlignmentChanger(self)
        self.line_height_changer = LineHeightChanger(self)
        self.font_color_changer = QPushButton(self)
        self.background_color_changer = BackgroundColorChanger(self)
        self.list_style_changer = ListStyleChanger(self)
        self.undo_redo_buttons = UndoRedoButtons(parent=self)

        self.format_actions = [
            self.font_family_changer,
            self.font_size_changer.btnIncreaseFontSize,
            self.font_size_changer.btnDecreaseFontSize,
            self.font_size_changer.lineEditFontSize,
            self.text_style_changers.bold_btn,
            self.text_style_changers.italic_btn,
            self.text_style_changers.underline_btn,
            self.text_alignment_changers.align_left_btn,
            self.text_alignment_changers.align_right_btn,
            self.text_alignment_changers.align_justify_btn,
            self.text_alignment_changers.align_center_btn,
            self.font_color_changer,
            self.background_color_changer.background_text_color_changer_btn,
            self.list_style_changer.ordered_list_btn,
            self.list_style_changer.un_ordered_list_btn,
            self.line_height_changer.menu,
            self.undo_redo_buttons.undo_btn,
            self.undo_redo_buttons.redo_btn,
        ]

        self.init_format_bar()
        self.init_menu_bar_components()

    def init_format_bar(self):
        """
                 Initializes the format bar with all the formatting controls and sets up their connections.
        """
        # Font Size Changer
        self.font_size_changer.btnIncreaseFontSize.clicked.connect(self.increase_font_size)
        self.font_size_changer.btnDecreaseFontSize.clicked.connect(self.decrease_font_size)
        self.font_size_changer.lineEditFontSize.lineEditMenuActionTriggeredSignal.connect(
            self.custom_font_size_trigger)

        # Font Family Changer
        self.font_family_changer.setEditable(False)
        self.font_family_changer.setFixedHeight(40)
        self.font_family_changer.currentFontChanged.connect(self.change_font_family)

        # Text Style changers
        self.text_style_changers.bold_btn.toggled.connect(self.on_bold_toggled)
        self.text_style_changers.italic_btn.toggled.connect(self.on_italic_toggled)
        self.text_style_changers.underline_btn.toggled.connect(self.on_underline_toggled)

        # Text Alignment Changers
        self.text_alignment_changers.align_left_btn.toggled.connect(
            lambda: self.set_alignment(Qt.AlignmentFlag.AlignLeft))
        self.text_alignment_changers.align_center_btn.toggled.connect(
            lambda: self.set_alignment(Qt.AlignmentFlag.AlignHCenter))
        self.text_alignment_changers.align_right_btn.toggled.connect(
            lambda: self.set_alignment(Qt.AlignmentFlag.AlignRight))
        self.text_alignment_changers.align_justify_btn.toggled.connect(
            lambda: self.set_alignment(Qt.AlignmentFlag.AlignJustify))

        # Font Color Changer
        self.font_color_changer.setFixedSize(QSize(15, 15))
        self.font_color_changer.setStyleSheet("background-color:black;border-radius:2;border:1px solid #c7c7c7;")
        self.font_color_changer.clicked.connect(self.change_font_color)
        # Save the original stylesheet of the button
        self.originalStyleSheet = self.font_color_changer.styleSheet()

        # Text Background Color Changer
        self.background_color_changer.background_text_color_changer_btn.clicked.connect(
            self.change_background_color)

        # List style Changer
        self.list_style_changer.ordered_list_btn.toggled.connect(self.insert_ordered_list)
        self.list_style_changer.un_ordered_list_btn.toggled.connect(self.insert_unordered_list)

        # Line Height Changer
        self.line_height_changer.menu.single_action.triggered.connect(lambda: self.change_line_height(100))
        self.line_height_changer.menu.one_point_15_action.triggered.connect(lambda: self.change_line_height(115))
        self.line_height_changer.menu.one_point_5_action.triggered.connect(lambda: self.change_line_height(150))
        self.line_height_changer.menu.double_action.triggered.connect(lambda: self.change_line_height(200))

        # Undo and Redo Buttons
        self.undo_redo_buttons.undo_btn.clicked.connect(self.undo_action)
        self.undo_redo_buttons.redo_btn.clicked.connect(self.redo_action)

        # Bar Seperator
        first_separator = QFrame()
        first_separator.setFrameStyle(QFrame.Shape.StyledPanel)
        first_separator.setFrameShadow(QFrame.Shadow.Raised)
        first_separator.setFixedSize(QSize(1, 20))

        second_separator = QFrame()
        second_separator.setFrameStyle(QFrame.Shape.StyledPanel)
        second_separator.setFrameShadow(QFrame.Shadow.Raised)
        second_separator.setFixedSize(QSize(1, 20))

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(40, 0, 40, 0)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        main_layout.addWidget(self.font_family_changer)
        main_layout.addWidget(self.text_style_changers)
        main_layout.addWidget(self.font_size_changer)
        main_layout.addWidget(self.text_alignment_changers)
        main_layout.addWidget(self.line_height_changer)
        main_layout.addWidget(first_separator)
        main_layout.addWidget(self.font_color_changer)
        main_layout.addWidget(self.background_color_changer)
        main_layout.addWidget(second_separator)
        main_layout.addWidget(self.list_style_changer)
        main_layout.addWidget(self.undo_redo_buttons)

        self.menu_bar_central_widget = QWidget()
        self.menu_bar_central_widget.setFixedHeight(60)
        self.menu_bar_central_widget.setFixedWidth(1300)
        self.menu_bar_central_widget.setObjectName("menu_bar_central_widget")
        self.menu_bar_central_widget.setStyleSheet("""
            QWidget {
                border-radius: 7px;
                background-color:white;
            }
            QFrame {
                background-color:#c7c7c7;
                border-radius:15px;
            }
            """)

        menu_bar_layout = QVBoxLayout(self.menu_bar_central_widget)
        menu_bar_layout.setContentsMargins(0, 0, 0, 0)
        menu_bar_layout.setSpacing(0)

        menu_bar_layout.addLayout(main_layout)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.menu_bar_central_widget)

        self.setLayout(layout)

    def undo_action(self):
        self.zeus_editor_text_box.undo()

    def redo_action(self):
        self.zeus_editor_text_box.redo()

    def change_line_height(self, line_height):
        """
               Changes the line height of the text in the text editorViews.

               Args:
                   line_height (int): The new line height value to be set.
        """
        block_ormat = QTextBlockFormat()
        block_ormat.setLineHeight(line_height, 1)

        # Apply the block format to the entire document
        cursor = self.zeus_editor_text_box.textCursor()
        cursor.mergeBlockFormat(block_ormat)

    def insert_ordered_list(self, checked):
        """
        Inserts an ordered list into the text editorViews's content or toggles off if already applied.

        Args:
            checked (bool): Indicates whether the ordered list option is toggled on or off.
        """
        self.toggle_list(QTextListFormat.Style.ListDecimal)
        self.list_style_changer.set_active_list_btn(self.list_style_changer.ordered_list_btn, checked)

    def insert_unordered_list(self, checked):
        """
             Inserts an unordered list into the text editorViews's content or toggles off if already applied.

             Args:
                 checked (bool): Indicates whether the unordered list option is toggled on or off.
             """
        self.toggle_list(QTextListFormat.Style.ListDisc)
        self.list_style_changer.set_active_list_btn(self.list_style_changer.un_ordered_list_btn, checked)

    def toggle_list(self, list_style: QTextListFormat.Style):
        """
             Toggles the list style of the selected text between ordered and unordered list formats.

             Args:
                 list_style (QTextListFormat): The list style to be applied.
             """
        cursor = self.zeus_editor_text_box.textCursor()
        text_list = cursor.currentList()

        if text_list:
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            removed = 0
            for i in range(text_list.count()):
                item = text_list.item(i - removed)
                if (item.position() <= end and
                        item.position() + item.length() > start):
                    text_list.remove(item)
                    block_cursor = QTextCursor(item)
                    block_format = block_cursor.blockFormat()
                    block_format.setIndent(0)
                    block_cursor.mergeBlockFormat(block_format)
                    removed += 1
            self.zeus_editor_text_box.setTextCursor(cursor)
            self.zeus_editor_text_box.setFocus()
        else:
            list_format = QTextListFormat()
            list_format.setStyle(list_style)
            cursor.insertList(list_format)
            self.zeus_editor_text_box.setTextCursor(cursor)
            self.zeus_editor_text_box.setFocus()

    def change_background_color(self):
        """
              Opens a color dialog to choose and set the text background color in the text editorViews.
              """
        color_dialog = ColorDialog(self)
        if color_dialog.exec() == QDialog.DialogCode.Accepted:
            color = color_dialog.getColor()
            if color.isValid():
                style = TextStyle(backgroundColor=color)
                self.change_format(style, "text-background", color)
            else:
                style = TextStyle(backgroundColor=None)
            self.change_format(style, "text-background", style.backgroundColor)

    def change_font_color(self):
        """
              Opens a color dialog to choose and set the font color in the text editorViews.
              """
        color = QColorDialog.getColor()
        if color.isValid():
            style = TextStyle(color=color)
            self.change_format(style, "font-color", color)
            self.set_current_font_color(color.name())

    def set_current_font_color(self, color):
        """
           Sets the current font color on the font color changer button background.

           Args:
               color (str): The color to be set for the color changer button background.
           """
        self.font_color_changer.setStyleSheet(f"background-color: {color};border-radius:2px;border:1px solid #c7c7c7")

    def set_alignment(self, alignment):
        """
              Sets the text alignment in the text editorViews.

              Args:
                  alignment (Qt.Alignment): The alignment to be applied to the text.
              """
        self.zeus_editor_text_box.setAlignment(alignment)

    # Font Bold Methods
    def on_bold_toggled(self, checked):
        """
             Toggles the bold style of the text in the text editorViews.

             Args:
                 checked (bool): Indicates whether the bold option is toggled on or off.
             """
        style = TextStyle(bold=checked)

        self.change_format(style, "font-weight", checked)
        # if not self.zeus_editor_text_box.textCursor().hasSelection():
        if self.text_style_changers.bold_btn.isChecked():
            self.set_active_bold_btn(True)
        else:
            self.set_active_bold_btn(False)
        # else:

    def set_active_bold_btn(self, checked):
        """
            Updates the bold button's style based on its toggle state.

            Args:
                checked (bool): Indicates whether the bold button is active or inactive.
            """
        self.text_style_changers.update_button_style(self.text_style_changers.bold_btn,
                                                     checked)

    def on_italic_toggled(self, checked):
        """
          Toggles the italic style of the text in the text editorViews.

          Args:
              checked (bool): Indicates whether the italic option is toggled on or off.
          """
        style = TextStyle(italic=checked)
        self.change_format(style, "font-italic", checked)
        if self.text_style_changers.italic_btn.isChecked():
            self.set_active_italic_btn(True)
        else:
            self.set_active_italic_btn(False)

    def set_active_italic_btn(self, checked):
        """
          Updates the italic button's style based on its toggle state.

          Args:
              checked (bool): Indicates whether the italic button is active or inactive.
          """
        self.text_style_changers.update_button_style(self.text_style_changers.italic_btn,
                                                     checked)

    def on_underline_toggled(self, checked):
        """
           Toggles the underline style of the text in the text editorViews.

           Args:
               checked (bool): Indicates whether the underline option is toggled on or off.
           """
        style = TextStyle(underline=checked)
        self.change_format(style, "font-underline", checked)
        if self.text_style_changers.underline_btn.isChecked():
            self.set_active_underline_btn(True)
        else:
            self.set_active_underline_btn(False)

    def set_active_underline_btn(self, checked):
        """
             Updates the underline button's style based on its toggle state.

             Args:
                 checked (bool): Indicates whether the underline button is active or inactive.
             """
        self.text_style_changers.update_button_style(self.text_style_changers.underline_btn,
                                                     checked)

    def change_font_family(self, font: QFont):
        """
          Changes the font family of the selected text in the text editorViews.

          Args:
              font (QFont): The new font to be applied to the selected text.
          """
        style = TextStyle(fontFamily=font.family())
        self.change_format(style, "font-family", font.family())

    @staticmethod
    def manipulate_html_font_weight_style(html_content):
        """
           Modifies the 'font-weight' within an HTML content string based on specified conditions:
           1. If any tag has a 'font-weight' and others do not, set all to '700'.
           2. If any tag has 'font-weight' as '400' and others as '700', set all to '700'.
           3. If no tags have 'font-weight', set all to '700'.
           4. If all tags have 'font-weight' as '700', set all to '400', otherwise set all to '700'.

           Args:
               html_content (str): The original HTML content.

           Returns:
               str: The updated HTML content with the 'font-weight' style changed as per conditions.
           """
        # Regex to find tags with style attributes
        tags_with_styles = re.findall(r'(<[^>]+style="[^"]*"[^>]*>)', html_content)

        # Analyze the existing 'font-weight' to determine what action to take
        font_weights = [re.search(r'font-weight:\s*([^;"]+)', tag) for tag in tags_with_styles]
        weights_found = [match.group(1) for match in font_weights if match]

        # Decide the uniform 'font-weight' to apply
        if not weights_found:
            # No 'font-weight' at all, set all to '700'
            uniform_weight = '700'
        elif all(w == '700' for w in weights_found):
            # All are '700', switch to '400'
            uniform_weight = '400'
        else:
            # Any variation or missing, set all to '700'
            uniform_weight = '700'

        # Apply the decided 'font-weight' to all tags
        new_html_content = html_content
        for tag in tags_with_styles:
            if 'font-weight' in tag:
                # Replace existing font-weight value
                new_tag = re.sub(r'font-weight:\s*[^;"]+', f'font-weight: {uniform_weight}', tag)
            else:
                # Add 'font-weight' where it's missing
                new_tag = re.sub(r'(style=")', rf'\1font-weight: {uniform_weight}; ', tag)

            # Replace the original tag with the new tag in the HTML content
            new_html_content = new_html_content.replace(tag, new_tag)

        return new_html_content

    @staticmethod
    def manipulate_html_font_size_style(html_content, option):

        """
            Modifies the 'font-size' within an HTML content string by either increasing or decreasing it by 1px or 1pt
            based on the provided option. It supports both 'px' and 'pt' units.

            Args:
                html_content (str): The original HTML content.
                option (str): The operation to perform ('increase' or 'decrease').

            Returns:
                str: The updated HTML content with 'font-size' adjusted as per the option.
            """
        # Regex to find tags with style attributes
        tags_with_styles = re.findall(r'(<[^>]+style="[^"]*"[^>]*>)', html_content)

        # Function to adjust font size
        def adjust_font_size(match):
            current_size = int(match.group(1))
            unit = match.group(2)

            if isinstance(option, str):
                if option == 'up':
                    new_size = current_size + 1
                elif option == 'down':
                    new_size = current_size - 1
                return f'font-size: {new_size}{unit}'

            else:
                new_size = option
                return f'font-size: {new_size}{unit}'

        # Modify the 'font-size' in each tag with a style attribute
        new_html_content = html_content
        for tag in tags_with_styles:
            if 'font-size' in tag:
                # Updated regex to capture both 'px' and 'pt'
                new_tag = re.sub(r'font-size:\s*(\d+)(px|pt)', adjust_font_size, tag)
                new_html_content = new_html_content.replace(tag, new_tag)

        return new_html_content

    @staticmethod
    def manipulate_html_font_style_style(html_content):
        """
        Modifies the 'font-style' within an HTML content string based on specified conditions:
        1. If any tag has 'font-style: italic', set all to 'normal'.
        2. If no tags have 'font-style: italic', set all to 'italic'.
        3. If all tags have 'font-style: italic', set all to 'normal', otherwise set all to 'italic'.

        Args:
            html_content (str): The original HTML content.

        Returns:
            str: The updated HTML content with the 'font-style' uniformly changed as per conditions.
        """
        # Regex to find tags with style attributes
        tags_with_styles = re.findall(r'(<[^>]+style="[^"]*"[^>]*>)', html_content)

        # Analyze the existing 'font-style' to determine what action to take
        font_styles = [re.search(r'font-style:\s*([^;"]+)', tag) for tag in tags_with_styles]
        styles_found = [match.group(1) for match in font_styles if match]

        # Decide the uniform 'font-style' to apply
        if not styles_found:
            # No 'font-style' at all, set all to 'italic'
            uniform_style = 'italic'
        elif all(style == 'italic' for style in styles_found):
            # All are 'italic', switch to 'normal'
            uniform_style = 'normal'
        else:
            # Any variation or missing, set all to 'italic'
            uniform_style = 'italic'

        # Apply the decided 'font-style' to all tags
        new_html_content = html_content
        for tag in tags_with_styles:
            if 'font-style' in tag:
                # Replace existing font-style value
                new_tag = re.sub(r'font-style:\s*[^;"]+', f'font-style: {uniform_style}', tag)
            else:
                # Add 'font-style' where it's missing
                new_tag = re.sub(r'(style=")', rf'\1font-style: {uniform_style}; ', tag)

            # Replace the original tag with the new tag in the HTML content
            new_html_content = new_html_content.replace(tag, new_tag)

        return new_html_content

    @staticmethod
    def manipulate_html_text_underline_underline(html_content):
        """
         Modifies the 'text-decoration' within an HTML content string based on specified conditions:
         1. If any tag has 'text-decoration: underline', set all to 'none' (remove underline).
         2. If no tags have 'text-decoration: underline', set all to 'underline'.
         3. If all tags have 'text-decoration: underline', set all to 'none', otherwise set all to 'underline'.

         Args:
             html_content (str): The original HTML content.

         Returns:
             str: The updated HTML content with 'text-decoration' uniformly changed as per conditions.
         """
        # Regex to find tags with style attributes
        tags_with_styles = re.findall(r'(<[^>]+style="[^"]*"[^>]*>)', html_content)

        # Analyze the existing 'text-decoration' to determine what action to take
        text_decorations = [re.search(r'text-decoration:\s*([^;"]+)', tag) for tag in tags_with_styles]
        decorations_found = [match.group(1) for match in text_decorations if match]

        # Decide the uniform 'text-decoration' to apply
        if not decorations_found:
            # No 'text-decoration' at all, set all to 'underline'
            uniform_decoration = 'underline'
        elif all(deco == 'underline' for deco in decorations_found):
            # All are 'underline', switch to 'none'
            uniform_decoration = 'none'
        else:
            # Any variation or missing, set all to 'underline'
            uniform_decoration = 'underline'

        # Apply the decided 'text-decoration' to all tags
        new_html_content = html_content
        for tag in tags_with_styles:
            if 'text-decoration' in tag:
                # Replace existing text-decoration value
                new_tag = re.sub(r'text-decoration:\s*[^;"]+', f'text-decoration: {uniform_decoration}', tag)
            else:
                # Add 'text-decoration' where it's missing
                new_tag = re.sub(r'(style=")', rf'\1text-decoration: {uniform_decoration}; ', tag)

            # Replace the original tag with the new tag in the HTML content
            new_html_content = new_html_content.replace(tag, new_tag)

        return new_html_content

    @staticmethod
    def manipulate_html_font_family(html_content, font_family):
        """
        Sets a uniform 'font-family' for all tags with style attributes within an HTML content string.

        Args:
            html_content (str): The original HTML content.
            font_family (str): The CSS font-family value to apply (e.g., 'Arial', 'Times New Roman').

        Returns:
            str: The updated HTML content with the 'font-family' style uniformly applied to all tags.
        """
        # Regex to find tags with style attributes
        tags_with_styles = re.findall(r'(<[^>]+style="[^"]*"[^>]*>)', html_content)

        # Apply the specified font-family to all tags with style attributes
        new_html_content = html_content
        for tag in tags_with_styles:
            if 'font-family' in tag:
                # Replace existing font-family value
                new_tag = re.sub(r'font-family:\s*[^;"]+', f'font-family: {font_family}', tag)
            else:
                # Add 'font-family' where it's missing
                new_tag = re.sub(r'(style=")', rf'\1font-family: {font_family}; ', tag)

            # Replace the original tag with the new tag in the HTML content
            new_html_content = new_html_content.replace(tag, new_tag)

        return new_html_content

    @staticmethod
    def manipulate_html_color_style(html_content, color):
        """
        Sets a uniform 'color' for all tags with style attributes within an HTML content string.

        Args:
            html_content (str): The original HTML content.
            color (str): The CSS color value to apply (e.g., 'red', '#FF0000', 'rgb(255, 0, 0)').

        Returns:
            str: The updated HTML content with the 'color' style uniformly applied to all tags.
        """
        # Regex to find tags with style attributes
        tags_with_styles = re.findall(r'(<[^>]+style="[^"]*"[^>]*>)', html_content)

        # Apply the specified color to all tags with style attributes
        new_html_content = html_content
        for tag in tags_with_styles:
            if 'color' in tag:
                # Replace existing color value
                new_tag = re.sub(r'color:\s*[^;"]+', f'color: {color}', tag)
            else:
                # Add 'color' where it's missing
                new_tag = re.sub(r'(style=")', rf'\1color: {color}; ', tag)

            # Replace the original tag with the new tag in the HTML content
            new_html_content = new_html_content.replace(tag, new_tag)

        return new_html_content

    @staticmethod
    def manipulate_html_background_color(html_content, background_color):
        """
        Sets a uniform 'background-color' for all tags with style attributes within an HTML content string.

        Args:
            html_content (str): The original HTML content.
            background_color (str): The CSS background-color value to apply (e.g., '#FFFFFF', 'rgba(255, 255, 255, 0.5)').

        Returns:
            str: The updated HTML content with the 'background-color' style uniformly applied to all tags.
        """
        # Regex to find tags with style attributes
        tags_with_styles = re.findall(r'(<[^>]+style="[^"]*"[^>]*>)', html_content)

        # Apply the specified background-color to all tags with style attributes
        new_html_content = html_content
        for tag in tags_with_styles:
            if 'background-color' in tag:
                # Replace existing background-color value
                new_tag = re.sub(r'background-color:\s*[^;"]+', f'background-color: {background_color}', tag)
            else:
                # Add 'background-color' where it's missing
                new_tag = re.sub(r'(style=")', rf'\1background-color: {background_color}; ', tag)

            # Replace the original tag with the new tag in the HTML content
            new_html_content = new_html_content.replace(tag, new_tag)

        return new_html_content

    def manipulate_html_format(self, html_content, option=None, option_value=None):

        if option == "font-size":
            html_content = self.manipulate_html_font_size_style(html_content, option_value)

        if option == "font-weight":
            html_content = self.manipulate_html_font_weight_style(html_content)

        if option == "font-italic":
            html_content = self.manipulate_html_font_style_style(html_content)

        if option == "font-underline":
            html_content = self.manipulate_html_text_underline_underline(html_content)

        if option == "font-color":
            html_content = self.manipulate_html_color_style(html_content, option_value.name())

        if option == "font-family":
            html_content = self.manipulate_html_font_family(html_content, option_value)

        if option == "text-background":
            html_content = self.manipulate_html_background_color(html_content,
                                                                 option_value.name() if option_value else "transparent")

        return html_content

    def change_format(self, style: TextStyle, option, option_value):
        """
          Changes the formatting of the selected text based on the specified style and option.

          Args:
              :param style: An object containing the new style properties.
              :param option_value: The new value for the specified option.
              :param option: The specific style option to be changed.
          """
        cursor = self.zeus_editor_text_box.textCursor()

        char_format = self.create_char_format(style, option)
        if cursor.hasSelection():
            if (cursor.hasSelection() and option == "font-size" or option == "font-italic" or option == "font-color"
                    or option == "font-underline" or option == "font-weight" or option == "font-family" or option == "text-background"):
                pos_start = cursor.selectionStart()
                pos_end = cursor.selectionEnd()

                html = cursor.selection().toHtml()
                new_html = self.manipulate_html_format(html, option, option_value)

                cursor.insertHtml(new_html)

                cursor.setPosition(pos_start)
                print(pos_start, pos_end)

                selection_length = pos_end - pos_start

                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, selection_length)
                self.zeus_editor_text_box.setTextCursor(cursor)
                self.zeus_editor_text_box.setFocus()

        else:
            self.zeus_editor_text_box.setCurrentCharFormat(char_format)
            cursor.mergeCharFormat(char_format)
            self.zeus_editor_text_box.setTextCursor(cursor)
            self.zeus_editor_text_box.setFocus()

    def increase_font_size(self):
        """
           Increases the font size of the selected text in the text editorViews.
           """
        new_font_size = None
        if not self.zeus_editor_text_box.textCursor().hasSelection():
            new_size = int(self.font_size_changer.lineEditFontSize.text()) + 1
            self.font_size_changer.lineEditFontSize.setText(str(new_size))
            new_font_size = new_size
        style = TextStyle(font_size=new_font_size)
        self.change_format(style, "font-size", "up")

    def decrease_font_size(self):
        """
         Decreases the font size of the selected text in the text editorViews.
         """
        new_font_size = None
        if not self.zeus_editor_text_box.textCursor().hasSelection():
            new_size = int(self.font_size_changer.lineEditFontSize.text()) - 1
            if new_size >= 1:
                self.font_size_changer.lineEditFontSize.setText(str(new_size))
                new_font_size = new_size
            else:
                self.font_size_changer.lineEditFontSize.setText(str(1))
                new_font_size = 1
        style = TextStyle(font_size=new_font_size)
        self.change_format(style, "font-size", "down")

    def custom_font_size_trigger(self, value):
        """
            Sets a custom font size for the selected text based on the provided value.

            Args:
                value (int): The new font size to be applied.
            """
        self.font_size_changer.lineEditFontSize.setText(str(value))
        style = TextStyle(font_size=int(value))
        self.change_format(style, "font-size", value)

    def check_if_different_char_format(self, cursor):
        """
        Checks if the selected text has different character formats (e.g., font size, font weight, etc).

        Args:
            cursor (QTextCursor): The cursor representing the current text selection.

        Returns:
            tuple: A tuple containing boolean values indicating whether different formats are present.
        """

        def is_valid_html(html):
            try:
                parser = html5lib.HTMLParser(strict=True)
                parser.parse(html)
                return True
            except:
                return False

        if cursor.hasSelection():
            def process_html(html):
                tags_with_styles = re.findall(r'<[^>]+style="([^"]+)"[^>]*>', html)
                style_pattern = r'font-size:\s*([^;\s]+)\s*;|font-weight:\s*([^;\s]+)\s*;|font-style:\s*([^;\s]+)\s*;|text-decoration:\s*([^;\s]+)\s*;|color:\s*([^;\s]+)\s*;|font-family:\s*([^;\s]+)\s*;'

                styles = {
                    'font-size': [],
                    'font-weight': [],
                    'font-family': [],
                    'font-style': [],
                    'text-decoration': [],
                    'color': []
                }

                for style_string in tags_with_styles:
                    found_weight, found_style, found_decoration, found_color, found_family = False, False, False, False, False
                    matches = re.findall(style_pattern, style_string)
                    for match in matches:
                        if match[0]:
                            styles['font-size'].append(match[0])
                        if match[1]:
                            styles['font-weight'].append(match[1])
                            found_weight = True
                        if match[2]:
                            styles['font-style'].append(match[2])
                            found_style = True
                        if match[3]:
                            styles['text-decoration'].append(match[3])
                            found_decoration = True
                        if match[4]:
                            styles['color'].append(match[4])
                            found_color = True
                        if match[5]:
                            styles['font-family'].append(match[5])
                            found_family = True

                    if not found_weight:
                        styles['font-weight'].append("400")
                    if not found_style:
                        styles['font-style'].append("normal")
                    if not found_decoration:
                        styles['text-decoration'].append("none")
                    if not found_color:
                        styles['color'].append("#000000")
                    if not found_family:
                        styles['font-family'].append(self.zeus_editor_text_box.currentFont().family())

                for key, values in styles.items():
                    styles[key] = all(value == values[0] for value in values) if values else True

                return styles

            html_content = cursor.selection().toHtml()

            if is_valid_html(html_content):
                style_results = process_html(html_content)

                current_char_format = self.zeus_editor_text_box.currentCharFormat()

                # Adjusted outputs based on the detected styles
                self.font_size_changer.lineEditFontSize.setText(
                    str(int(current_char_format.fontPointSize())) if style_results["font-size"] else "")
                self.set_active_bold_btn(style_results["font-weight"] and current_char_format.fontWeight() >= 700)
                self.set_active_italic_btn(
                    style_results[
                        "font-style"] and self.zeus_editor_text_box.currentFont().style() == QFont.Style.StyleItalic)
                self.set_active_underline_btn(style_results["text-decoration"] and current_char_format.fontUnderline())
                self.set_current_font_color(
                    current_char_format.foreground().color().name() if style_results["color"] else "white")

                self.font_family_changer.setCurrentFont(QFont(
                    current_char_format.fontFamily() if style_results["font-family"] else ''))

                return style_results
            else:
                pass

        return None  # Or some other appropriate return value if no selection or invalid HTML

    def init_menu_bar_components(self):
        """
           Initializes the components of the menu bar and links them with the text editorViews.
           """
        self.zeus_editor_text_box.font_size_changer = self.font_size_changer
        self.zeus_editor_text_box.font_family_changer = self.font_family_changer
        self.zeus_editor_text_box.text_style_changers = self.text_style_changers
        self.zeus_editor_text_box.text_alignment_changer = self.text_alignment_changers
        self.zeus_editor_text_box.line_height_changer = self.line_height_changer.menu
        self.zeus_editor_text_box.font_color_changer = self.font_color_changer
        self.zeus_editor_text_box.background_color_changer = self.background_color_changer.background_text_color_changer_btn
        self.zeus_editor_text_box.list_style_changer = self.list_style_changer
        self.zeus_editor_text_box.undo_redo_buttons = self.undo_redo_buttons

    def create_char_format(self, style: TextStyle, option):
        """
        Creates a QTextCharFormat based on the provided style and option.

        Args:
            style (TextStyle): The style to be applied.
            option (str): The specific option for which the format is to be created.

        Returns:
            QTextCharFormat: The created character format with the specified style.
        """
        new_char_format = self.zeus_editor_text_box.currentCharFormat()

        option_map = {
            "font-size": (style.font_size, new_char_format.setFontPointSize),
            "font-weight": (
                style.bold,
                lambda val: new_char_format.setFontWeight(QFont.Weight.Bold if val else QFont.Weight.Normal)),
            "font-family": (style.fontFamily, new_char_format.setFontFamily),
            "font-italic": (style.italic, new_char_format.setFontItalic),
            "font-underline": (style.underline, new_char_format.setFontUnderline),
            "font-color": (style.color, new_char_format.setForeground),
            "text-background": (style.backgroundColor,
                                new_char_format.setBackground if style.backgroundColor is not None else lambda
                                    _: new_char_format.setBackground(QBrush()))
        }

        value, func = option_map.get(option, (None, None))

        if value is not None:
            func(value)

        return new_char_format
