import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# Inventory and sales
inventory = {}
sales = []

# --- Functions ---
def refresh_inventory():
    inv_text.delete("1.0", tk.END)
    if not inventory:
        inv_text.insert(tk.END, "No items available.\n")
    else:
        for item, (price, qty) in inventory.items():
            inv_text.insert(tk.END, f"{item}: ₹{price:.2f} | Available: {qty}\n")

def add_item():
    item = item_entry.get().title().strip()
    if not item:
        messagebox.showerror("Error", "Item name required.")
        return
    try:
        price = float(price_entry.get())
        qty = int(qty_entry.get())
        inventory[item] = [price, qty]
        messagebox.showinfo("Success", f"{item} added successfully!")
        refresh_inventory()
        # Clear inputs after adding
        item_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Error", "Invalid input! Numbers required.")

def delete_item():
    item = delete_entry.get().title().strip()
    if not item:
        messagebox.showerror("Error", "Enter item name to delete.")
        return
    if item in inventory:
        del inventory[item]
        messagebox.showinfo("Deleted", f"{item} deleted successfully!")
        refresh_inventory()
        delete_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Item not found.")

def process_order():
    item = order_item_entry.get().title().strip()
    if not item:
        messagebox.showerror("Error", "Enter item name to order.")
        return
    try:
        qty = int(order_qty_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid quantity!")
        return

    if item not in inventory:
        messagebox.showerror("Error", "Item not found!")
        return
    if qty > inventory[item][1]:
        messagebox.showerror("Error", f"Only {inventory[item][1]} {item}(s) available!")
        return

    cost = qty * inventory[item][0]
    inventory[item][1] -= qty
    sales.append((datetime.datetime.now(), {item: (qty, cost)}, cost))
    messagebox.showinfo("Order Summary", f"{item} x{qty} = ₹{cost:.2f}\nTotal Bill: ₹{cost:.2f}")
    refresh_inventory()
    show_sales()
    # Clear inputs after processing
    order_item_entry.delete(0, tk.END)
    order_qty_entry.delete(0, tk.END)

def show_sales():
    sales_text.delete("1.0", tk.END)
    if not sales:
        sales_text.insert(tk.END, "No sales yet.\n")
    else:
        for time, order, total in sales:
            sales_text.insert(tk.END, f"\n{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for item, (qty, cost) in order.items():
                sales_text.insert(tk.END, f"{item} x{qty} = ₹{cost:.2f}\n")
            sales_text.insert(tk.END, f"Total: ₹{total:.2f}\n")

# --- GUI Setup ---
root = tk.Tk()
root.title("Cafe Management System")
root.state("zoomed")   # scale to device resolution
root.configure(bg="black")

style = ttk.Style()
style.theme_use("default")
style.configure("TNotebook", background="black")
style.configure("TNotebook.Tab", font=("Arial", 14, "bold"), foreground="white", background="black")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Inventory Tab
inventory_frame = tk.Frame(notebook, bg="black")
inv_text = tk.Text(inventory_frame, font=("Consolas", 16), bg="black", fg="white")
inv_text.pack(fill="both", expand=True, padx=20, pady=20)
notebook.add(inventory_frame, text="Inventory")

# Add Item Tab
add_frame = tk.Frame(notebook, bg="black")
tk.Label(add_frame, text="Item Name:", fg="white", bg="black", font=("Arial", 16)).pack(pady=5)
item_entry = tk.Entry(add_frame, font=("Arial", 16), width=30)
item_entry.pack(pady=5)
tk.Label(add_frame, text="Price:", fg="white", bg="black", font=("Arial", 16)).pack(pady=5)
price_entry = tk.Entry(add_frame, font=("Arial", 16), width=30)
price_entry.pack(pady=5)
tk.Label(add_frame, text="Quantity:", fg="white", bg="black", font=("Arial", 16)).pack(pady=5)
qty_entry = tk.Entry(add_frame, font=("Arial", 16), width=30)
qty_entry.pack(pady=5)
tk.Button(add_frame, text="Add Item", command=add_item, bg="black", fg="white", font=("Arial", 16)).pack(pady=15)
notebook.add(add_frame, text="Add Item")

# Delete Item Tab
delete_frame = tk.Frame(notebook, bg="black")
tk.Label(delete_frame, text="Delete Item Name:", fg="white", bg="black", font=("Arial", 16)).pack(pady=5)
delete_entry = tk.Entry(delete_frame, font=("Arial", 16), width=30)
delete_entry.pack(pady=5)
tk.Button(delete_frame, text="Delete Item", command=delete_item, bg="black", fg="white", font=("Arial", 16)).pack(pady=15)
notebook.add(delete_frame, text="Delete Item")

# Process Order Tab
order_frame = tk.Frame(notebook, bg="black")
tk.Label(order_frame, text="Order Item:", fg="white", bg="black", font=("Arial", 16)).pack(pady=5)
order_item_entry = tk.Entry(order_frame, font=("Arial", 16), width=30)
order_item_entry.pack(pady=5)
tk.Label(order_frame, text="Order Quantity:", fg="white", bg="black", font=("Arial", 16)).pack(pady=5)
order_qty_entry = tk.Entry(order_frame, font=("Arial", 16), width=30)
order_qty_entry.pack(pady=5)
tk.Button(order_frame, text="Process Order", command=process_order, bg="black", fg="white", font=("Arial", 16)).pack(pady=15)
notebook.add(order_frame, text="Process Order")

# Sales Record Tab
sales_frame = tk.Frame(notebook, bg="black")
sales_text = tk.Text(sales_frame, font=("Consolas", 16), bg="black", fg="white")
sales_text.pack(fill="both", expand=True, padx=20, pady=20)
notebook.add(sales_frame, text="Sales Record")

root.mainloop()