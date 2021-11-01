# Data Aquisition using NI-DAQmx python API

Based on this [project](https://github.com/toastytato/DAQ_Interface)


It is a minimal working example for data acquisition using the [NI-DAQmx python API](https://nidaqmx-python.readthedocs.io/en/latest/index.html).

It works only in Windows systems.

Using ```DEBUG_MODE = True``` in the configuration file allows the use of the GUI without having nidaqmx installed. Data is simulated.

## Content:

* ```daq_interface_main.py```: main script with the GUI definition
 
* ```reader.py```: definitions related to data acquisition
 
* ```plotter.py```: definitions related to visualizing the data
 
* ```parameters.py```: definition of the parameters
 
* ```config.py```: configuration file of the interface
 
* ```misc_functions.py```: keeping apart auxiliary functions

* ```data_io.py```: record acquiered data to file


By defoult the data is writen in ```Output_Data.dat``` (see ```data_io.py```). One column per channel.
