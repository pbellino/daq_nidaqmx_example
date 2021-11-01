#!/usr/bin/env python3
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
# --- From DAQ Control --- #
from config import DEBUG_MODE
from parameters import ConfigParamTree
from plotter import SignalPlot, Legend
if DEBUG_MODE:
    from reader_debug import SignalReader
else:
    from reader import SignalReader


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__()

        # initialize parameters database
        self.setting_param_tree = ConfigParamTree()

        self.init_ui()
        self.init_daq_io()

        self.read_thread.incoming_data.connect(self.plotter.update_plot)
        self.read_thread.incoming_data.connect(self.legend.on_new_data)

        # Connect the output signal from changes in the param tree to change
        self.start_signal_btn.clicked.connect(self.start_signal_btn_click)
        self.save_settings_btn.clicked.connect(self.commit_settings_btn_click)
        # The signal paramChange is not implemented yet
        self.setting_param_tree.paramChange.connect(self.settings_param_change)


    def init_ui(self):
        """ Define and initialize GUI """
        self.resize(700, 800)  # non maximized size
        # self.setWindowState(QtCore.Qt.WindowMinimized)
        # self.setMinimumSize(QSize(500, 400))
        self.setWindowTitle("DAQ Interface")

        self.mainbox = QWidget(self)
        self.setCentralWidget(self.mainbox)
        layout = QVBoxLayout()
        self.mainbox.setLayout(layout)
        title = QLabel("DAQ Controller")
        title.setAlignment(Qt.AlignHCenter)
        self.legend = Legend(self.setting_param_tree.get_read_channels())

        # TODO: update legend frequency on startup with param tree values
        #   use signals instead of passing in legend might be better
        self.plotter = SignalPlot(self.legend)
        # self.plotter.setMaximumSize(800, 360)

        self.start_signal_btn = QPushButton("Press to start signal out")

        # Definition of the tab "DAQ Settings"
        self.settings_tab = QWidget(self)
        self.settings_tab.layout = QVBoxLayout(self)
        self.save_settings_btn = QPushButton("Commit Settings")
        self.settings_tab.layout.addWidget(self.setting_param_tree)
        self.settings_tab.layout.addWidget(self.save_settings_btn)
        self.settings_tab.setLayout(self.settings_tab.layout)

        # Definition of the tab widget
        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.settings_tab, "DAQ Settings")
        self.current_tab = 0
        self.tabs.setCurrentIndex(self.current_tab)

        # place widgets in their respective locations
        layout.addWidget(title)  # row, col, rowspan, colspan
        layout.addWidget(self.plotter)
        layout.addWidget(self.legend)
        layout.addWidget(self.start_signal_btn)
        layout.addWidget(self.tabs)

        self.save_settings_btn.setEnabled(False)

    def init_daq_io(self):
        # initiate read threads for analog input
        self.read_thread = SignalReader(
            sample_rate=self.setting_param_tree.get_param_value(
                "Reader Config", "Sample Rate"
            ),
            sample_size=self.setting_param_tree.get_param_value(
                "Reader Config", "Sample Size"
            ),
            channels=self.setting_param_tree.get_read_channels(),
            dev_name=self.setting_param_tree.get_param_value(
                "Reader Config", "Device Name"
            ),
        )


    @pyqtSlot()
    def start_signal_btn_click(self):
        """ Start and Stop the data acquisition """
        if self.read_thread.is_running:
            print("Stopped DAQ acquisition")
            self.read_thread.is_running = False
            self.save_settings_btn.setEnabled(False)
            self.read_thread.wait()

            self.setting_param_tree.save_settings()
            self.start_signal_btn.setText("Press to start acquisition")
        else:
            print("Started DAQ acquisition")
            self.read_thread.start()
            self.start_signal_btn.setText("Press to stop acquisition")
            self.save_settings_btn.setEnabled(True)


    @pyqtSlot()
    def commit_settings_btn_click(self):
        """ Apply changes to inputs parameters during acquisition"""
        print("Commit settings btn pressed")

        reader_sample_rate = self.setting_param_tree.get_param_value(
            "Reader Config", "Sample Rate"
        )
        reader_sample_size = self.setting_param_tree.get_param_value(
            "Reader Config", "Sample Size"
        )
        # update read channel names
        self.legend.update_channels(
                        self.setting_param_tree.get_read_channels())

        # change the task parameters
        self.read_thread.input_channels = (
            self.setting_param_tree.get_read_channels()
        )
        self.read_thread.sample_rate = reader_sample_rate
        self.read_thread.sample_size = reader_sample_size

        self.read_thread.restart()

    @pyqtSlot()
    def settings_param_change(self, parameter, changes):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
