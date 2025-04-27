from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QTreeWidgetItem, \
    QLineEdit, QTreeWidgetItemIterator, QCheckBox, QHBoxLayout, QMessageBox, QWidget, QComboBox, QAbstractItemView

from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.tree_widget.custom_tree_widget import CustomTreeWidget
from views.componenets.treeWidgets.event_filter import PageEventFilter
from views.componenets.treeWidgets.LineEdit import LineEditLayout
from views.componenets.treeWidgets.menu_layout import MenuLayout, MenuOptionWidget
import uuid


class OptionTreeStructure(QWidget):
    currentItemIsChangedSignal = pyqtSignal()

    # New Project

    def __init__(self):
        super().__init__()

        self.c_input_item = None
        self.c_menu_item = None
        self.parent_menu = None
        self.menu_item = None
        self.child_menu_item = None
        self.child_menu = None
        self.filter_instance = None
        self.parentLineEdit = None
        self.input_item = None
        self.childLineEdit = None
        self.topLevelMenu = None
        self.childItems = None
        self.init_ui()

    def init_ui(self):

        self.treeWidget = CustomTreeWidget()
        self.treeWidget.setMinimumHeight(500)

        self.data = []

        self.current_column_width = self.treeWidget.columnWidth(0)

        option_structure_label = CustomLabel(name="Option Structure")

        remove_item = ButtonWithLoader("Remove Item", size=QSize(150, 34), parent=self)
        remove_item.clicked.connect(self.removeCurrentItem)

        menu_btn = ButtonWithLoader("Menu", size=QSize(95, 34), parent=self)
        menu_btn.clicked.connect(self.parentDropDownGenerator)

        input_box_btn = ButtonWithLoader("Input Box", size=QSize(150, 34), parent=self)
        input_box_btn.clicked.connect(self.parentInputBoxGenerator)

        de_select_btn = ButtonWithLoader("De-select", size=QSize(150, 34), parent=self)
        de_select_btn.clicked.connect(self.deSelectCurrentItem)

        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        buttons_layout.setSpacing(50)

        buttons_layout.addWidget(menu_btn)
        buttons_layout.addWidget(input_box_btn)
        buttons_layout.addWidget(de_select_btn)
        buttons_layout.addWidget(remove_item)

        # Setting the layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(option_structure_label)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.treeWidget, 1)
        self.setLayout(main_layout)

        self.treeWidget.itemClicked.connect(self.setActiveItem)

    def setTreeData(self, data):
        self.data = data

    def getTreeStructure(self, tree: CustomTreeWidget):
        iterator = QTreeWidgetItemIterator(tree, QTreeWidgetItemIterator.IteratorFlag.All)
        while iterator.value():
            item = iterator.value()
            item_widget = tree.itemWidget(item, 0)
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
            matched_obj = self.find_key_in_array_of_objects(item_id)
            name_widget = item_widget.findChild(QLineEdit, "name")

            if matched_obj:
                if matched_obj["widget_type"] == "line_edit":
                    actual_content_widget = item_widget.findChild(QLineEdit, "content")
                    if actual_content_widget:
                        matched_obj["content"] = actual_content_widget.text()

                place_holder_widget = item_widget.findChild(QLineEdit, matched_obj["place_holder_id"])
                depends_on_dropdown_value = item_widget.findChild(QComboBox, matched_obj["depends_on_dropdown_id"])
                depends_on_input_value = item_widget.findChild(QLineEdit, matched_obj["depends_on_input_id"])
                tool_tip_widget = item_widget.findChild(QLineEdit, matched_obj["tool_tip_id"])
                is_required_widget = item_widget.findChild(QCheckBox, matched_obj["is_required_id"])
                if name_widget:
                    matched_obj["name"] = name_widget.text()
                if depends_on_dropdown_value:
                    matched_obj["depends_on"]["trigger_id"] = depends_on_dropdown_value.currentText()
                if depends_on_input_value:
                    matched_obj["depends_on"]["value"] = depends_on_input_value.text()
                if place_holder_widget:
                    matched_obj["place_holder_content"] = place_holder_widget.text()
                if tool_tip_widget:
                    matched_obj["tool_tip_content"] = tool_tip_widget.text()
                if is_required_widget:
                    matched_obj["is_required_state"] = is_required_widget.isChecked()
                if matched_obj["widget_type"] == "menu":
                    for option in matched_obj["options"]:
                        option_widget = item_widget.findChild(MenuOptionWidget, str(option["option_id"]))
                        if option_widget:
                            option_name_line_edit_widget = option_widget.findChild(QLineEdit, str(option["option_id"]))
                            option_content_line_edit_widget = option_widget.findChild(QLineEdit, "option_content")
                            if option_name_line_edit_widget.text():
                                option["option_name"] = option_name_line_edit_widget.text()
                            if option_content_line_edit_widget:
                                option["option_content"] = option_content_line_edit_widget.text()

            iterator += 1

        return self.data

    def ValidateTree(self, tree: CustomTreeWidget):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)

        if tree.topLevelItemCount() == 0:
            return None
        iterator = QTreeWidgetItemIterator(tree, QTreeWidgetItemIterator.IteratorFlag.All)
        while iterator.value():
            item = iterator.value()
            item_widget = tree.itemWidget(item, 0)
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
            matched_obj = self.find_key_in_array_of_objects(item_id)
            if matched_obj:
                name_widget = item_widget.findChild(QLineEdit, "name")
                if name_widget:
                    if not name_widget.text():
                        msg.setText('Name structure is required')
                        msg.exec()
                        return
                    # if matched_obj["widget_type"] == "line_edit":
                    #     content_widget = item_widget.findChild(QLineEdit, "content")
                    #     if content_widget and not content_widget.text():
                    #         msg.setText(f"content of {matched_obj['name']} input box is required")
                    #         msg.exec()
                    #         return None
                    if matched_obj["widget_type"] == "menu":
                        for option in matched_obj["options"]:
                            option_widget = item_widget.findChild(MenuOptionWidget, str(option["option_id"]))
                            if option_widget:
                                option_name_line_edit_widget = option_widget.findChild(QLineEdit,
                                                                                       str(option["option_id"]))
                                option_content_line_edit_widget = option_widget.findChild(QLineEdit, "option_content")
                                if option_name_line_edit_widget:
                                    if not option_name_line_edit_widget.text():
                                        msg.setText(f"option {str(option['option_id'])} of {name_widget.text()} Menu is required")
                                        msg.exec()
                                        return None
                                if option_content_line_edit_widget:
                                    if not option_content_line_edit_widget.text():
                                        msg.setText(f"option {str(option['option_id'])} content of {name_widget.text()} Menu is required")
                                        msg.exec()
                                        return None
            iterator += 1
        return True

    def setActiveItem(self, item):
        self.treeWidget.setCurrentItem(item)
        self.getTreeStructure(self.treeWidget)
        self.currentItemIsChangedSignal.emit()

    def deSelectCurrentItem(self):
        if self.treeWidget.currentItem():
            self.treeWidget.setCurrentItem(None)

    def renderTree(self, data):
        self.setTreeData([])
        self.generate_tree_items(data)
        self.setTreeData(data)
        if self.childLineEdit:
            self.childLineEdit.setData(self.data)
        if self.child_menu:
            self.child_menu.menu_header_layout.setData(self.data)
        if self.parentLineEdit:
            self.parentLineEdit.setData(self.data)
        if self.parent_menu:
            self.parent_menu.menu_header_layout.setData(self.data)

    def generate_tree_items(self, data, parent=None):
        if data:
            for item in data:
                if item["type"] == "child":
                    if parent:
                        if item["widget_type"] == "line_edit":
                            self.childLineEdit, self.c_input_item = self.renderInputBox(item, parent)
                            if len(item['children']) > 0:
                                self.generate_tree_items(item["children"], parent=self.c_input_item)

                        if item["widget_type"] == "menu":
                            self.child_menu, self.c_menu_item = self.renderMenu(item, parent)

                            if len(item['children']) > 0 and self.c_input_item:
                                self.generate_tree_items(item["children"], parent=self.c_menu_item)

                else:
                    if item["widget_type"] == "line_edit":
                        self.parentLineEdit, self.input_item = self.renderInputBox(item, self.input_item)

                        if len(item['children']) > 0:
                            self.generate_tree_items(item["children"], parent=self.input_item)

                    if item["widget_type"] == "menu":
                        self.parent_menu, self.menu_item = self.renderMenu(item, self.menu_item)

                        if len(item['children']) > 0:
                            self.generate_tree_items(item["children"], parent=self.menu_item)

    def parentInputBoxGenerator(self):
        uui = str(uuid.uuid4())
        if self.treeWidget.currentItem() is not None:
            self.childInputBoxGenerator()
            return

            # Generate input item here
        self.input_item = QTreeWidgetItem()
        self.parentLineEdit = LineEditLayout(parent=self)

        place_holder_id = "placeHolderLineEdit_" + str(uui)
        tooltip_id = "toolTipLineEdit_" + str(uui)
        is_required_id = "isRequiredCheckBox" + str(uui)
        depends_on_input = "dependsOnInput" + str(uui)
        depends_on_input_value = "dependsOnInputValue" + str(uui)

        self.parentLineEdit.name_input.setObjectName("name")
        self.parentLineEdit.place_holder_input.setObjectName(place_holder_id)
        self.parentLineEdit.tool_tip_input.setObjectName(tooltip_id)
        self.parentLineEdit.required.setObjectName(is_required_id)
        self.parentLineEdit.depends_on_input.setObjectName(depends_on_input)
        self.parentLineEdit.depends_on_input_value.setObjectName(depends_on_input_value)

        self.treeWidget.addTopLevelItem(self.input_item)
        self.treeWidget.setItemWidget(self.input_item, 0, self.parentLineEdit)
        self.input_item.setData(0, Qt.ItemDataRole.UserRole, uui)

        self.data.append({
            "type": "parent",
            "uuid": uui,
            "widget_type": "line_edit",
            "type_name": "input_box_" + str(len(self.data) + 1),
            "name": "",
            "content": "",
            "place_holder_id": place_holder_id,
            "place_holder_content": "",
            "tool_tip_id": tooltip_id,
            "tool_tip_content": "",
            "is_required_id": is_required_id,
            "is_required_state": False,
            "depends_on_dropdown_id": depends_on_input,
            "depends_on_input_id": depends_on_input_value,
            "depends_on": {
                "trigger_id": "",
                "value": ""
            },
            "children": []
        })

        self.filter_instance = PageEventFilter(self, self.input_item)
        self.parentLineEdit.name_input.installEventFilter(PageEventFilter(self, self.input_item))
        self.parentLineEdit.place_holder_input.installEventFilter(PageEventFilter(self, self.input_item))
        self.parentLineEdit.tool_tip_input.installEventFilter(PageEventFilter(self, self.input_item))
        self.parentLineEdit.required.installEventFilter(PageEventFilter(self, self.input_item))
        self.parentLineEdit.depends_on_input.installEventFilter(PageEventFilter(self, self.input_item))
        self.parentLineEdit.depends_on_input_value.installEventFilter(PageEventFilter(self, self.input_item))

        self.input_item.setExpanded(True)
        self.parentLineEdit.setData(self.data)

    def childInputBoxGenerator(self):
        uui = str(uuid.uuid4())
        self.c_input_item = QTreeWidgetItem()
        self.childLineEdit = LineEditLayout(parent=self)

        place_holder_id = "placeHolderLineEdit_" + str(uui)
        tooltip_id = "toolTipLineEdit_" + str(uui)
        is_required_id = "isRequiredCheckBox" + str(uui)
        depends_on_input = "dependsOnInput" + str(uui)
        depends_on_input_value = "dependsOnInputValue" + str(uui)

        self.childLineEdit.place_holder_input.setObjectName(place_holder_id)
        self.childLineEdit.tool_tip_input.setObjectName(tooltip_id)
        self.childLineEdit.required.setObjectName(is_required_id)
        self.childLineEdit.depends_on_input.setObjectName(depends_on_input)
        self.childLineEdit.depends_on_input_value.setObjectName(depends_on_input_value)

        # Update Column Width
        self.current_column_width += 50
        self.treeWidget.header().resizeSection(0, self.current_column_width)

        self.c_input_item.setData(0, Qt.ItemDataRole.UserRole, uui)

        self.treeWidget.currentItem().addChild(self.c_input_item)

        self.treeWidget.setItemWidget(self.c_input_item, 0, self.childLineEdit)

        parent = self.find_key_in_array_of_objects(self.treeWidget.currentItem().data(0, Qt.ItemDataRole.UserRole))

        if parent is not None:
            parent["children"].append({
                "type": "child",
                "uuid": uui,
                "widget_type": "line_edit",
                "name": "",
                "type_name": "input_box_" + str(len(parent["children"]) + 1),
                "content": "",
                "place_holder_id": place_holder_id,
                "place_holder_content": "",
                "tool_tip_id": tooltip_id,
                "tool_tip_content": "",
                "depends_on_dropdown_id": depends_on_input,
                "depends_on_input_id": depends_on_input_value,
                "depends_on": {
                    "trigger_id": "",
                    "value": ""
                },
                "is_required_id": is_required_id,
                "is_required_state": False,
                "children": []
            })

        self.treeWidget.setCurrentIndex(self.treeWidget.indexFromItem(self.c_input_item))
        self.treeWidget.expandRecursively(self.treeWidget.indexFromItem(self.c_input_item), -1)

        self.childLineEdit.name_input.installEventFilter(PageEventFilter(self, self.c_input_item))
        self.childLineEdit.tool_tip_input.installEventFilter(PageEventFilter(self, self.c_input_item))
        self.childLineEdit.place_holder_input.installEventFilter(PageEventFilter(self, self.c_input_item))
        self.childLineEdit.required.installEventFilter(PageEventFilter(self, self.c_input_item))
        self.childLineEdit.depends_on_input.installEventFilter(PageEventFilter(self, self.c_input_item))
        self.childLineEdit.depends_on_input_value.installEventFilter(PageEventFilter(self, self.c_input_item))

        self.childLineEdit.setData(self.data)
        self.c_input_item.setExpanded(True)
        self.treeWidget.scrollToItem(self.c_input_item)

        self.treeWidget.update()
        self.treeWidget.updateGeometries()

    def parentDropDownGenerator(self):
        uui = str(uuid.uuid4())
        if self.treeWidget.currentItem() is not None:
            self.childDropDownGenerator()
            return

        self.menu_item = QTreeWidgetItem()
        self.parent_menu = MenuLayout(parent_item=self.menu_item, tree=self.treeWidget, data=self.data, parent=self)

        place_holder_id = "placeHolderLineEdit_" + str(uui)
        tooltip_id = "toolTipLineEdit_" + str(uui)
        is_required_id = "isRequiredCheckBox" + str(uui)
        depends_on_input = "dependsOnInput" + str(uui)
        depends_on_input_value = "dependsOnInputValue" + str(uui)

        self.parent_menu.menu_header_layout.place_holder_input.setObjectName(place_holder_id)
        self.parent_menu.menu_header_layout.tool_tip_input.setObjectName(tooltip_id)
        self.parent_menu.menu_header_layout.required.setObjectName(is_required_id)
        self.parent_menu.menu_header_layout.depends_on_input.setObjectName(depends_on_input)
        self.parent_menu.menu_header_layout.depends_on_input_value.setObjectName(depends_on_input_value)
        self.parent_menu.newOptionIsAdded.connect(self.addNewOptionObjectToData)
        self.parent_menu.existingOptionIsRemoved.connect(self.removeExistingOptionObjectFromData)

        self.treeWidget.addTopLevelItem(self.menu_item)
        self.treeWidget.setItemWidget(self.menu_item, 0, self.parent_menu)

        self.treeWidget.update()

        self.menu_item.setData(0, Qt.ItemDataRole.UserRole, uui)

        self.data.append({
            "type": "parent",
            "uuid": uui,
            "widget_type": "menu",
            "name": "",
            "type_name": "dropdown_box_" + str(len(self.data) + 1),
            "place_holder_id": place_holder_id,
            "place_holder_content": "",
            "tool_tip_id": tooltip_id,
            "depends_on_dropdown_id": depends_on_input,
            "depends_on_input_id": depends_on_input_value,
            "depends_on": {
                "trigger_id": "",
                "value": ""
            },
            "tool_tip_content": "",
            "is_required_id": is_required_id,
            "is_required_state": False,
            "options": [{
                "option_id": 1,
                "option_name": "",
                "option_content": "", },
                {
                    "option_id": 2,
                    "option_name": "",
                    "option_content": "", }
            ],
            "children": []
        })

        self.filter_instance = PageEventFilter(self, self.menu_item)
        self.parent_menu.menu_header_layout.name_input.installEventFilter(PageEventFilter(self, self.menu_item))
        self.parent_menu.menu_header_layout.place_holder_input.installEventFilter(PageEventFilter(self, self.menu_item))
        self.parent_menu.menu_header_layout.tool_tip_input.installEventFilter(PageEventFilter(self, self.menu_item))
        self.parent_menu.menu_header_layout.required.installEventFilter(PageEventFilter(self, self.menu_item))
        self.parent_menu.menu_header_layout.depends_on_input.installEventFilter(PageEventFilter(self, self.menu_item))
        self.parent_menu.menu_header_layout.depends_on_input_value.installEventFilter(
            PageEventFilter(self, self.menu_item))

        self.menu_item.setExpanded(True)

        # self.menu_item.setSizeHint(0, self.parent_menu.sizeHint())
        self.parent_menu.menu_header_layout.setData(self.data)
        self.treeWidget.scrollToItem(self.menu_item)

    def childDropDownGenerator(self):
        uui = str(uuid.uuid4())

        self.child_menu_item = QTreeWidgetItem()

        self.child_menu = MenuLayout(parent_item=self.child_menu_item, tree=self.treeWidget, parent=self)
        place_holder_id = "placeHolderLineEdit_" + str(uui)
        tooltip_id = "toolTipLineEdit_" + str(uui)
        is_required_id = "isRequiredCheckBox" + str(uui)
        depends_on_input = "dependsOnInput" + str(uui)
        depends_on_input_value = "dependsOnInputValue" + str(uui)

        self.child_menu.menu_header_layout.place_holder_input.setObjectName(place_holder_id)
        self.child_menu.menu_header_layout.tool_tip_input.setObjectName(tooltip_id)
        self.child_menu.menu_header_layout.required.setObjectName(is_required_id)
        self.child_menu.menu_header_layout.depends_on_input.setObjectName(depends_on_input)
        self.child_menu.menu_header_layout.depends_on_input_value.setObjectName(depends_on_input_value)

        # Update Column Width
        self.current_column_width += 50
        self.treeWidget.header().resizeSection(0, self.current_column_width)

        self.child_menu_item.setData(0, Qt.ItemDataRole.UserRole, uui)
        self.child_menu.newOptionIsAdded.connect(self.addNewOptionObjectToData)
        self.child_menu.existingOptionIsRemoved.connect(self.removeExistingOptionObjectFromData)

        self.treeWidget.currentItem().addChild(self.child_menu_item)
        self.treeWidget.setItemWidget(self.child_menu_item, 0, self.child_menu)

        self.child_menu_item.setExpanded(True)

        parent = self.find_key_in_array_of_objects(self.treeWidget.currentItem().data(0, Qt.ItemDataRole.UserRole))

        if parent is not None:
            parent["children"].append({
                "type": "child",
                "uuid": uui,
                "widget_type": "menu",
                "name": "",
                "place_holder_id": place_holder_id,
                "type_name": "dropdown_box_" + str(len(parent["children"]) + 1),
                "place_holder_content": "",
                "tool_tip_id": tooltip_id,
                "tool_tip_content": "",
                "depends_on_dropdown_id": depends_on_input,
                "depends_on_input_id": depends_on_input_value,
                "depends_on": {
                    "trigger_id": "",
                    "value": ""
                },
                "is_required_id": is_required_id,
                "is_required_state": False,
                "options": [{
                    "option_id": int(self.child_menu.option_1.objectName()),
                    "option_name": "",
                    "option_content": "",
                },
                    {
                        "option_id": int(self.child_menu.option_2.objectName()),
                        "option_name": "",
                        "option_content": "",

                    }
                ],
                "children": []
            })

        self.treeWidget.setCurrentIndex(self.treeWidget.indexFromItem(self.child_menu_item))
        self.filter_instance = PageEventFilter(self, self.child_menu_item)
        self.child_menu.menu_header_layout.name_input.installEventFilter(PageEventFilter(self, self.child_menu_item))
        self.child_menu.menu_header_layout.place_holder_input.installEventFilter(
            PageEventFilter(self, self.child_menu_item))
        self.child_menu.menu_header_layout.required.installEventFilter(PageEventFilter(self, self.child_menu_item))
        self.child_menu.menu_header_layout.depends_on_input.installEventFilter(
            PageEventFilter(self, self.child_menu_item))
        self.child_menu.menu_header_layout.depends_on_input_value.installEventFilter(
            PageEventFilter(self, self.child_menu_item))
        self.child_menu.menu_header_layout.required.installEventFilter(PageEventFilter(self, self.child_menu_item))
        self.child_menu.menu_header_layout.tool_tip_input.installEventFilter(
            PageEventFilter(self, self.child_menu_item))

        # self.setActiveItem(self.child_menu_item)
        self.child_menu.menu_header_layout.setData(self.data)

        self.treeWidget.update()
        self.treeWidget.updateGeometries()

    def find_key_in_array_of_objects(self, value_to_find):
        stack = [self.data]
        while stack:
            current = stack.pop()

            for obj in current:
                if value_to_find in obj.values():
                    # You can return the object or perform any other operation needed
                    return obj

                for value in obj.values():
                    if isinstance(value, list):
                        stack.append(value)
        return None

    def removeCurrentItem(self):
        # Removing the item from data also
        current_item = self.treeWidget.currentItem()
        if self.treeWidget.currentItem() is not None:
            item_parent_id = current_item.parent().data(0,
                                                        Qt.ItemDataRole.UserRole) if current_item.parent() is not None else current_item.data(
                0, Qt.ItemDataRole.UserRole)
            matched_parent_obj = self.find_key_in_array_of_objects(item_parent_id)

            if current_item.parent() is None:
                self.data.remove(matched_parent_obj)
            else:
                for i, child in enumerate(matched_parent_obj["children"]):
                    if child["uuid"] == current_item.data(0, Qt.ItemDataRole.UserRole):
                        matched_parent_obj["children"].pop(i)
                        break

            index = self.treeWidget.indexFromItem(current_item)
            parent_index = self.treeWidget.indexFromItem(current_item.parent())
            self.treeWidget.model().removeRow(index.row(), parent_index)

    def addNewOptionObjectToData(self, menu_item_id, option_id):
        matched_obj = self.find_key_in_array_of_objects(menu_item_id)
        if matched_obj and matched_obj['widget_type'] == "menu":
            matched_obj["options"].append({
                "option_id": option_id,
                "option_name": "",
                "option_content": "",
            })

    def removeExistingOptionObjectFromData(self, menu_item_id, option_id):
        matched_obj = self.find_key_in_array_of_objects(menu_item_id)
        option_id = int(option_id)
        # Find the index of the option to remove
        index_to_remove = None
        for i, option in enumerate(matched_obj["options"]):
            if option["option_id"] == option_id:
                index_to_remove = i
                break

        # If a matching option is found, remove it
        if index_to_remove is not None:
            matched_obj["options"].pop(index_to_remove)

    def renderInputBox(self, item, parent: QTreeWidgetItem):
        line_edit = LineEditLayout(parent=self)

        line_edit.name_input.setObjectName("name")
        line_edit.name_input.setText(item["name"])

        line_edit.content_input.setObjectName("content")
        line_edit.content_input.setText(item["content"])

        line_edit.place_holder_input.setObjectName(item["place_holder_id"])
        line_edit.place_holder_input.setText(item["place_holder_content"])

        line_edit.tool_tip_input.setObjectName(item["tool_tip_id"])
        line_edit.tool_tip_input.setText(item["tool_tip_content"])

        line_edit.required.setObjectName(item["is_required_id"])
        line_edit.required.setChecked(item["is_required_state"])

        line_edit.depends_on_input.setObjectName(item["depends_on_dropdown_id"])
        line_edit.depends_on_input.setCurrentText(item["depends_on"]["trigger_id"])

        line_edit.depends_on_input_value.setObjectName(item["depends_on_input_id"])
        line_edit.depends_on_input_value.setText(item["depends_on"]["value"])

        input_item = QTreeWidgetItem()
        input_item.setData(0, Qt.ItemDataRole.UserRole, item["uuid"])

        # Update Column Width
        self.current_column_width += 50
        self.treeWidget.header().resizeSection(0, self.current_column_width)

        if item["type"] == "parent":
            self.treeWidget.addTopLevelItem(input_item)
            self.treeWidget.setItemWidget(input_item, 0, line_edit)
            self.setActiveItem(input_item)
            input_item.setExpanded(True)

        else:
            parent.addChild(input_item)
            self.treeWidget.setItemWidget(input_item, 0, line_edit)
            input_item.setExpanded(True)

        if input_item:
            line_edit.name_input.installEventFilter(PageEventFilter(self, input_item))
            line_edit.tool_tip_input.installEventFilter(PageEventFilter(self, input_item))
            line_edit.place_holder_input.installEventFilter(PageEventFilter(self, input_item))
            line_edit.required.installEventFilter(PageEventFilter(self, input_item))
            line_edit.depends_on_input.installEventFilter(PageEventFilter(self, input_item))
            line_edit.depends_on_input_value.installEventFilter(PageEventFilter(self, input_item))

        return line_edit, input_item

    def renderMenu(self, item, parent: QTreeWidgetItem):

        menu_item = QTreeWidgetItem()
        menu = MenuLayout(parent_item=menu_item, tree=self.treeWidget, parent=self)

        menu.menu_header_layout.name_input.setObjectName("name")
        menu.menu_header_layout.name_input.setText(item["name"])

        menu.menu_header_layout.place_holder_input.setObjectName(item["place_holder_id"])
        menu.menu_header_layout.place_holder_input.setText(item["place_holder_content"])

        menu.menu_header_layout.tool_tip_input.setObjectName(item["tool_tip_id"])
        menu.menu_header_layout.tool_tip_input.setText(item["tool_tip_content"])

        menu.menu_header_layout.required.setObjectName(item["is_required_id"])
        menu.menu_header_layout.required.setChecked(item["is_required_state"])

        menu.menu_header_layout.depends_on_input.setObjectName(item["depends_on_dropdown_id"])
        menu.menu_header_layout.depends_on_input.setCurrentText(item["depends_on"]["trigger_id"])

        menu.menu_header_layout.depends_on_input_value.setObjectName(item["depends_on_input_id"])
        menu.menu_header_layout.depends_on_input_value.setText(item["depends_on"]["value"])

        menu.newOptionIsAdded.connect(self.addNewOptionObjectToData)
        menu.existingOptionIsRemoved.connect(self.removeExistingOptionObjectFromData)

        self.current_column_width += 50
        self.treeWidget.header().resizeSection(0, self.current_column_width)

        for i, option in enumerate(item["options"]):
            if option["option_id"] == int(menu.option_1.objectName()):
                menu.option_1.option_input.setText(option["option_name"])
                menu.option_1.option_actual_input.setText(option["option_content"])
            elif option["option_id"] == int(menu.option_2.objectName()):
                menu.option_2.option_input.setText(option["option_name"])
                menu.option_2.option_actual_input.setText(option["option_content"])
            else:
                menu.generateMenuOption(option["option_id"])
                option_widget = menu.findChild(MenuOptionWidget, str(option["option_id"]))
                option_name_line_edit_widget = option_widget.findChild(QLineEdit, str(option["option_id"]))
                option_content_line_edit_widget = option_widget.findChild(QLineEdit, "option_content")
                if option_name_line_edit_widget:
                    option_name_line_edit_widget.setText(option["option_name"])
                if option_content_line_edit_widget:
                    option_content_line_edit_widget.setText(option["option_content"])
                menu.options_instance_counter = menu.options_layout.count()

        if item["type"] == "parent":
            self.treeWidget.addTopLevelItem(menu_item)
            self.treeWidget.setItemWidget(menu_item, 0, menu)
            menu_item.setData(0, Qt.ItemDataRole.UserRole, item["uuid"])
            menu_item.setExpanded(True)

        else:
            menu_item = QTreeWidgetItem()
            parent.addChild(menu_item)
            self.treeWidget.setItemWidget(menu_item, 0, menu)
            menu_item.setExpanded(True)
            menu_item.setData(0, Qt.ItemDataRole.UserRole, item["uuid"])

        if menu:
            menu.menu_header_layout.name_input.installEventFilter(PageEventFilter(self, menu_item))
            menu.menu_header_layout.tool_tip_input.installEventFilter(PageEventFilter(self, menu_item))
            menu.menu_header_layout.place_holder_input.installEventFilter(PageEventFilter(self, menu_item))
            menu.menu_header_layout.required.installEventFilter(PageEventFilter(self, menu_item))
            menu.menu_header_layout.depends_on_input.installEventFilter(PageEventFilter(self, menu_item))
            menu.menu_header_layout.depends_on_input_value.installEventFilter(PageEventFilter(self, menu_item))

        return menu, menu_item
