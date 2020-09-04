from tkinter import *
from tkinter import ttk
import sqlite3


class Menu:
    db_name = "sqlite3.db"

    def __init__(self, wind):
        self.wind = wind
        self.wind.title("Nirajan Ko Restaurant")
        self.wind.iconbitmap("icon.ico")

        # <!----- GUI ----- >

        # Bills
        frame = LabelFrame(self.wind)
        frame.grid(row=10, column=0)

        Label(frame, text="Nett").grid(row=1, column=1, padx=10, pady=2)
        self.total = Entry(frame, state="readonly")
        self.total.grid(row=1, column=2, padx=10)

        Label(frame, text="VAT").grid(row=2, column=1)
        self.vat = Entry(frame, state="readonly")
        self.vat.grid(row=2, column=2, padx=10)

        Label(frame, text="Total").grid(row=3, column=1)
        self.total_with_vat = Entry(frame, state="readonly")
        self.total_with_vat.grid(row=3, column=2, padx=10)

        ttk.Button(frame, text="Pay", command=self.pay).grid(row=5, column=2, pady=5)

        # messages
        self.message = Label(text="", fg="#ff0000", font=('', 14, "normal"))
        self.message.grid(row=3, column=0, pady=5, columnspan=4)

        Label(wind, text="[ Available on Menu ]", font=('', 10, 'bold')).grid(row=4, column=0)
        Label(wind, text="[    Your Orders    ]", font=('', 10, 'bold')).grid(row=7, column=0)
        Label(wind, text="[    Your Bills    ]", font=('', 10, 'bold')).grid(row=9, column=0, pady=10)

        # Menu Tree
        self.tree = ttk.Treeview(height=6, columns=("name", "price", "type"))
        self.tree.grid(row=5, column=0, columnspan=3)
        self.tree.heading("#0", text="ID", anchor=W)
        self.tree.heading("name", text="Name", anchor=W)
        self.tree.heading("price", text="Price", anchor=W)
        self.tree.heading("type", text="Type", anchor=W)

        # Place order button
        ttk.Button(text="Order", command=self.place_order).grid(row=6, column=1, pady=5)

        # order tree
        self.order_tree = ttk.Treeview(height=4, columns=("name", "price", "quantity"))
        self.order_tree.grid(row=8, column=0, columnspan=3)
        self.order_tree.heading("#0", text="ID", anchor=W)
        self.order_tree.heading("name", text="Name", anchor=W)
        self.order_tree.heading("price", text="Price", anchor=W)
        self.order_tree.heading("quantity", text="Quantity", anchor=W)

        # Cancel Order button
        ttk.Button(text="Cancel Order", command=self.cancel_order).grid(row=9, column=1, pady=5)
        self.view_menu()
        self.view_orders()

    # <---------- GUI ENDS ------------>

    # connecting to database
    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            query_result = cursor.execute(query, parameters)
            connect.commit()
        return query_result

    def pay(self):
        self.message['text'] = "Please, proceed to counter for payment."

    def place_order(self):
        self.message['text'] = ""
        if self.tree.item(self.tree.selection())['text'] == "":
            self.message['text'] = "Please, select an item."
        else:
            self.message['text'] = ""
            id = self.tree.item(self.tree.selection())['text']
            query = "SELECT * FROM orders WHERE customer_orders = ?"
            qs = self.run_query(query, (id,))
            for object in qs:
                quantity = object[4]
                quantity = quantity + 1
                id = object[0]
                query = "UPDATE orders SET quantity = ? WHERE id = ?"
                self.run_query(query, parameters=(quantity, id))
                self.message['text'] = "Quantity updated!"
                self.view_orders()
                return
            query = 'INSERT INTO orders VALUES (NULL, 1, 0, ?, 1)'
            self.run_query(query, (id,))
            self.message['text'] = "Order succesful."
            self.view_orders()

    # deleting items from menu
    def cancel_order(self):
        self.message['text'] = ""
        if self.order_tree.item(self.order_tree.selection())['text'] == "":
            self.message['text'] = "Please, select an order."
        else:
            self.message['text'] = ""
            id = self.order_tree.item(self.order_tree.selection())['text']
            query = 'DELETE FROM orders WHERE id = ?'
            self.run_query(query, (id,))
            self.message['text'] = "Order with id: {} cancelled.".format(id)
            self.view_orders()

    # getting results from database
    def view_menu(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = 'SELECT * FROM menu ORDER BY id DESC'
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert('', 0, text=row[0], values=(row[1], row[2], row[3]))

    def view_orders(self):
        orders = self.order_tree.get_children()
        for element in orders:
            self.order_tree.delete(element)
        query = 'SELECT orders.id, orders.quantity, menu.name, menu.price FROM orders INNER JOIN menu ON customer_orders' \
                ' = menu.id WHERE orders.table_number = 1 ORDER BY orders.id DESC'
        db_rows = self.run_query(query)
        for row in db_rows:
            self.order_tree.insert('', 0, text=row[0], values=(row[2], row[3], row[1]))
        self.view_bills()

    def view_bills(self):
        query = 'SELECT orders.quantity, menu.price FROM orders INNER JOIN menu ON customer_orders = menu.id WHERE ' \
                'orders.table_number = 1'
        db_rows = self.run_query(query)
        total = 0
        for row in db_rows:
            total += row[0] * row[1]
        vat = .13 * total
        total_with_vat = vat + total

        self.total.config(state=NORMAL)
        self.total.delete(0, END)
        self.total.insert(0, total)
        self.total.config(state="readonly")

        self.vat.config(state=NORMAL)
        self.vat.delete(0, END)
        self.vat.insert(0, vat)
        self.vat.config(state="readonly")

        self.total_with_vat.config(state=NORMAL)
        self.total_with_vat.delete(0, END)
        self.total_with_vat.insert(0, total_with_vat)
        self.total_with_vat.config(state="readonly")


if __name__ == '__main__':
    wind = Tk()
    application = Menu(wind)
    wind.mainloop()