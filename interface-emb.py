import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QLineEdit
from PyQt5.QtSerialPort import QSerialPort
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

class SerialThread(QtCore.QThread):
    data_received = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        serial = QSerialPort()
        serial.setPortName('COM3')
        if serial.open(QtCore.QIODevice.ReadWrite):
            print('Port opened')
            serial.setBaudRate(115200)
            serial.setStopBits(QSerialPort.OneStop)
            serial.setParity(QSerialPort.NoParity)
            serial.setDataBits(QSerialPort.Data8)
            serial.setFlowControl(QSerialPort.NoFlowControl)
            
            while True:
                if serial.waitForReadyRead(100):
                    data = serial.readAll().data().decode('utf-8')
                    self.data_received.emit(data)

class NavigationToolbar(NavigationToolbar2QT):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setMinimumSize(800, 500)
        self.setWindowTitle("Gesture")
        
        widget = QWidget()
        self.label_recvd = QLabel('Message Reçu :')
        self.line_recvd = QLineEdit()
        
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        
        layout.addWidget(self.canvas)
        layout.addStretch()
        layout.addWidget(self.label_recvd)
        layout.addWidget(self.line_recvd)
        
        # Add NavigationToolbar
        self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(self.canvas, self))
        
        self.serial_thread = SerialThread()
        self.serial_thread.data_received.connect(self.update_data)
        self.serial_thread.start()
        
        self.data_sets = []
        self.update_plot()

    def update_data(self, data):
        data_list = [math.log2(int(x.strip())) for x in data.split(',')]
        self.plot_data(data_list)
        self.line_recvd.clear()
        self.line_recvd.setText(data)

    def plot_data(self, data):
        current_time = datetime.now()
        self.data_sets.append((current_time, data))
        self.update_plot()

    def update_plot(self):
        self.axes.clear()
        
        if self.data_sets:
            # Get distinct times and corresponding data values
            times = [x[0] for x in self.data_sets]
            unique_times = np.unique(times)
            
            # Resample data to get 5 distinct times
            if len(unique_times) > 5:
                resampled_times = np.linspace(min(unique_times), max(unique_times), 5)
            else:
                resampled_times = unique_times
            
            # Get corresponding data for the resampled times
            resampled_data = [next((data for (time, data) in self.data_sets if time == t), [0]) for t in resampled_times]
            
            for i, (x_values, data) in enumerate(zip(resampled_times, resampled_data)):
                self.axes.plot([x_values] * len(data), data, marker='o')
            
            self.axes.set_ylabel('Y Value')
            self.axes.set_title('Input Plot')
            
            y_ticks = np.arange(0, 9, 1)
            self.axes.set_yticks(y_ticks)
            y_tick_labels = [str(int(2**y)) for y in y_ticks]
            self.axes.set_yticklabels(y_tick_labels)
            
            # Format x-axis to display only time
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            
            # Set x-axis limits based on the range of time data
            min_time = min(resampled_times)
            max_time = max(resampled_times)
            self.axes.set_xlim(min_time, max_time)
            
            # Set only 5 ticks on the x-axis
            self.axes.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))
        
        else:
            # If no data is received, append a data point with a value of 0
            self.data_sets.append((datetime.now(), [0]))
    
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
