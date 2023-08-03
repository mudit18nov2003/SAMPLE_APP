from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from datetime import datetime
import sqlite3
from kivy.lang import Builder


class DataItem(RecycleDataViewBehavior, BoxLayout):
    text = ObjectProperty()


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []

    def add_item(self, item):
        self.data.append({'text': item})
        self.refresh_from_data()


class AddDeleteDataApp(App):

    def build(self):
        layout = BoxLayout(orientation='vertical')

        layout.add_widget(Label(text="Item:"))
        self.entry_item = TextInput()
        layout.add_widget(self.entry_item)

        layout.add_widget(Label(text="Price:"))
        self.entry_price = TextInput()
        layout.add_widget(self.entry_price)

        btn_add_data = Button(text="Add Data")
        btn_add_data.bind(on_press=self.add_data)
        layout.add_widget(btn_add_data)

        btn_delete_data = Button(text="Delete Data")
        btn_delete_data.bind(on_press=self.delete_data)
        layout.add_widget(btn_delete_data)

        self.recycleview = RV()
        layout.add_widget(self.recycleview)

        self.conn = sqlite3.connect('my_database.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS my_table (
                            id INTEGER PRIMARY KEY,
                            item TEXT NOT NULL,
                            price REAL,
                            date_added DATE
                        )''')

        self.refresh_data()

        return layout

    def add_data(self, instance):
        item = self.entry_item.text
        price = self.entry_price.text

        if not item or not price:
            self.show_popup("Error", "Please enter both item and price.")
            return

        try:
            price = float(price)
        except ValueError:
            self.show_popup("Error", "Invalid price. Please enter a number.")
            return

        date_added = datetime.now().strftime('%Y-%m-%d')

        try:
            self.cursor.execute('INSERT INTO my_table (item, price, date_added) VALUES (?, ?, ?)', (item, price, date_added))
            self.conn.commit()
            self.show_popup("Success", "Data added successfully.")
        except sqlite3.Error as e:
            self.show_popup("Error", f"An error occurred: {e}")
            self.conn.rollback()

        self.refresh_data()

        self.entry_item.text = ''
        self.entry_price.text = ''

    def delete_data(self, instance):
        selected_item = self.recycleview.get_select_data()
        if not selected_item:
            self.show_popup("Error", "Please select a row to delete.")
            return

        selected_item = selected_item[0]
        row_id = selected_item['text'][0]

        try:
            self.cursor.execute('DELETE FROM my_table WHERE id=?', (row_id,))
            self.conn.commit()
            self.show_popup("Success", "Data deleted successfully.")
        except sqlite3.Error as e:
            self.show_popup("Error", f"An error occurred: {e}")
            self.conn.rollback()

        self.refresh_data()

    def refresh_data(self):
        self.recycleview.data = []

        self.cursor.execute('SELECT * FROM my_table')
        rows = self.cursor.fetchall()

        total_price = 0.0

        for row in rows:
            self.recycleview.add_item(row)
            total_price += row[2]

        self.recycleview.add_item(('Total Price', '', total_price))

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical')
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text="OK", size_hint=(1, 0.3))
        popup_layout.add_widget(close_button)
        popup = Popup(title=title, content=popup_layout, size_hint=(None, None), size=(400, 200))
        close_button.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    AddDeleteDataApp().run()
