import pprint
import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader
from pyqtgraph.Qt import QtCore
from data_io import DataWriter


class SignalReader(QtCore.QThread):
    """
    Thread for capturing input signal through DAQ

    TODO: Add reset device.
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
        # actual data received from the DAQ
        self.input = np.empty(shape=(len(channels), self.sample_size))


    def run(self):
        """ Start thread for data acuisition. Called by QThread.start() """

        self.writer = DataWriter()

        self.is_running = True
        self.create_task()

        while self.is_running:
            if not self.is_paused:
                try:
                    # TODO: total_sampl_per_chan_acquired should be class property?
                    print(f"Total data acquired: {self.task.in_stream.total_samp_per_chan_acquired}")

                    # Read data acquiered
                    self.reader.read_many_sample(data=self.input,
                                number_of_samples_per_channel=self.sample_size)
                    # Emit signal with the data
                    self.incoming_data.emit(self.input)
                    # Write data to file
                    try:
                        self.writer.write_data(self.input)
                    except ValueError:
                        # TODO: if the file is closed elsewhere before....
                        print("WARMING: Block of data could not be writen to file")
                    # Print data to screen
                    pprint.pprint(self.input.T)
                except Exception as e:
                    print("Error with read_many_sample")
                    print(e)
                    # Finish data writer
                    self.writer.close_file()
                    break
        # Stops acquisition
        self.task.close()
        # Finish data writer
        self.writer.close_file()
        # Returns run and the thread is closed
        return None

    def create_task(self):
        print("reader input channels:", self.input_channels)
        try:
            self.task = nidaqmx.Task("Reader Task")
        except OSError:
            print("DAQ is not connected, task could not be created")
            return

        try:
            chan_args = {
                          "min_val": -10,
                          "max_val": 10,
                          "terminal_config": nidaqmx.constants.TerminalConfiguration.RSE
                         }
            for ch in self.input_channels:
                channel_name = self.daq_in_name + "/ai" + str(ch)
                self.task.ai_channels.add_ai_voltage_chan(channel_name,
                                                          **chan_args)
                print(channel_name)
        except Exception as e:
            print("DAQ is not connected, channel could not be added")
            print(e)
            return

        # Timing definition
        self.task.timing.cfg_samp_clk_timing(
            rate=self.sample_rate, sample_mode=AcquisitionType.CONTINUOUS
        )
        self.task.start()
        # Start acquisition
        self.reader = AnalogMultiChannelReader(self.task.in_stream)

    def restart(self):
        print("Restarting the task")
        # Closing
        self.is_paused = True
        self.task.stop()
        self.task.close()
        self.writer.close_file()
        # Starting
        self.writer = DataWriter()
        self.create_task()
        self.is_paused = False


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
