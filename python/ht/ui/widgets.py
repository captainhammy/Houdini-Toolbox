"""This module contains custom PySide widgets."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from PySide2 import QtCore, QtGui, QtWidgets
import enum
import os

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================


class BaseInputItemWidget(QtWidgets.QWidget):

    def __init__(self, base_widget, label=None):
        super(BaseInputItemWidget, self).__init__()

        self.base_widget = base_widget

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(hou.ui.scaledSize(2))
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.label_widget = None

        # Create (optional) label.
        if label is not None and label != "":
            self.label_widget = hou.qt.FieldLabel(label)

            layout.addWidget(self.label_widget)

        layout.addWidget(self.base_widget)


class DefaultComboBox(QtWidgets.QComboBox):

    def __init__(self, default_index=0, parent=None):

        super(DefaultComboBox, self).__init__(parent=parent)

        self._default_index = default_index

        # Set the view to a non-abstract view so that the QAbstractItemView
        # styling gets applied.
        self.setView(QtWidgets.QListView())
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.setObjectName("DefaultCombo")

        self.setStyleSheet(
            """QComboBox#DefaultCombo[nondefault=true] {
    font-weight: bold;
}"""
        )

        self.currentIndexChanged.connect(self._adjust_styling)

    def _adjust_styling(self, index):
        self.setProperty("nondefault", index != self._default_index)

        self.setStyle(self.style())

    def set_and_assume_default(self, default_index=0):
        self._default_index = default_index

        self.setCurrentIndex(default_index)

    def wheelEvent(self, event):
        event.ignore()



class EmptySeparator(QtWidgets.QWidget):

    def __init__(self, height=10, parent=None):
        super(EmptySeparator, self).__init__(parent=parent)

        self.setMinimumHeight(hou.ui.scaledSize(height))


class FileChooser(QtWidgets.QWidget):
    """This class represents a file choosing widget."""

    def __init__(self, parent=None, file_pattern=None):
        super(FileChooser, self).__init__(parent)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # ---------------------------------------------------------------------

        self.field = QtWidgets.QLineEdit()
        layout.addWidget(self.field)

        # ---------------------------------------------------------------------

        self.button = hou.qt.FileChooserButton()

        layout.addWidget(self.button)

        current = self.get_path()

        self.button.start_directory = None
        self.button.default_value = None

        if current:
            self.button.start_directory = os.path.dirname(current)
            self.button.default_value = os.path.basename(current)

        self.button.file_pattern = file_pattern
        self.button.chooser_mode = hou.fileChooserMode.Write

        self.button.fileSelected.connect(self.handle_selection)

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def handle_selection(self, path):
        # ext = os.path.splitext(path)[1]

        # if not ext:
        #     path = "{}.json".format(path)

        self.set_path(path)

    def enable(self, enable):
        """Set the UI element's enabled state."""
        self.field.setEnabled(enable)
        self.button.setEnabled(enable)

    def get_path(self):
        """Get the text."""
        return self.field.text()

    def set_path(self, path):
        """Set the path."""

        self.field.setText(path)

        current = self.get_path()

        if current:
            self.button.start_directory = os.path.dirname(current)
            self.button.default_value = os.path.basename(current)


class FilterWidget(QtWidgets.QWidget):
    """This class represents a Filter widget."""
    filter_changed = QtCore.Signal(str)

    def __init__(self, label="Filter", tooltip=None, parent=None):
        super(FilterWidget, self).__init__(parent)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QtWidgets.QLabel("Filter"))

        self.field = QtWidgets.QLineEdit()
        layout.addWidget(self.field)

        if tooltip is not None:
            self.field.setToolTip(tooltip)

        self.field.textChanged.connect(self._emit_filter_changed)

    def _emit_filter_changed(self, text):
        self.filter_changed.emit(text)


class GenericTableView(QtWidgets.QTableView):
    """This class represents a generic table view for information."""

    def __init__(self, parent=None):
        super(GenericTableView, self).__init__(parent)

        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setWordWrap(False)

        h_header = self.horizontalHeader()
        h_header.setVisible(False)
        h_header.setStretchLastSection(True)
        h_header.resizeSection(0, 250)

    def _copy_table_cell(self, index):
        """Copy the contents of a table cell to the clipboard."""
        result = self.model().data(index)

        if result is not None:
            clipboard = QtGui.QApplication.clipboard()  # pylint: disable=c-extension-no-member
            clipboard.setText(result)

    def contextMenuEvent(self, event):
        """Handle RMB menu clicks."""
        index = self.indexAt(event.pos())

        if not index.isValid():
            return

        # Create a menu.
        menu = QtWidgets.QMenu(self)

        # Create an entry to copy cells.
        copy_action = QtWidgets.QAction("Copy", self)
        menu.addAction(copy_action)

        copy_action.setShortcut(
            QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_C)
        )

        # Display the menu and get the choice..
        action = menu.exec_(event.globalPos())

        # Copy the cell.
        if action == copy_action:
            self._copy_table_cell(index)


class InputMenuFieldWidget(BaseInputItemWidget):
    # current_index_changed = QtCore.Signal(int)

    def __init__(self, menu_field_widget, label=None):
        super(InputMenuFieldWidget, self).__init__(menu_field_widget, label=label)

        self.menu_field_widget = menu_field_widget

        # self.menu_widget.field.textChanged.connect(self._emit_index_changed)

    # def _emit_index_changed(self, index):
    #     self.current_index_changed.emit(index)

    def set_and_assume_default(self, default_value):
        self.menu_field_widget.set_and_assume_default(default_value)

    def value(self):
        self.menu_field_widget.value()


class InputMenuWidget(BaseInputItemWidget):
    current_index_changed = QtCore.Signal(int)

    def __init__(self, menu_widget, label=None):
        super(InputMenuWidget, self).__init__(menu_widget, label=label)

        self.menu_widget = menu_widget

        self.menu_widget.currentIndexChanged.connect(self._emit_index_changed)

    def _emit_index_changed(self, index):
        self.current_index_changed.emit(index)

    def set_and_assume_default(self, default_value):
        self.menu_widget.set_and_assume_default(default_value)

    def value(self):
        self.menu_widget.value()


class InputSpinboxWidget(BaseInputItemWidget):

    value_changed = QtCore.Signal(int)

    def __init__(self, label=None, min_value=None, max_value=None, default_value=0):
        self.spin_box = QtWidgets.QSpinBox()

        super(InputSpinboxWidget, self).__init__(self.spin_box, label)

        if min_value is not None:
            self.spin_box.setMinimum(min_value)

        if max_value is not None:
            self.spin_box.setMaximum(max_value)

        self.spin_box.valueChanged.connect(self._emit_value_changed)

        self._default_value = default_value

        self.spin_box.setObjectName("DefaultedSpinBox")

        self.setStyleSheet(
            """QSpinBox#DefaultedSpinBox[nondefault=true] {
                font-weight: bold;
            }"""
        )

    def _adjust_styling(self, is_default):
        self.spin_box.setProperty("nondefault", not is_default)

        self.spin_box.setStyle(self.spin_box.style())

    def _emit_value_changed(self, value):
        self._adjust_styling(value == self._default_value)

        self.value_changed.emit(value)

    def set_and_assume_default(self, default_value):
        self._default_value = default_value

        self.set_value(default_value)

    def set_value(self, value):
        self.spin_box.setValue(value)

    def value(self):
        return self.spin_box.value()


class ClickableLabel(QtWidgets.QLabel):

    clicked = QtCore.Signal()

    def __init__(self, text, parent=None):
        super(ClickableLabel, self).__init__(text, parent=parent)

        self.setObjectName("DefaultLabel")

        self.setStyleSheet(
"""ClickableLabel#DefaultLabel[nondefault=true] {
    font-weight: bold;
}"""
        )

    def adjust_styling(self, is_default):
        self.setProperty("nondefault", not is_default)

        self.setStyle(self.style())

    def mousePressEvent(self, event):
        self.clicked.emit()


class LabeledToggleWidget(QtWidgets.QWidget):
    state_changed = QtCore.Signal(int)

    def __init__(self, label, default_state=False, parent=None):

        super(LabeledToggleWidget, self).__init__(parent=parent)

        self._default_state = default_state

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.check_box = QtWidgets.QCheckBox()
        layout.addWidget(self.check_box)

        self.check_box.stateChanged.connect(self._emit_state_change)

        self.label = ClickableLabel(label)
        layout.addWidget(self.label)

        layout.addStretch(1)

        self.label.clicked.connect(self._label_click)

    def _emit_state_change(self, state):
        self.label.adjust_styling(state == self._default_state)

        self.state_changed.emit(state)

    def _label_click(self):
        self.check_box.toggle()

    def set_and_assume_default(self, default_state):
        self.set_default(default_state)

        self.set_checked(default_state)

    def set_default(self, default_state):
        self._default_state = default_state

    def set_checked(self, checked):
        self.check_box.setChecked(checked)

    def value(self):
        return self.check_box.isChecked()


class InputToggleWidget(QtWidgets.QWidget):

    state_changed = QtCore.Signal(int)

    def __init__(self, text, default_state=False, parent=None):

        super(InputToggleWidget, self).__init__(parent=parent)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(hou.ui.scaledSize(2))
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        # Create (optional) label.
        label = hou.qt.FieldLabel("")

        layout.addWidget(label)

        self.toggle = LabeledToggleWidget(text, default_state=default_state)
        layout.addWidget(self.toggle)

        self.toggle.state_changed.connect(self._emit_state_change)

    def _emit_state_change(self, state):
        self.state_changed.emit(state)

    def set_and_assume_default(self, default_state):
        self.toggle.set_and_assume_default(default_state)

    def set_checked(self, checked):
        self.toggle.set_checked(checked)

    def value(self):
        return self.toggle.value()


class MenuFieldMode(enum.Enum):
    """Mode settings for MenuFields."""

    Replace = "replace"
    Toggle = "toggle"


class MenuField(QtWidgets.QWidget):
    """This class represents a crappy attempt at a Replace/Toggle style
    string menu.

    """

    def __init__(self, menu_items, mode=MenuFieldMode.Replace, default_value="", parent=None):
        super(MenuField, self).__init__(parent)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)

        # ---------------------------------------------------------------------

        self.field = DefaultedLineEdit(default_value)
        layout.addWidget(self.field)

        # ---------------------------------------------------------------------

        # button = QtWidgets.QPushButton()
        # layout.addWidget(button)

        # button.setProperty("menu", True)

        # menu = QtWidgets.QMenu()#button)
        menu = hou.qt.Menu()

        for item in menu_items:
            label, value = item

            action = menu.addAction(label)

            if mode == MenuFieldMode.Replace:
                action.triggered.connect(
                    lambda val=value: self.set_value(val)
                )

            elif mode == MenuFieldMode.Toggle:
                action.triggered.connect(
                    lambda val=value: self.toggle_value(val)
                )
        # button.setMenu(menu)

        button = hou.qt.MenuButton(menu)
        layout.addWidget(button)

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def set_and_assume_default(self, default_value):
        self.field.set_and_assume_default(default_value)

    def set_value(self, value):
        """Set the field to a value."""
        self.field.setText(value)

    def toggle_value(self, value):
        """Toggle a value in the field."""
        text = self.value()

        if value in text:
            text = text.replace(value, "")

            self.set(text.strip())

        else:
            if not text:
                text = value

            else:
                text = "{} {}".format(text, value)

            self.set_value(text)

    def value(self):
        """The field value."""
        return self.field.text()


class StatusMessageWidget(QtWidgets.QWidget):
    """This class represents an status notification widget."""

    Error = 0
    Warning = 1
    Info = 2

    def __init__(self, icon_size=24, parent=None):
        super(StatusMessageWidget, self).__init__(parent)

        self._error_mappings = {}
        self._warning_mappings = {}
        self._info_mappings = {}

        self.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        layout.setContentsMargins(0, 0, 0, 0)

        self.info_pixmap = hou.qt.createIcon("DIALOG_info").pixmap(icon_size, icon_size)
        self.warning_pixmap = hou.qt.createIcon("DIALOG_warning").pixmap(icon_size, icon_size)
        self.error_pixmap = hou.qt.createIcon("DIALOG_error").pixmap(icon_size, icon_size)

        # ---------------------------------------------------------------------

        self.icon = QtWidgets.QLabel()
        layout.addWidget(self.icon)

        self.icon.setFixedSize(icon_size, icon_size)
        self.icon.setPixmap(self.info_pixmap)
        self.icon.hide()

        # ---------------------------------------------------------------------

        self.display = QtWidgets.QLabel()
        layout.addWidget(self.display)

        self.setFixedHeight(24)

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _clear_error(self, level):
        """Clear any error messages at a specific level."""
        if level in self._error_mappings:
            del self._error_mappings[level]

        self._update_display()

    def _clear_info(self, level):
        """Clear any info messages at a specific level."""
        if level in self._info_mappings:
            del self._info_mappings[level]

        self._update_display()

    def _clear_warning(self, level):
        """Clear any warning messages at a specific level."""
        if level in self._warning_mappings:
            del self._warning_mappings[level]

        self._update_display()

    def _get_message(self):
        """Get the current error/warning/info value, if any."""
        if self._error_mappings:
            highest = sorted(self._error_mappings.keys())[0]

            self.icon.setPixmap(self.error_pixmap)
            return self._error_mappings[highest]

        elif self._warning_mappings:
            highest = sorted(self._warning_mappings.keys())[0]

            self.icon.setPixmap(self.warning_pixmap)
            return self._warning_mappings[highest]

        elif self._info_mappings:
            highest = sorted(self._info_mappings.keys())[0]

            self.icon.setPixmap(self.info_pixmap)
            return self._info_mappings[highest]

        return ""

    def _update_display(self):
        """Update the display items."""
        error = self._get_message()

        # Ensure everything is shown and the message is correct.
        if error:
            self.display.setText(error)
            self.display.show()
            self.icon.show()

        # Clear existing messages and hide the elements.
        else:
            self.display.clear()
            self.display.hide()
            self.icon.hide()

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def add_error(self, level, msg):
        """Add an error message at a specific level."""
        self._error_mappings[level] = msg
        self._update_display()

    def add_info(self, level, msg):
        """Add a display message at a specific level."""
        self._info_mappings[level] = msg
        self._update_display()

    def add_warning(self, level, msg):
        """Add a warning message at a specific level."""
        self._warning_mappings[level] = msg
        self._update_display()

    def clear(self, level):
        """Clear all notifications for a level."""
        self._clear_error(level)
        self._clear_warning(level)
        self._clear_info(level)


class DefaultedLineEdit(QtWidgets.QLineEdit):

    def __init__(self, default_value="", parent=None):
        super(DefaultedLineEdit, self).__init__(parent=parent)

        self._default_value = default_value
        self.setText(default_value)

        self.textChanged.connect(self._adjust_styling)

        # self.field.setObjectName("DefaultedLineEdit")

        self.setStyleSheet(
            """QLineEdit[nondefault=true] {
                font-weight: bold;
            }"""
        )

    def _adjust_styling(self, value):
        self.setProperty("nondefault", value != self._default_value)

        self.setStyle(self.style())

    def set_and_assume_default(self, default_value):
        self._default_value = default_value

        self.set_value(default_value)

    def set_value(self, value):
        self.setText(value)

    def value(self):
        return self.text()


class StringInputWidget(BaseInputItemWidget):

    value_changed = QtCore.Signal(str)

    def __init__(self, label, default_value=""):
        self.field = DefaultedLineEdit(default_value)

        super(StringInputWidget, self).__init__(self.field, label)

        # self._default_value = default_value
        # self.field.setText(default_value)

        self.field.textChanged.connect(self._emit_value_changed)

    #     self.field.setObjectName("DefaultedLineEdit")
    #
    #     self.field.setStyleSheet(
    #         """QLineEdit#DefaultedLineEdit[nondefault=true] {
    #             font-weight: bold;
    #         }"""
    #     )
    #
    # def _adjust_styling(self, is_default):
    #     self.field.setProperty("nondefault", not is_default)
    #
    #     self.field.setStyle(self.field.style())

    def _emit_value_changed(self, value):
        # self._adjust_styling(value == self._default_value)

        self.value_changed.emit(value)

    def set_and_assume_default(self, default_value):
        self.field.set_and_assume_default(default_value)

        # self.set_value(default_value)

    def set_value(self, text):
        self.field.set_value(text)

    def value(self):
        return self.field.value()
