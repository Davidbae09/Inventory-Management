import sys
import sqlite3
import csv
from PyQt5 import QtWidgets

# Database Setup
def initialize_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL
        )
    ''')
    conn.commit()
    conn.close()

# Database Interaction Functions
def add_item(item_name, quantity, price):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO inventory (item_name, quantity, price) VALUES (?, ?, ?)',
                   (item_name, quantity, price))
    conn.commit()
    conn.close()

def update_item(item_id, item_name, quantity, price):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE inventory
        SET item_name = ?, quantity = ?, price = ?
        WHERE item_id = ?
    ''', (item_name, quantity, price, item_id))
    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM inventory WHERE item_id = ?', (item_id,))
    conn.commit()
    conn.close()

def get_items():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inventory')
    items = cursor.fetchall()
    conn.close()
    return items

def generate_report():
    items = get_items()
    with open('inventory_report.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name', 'Quantity', 'Price'])
        writer.writerows(items)

# GUI Application
class InventoryApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set up layout
        layout = QtWidgets.QVBoxLayout()
        
        # Inventory Table
        self.inventory_table = QtWidgets.QTableWidget()
        self.inventory_table.setColumnCount(4)
        self.inventory_table.setHorizontalHeaderLabels(['ID', 'Name', 'Quantity', 'Price'])
        self.inventory_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.inventory_table.cellClicked.connect(self.select_item)
        layout.addWidget(self.inventory_table)
        
        # Add Item Form
        form_layout = QtWidgets.QFormLayout()
        self.item_name = QtWidgets.QLineEdit()
        self.quantity = QtWidgets.QSpinBox()
        self.price = QtWidgets.QDoubleSpinBox()
        self.price.setDecimals(2) 
        self.price.setRange(0, 999999.9999)  # Adjust as needed
        
        form_layout.addRow('Item Name:', self.item_name)
        form_layout.addRow('Quantity:', self.quantity)
        form_layout.addRow('Price:', self.price)
        
        layout.addLayout(form_layout)
        
        # Buttons
        self.add_button = QtWidgets.QPushButton('Add Item')
        self.update_button = QtWidgets.QPushButton('Update Item')
        self.delete_button = QtWidgets.QPushButton('Delete Item')
        self.report_button = QtWidgets.QPushButton('Generate Report')
        
        self.add_button.clicked.connect(self.add_item)
        self.update_button.clicked.connect(self.update_item)
        self.delete_button.clicked.connect(self.delete_item)
        self.report_button.clicked.connect(generate_report)
        
        layout.addWidget(self.add_button)
        layout.addWidget(self.update_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.report_button)
        
        self.setLayout(layout)
        self.setWindowTitle('Inventory Management System')
        
        # Load Data
        self.load_inventory_table()

    def load_inventory_table(self):
        # Clear the table
        self.inventory_table.setRowCount(0)
        
        # Fetch data from the database and populate table
        items = get_items()
        for row_num, row_data in enumerate(items):
            self.inventory_table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.inventory_table.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(data)))

    def add_item(self):
        item_name = self.item_name.text()
        quantity = self.quantity.value()
        price = self.price.value()
        
        add_item(item_name, quantity, price)
        self.load_inventory_table()
        self.clear_form()

    def update_item(self):
        if not hasattr(self, 'selected_item_id'):
            return
        item_name = self.item_name.text()
        quantity = self.quantity.value()
        price = self.price.value()
        
        update_item(self.selected_item_id, item_name, quantity, price)
        self.load_inventory_table()
        self.clear_form()

    def delete_item(self):
        if not hasattr(self, 'selected_item_id'):
            return
        
        delete_item(self.selected_item_id)
        self.load_inventory_table()
        self.clear_form()

    def select_item(self, row, column):
        item_id = int(self.inventory_table.item(row, 0).text())
        self.selected_item_id = item_id
        self.item_name.setText(self.inventory_table.item(row, 1).text())
        self.quantity.setValue(int(self.inventory_table.item(row, 2).text()))
        self.price.setValue(float(self.inventory_table.item(row, 3).text()))

    def clear_form(self):
        self.item_name.clear()
        self.quantity.setValue(0)
        self.price.setValue(0.0)
        if hasattr(self, 'selected_item_id'):
            del self.selected_item_id

# Initialize Database and Run Application
if __name__ == '__main__':
    initialize_db()
    app = QtWidgets.QApplication(sys.argv)
    inventory_app = InventoryApp()
    inventory_app.show()
    sys.exit(app.exec_())
