import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QLineEdit
from PyQt5.QtSerialPort import QSerialPort
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from collections import deque
import sqlite3

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
        
        self.data_sets = deque(maxlen=60)  # Keep the last 60 data points (10 seconds at 6 data points per second)
        self.update_plot()

    def update_data(self, data):
        data_list = [math.log2(int(x.strip())) for x in data.split(',')]
        data_list1= [int(x.strip()) for x in data.split(',')]
        self.plot_data(data_list)
        self.line_recvd.clear()
        self.line_recvd.setText(data)

        state_dict = {
            1: 'Up',
            2: 'Down',
            4: 'Right',
            8: 'Left',
            16: 'Forward',
            32: 'Backward',
            64: 'Clockwise',
            128: 'Counter Clockwise',
            256: 'Wave'
        }
        state = state_dict.get(data_list1[0], 'Unknown')
        
        # Connect to the database
        conn = sqlite3.connect('gesture_data.db')
        cursor = conn.cursor()

        # Check if the table exists, if not, create it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gesture_data'")
        table_exists = cursor.fetchone()
        if not table_exists:
            cursor.execute('''CREATE TABLE gesture_data
                          (data INTEGER, state TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()

        # Insert data and state into the SQLite database
        cursor.execute("INSERT INTO gesture_data (data, state) VALUES (?, ?)", (data_list1[0], state))
        conn.commit()
    
        # Close the connection
        conn.close()

    def plot_data(self, data):
        current_time = datetime.now()
        self.data_sets.append((current_time, data))
        self.update_plot()

    def update_plot(self):
        self.axes.clear()
        
        x_values = []
        y_values = []
        
        if self.data_sets:
            for timestamp, data in self.data_sets:
                x_values.append(timestamp)
                y_values.extend(data)
            
            # Plot all data
            self.axes.plot(x_values, y_values, marker='o')
            
            # Set ylabel, title, and yticks
            self.axes.set_ylabel('Y Value')
            self.axes.set_title('Input Plot')
            y_ticks = np.arange(0, 9, 1)
            self.axes.set_yticks(y_ticks)
            y_tick_labels = [str(int(2**y)) for y in y_ticks]
            self.axes.set_yticklabels(y_tick_labels)
            
            # Format x-axis to display only time
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            
            # Set x-axis limits to show the last 10 seconds of data
            current_time = datetime.now()
            min_time = current_time - timedelta(seconds=10)
            max_time = current_time
            self.axes.set_xlim(min_time, max_time)
        
        else:
            # If no data is received, plot a single point at (0, 0)
            self.axes.plot(0, 0, marker='o')
        
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())