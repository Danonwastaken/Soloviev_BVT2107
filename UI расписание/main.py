from datetime import datetime, date, time
from PyQt5.QtCore import qInfo
import psycopg2
import sys
from PyQt5.QtWidgets import (QApplication, QCheckBox, QInputDialog, QLineEdit, QSpinBox, QWidget,
                             QTabWidget, QAbstractScrollArea,
                             QVBoxLayout, QHBoxLayout,
                             QTableWidget, QGroupBox,
                             QTableWidgetItem, QPushButton, QMessageBox, QMainWindow)


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.datetime()
        self._connect_to_db()
        self.setWindowTitle("Schedule")

        self.vbox = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self._create_schedule_tab()

    def datetime(self):
        self.row_max = 5
        self.day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        start = date(2021, 9, 1)
        d = datetime.now()
        self.week = d.isocalendar()[1] - start.isocalendar()[1] + 1
        if self.week % 2 == 1:
            self.top_week = 'odd'
        else:
            self.top_week = 'even'

    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="teleschedule",
                                     user="postgres",
                                     password="XdanMST",
                                     host="localhost",
                                     port="5432")

        self.cursor = self.conn.cursor()

    def _create_schedule_tab(self):

        self.schedule_tab = QWidget()
        self.tabs.addTab(self.schedule_tab, "Schedule")


        self.dof = int(input("Выберите день недели: 1 - Понедельник; 2 - Вторник; 3 - Среда; 4- Четверг; 5 - Пятница; 6 - Суббота\n"))
        if self.dof == 1:
            self.day_of_week = 'monday'
        if self.dof == 2:
            self.day_of_week = 'tuesday'
        if self.dof == 3:
            self.day_of_week = 'wednesday'
        if self.dof == 4:
            self.day_of_week = 'thursday'
        if self.dof == 5:
            self.day_of_week = 'friday'
        if self.dof == 6:
            self.day_of_week = 'saturday'            
        self.day_gbox = QGroupBox(f"{self.day_name[self.dof - 1]}")

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.day_gbox)

        self._create_monday_table()

        self.update_schedule_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_schedule_button)
        self.update_schedule_button.clicked.connect(self._update_day_table)

        self.saveButton = QPushButton("Save all")
        self.shbox2.addWidget(self.saveButton)
        self.saveButton.clicked.connect(lambda: self._change_day_from_table(self.row_max))
        self.saveButton.clicked.connect(self._update_day_table)

        self.schedule_tab.setLayout(self.svbox)

    def _create_monday_table(self):
        self.monday_table = QTableWidget()
        self.monday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.monday_table.setColumnCount(5)
        self.monday_table.setHorizontalHeaderLabels(["Start time", "Subject", "Migalka", "Room", "Delete"])

        self._update_day_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.monday_table)
        self.day_gbox.setLayout(self.mvbox)

    def _update_day_table(self):
        self.records = []
        self._connect_to_db()
        self.cursor.execute(f"Select * from service.timetable where service.timetable.day='{self.day_of_week}' and migalka in ('{self.top_week}', 'always')")
        self.records = list(self.cursor.fetchall())
        self.cursor.execute(f"select * from service.subject")
        recors_subj = list(self.cursor.fetchall())
        self.names = {rname:rpublicname for (rname,rpublicname) in recors_subj}
        self.publicnames = {rpublicname:rname for (rname,rpublicname) in recors_subj}
        #print(self.names)
        self.monday_table.setRowCount(self.row_max)
        for i, r in enumerate(self.records):
           # print(r)
            r = list(r)
            drop_button1 = QPushButton("Delete")
            drop_button2 = QPushButton("Delete")
            drop_button3 = QPushButton("Delete")
            drop_button4 = QPushButton("Delete")
            drop_button5 = QPushButton("Delete")
            self.monday_table.setItem(i, 0, QTableWidgetItem(str(r[4])))  # Time
            self.monday_table.setItem(i, 1, QTableWidgetItem(self.names[r[2]] if (self.names[r[2]] != None ) else r[2]))  # Subject
            self.monday_table.setItem(i, 2, QTableWidgetItem(str(r[5])))  # Migalka
            self.monday_table.setItem(i, 3, QTableWidgetItem(str(r[3])))  # Room
            self.monday_table.setCellWidget(0, 4, drop_button1)
            self.monday_table.setCellWidget(1, 4, drop_button2)
            self.monday_table.setCellWidget(2, 4, drop_button3)
            self.monday_table.setCellWidget(3, 4, drop_button4)
            self.monday_table.setCellWidget(4, 4, drop_button5)
            drop_button1.clicked.connect(lambda: self._delete_row(0))
            drop_button2.clicked.connect(lambda: self._delete_row(1))
            drop_button3.clicked.connect(lambda: self._delete_row(2))
            drop_button4.clicked.connect(lambda: self._delete_row(3))
            drop_button5.clicked.connect(lambda: self._delete_row(4))
        self.monday_table.resizeRowsToContents()

        for j in range(len(self.records), self.row_max):
            self.monday_table.setItem(j, 0, QTableWidgetItem(None))  # Time
            self.monday_table.setItem(j, 1, QTableWidgetItem(None))  # Subject
            self.monday_table.setItem(j, 2, QTableWidgetItem(None))  # Migalka
            self.monday_table.setItem(j, 3, QTableWidgetItem(None))  # Room

    def _delete_row(self, rowNum):
        #try:
            #print(self.records[rowNum])
        #except:
         #   return
        try:
            self.cursor.execute(f"DELETE FROM service.timetable WHERE id = {self.records[rowNum][0]};")
            self.conn.commit()

        except:
            QMessageBox.about(self, "Error", f"Can't delete row = {rowNum + 1}")
        self._update_day_table()

    def _change_day_from_table(self, rowNum):      
        for j in range(len(self.records)):
            row = list()
            for i in range(self.monday_table.columnCount()):
                try:
                    row.append(self.monday_table.item(j, i).text())
                except:
                    row.append(None)
            #try:

            self.cursor.execute(f"UPDATE service.timetable SET start_time = '{row[0]}' WHERE id = {self.records[j][0]}")
            self.cursor.execute(f"UPDATE service.subject SET public_name = '{row[1]}' WHERE name = '{self.records[j][2]}'")

            self.cursor.execute(f"UPDATE service.timetable SET room_numb = '{row[3]}' WHERE id = {self.records[j][0]}")

            self.conn.commit() 
            #except:
                #QMessageBox.about(self, "Error", "SQL UPDATE error") 

        # Insert row
        for j in range(len(self.records), self.row_max):
            row = list()
            for i in range(self.monday_table.columnCount() - 1):
                try:
                    row.append(self.monday_table.item(j, i).text())
                except:
                    row.append(None)

            #try:

            if any([(e == '' or e == ' ') for e in row]):
                continue
           
           # print(row)
           # print('row') #['12:00', 'qwe', 'ewq', '1']
            if not(row[1] in self.names):
                self.cursor.execute(f"insert into service.subject (name,public_name) values ('{row[1]}','{row[1]}')")
            self.cursor.execute(f"insert into service.timetable (start_time,day,subject,migalka,room_numb) values ('{row[0]}','{self.day_of_week}','{row[1]}','{row[2]}',{row[3]})")
            self.conn.commit()
            #self.cursor.execute("SELECT id FROM service.subject ORDER BY id DESC LIMIT 1;")
            #self.last_id_sub = self.cursor.fetchall()[0][0] + 1
            #self.cursor.execute(f"INSERT INTO service.subject(name) VALUES ({self.last_id_sub}, '{row[1]}');")
            #self.cursor.execute("SELECT id FROM service.timetable ORDER BY id DESC LIMIT 1;")
            #self.last_id_tb = self.cursor.fetchall()[0][0] + 1
            #self.cursor.execute("SELECT id FROM service.teacher ORDER BY id DESC LIMIT 1;")
            #self.last_id_teach = self.cursor.fetchall()[0][0] + 1
            #self.cursor.execute(
            #    f"INSERT INTO service.teacher (id, full_name, subject) VALUES ({self.last_id_teach}, '{row[2]}', {self.last_id_sub});")
            #self.cursor.execute(f"INSERT INTO service.timetable (day, room_numb, start_time, subject,migalka)\
            #                        VALUES ({self.day_of_week}, '{row[3]}', '{row[0]}','{row[1]}' {'odd' if self.top_week else 'even'})")
            #self.conn.commit()
            #except:
                #p

app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())