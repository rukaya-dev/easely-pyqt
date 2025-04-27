from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy, QSpacerItem
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.custom_push_button_with_icon import CustomAddButton
from views.componenets.customsComponents.custom_searchbar import CustomSearchBar
from views.componenets.customsComponents.loaders.internal_loader import InternalLoader

logger = set_up_logger('main.views.components.table.management.table_header_filtration_component')


class TableHeaderFiltration(QWidget):
    def __init__(self,  add_btn_name, controller, apply_filter=False, page_filter_widget=None, apply_search=False, search_place_holder="",
                 parent=None):
        super().__init__(parent)

        self.internal_loader = None
        self.parent = parent
        self.apply_search = apply_search
        self.search_place_holder = search_place_holder
        self.apply_filter = apply_filter
        self.filter_widget = page_filter_widget
        self.add_btn_name = add_btn_name

        self.add_btn = None
        self.left_layout = None
        self.search_bar = None
        self.right_layout = None

        self.controller = controller
        self.signals = SignalRepositorySingleton.instance()

        self.spacer = QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.main_h_layout.setContentsMargins(30, 0, 30, 10)

        if self.apply_search:
            self.setupLeftLayout()

        if not self.apply_search:
            self.main_h_layout.addSpacerItem(self.spacer)

        self.setupRightLayout()

        self.setLayout(self.main_h_layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def setupLeftLayout(self):
        self.search_bar = CustomSearchBar()

        if self.search_place_holder:
            self.search_bar.search_bar.setPlaceholderText(self.search_place_holder)
            self.search_bar.setToolTip(self.search_place_holder)
        self.search_bar.search_bar.textChanged.connect(self.on_search_text_change)

        self.left_layout = QHBoxLayout()
        self.left_layout.setSpacing(0)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        self.left_layout.addWidget(self.search_bar, 0, Qt.AlignmentFlag.AlignLeft)

        if self.apply_filter:
            self.left_layout.addWidget(self.filter_widget, 1, Qt.AlignmentFlag.AlignLeft)
        self.left_layout.addSpacerItem(self.spacer)

        self.main_h_layout.addLayout(self.left_layout)

    def setupRightLayout(self):
        self.add_btn = CustomAddButton(":/resources/icons/plus.svg", self.add_btn_name, parent=self)

        self.right_layout = QHBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.right_layout.addWidget(self.add_btn, Qt.AlignmentFlag.AlignRight)

        self.main_h_layout.addLayout(self.right_layout)

    @pyqtSlot(str)
    def on_search_text_change(self, text):
        QTimer.singleShot(100, lambda: (self.update_search_filter(text)))

    @asyncSlot(str)
    async def update_search_filter(self, text):
        if len(text) >= 1:
            self.controller.store.set_search_text(text)
            self.parent.refresh_table()

        else:
            self.controller.store.set_search_text("")
            self.parent.refresh_table()

