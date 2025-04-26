import datetime

# Empty inventory: items must be added manually
inventory = {}

# Sales record
sales = []

def show_inventory():
    print("\n--- Inventory ---")
    if not inventory:
        print("No items available.")
    else:
        for item, (price, qty) in inventory.items():
            print(f"{item}: ₹{price:.2f} | Available: {qty}")
    input("\nPress Enter to return to the main menu...")

def add_item():
    item = input("Enter new item name: ").title()
    if item in inventory:
        print("Item already exists! Use update function instead.")
        return
    try:
        price = float(input(f"Enter price of {item}: ₹"))
        qty = int(input(f"Enter quantity of {item}: "))
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
    if not inventory:
        print("No items available to order.")
        return

    order = {}
    total = 0

    while True:
        show_inventory()
        item = input("Enter item name to order (or 'done' to finish): ").title()
        if item == 'Done':
            break
        if item not in inventory:
            print("Item not found!")
            continue
        try:
            qty = int(input(f"Enter quantity for {item}: "))
        except ValueError:
            print("Invalid quantity!")
            continue

        if qty > inventory[item][1]:
            print(f"Only {inventory[item][1]} {item}(s) available!")
            continue

        cost = qty * inventory[item][0]
        inventory[item][1] -= qty
        order[item] = (qty, cost)
        total += cost
        print(f"Added {qty} {item}(s) to order. Subtotal: ₹{total:.2f}")

    if order:
        sales.append((datetime.datetime.now(), order, total))
        print("\n--- Order Summary ---")
        for item, (qty, cost) in order.items():
            print(f"{item} x{qty} = ₹{cost:.2f}")
        print(f"Total Bill: ₹{total:.2f}")
    else:
        print("No items ordered.")

    input("\nPress Enter to return to the main menu...")

def show_sales():
    print("\n--- Sales Record ---")
    if not sales:
        print("No sales yet.")
    else:
        for time, order, total in sales:
            print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')}")
            for item, (qty, cost) in order.items():
                print(f"{item} x{qty} = ₹{cost:.2f}")
            print(f"Total: ₹{total:.2f}")
    input("\nPress Enter to return to the main menu...")

def main():
    while True:
        print("\n=== Cafe Management System ===")
        print("1. Show Inventory")
        print("2. Add New Item")
        print("3. Delete Item")
        print("4. Process Order")
        print("5. View Sales Record")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

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
            print("Thank you for using Cafe Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
