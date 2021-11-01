import pprint

from pyqtgraph.Qt import QtCore
from pyqtgraph.parametertree import *
from PyQt5.QtCore import QSettings

from config import *


class ParamTreeBase(ParameterTree):
    # ParamTree will output a signal that has the param and the output
    # TODO: not implemented yet
    paramChange = QtCore.pyqtSignal(object, object)

    def __init__(self, name, params):
        super().__init__()

        self.name = name
        self.settings = QSettings("DAQ_Control", self.name)

        self.params = Parameter.create(name=self.name, type="group", children=params)

        # load saved data when available or otherwise specified in config.py
        if self.settings.value("State") != None and not RESET_DEFAULT_PARAMS:
            self.state = self.settings.value("State")
            self.params.restoreState(self.state)
        else:
            print("Loading default params for", self.name)

        self.setParameters(self.params, showTop=False)
        # When the params change, send to method to emit.
        self.params.sigTreeStateChanged.connect(self.send_change)

    def send_change(self, param, changes):
        self.paramChange.emit(param, changes)

    # Convienience methods for modifying parameter values.
    def get_param_value(self, *childs):
        """Get the current value of a parameter."""
        return self.params.param(*childs).value()

    def set_param_value(self, value, *childs):
        """Set the current value of a parameter."""
        return self.params.param(*childs).setValue(value)


    def save_settings(self):
        self.state = self.params.saveState()
        self.settings.setValue("State", self.state)

    def print(self):
        print(self.name)
        print(self.params)


class ConfigParamTree(ParamTreeBase):
    """
    Data container for parameters controlling settings saved in configurations
    tab
    """
    def __init__(self):
        self.setting_params = [
            {
                "name": "Reader Config",
                "type": "group",
                "children": [
                    {
                        "name": "Device Name",
                        "type": "str",
                        "value": "Dev1",
                    },
                    {
                        "name": "Sample Rate",
                        "type": "int",
                        "value": 1000,
                        "limits": (1, 10000),
                    },
                    {
                        "name": "Sample Size",
                        "type": "int",
                        "value": 1000,
                        "limits": (1, 10000),
                    },
                ],
            },
        ]
        # Reader Config
        # TODO: ai are defined from 0 (could be added to config.py)
        for i, ch in enumerate(CHANNEL_NAMES_IN):

            self.setting_params[0]["children"].append(
                {
                    "name": ch + " Input Channel",
                    "type": "int",
                    "value": i,
                }
            )

        super().__init__(name="Config Param", params=self.setting_params)


    def get_read_channels(self):
        channels = [
            self.get_param_value("Reader Config", ch + " Input Channel")
            for ch in CHANNEL_NAMES_IN
        ]
        return channels


if __name__ == "__main__":
    print("\nRunning demo for ParameterTree\n")
    # param_tree = ChannelParameters()
    # param_tree.print()
