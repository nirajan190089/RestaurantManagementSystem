from tkinter import *
from tkinter import ttk
import sqlite3


class Menu:
    db_name = "sqlite3.db"

    def __init__(self, wind):
        self.wind = wind
        self.wind.title("My Cafe")
        self.wind.iconbitmap("icon.ico")

        frame = LabelFrame(self.wind)
        frame.grid(row=0, column=0, padx=20, pady=10, columnspan=2)

        Label(frame, text="Name: ").grid(row=1, column=1)
        self.name = Entry(frame)
        self.name.grid(row=1, column=2)

        Label(frame, text="Price: ").grid(row=2, column=1)
        self.price = Entry(frame)
        self.price.grid(row=2, column=2)

        Label(frame, text="Type: ").grid(row=3, column=1)
        self.type = Entry(frame)
        self.type.grid(row=3, column=2)

        ttk.Button(frame, text="Add to Menu", command=self.adding).grid(row=4, column=2)
        self.message = Label(text="", fg="red")
        self.message.grid(row=4, column=0)

        self.tree = ttk.Treeview(height=10, columns=("name", "price", "type"))
        self.tree.grid(row=5, column=0, columnspan=4, padx=10, pady=5)
        self.tree.heading("#0", text="ID", anchor=W)
        self.tree.heading("name", text="Name", anchor=W)
        self.tree.heading("price", text="Price", anchor=W)
        self.tree.heading("type", text="Type", anchor=W)

        ttk.Button(text="Delete Menu", command=self.delete_menu).grid(row=6, column=0)
        ttk.Button(text="Edit Menu", command=self.edit).grid(row=6, column=1)

        self.view_records()

        # connecting to database

    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            query_result = cursor.execute(query, parameters)
            connect.commit()
        return query_result

    # validating and adding records
    def validation(self):
        return len(self.name.get()) != 0 and len(self.price.get()) != 0 and len(self.type.get()) != 0

    # adding items to menu
    def adding(self):
        if self.validation():
            query = 'INSERT INTO menu VALUES (NULL, ?, ?, ?, NULL)'
            parameters = (self.name.get(), self.price.get(), self.type.get())
            self.run_query(query, parameters)
            self.message['text'] = 'Record {} added'.format(self.name.get())
            self.name.delete(0, END)
            self.price.delete(0, END)
            self.type.delete(0, END)
        else:
            self.message['text'] = 'Name or Price or Type field is empty.'
        self.view_records()

    # deleting items from menu
    def delete_menu(self):
        self.message['text'] = ""
        try:
            self.tree.item(self.tree.selection())['text']
        except IndexError:
            self.message['text'] = "Please, select a record."
        self.message['text'] = ""
        id = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM menu WHERE id = ?'
        self.run_query(query, (id,))
        self.message['text'] = "Record with id: {} deleted".format(id)
        self.view_records()

    # getting results from database
    def view_records(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = 'SELECT * FROM menu ORDER BY id DESC'
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert('', 0, text=row[0], values=(row[1], row[2], row[3]))

    def edit(self):
        self.message['text'] = ""
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError:
            self.message['text'] = "Please, select a record."
            return

        id = self.tree.item(self.tree.selection())['text']
        old_name = self.tree.item(self.tree.selection())['values'][0]
        old_price = self.tree.item(self.tree.selection())['values'][1]
        self.edit_wind = Toplevel()
        self.edit_wind.title('Editing')

        Label(self.edit_wind, text="Old Name").grid(row=0, column=1, padx=10, pady=5)
        Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=old_name), state='readonly').grid(row=0,
                                                                                                             column=2,
                                                                                                             padx=10,
                                                                                                             pady=5)
        Label(self.edit_wind, text="New Name").grid(row=1, column=1, padx=10, pady=5)
        new_name = Entry(self.edit_wind)
        new_name.grid(row=1, column=2, padx=10, pady=5)

        Label(self.edit_wind, text="Old Price").grid(row=2, column=1, padx=10, pady=5)
        Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=old_price), state='readonly').grid(row=2,
                                                                                                              column=2,
                                                                                                              padx=10,
                                                                                                              pady=5)
        Label(self.edit_wind, text="New Price").grid(row=3, column=1, padx=10, pady=5)
        new_price = Entry(self.edit_wind)
        new_price.grid(row=3, column=2, padx=10, pady=5)

        update_button = ttk.Button(self.edit_wind, text="Save Changes",
                                   command=lambda: self.edit_records(new_name.get(), new_price.get(), id))
        update_button.grid(row=4, column=2, padx=10, pady=5)

    def edit_records(self, new_name, new_price, id):
        query = "UPDATE menu SET name = ?, price = ? WHERE id = ?"
        parameters = (new_name, new_price, id)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['text'] = "Record with id {} changed.".format(id)
        self.view_records()

        self.edit_wind.mainloop()


if __name__ == '__main__':
    wind = Tk()
    application = Menu(wind)
    wind.mainloop()