import pprint
import numpy as np
import time
from pyqtgraph.Qt import QtCore
from data_io import DataWriter


class SignalReader(QtCore.QThread):
    """
    Thread for simulating a signal

    """

    # Signal with read data
    incoming_data = QtCore.pyqtSignal(object)

    def __init__(self, sample_rate, sample_size, channels, dev_name):
        super().__init__()

        self.reader = None
        self.is_running = False
        self.is_paused = False
        self.input_channels = channels
        self.daq_in_name = dev_name

        self.sample_rate = sample_rate
        self.sample_size = sample_size


    def run(self):
        """ Start thread for data simulation. Called by QThread.start() """

        self.writer = DataWriter()

        self.is_running = True
        while self.is_running:
            if not self.is_paused:
                # Simulate data
                self.input = np.random.normal(0, 0.1,
                        size=(len(self.input_channels), self.sample_size)
                        )
                # Add different offset for each cchannel
                for i, _ in enumerate(self.input):
                    self.input[i, :] += i

                # Emit signal with the data
                self.incoming_data.emit(self.input)
                # Write data to file
                self.writer.write_data(self.input)
                # Print data to screen
                pprint.pprint(self.input.T)
                # Wait the time it would have taken to acquiere the real signal
                _time_acq = self.sample_size / self.sample_rate
                time.sleep(_time_acq)
        # Finish data writer
        self.writer.close_file()
        # Returns run and the thread is closed
        return None


    def restart(self):
        print("Restarting the task")
        self.is_paused = True
        self.writer.close_file()
        self.is_paused = False
        self.writer = DataWriter()

if __name__ == "__main__":
    print("\nRunning demo for SignalReader\n")

    reader_thread = SignalReader(sample_rate=1000,
                                 sample_size=1000,
                                 channels=[0, 1, 2],
                                 dev_name='Dev1',
                                 )
    reader_thread.start()
    input("Press return to stop")
    reader_thread.is_running = False
    # Wait for the thread to finish (see QThread class)
    reader_thread.wait()
    print("\nTask done")
