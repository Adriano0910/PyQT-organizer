from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton,
    QWidget, QTableView, QLineEdit, QTextEdit, QDateTimeEdit,
    QDialog, QLabel, QStyledItemDelegate, QHeaderView
)
from PyQt5.QtGui import QBrush, QColor, QPalette, QStandardItem, QStandardItemModel
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtSql import QSqlDatabase
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys

# Inicjalizacja bazy danych SQLAlchemy
engine = create_engine('sqlite:///harmonogram.db', echo=True)
Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    deadline = Column(DateTime)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

db = QSqlDatabase.addDatabase('QSQLITE')
db.setDatabaseName('harmonogram.db')
if not db.open():
    print('Nie można otworzyć bazy danych.')
    sys.exit(1)

#class FirstRowRedDelegate(QStyledItemDelegate):
#    def initStyleOption(self, option, index):
#        super().initStyleOption(option, index)
#        if index.row() == 0:
#            option.backgroundBrush = QBrush(QColor(255, 0, 0))
#            option.palette.setColor(QPalette.Text, Qt.white)

class ScheduleApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('organizer 2888')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.init_ui()

    def init_ui(self):
        self.button_add_task = QPushButton('Dodaj zadanie')
        self.button_add_task.setStyleSheet("font-family: Impact; font-size: 14px; color: white; background-color: green;")
        self.button_add_task.clicked.connect(self.add_task)
        self.layout.addWidget(self.button_add_task)

        self.button_edit_task = QPushButton('Edytuj zadanie')
        self.button_edit_task.setStyleSheet("font-family: Impact; font-size: 14px; color: white; background-color: blue;")
        self.button_edit_task.clicked.connect(self.edit_task)
        self.layout.addWidget(self.button_edit_task)

        self.button_delete_task = QPushButton('Usuń zadanie')
        self.button_delete_task.setStyleSheet("font-family: Impact; font-size: 14px; color: white; background-color: red;")
        self.button_delete_task.clicked.connect(self.delete_task)
        self.layout.addWidget(self.button_delete_task)

        self.task_view = QTableView()
        self.task_model = QStandardItemModel()
        self.task_model.setColumnCount(4)
        self.task_model.setHorizontalHeaderLabels(["ID", "Nazwa", "Opis", "Termin"])

        tasks = session.query(Task).order_by(Task.deadline.asc()).all()

        current_datetime = QDateTime.currentDateTime()

        for task in tasks:
            row = []
            id_item = QStandardItem(str(task.id))
            name_item = QStandardItem(task.name) 
            task_item = QStandardItem(task.description)
            deadline_item = QStandardItem(str(task.deadline))

            row.append(id_item)
            row.append(name_item)
            row.append(task_item)
            row.append(deadline_item)

            # Dodajemy flagę, jeśli termin zadania jest wcześniejszy niż bieżąca data
            if task.deadline < current_datetime.addDays(7):
                id_item.setBackground(QBrush(QColor(255, 255, 0)))
                id_item.setForeground(QBrush(QColor(0, 0, 0)))
                name_item.setBackground(QBrush(QColor(255, 255, 0)))
                name_item.setForeground(QBrush(QColor(0, 0, 0)))
                task_item.setBackground(QBrush(QColor(255, 255, 0)))
                task_item.setForeground(QBrush(QColor(0, 0, 0)))
                deadline_item.setBackground(QBrush(QColor(255, 255, 0)))
                deadline_item.setForeground(QBrush(QColor(0, 0, 0)))

            if task.deadline < current_datetime:
                id_item.setBackground(QBrush(QColor(255, 0, 0)))
                id_item.setForeground(QBrush(QColor(255, 255, 255)))
                name_item.setBackground(QBrush(QColor(255, 0, 0)))
                name_item.setForeground(QBrush(QColor(255, 255, 255)))
                task_item.setBackground(QBrush(QColor(255, 0, 0)))
                task_item.setForeground(QBrush(QColor(255, 255, 255)))
                deadline_item.setBackground(QBrush(QColor(255, 0, 0)))
                deadline_item.setForeground(QBrush(QColor(255, 255, 255)))



            self.task_model.appendRow(row)

        self.task_view.setModel(self.task_model)

        header = self.task_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

       # self.task_view.setItemDelegateForRow(0, FirstRowRedDelegate(self.task_view))

        self.task_view.resizeColumnsToContents()
        self.layout.addWidget(self.task_view)

    def add_task(self):
        dialog = AddTaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_task_view()

    def edit_task(self):
        selected_row = self.task_view.selectionModel().currentIndex()
        if selected_row.isValid():
            task_id = self.task_model.index(selected_row.row(), 0).data()
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                dialog = EditTaskDialog(task, self)
                if dialog.exec_() == QDialog.Accepted:
                    self.refresh_task_view()

    def delete_task(self):
        selected_row = self.task_view.selectionModel().currentIndex()
        if selected_row.isValid():
            task_id = self.task_model.index(selected_row.row(), 0).data()
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                session.delete(task)
                session.commit()
                self.refresh_task_view()

    def refresh_task_view(self):
        self.task_model.clear()
        self.task_model.setColumnCount(4)
        self.task_model.setHorizontalHeaderLabels(["ID", "Nazwa", "Opis", "Termin"])

        tasks = session.query(Task).order_by(Task.deadline.asc()).all()

        current_datetime = QDateTime.currentDateTime()

        for task in tasks:
            row = []
            id_item = QStandardItem(str(task.id))
            name_item = QStandardItem(task.name) 
            task_item = QStandardItem(task.description)
            deadline_item = QStandardItem(str(task.deadline))

            row.append(id_item)
            row.append(name_item)
            row.append(task_item)
            row.append(deadline_item)

            # Dodajemy flagę, jeśli termin zadania jest wcześniejszy niż bieżąca data
            if task.deadline < current_datetime.addDays(7):
                id_item.setBackground(QBrush(QColor(255, 255, 0)))
                id_item.setForeground(QBrush(QColor(0, 0, 0)))
                name_item.setBackground(QBrush(QColor(255, 255, 0)))
                name_item.setForeground(QBrush(QColor(0, 0, 0)))
                task_item.setBackground(QBrush(QColor(255, 255, 0)))
                task_item.setForeground(QBrush(QColor(0, 0, 0)))
                deadline_item.setBackground(QBrush(QColor(255, 255, 0)))
                deadline_item.setForeground(QBrush(QColor(0, 0, 0)))

            
            if task.deadline < current_datetime:
                id_item.setBackground(QBrush(QColor(255, 0, 0)))
                id_item.setForeground(QBrush(QColor(255, 255, 255)))
                name_item.setBackground(QBrush(QColor(255, 0, 0)))
                name_item.setForeground(QBrush(QColor(255, 255, 255)))
                task_item.setBackground(QBrush(QColor(255, 0, 0)))
                task_item.setForeground(QBrush(QColor(255, 255, 255)))
                deadline_item.setBackground(QBrush(QColor(255, 0, 0)))
                deadline_item.setForeground(QBrush(QColor(255, 255, 255)))

            self.task_model.appendRow(row)

        self.task_view.setModel(self.task_model)
        #self.task_view.setItemDelegateForRow(0, FirstRowRedDelegate(self.task_view))
        self.task_view.resizeColumnsToContents()

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Dodaj zadanie')

        layout = QVBoxLayout()

        self.name_label = QLabel('Nazwa:')
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        self.description_label = QLabel('Opis:')
        self.description_input = QTextEdit()
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)

        self.deadline_label = QLabel('Termin:')
        self.deadline_input = QDateTimeEdit()
        self.deadline_input.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        layout.addWidget(self.deadline_label)
        layout.addWidget(self.deadline_input)

        self.save_button = QPushButton('Zapisz')
        self.save_button.setStyleSheet("font-family: Impact; font-size: 14px; color: white; background-color: green;")
        self.save_button.clicked.connect(self.save_task)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_task(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        deadline = self.deadline_input.dateTime().toPyDateTime()
        new_task = Task(name=name, description=description, deadline=deadline)
        session.add(new_task)
        session.commit()

        self.accept()

class EditTaskDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edytuj zadanie')

        layout = QVBoxLayout()

        self.name_label = QLabel('Nazwa:')
        self.name_input = QLineEdit()
        self.name_input.setText(task.name)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        self.description_label = QLabel('Opis:')
        self.description_input = QTextEdit()
        self.description_input.setPlainText(task.description)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)

        self.deadline_label = QLabel('Termin:')
        self.deadline_input = QDateTimeEdit()
        self.deadline_input.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.deadline_input.setDateTime(task.deadline)
        layout.addWidget(self.deadline_label)
        layout.addWidget(self.deadline_input)

        self.save_button = QPushButton('Zapisz')
        self.save_button.setStyleSheet("font-family: Impact; font-size: 14px; color: white; background-color: green;")
        self.save_button.clicked.connect(self.save_task)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.task = task  

    def save_task(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        deadline = self.deadline_input.dateTime().toPyDateTime()

        deadline = deadline.replace(microsecond=0)
        self.task.name = name
        self.task.description = description
        self.task.deadline = deadline

        session.commit()

        self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec_())