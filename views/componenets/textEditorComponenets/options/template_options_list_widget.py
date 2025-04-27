from PyQt6 import QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel
from PyQt6.QtGui import QPalette, QStandardItemModel, QStandardItem, QFont, QBrush, QColor

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView, QStyledItemDelegate, \
    QAbstractItemView, QHBoxLayout, QStyle, QSizePolicy

from utils.utlis import string_to_slug
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.textEditorComponenets.options.custom_line_edit import CustomLineEdit


class TemplateOptionsListWidget(QWidget):
    """
    A custom widget that provides a list view for displaying and interacting with a list of options.
    It supports searching, selecting, and checking options within a specific category.

    Attributes:
        optionChecked (pyqtSignal): Signal emitted when an option is checked or unchecked, carrying the option's details.

    Args:
        category (str): The category of options to be displayed.
        :param: Parent (QWidget, optional): The parent widget. Defaults to None.

    Methods:
        search_options: Filters the list view based on the entered search text.
        toggle_check_box: Toggles the check state of an item when clicked.
        set_checked_items_by_default: Sets initially checked state for items based on a given list.
        add_options_to_list_view: Populates the list view with options.
        on_option_clicked_slot: Slot to handle the itemChanged signal from the list item model.
    """
    optionChecked = pyqtSignal(dict)

    def __init__(self, category, parent=None):
        """
               Constructor for TemplateOptionsListWidget. Initializes the UI components and sets up the model-view architecture.
        """
        super().__init__()
        self.options = []

        central_widget = QWidget()
        central_widget.setObjectName("template_options_central_widget")
        central_widget.setStyleSheet("background-color:white;")
        central_widget.setFixedWidth(480)

        self.category_label = QLabel()
        self.category_label.setStyleSheet("color:black;")
        self.category_label.setText(f"{category} Options")
        self.category_label.setFixedHeight(50)

        font = self.category_label.font()
        font.setPointSize(16)
        self.category_label.setFont(font)

        self.options_list_view = QListView()
        self.options_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.options_list_view.setItemDelegate(ListViewDelegate())

        self.options_list_item_model = QStandardItemModel(self.options_list_view)
        self.options_list_item_model.setColumnCount(2)
        self.options_list_view.setModel(self.options_list_item_model)

        self.options_list_item_model.itemChanged.connect(self.on_option_clicked)

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.options_list_item_model)
        self.proxy_model.setFilterKeyColumn(0)
        self.proxy_model.invalidate()
        self.options_list_view.setModel(self.proxy_model)

        search_bar = CustomLineEdit(self)
        search_bar.textChanged.connect(self.search_options)

        search_line_edit_layout = QHBoxLayout()
        search_line_edit_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        search_line_edit_layout.setContentsMargins(0, 20, 0, 10)
        search_line_edit_layout.addWidget(search_bar)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.setContentsMargins(30, 10, 30, 10)

        main_layout.addLayout(search_line_edit_layout)
        main_layout.addWidget(self.category_label)
        main_layout.addWidget(self.options_list_view)

        central_widget.setLayout(main_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(central_widget)
        self.setLayout(layout)

        self.setStyleSheet("""
        QWidget#template_options_central_widget {
             border-radius: 7px;
             background-color:white;
        }
        QLabel {
          font-size:12pt;
        }
        QListView {
            border:0;
            show-decoration-selected: 0; /* make the selection span the entire width of the view */
        }
        QListView::item {
            spacing: 20px;
            color:black;
            background-color:transparent;
        }
        QListView::item::selected {
            background-color:#FCFDFF;
            border:0;
            border-radius:3px;

        }
        QListView::item:selected:active {
            background: #FCFDFF;
        }
        QListView::indicator {
            width: 17;
            height: 17;
            border-radius: 2px;
            border-style: solid;
            border-width: 1px;
            border-color: #A1AEB4;
            background-color : transparent;
        }
        QListView::indicator:checked {
            image: url(:/resources/icons/active_check.svg);
            background-color : transparent;
            border:0;
            width: 17;
            height: 17;
        }
        """)

    def search_options(self, text):
        """
            Filters the option list view based on the search text.

            Args:
                text (str): The text to be used as the filter criterion.
            """
        # Apply a case-insensitive filter for the given text
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterWildcard('*' + text + '*')

    def set_checked_items_by_default(self, options):
        if options:
            for index in range(self.options_list_item_model.rowCount()):
                item = self.options_list_item_model.item(index)
                if item is not None:
                    # Generate a set of slugs from the options for efficient membership testing
                    item_data = item.data(Qt.ItemDataRole.DisplayRole)
                    if item_data in options:
                        item.setCheckState(Qt.CheckState.Checked)

    def add_options_to_list_view(self, options):
        self.options_list_item_model.clear()
        self.options = []
        if options:
            for option in options:
                item = QStandardItem()
                item.setCheckable(True)
                item.setData(option, Qt.ItemDataRole.DisplayRole)
                self.options_list_item_model.appendRow(item)
                self.options.append(option)

    def on_option_clicked(self, item: QStandardItem):
        """
          Slot function that gets triggered when an option in the list is clicked.

          Args:
              item (QStandardItem): The item that was clicked.
          """

        option_check_state = True if item.checkState() == item.checkState().Checked else False
        option = {'option_name': item.data(Qt.ItemDataRole.DisplayRole), 'option_check_state': option_check_state}
        self.optionChecked.emit(option)


class ListViewDelegate(QStyledItemDelegate):
    """
     A custom delegate for styling and layout adjustments of items within the list view.

     Methods:
         initStyleOption: Customizes the style options for each item.
         sizeHint: Provides a custom size hint for each item in the list.
     """

    def initStyleOption(self, option, index):
        """
         Adjusts the style option of each item in the list.

         Args:
             option (QStyleOptionViewItem): The option to be adjusted.
             Index (QModelIndex): The index of the item.
             :param option:
             :param index:
         """
        super(ListViewDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignVCenter
        font = option.font
        font.setPointSize(14)  # Set the desired font size here
        option.font = font
        option.textElideMode = Qt.TextElideMode.ElideNone

        if option.state & QStyle.StateFlag.State_Selected:
            option.backgroundBrush = QBrush(QColor('lightblue'))  # Set the background to light blue
            option.palette.setBrush(QPalette.ColorRole.Highlight,
                                    QBrush(Qt.BrushStyle.NoBrush))  # Remove selection border

    def sizeHint(self, option, index):
        """
         Provides a custom size hint for the items in the list.

         Args:
             option (QStyleOptionViewItem): The option used for the size hint calculation.
             Index (QModelIndex): The index of the item.
             :param option:
             :param index:
         """
        original_hint = super(ListViewDelegate, self).sizeHint(option, index)
        min_height = 40  # Set your desired minimum height here
        width = original_hint.width()
        height = max(original_hint.height(), min_height)
        return QtCore.QSize(width, height)
