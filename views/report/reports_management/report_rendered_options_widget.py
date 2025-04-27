from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QStandardItemModel, QStandardItem

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyledItemDelegate, \
    QComboBox, QTreeWidgetItem, QHBoxLayout, QLineEdit, QTreeWidgetItemIterator, \
    QMessageBox, QPushButton, QToolButton, QSpacerItem, QSizePolicy, QDataWidgetMapper

from utils.utlis import string_to_slug
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.custom_searchbar import CustomSearchBar
from views.componenets.customsComponents.tree_widget.custom_tree_widget import CustomTreeWidget


class ReportRenderedOptionsWidgets(QWidget):
    """
     A custom QWidget class for rendering and interacting with report options in a structured tree format.

     Attributes:
         optionIsAddedToEditor (pyqtSignal): Signal emitted when an option is added to the editorViews.
         :param Options_data (list): The data for the options to be rendered.
         :arg Options_controller (OptionController): Controller for managing option-related operations.

     Args:
         options_data (list): The data for the options to be rendered.
         Parent (QWidget, optional): The parent widget. Defaults to None.
     """
    optionIsAddedToEditor = pyqtSignal(str)

    def __init__(self, options_data, parent=None):
        """
                Initializes the widget with necessary data and UI components.
                """
        super().__init__(parent)

        self.option_content = None
        self.single_option_structure = None
        self.line_edit_widget = None
        self.child_line_edit_item = None
        self.menu_widget = None
        self.parent_menu_item = None

        self.options_data = options_data

        self.search_bar = CustomSearchBar()
        self.search_bar.setFixedSize(QSize(440, 40))
        self.search_bar.search_bar.textChanged.connect(self.search_tree)

        search_line_edit_layout = QHBoxLayout()
        search_line_edit_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        search_line_edit_layout.setContentsMargins(0, 20, 20, 20)
        search_line_edit_layout.addWidget(self.search_bar)

        self.treeWidget = CustomTreeWidget()
        self.treeWidget.setRootIsDecorated(True)
        self.treeWidget.setIndentation(10)
        self.treeWidget.setItemsExpandable(True)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.setContentsMargins(20, 20, 5, 20)

        central_widget = QWidget()
        central_widget.setObjectName("report_options_rendered_widget")

        main_layout.addWidget(self.search_bar)
        main_layout.addWidget(self.treeWidget)
        central_widget.setLayout(main_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

        self.setLayout(layout)
        self.setStyleSheet("""
        QWidget#report_options_rendered_widget {
             border-radius: 7px;
             background-color: white;
        }
        QLabel {
          font-size:16px;
        }
        """)

        self.renderMainOptionsList()
        self.treeWidget.itemClicked.connect(self.toggle_item_expandtion)

    def toggle_item_expandtion(self, item: QTreeWidgetItem):
        if item:
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)

    def set_single_option_structure(self, new_option_structure):
        self.single_option_structure = new_option_structure

    def get_single_option_structure(self):
        return self.single_option_structure

    def search_tree(self, text):
        """
            Searches the tree widget for items matching the given text.

            Args:
                text (str): The text to search for in the tree widget.
            """
        ...
        # First, hide all the items in the tree
        self.hide_all_items_after_search()

        # Search for the items that match the criteria
        matched_items = self.treeWidget.findItems(text, Qt.MatchFlag.MatchStartsWith, 0)

        # Show only the items that match the search criteria
        for item in matched_items:
            self.show_all_items_and_children(item)

        # Optionally, set the first search result as the current item
        if matched_items:
            self.treeWidget.setCurrentItem(matched_items[0])

    def hide_all_items_after_search(self):
        """
               Hides all items in the tree widget after performing a search operation.
               """
        iterator = QTreeWidgetItemIterator(self.treeWidget, QTreeWidgetItemIterator.IteratorFlag.All)
        while iterator.value():
            item = iterator.value()
            item.setHidden(True)
            iterator += 1

    def show_all_items_and_children(self, matched_item):
        """
              Shows all items and their children that match the search criteria in the tree widget.

              Args:
                  matched_item (QTreeWidgetItem): The tree widget item that matches the search criteria.
              """
        iterator = QTreeWidgetItemIterator(self.treeWidget, QTreeWidgetItemIterator.IteratorFlag.All)
        while iterator.value():
            item = iterator.value()
            if item.data(0, Qt.ItemDataRole.DisplayRole) == matched_item.data(0, Qt.ItemDataRole.DisplayRole):
                item.setHidden(False)
                self.show_children(item)
            iterator += 1

    def show_children(self, parent: QTreeWidgetItem):
        # Only proceed if the parent has children
        if parent.childCount() == 0:
            return

        # Retrieve the widget associated with the parent item
        parent_widget = self.treeWidget.itemWidget(parent, 0)

        # Loop through each child of the parent
        for i in range(parent.childCount()):
            child = parent.child(i)
            # Retrieve the widget associated with the child item
            child_widget = self.treeWidget.itemWidget(child, 0)

            # Determine if the child should be shown or hidden
            should_hide_child = self.should_hide_child_based_on_parent(child, child_widget, parent, parent_widget)

            # Hide or show the child based on the above determination
            child.setHidden(should_hide_child)

            # Recursively apply this function to the children of this child
            if child.childCount() > 0:
                self.show_children(child)

    def should_hide_child_based_on_parent(self, child, child_widget, parent, parent_widget):
        # Function to decide if a child should be hidden based on the parent's state

        # Case for parent with OptionMenuWidget
        if isinstance(parent_widget, OptionMenuWidget):
            # Check if the child also has a custom widget and has user role data
            if isinstance(child_widget, (OptionMenuWidget, OptionLineEditWidget)) and child.data(2,
                                                                                                 Qt.ItemDataRole.UserRole):
                return not (child.data(1, Qt.ItemDataRole.UserRole) == parent.data(1, Qt.ItemDataRole.UserRole) and
                            child.data(2, Qt.ItemDataRole.UserRole) == parent_widget.combo.currentText())

        # Case for parent with OptionLineEditWidget
        elif isinstance(parent_widget, OptionLineEditWidget):
            if isinstance(child_widget, (OptionMenuWidget, OptionLineEditWidget)) and child.data(2,
                                                                                                 Qt.ItemDataRole.UserRole):
                return child.data(2, Qt.ItemDataRole.UserRole) != parent_widget.line_edit.text()

        # If none of the above conditions are met, the child is not hidden
        return False

    def set_option_content(self, content):
        """
           Sets the content for the selected option.

           Args:
               content: The content to be set for the selected option.
           """
        self.option_content = content

    def get_option_content(self):
        """
             Retrieves the content of the currently selected option.

             Returns:
                 The content of the selected option.
             """
        return self.option_content

    def validate_option_content(self, checked, parent_item: QTreeWidgetItem, parent_item_name):
        """
        Validates the content of the selected option.

        Args:
            checked: Indicates whether the option is checked.
            :param parent_item: The parent item of the selected option.
            :param parent_item_name: The name of the parent item.
        """
        if not parent_item or not parent_item_name:
            raise ValueError("parent_item and parent_item_name must not be None")

        self.option_content = {'parent_item_name': parent_item_name, 'children_values': []}
        if self._find_option_children_content(parent_item):
            self.set_option_content(self.option_content)
            option_name_slug = string_to_slug(self.option_content["parent_item_name"])
            self.optionIsAddedToEditor.emit(option_name_slug)

    def _find_option_children_content(self, item=None):
        """
        Recursively finds and validates children of a given tree item.

        :param item: The QTreeWidgetItem to start searching from.
        :return: False if validation fails, True otherwise.
        """
        if item and item.childCount() > 0:
            for i in range(item.childCount()):
                child_item = item.child(i)
                if not child_item.isHidden():
                    child_item.data(0, Qt.ItemDataRole.UserRole)
                    child_widget = self.treeWidget.itemWidget(child_item, 0)

                    if isinstance(child_widget, OptionMenuWidget):
                        if child_widget.item["is_required_state"]:
                            if not child_widget.combo.currentText():
                                QMessageBox.warning(self, "Warning", f"{child_widget.item['name']} value is required.")
                                return False
                        if child_widget.combo.currentText():
                            row = child_widget.combo.currentIndex()
                            index = child_widget.combo.model().index(row, 0)
                            option_content = child_widget.combo.model().data(index, Qt.ItemDataRole.UserRole)
                            self.option_content["children_values"].append(option_content)

                    elif isinstance(child_widget, OptionLineEditWidget):
                        if child_widget.item["is_required_state"]:
                            if not child_widget.line_edit.text():
                                QMessageBox.warning(self, "Warning", f"{child_widget.item['name']} value is required.")
                                return False
                        if child_widget.line_edit.text():
                            content = child_widget.model.item(0, 0).text()
                            self.option_content["children_values"].append(content)
                            self.option_content["children_values"].append(child_widget.line_edit.text())
                    if child_item.childCount() > 0 and not self._find_option_children_content(child_item):
                        return False

        return True

    def renderMainOptionsList(self):
        """
               Renders the main options list in the tree widget.
               """
        if self.options_data:
            for option in self.options_data:
                if option:
                    option_main_widget = OptionMainWidget()
                    option_main_item = QTreeWidgetItem()

                    self.treeWidget.addTopLevelItem(option_main_item)
                    self.treeWidget.setItemWidget(option_main_item, 0, option_main_widget)

                    option_main_item.setData(0, Qt.ItemDataRole.DisplayRole, option["name"])
                    option_main_item.setText(0, option["name"])

                    font = option_main_item.font(0)
                    font.setPointSize(16)
                    option_main_item.setFont(0, font)

                    option_main_item.setExpanded(True)
                    option_structure = option["option_structure"]
                    self.set_single_option_structure(option_structure)
                    self.renderSingleOption(option_structure, option_main_item)
                    option_main_widget.add_option_to_editor.clicked.connect(
                        lambda checked, item=option_main_item,
                               item_name=option["name"]: self.validate_option_content(
                            checked, item, item_name))

    def renderSingleOption(self, option, main_parent_item: QTreeWidgetItem):
        """
         Renders a single option in the tree widget.

         Args:
             :param option: The option data to be rendered.
             :param main_parent_item: The parent item under which the option will be rendered.
         """
        for option_obj in option:
            if option_obj["widget_type"] == "menu":
                self.menu_widget, self.parent_menu_item = self.renderMenu(option_obj, main_parent_item)
                if len(option_obj["children"]) > 0:
                    self.renderSingleOption(option_obj["children"], main_parent_item=self.parent_menu_item)

            else:
                if option_obj["widget_type"] == "line_edit":
                    self.line_edit_widget, self.child_line_edit_item = self.renderLineEdit(option_obj, main_parent_item)
                    if len(option_obj["children"]) > 0:
                        self.renderSingleOption(option_obj["children"], main_parent_item=self.child_line_edit_item)

    def renderMenu(self, item, parent: QTreeWidgetItem):
        """
              Renders a menu widget in the tree widget.

              Args:
                  :param item: The menu item data to be rendered.
                  :param parent: The parent item under which the menu will be rendered.
              """
        menu_item = QTreeWidgetItem()
        menu_widget = OptionMenuWidget(item)
        menu_widget.onComboSelectionChange.connect(self.menu_value_changed)
        parent.addChild(menu_item)
        self.treeWidget.setItemWidget(menu_item, 0, menu_widget)
        menu_item.setData(0, Qt.ItemDataRole.UserRole, item["uuid"])
        menu_item.setData(1, Qt.ItemDataRole.UserRole, item["depends_on"]["trigger_id"])
        menu_item.setData(2, Qt.ItemDataRole.UserRole, item["depends_on"]["value"])

        menu_item.setExpanded(True)
        if item["depends_on"]["value"]:
            menu_item.setHidden(True)
        return menu_widget, menu_item

    def menu_value_changed(self, data):
        # Find the object with the id in the received data
        trigger_id = data["type_name"] + "--" + data["name"]

        iterator = QTreeWidgetItemIterator(self.treeWidget, QTreeWidgetItemIterator.IteratorFlag.All)
        while iterator.value():
            item = iterator.value()
            if item.data(1, Qt.ItemDataRole.UserRole) == trigger_id and item.data(2, Qt.ItemDataRole.UserRole):
                if item.data(2, Qt.ItemDataRole.UserRole) == data["triggered_value"]:
                    item.setHidden(False)
                elif item.data(2, Qt.ItemDataRole.UserRole) != data["triggered_value"]:
                    item.setHidden(True)

            iterator += 1

    def renderLineEdit(self, item, parent: QTreeWidgetItem):
        """
         Renders a line edit widget in the tree widget.

         Args:
             :param item: The line edit item data to be rendered.
             :param parent: The parent item under which the line edit will be rendered.
         """
        line_edit_item = QTreeWidgetItem()
        line_edit_widget = OptionLineEditWidget(item)

        parent.addChild(line_edit_item)
        self.treeWidget.setItemWidget(line_edit_item, 0, line_edit_widget)
        line_edit_item.setData(0, Qt.ItemDataRole.UserRole, item["uuid"])
        line_edit_item.setData(1, Qt.ItemDataRole.UserRole, item["depends_on"]["trigger_id"])
        line_edit_item.setData(2, Qt.ItemDataRole.UserRole, item["depends_on"]["value"])

        line_edit_item.setExpanded(True)
        if item["depends_on"]["value"]:
            line_edit_item.setHidden(True)
        return line_edit_widget, line_edit_item

    def find_object_with_dependency_on_trigger_id(self, trigger_id, trigger_value):
        stack = [self.single_option_structure]
        found_objects = []
        while stack:
            current = stack.pop()

            for obj in current:
                if 'depends_on' in obj:
                    for value in obj.values():
                        if isinstance(value, list):
                            stack.append(value)
                        elif isinstance(value, dict):
                            if value["trigger_id"] == trigger_id and value["value"] == trigger_value:
                                found_objects.append(obj['uuid'])
        if found_objects:
            return found_objects
        else:
            return None


class OptionMenuWidget(QWidget):
    onComboSelectionChange = pyqtSignal(dict)
    """
     A custom QWidget class for rendering a menu widget as part of the report options.

     Args:
         item: The data for the menu item to be rendered.
     """

    def __init__(self, item):
        """
             Initializes the menu widget with the provided item data.
             """
        super().__init__()

        self.item = item

        label_stylesheet = "background-color:transparent;color:black;"

        self.menu_label = QLabel(self.item["name"])
        self.menu_label.setStyleSheet(label_stylesheet)

        self.is_required = QLabel()
        self.is_required.setStyleSheet(label_stylesheet)
        self.is_required.setFixedSize(16, 16)
        required_icon = QIcon(":/resources/icons/star.svg")
        pixmap = required_icon.pixmap(13, 13)  # You can specify the size of the icon
        self.is_required.setPixmap(pixmap)

        option_name_is_required_layout = QHBoxLayout()
        option_name_is_required_layout.setSpacing(0)
        option_name_is_required_layout.addWidget(self.is_required)
        option_name_is_required_layout.addWidget(self.menu_label)

        self.combo = CustomComboBox()
        self.combo.setObjectName(self.item["uuid"])
        self.combo.currentTextChanged.connect(self.on_combo_index_changed)
        self.combo.setFixedSize(QSize(320, 39))
        self.combo.setEditable(False)
        self.model = QStandardItemModel()
        self.combo.setModel(self.model)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addLayout(option_name_is_required_layout)
        layout.addWidget(self.combo)
        self.setLayout(layout)
        self.setComboProperties()

    def setComboProperties(self):
        """
             Sets the properties for the combo box in the menu widget.
             """
        for item_option in self.item["options"]:
            item = QStandardItem(item_option["option_name"])
            item.setData(item_option["option_content"],
                         QtCore.Qt.ItemDataRole.UserRole)  # Qt.UserRole is a custom role you can use
            item.setData(item_option["option_name"],
                         QtCore.Qt.ItemDataRole.DisplayRole)  # Qt.UserRole is a custom role you can use
            self.model.appendRow(item)

        if not self.item["is_required_state"]:
            self.is_required.hide()

        if self.item["tool_tip_content"]:
            self.combo.setToolTip(self.item["tool_tip_content"])

    def on_combo_index_changed(self, text):
        data = {"triggered_value": text, "combo_id": self.item["uuid"], "name": self.item["name"],
                "type_name": self.item["type_name"]}
        self.onComboSelectionChange.emit(data)


class OptionLineEditWidget(QWidget):
    """
    A custom QWidget class for rendering a line edit widget as part of the report options.

    Args:
        item: The data for the line edit item to be rendered.
    """

    def __init__(self, item):
        """
               Initializes the line edit widget with the provided item data.
               """
        super().__init__()

        self.item = item

        self.line_edit_label = QLabel(self.item["name"])
        self.line_edit_label.setStyleSheet("background-color:transparent;color:black;")

        self.is_required = QLabel()
        self.is_required.setFixedSize(16, 16)

        required_icon = QIcon(":/resources/icons/star.svg")
        pixmap = required_icon.pixmap(13, 13)  # You can specify the size of the icon
        self.is_required.setPixmap(pixmap)

        option_name_is_required_layout = QHBoxLayout()
        option_name_is_required_layout.setSpacing(0)

        option_name_is_required_layout.addWidget(self.is_required)
        option_name_is_required_layout.addWidget(self.line_edit_label)

        self.model = QStandardItemModel(2, 1)
        self.model.setItem(0, 0, QStandardItem(self.item["content"]))
        #
        self.line_edit = QLineEdit()
        self.line_edit.setFixedSize(QSize(320, 39))
        self.line_edit.setStyleSheet("""
         QLineEdit {
            border:1px solid #A1AEB4;
            padding-left:7px;
            border-radius:7px;
            color:black;
            }
        """)
        self.line_edit.setFocus()
        self.line_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        mapper = QDataWidgetMapper()
        mapper.setModel(self.model)
        mapper.addMapping(self.line_edit, 1)
        mapper.setCurrentIndex(1)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addLayout(option_name_is_required_layout)
        layout.addWidget(self.line_edit)

        self.setLayout(layout)
        self.setLineEditProperties()

    def setLineEditProperties(self):
        """
             Sets the properties for the line edit in the widget.
             """
        if not self.item["is_required_state"]:
            self.is_required.hide()

        if self.item["place_holder_content"]:
            self.line_edit.setPlaceholderText(self.item["place_holder_content"])

        if self.item["tool_tip_content"]:
            self.line_edit.setToolTip(self.item["tool_tip_content"])


class OptionMainWidget(QWidget):
    """
     A custom QWidget class for rendering the main widget for each option in the report options.

     """

    def __init__(self):
        """
              Initializes the main widget with the provided option data.
              """
        super().__init__()

        self.add_option_to_editor = QPushButton()
        self.add_option_to_editor.setFixedHeight(35)
        self.add_option_to_editor.setIcon(QIcon(":/resources/icons/active_add.svg"))
        self.add_option_to_editor.setIconSize(QSize(28, 28))
        self.add_option_to_editor.setStyleSheet("""
        QPushButton {
            border:0;
            background-color:transparent;
        }
        QPushButton:pressed {
            background-color: lightgrey;
            border-radius:16px;
            border:0;
            color: #E0E0E0;
        }


        """)
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        option_name_check_box_layout = QHBoxLayout()
        option_name_check_box_layout.addSpacerItem(spacer)
        option_name_check_box_layout.addWidget(self.add_option_to_editor)

        layout = QVBoxLayout()
        layout.addLayout(option_name_check_box_layout)
        self.setLayout(layout)
