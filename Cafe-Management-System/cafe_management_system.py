import datetime

# Inventory with item: [price, quantity]
inventory = {
    "Coffee": [50, 100],
    "Tea": [30, 100],
    "Sandwich": [80, 50],
    "Cake": [120, 30]
}

# Sales record
sales = []


def show_inventory():
    print("\n--- Inventory ---")
    for item, (price, qty) in inventory.items():
        print(f"{item}: ₹{price} | Available: {qty}")
    print()


def add_item():
    item = input("Enter new item name: ").title()
    if item in inventory:
        print("Item already exists! Use update function instead.")
        return
    try:
        price = float(input("Enter price of the item: ₹"))
        qty = int(input("Enter quantity available: "))
        inventory[item] = [price, qty]
        print(f"{item} added successfully!")
    except ValueError:
        print("Invalid input! Please enter numbers for price and quantity.")


def delete_item():
    item = input("Enter item name to delete: ").title()
    if item in inventory:
        del inventory[item]
        print(f"{item} deleted successfully!")
    else:
        print("Item not found in inventory.")


def process_order():
    order = {}
    total = 0
    while True:
        show_inventory()
        item = input("Enter item name (or 'done' to finish order): ").title()
        if item == 'Done':
            break
        if item not in inventory:
            print("Item not found!")
            continue
        try:
            qty = int(input(f"Enter quantity for {item}: "))
        except ValueError:
            print("Please enter a valid number!")
            continue
        if qty > inventory[item][1]:
            print("Insufficient stock!")
            continue
        cost = qty * inventory[item][0]
        inventory[item][1] -= qty
        order[item] = (qty, cost)
        total += cost
    if order:
        sales.append((datetime.datetime.now(), order, total))
        print("\nOrder Summary:")
        for item, (qty, cost) in order.items():
            print(f"{item} x{qty} = ₹{cost}")
        print(f"Total Bill: ₹{total}\n")


def show_sales():
    print("\n--- Sales Record ---")
    for time, order, total in sales:
        print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')}")
        for item, (qty, cost) in order.items():
            print(f"{item} x{qty} = ₹{cost}")
        print(f"Total: ₹{total}")
    print()


def main():
    while True:
        print("\n=== Cafe Management System ===")
        print("1. Show Inventory")
        print("2. Add New Item")
        print("3. Delete Item")
        print("4. Process Order")
        print("5. View Sales Record")
        print("6. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            show_inventory()
        elif choice == '2':
            add_item()
        elif choice == '3':
            delete_item()
        elif choice == '4':
            process_order()
        elif choice == '5':
            show_sales()
        elif choice == '6':
            print("Exiting Cafe Management System. Goodbye!")
            break
        else:
            print("Invalid choice! Please select from 1-6.")


if __name__ == "__main__":
    main()