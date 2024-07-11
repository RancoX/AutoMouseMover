import pyautogui as pg
from datetime import datetime
from time import sleep
from random import randint,random
from screeninfo import get_monitors
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QSpinBox, QVBoxLayout, QHBoxLayout, QWidget, QComboBox, QMessageBox, QDateEdit
from PySide6.QtCore import Qt, QRunnable, QThreadPool, QDate
from PySide6.QtGui import QAction
import sys


# =================================== params ===================================
pg.FAILSAFE=False
# stop time
stop_hr=17
stop_min=0
# Iterate through each monitor and print its width and height
max_x=0
min_y=100_000
# get date
now=datetime.now()
# press key
keys=["ctrl","shift","alt","space","tab","enter","esc","capslock","up","down","left","right","add","subtract","divide","multiply"]


# =================================== GUI ===================================
class ZeroPaddedSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()

    def textFromValue(self, value):
        # Customize the display format to add a leading zero if value < 10
        return f'{value:02}'

# =================================== QThreadpool Worker ===================================
class Mover(QRunnable):
    def __init__(self,stop_date,stop_hr,stop_min,max_x,min_y,flag,now,key,QtObj):
        super().__init__()
        self.stop_date=stop_date
        self.stop_hr=stop_hr
        self.stop_min=stop_min
        self.max_x=max_x
        self.min_y=min_y
        self.flag=flag
        self.now=now
        self.key=key
        self.QtObj=QtObj

    def run(self):
        self.QtObj.stop_btn.setEnabled(True)
        self.auto_cursor()

    # =================================== main function ===================================
    def auto_cursor(self):
        print(f'Beeeeeep...zzZZzzZZZzzz...It\'s {self.now.strftime(r"%A, %Y-%m-%d %H:%M:%S")}\nI\'m your pc scout, automobility initiated until {self.stop_date} {self.stop_hr}:{self.stop_min:02}:00')
        # Get a list of all connected monitors
        monitors = get_monitors()

        for monitor in monitors:
            # print(f"Monitor <{monitor.name}>: Width: {monitor.width} pixels, Height: {monitor.height} pixels")
            self.max_x+=monitor.width
            self.min_y=min(self.min_y,monitor.height)


        while self.flag:
            # generate the next x,y, moving time, sleep time
            x=randint(0,self.max_x-1)
            y=randint(0,self.min_y-1)
            duration=round(2*random(),2)
            sleeping_time=randint(2,180)

            print(f"Now moving cursor to <{x},{y}> and then will sleep for {sleeping_time}s")
            # move cursor
            pg.moveTo(x,y,duration=duration)
            if sleeping_time>60:
                pg.press(self.key)
                print(f"Key <{self.key}> has been pressed!")

            # hold off
            sleep(sleeping_time)

            # check if time's up
            nowTime=datetime.now()
            now_date,now_hr, now_min = nowTime.date(), nowTime.hour, nowTime.minute
            if now_date > self.stop_date:
                # passed user defined stop date, stop
                self.flag=False
                print(f"It's already {now_date},relaxxxxxxx......")
            else:
                # stop date not yet reached
                if now_hr > self.stop_hr:
                    self.flag=False
                    print(f"It's {self.stop_hr}:{self.stop_min:02}:00! No one's watching anymore...")
                if now_hr == self.stop_hr:
                    if now_min >= self.stop_min:
                        self.flag=False
                        print(f"It's {self.stop_hr}:{self.stop_min:02}:00! No one's watching anymore...")
        
        # enable run button again
        self.QtObj.run_btn.setEnabled(True)
        self.QtObj.stop_btn.setEnabled(False)

    
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Auto mouse mover 2.0')
        self.setFixedSize(400,200)

        layout=QVBoxLayout()

        about_menu=self.menuBar().addMenu('&About')
        author_info = QAction('Author',self)
        author_info.triggered.connect(self.show_about)
        about_menu.addAction(author_info)

        # DateEdit set up
        date_label=QLabel('End date:')
        font=date_label.font()
        font.setBold(True)
        font.setPointSize(13)
        date_label.setFont(font)

        self.date = QDateEdit()
        self.date.setDate(QDate.currentDate())
        self.date.setFixedWidth(150)

        date_row=QHBoxLayout()
        date_row.setSpacing(10)
        date_row.addWidget(date_label)
        date_row.addWidget(self.date,alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # end_time set up
        end_time_label=QLabel('End time:')
        font=end_time_label.font()
        font.setBold(True)
        font.setPointSize(13)
        end_time_label.setFont(font)

        self.end_time_hr=QSpinBox()
        self.end_time_hr.setFixedWidth(70)
        self.end_time_hr.setValue(stop_hr)
        self.end_time_hr.setRange(0,23)
        self.end_time_hr.setSingleStep(1)

        end_time_colon=QLabel(' : ')
        font=end_time_colon.font()
        font.setBold(True)
        font.setPointSize(13)
        end_time_colon.setFont(font)
        end_time_colon.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.end_time_min=ZeroPaddedSpinBox()
        self.end_time_min.setFixedWidth(70)
        self.end_time_min.setRange(0,59)
        self.end_time_min.setSingleStep(1)
        self.end_time_min.setValue(stop_min)

        end_time_row=QHBoxLayout()
        end_time_row.setSpacing(10)
        end_time_row.addWidget(end_time_label)
        end_time_row.addWidget(self.end_time_hr,alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        end_time_row.addWidget(end_time_colon)
        end_time_row.addWidget(self.end_time_min,alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        end_time_row.addStretch()

        # keypress set up
        # key to press
        key_lable=QLabel('Key to press:')
        font=key_lable.font()
        font.setBold(True)
        font.setPointSize(13)
        key_lable.setFont(font)

        self.key_combo=QComboBox()
        for key in keys:
            self.key_combo.addItem(key.upper())
        self.key_combo.setCurrentIndex(0)

        key_row=QHBoxLayout()
        key_row.setSpacing(10)
        key_row.addWidget(key_lable)
        key_row.addWidget(self.key_combo,alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        key_row.addStretch()

        # functional buttons
        self.run_btn=QPushButton('Run')
        self.run_btn.clicked.connect(self.run_worker)

        self.stop_btn=QPushButton('Stop')
        self.stop_btn.clicked.connect(self.stop)
        self.stop_btn.setEnabled(False)

        btn_layout=QHBoxLayout()
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.stop_btn)

        container=QWidget()
        layout.addLayout(date_row)
        layout.addLayout(end_time_row)
        layout.addLayout(key_row)
        layout.addLayout(btn_layout)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.threadpool=QThreadPool()
        print(f"Multi-threading initiated with maximum {self.threadpool.maxThreadCount()} threads")


    def run_worker(self,s):
        flag=True
        key=self.key_combo.currentText()
        stop_date=self.date.date().toPython() # convert selected date to datetime.date object
        stop_hr, stop_min = self.end_time_hr.value(), self.end_time_min.value()
        self.worker=Mover(stop_date,stop_hr,stop_min,max_x,min_y,flag,now,key,self)
        self.threadpool.start(self.worker)
        self.run_btn.setEnabled(False)
    
    def stop(self,s):
        self.worker.flag=False
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        print('Automover was termianted manually. Time for some real work!')

    def show_about(self):
        QMessageBox.information(self,'About Auto Mouse Mover','Auto Mouse Mover was a tool developed by Ranco Xu in Sep 2023 from down under!'
                                '\nAnyone who possesses a copy of this software is free to use, modify and redistribute it without obtaining my permission.\nHope you enjoy your WFH time:)'
                                'Update 2.0 Added stop date to allow cross day operation')


app=QApplication(sys.argv)
win=MyMainWindow()
win.show()
app.exec()

# pyinstaller --noconsole "C:\Users\RancoXu\ArgyleLaptop\Ranco\Python\AMM\auto_mover_multiDays.py" --icon="C:\Users\RancoXu\ArgyleLaptop\Ranco\Python\AMM\icon.png" --paths "C:\Users\RancoXu\ArgyleLaptop\Ranco\Python\AMM\venv_automover\Lib\site-packages" --paths "C:\Users\RancoXu\ArgyleLaptop\Ranco\Python\AMM"