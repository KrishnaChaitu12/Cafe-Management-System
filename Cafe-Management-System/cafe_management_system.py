import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import datetime

try:
    from PIL import Image, ImageDraw, ImageColor, ImageTk
except ImportError:
    Image = None
    ImageDraw = None
    ImageColor = None
    ImageTk = None

# Inventory and sales
inventory = {}
sales = []
order_cart = {}
dark_mode = False
wallpaper_color = None
wallpaper_image = None
wallpaper_source = None
wallpaper_resize_job = None
page_frames = {}
page_wallpaper_labels = {}
entry_widgets = []
text_widgets = []
label_widgets = []
button_widgets = []

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
        messagebox.showerror("Error", "Enter an item name to add to the order.")
        return
    try:
        qty = int(order_qty_entry.get())
        if qty <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a positive whole number.")
        return

    if item not in inventory:
        messagebox.showerror("Error", f"{item} is not in inventory.")
        return

    # Keep a cart of quantities. Repeatedly adding the same item combines its line.
    order_cart[item] = order_cart.get(item, 0) + qty
    refresh_order_cart()
    order_item_entry.delete(0, tk.END)
    order_qty_entry.delete(0, tk.END)


def refresh_order_cart():
    cart_text.configure(state="normal")
    cart_text.delete("1.0", tk.END)
    if not order_cart:
        cart_text.insert(tk.END, "Your order is empty. Add items above.")
        total_label.configure(text="Total: ₹0.00")
    else:
        total = 0.0
        for item, qty in order_cart.items():
            price = inventory[item][0]
            line_total = qty * price
            total += line_total
            cart_text.insert(tk.END, f"{item}  × {qty}   —   ₹{line_total:.2f}\n")
        total_label.configure(text=f"Total: ₹{total:.2f}")
    cart_text.configure(state="disabled")


def remove_cart_item():
    item = order_item_entry.get().title().strip()
    if item in order_cart:
        del order_cart[item]
        refresh_order_cart()
        order_item_entry.delete(0, tk.END)
    elif order_cart:
        # With an empty item field, remove the most recently added line.
        order_cart.popitem()
        refresh_order_cart()
    else:
        messagebox.showinfo("Order is empty", "There are no items to remove.", parent=root)


def checkout_order():
    if not order_cart:
        messagebox.showerror("Empty order", "Add at least one item before checkout.", parent=root)
        return

    # Validate the entire cart before changing any stock.
    for item, qty in order_cart.items():
        if item not in inventory:
            messagebox.showerror("Item unavailable", f"{item} is no longer in inventory.", parent=root)
            return
        available = inventory[item][1]
        if qty > available:
            messagebox.showerror(
                "Not enough stock",
                f"Only {available} {item}(s) available; the order needs {qty}.",
                parent=root,
            )
            return

    order_details = {}
    total = 0.0
    for item, qty in order_cart.items():
        line_total = qty * inventory[item][0]
        order_details[item] = (qty, line_total)
        total += line_total
    for item, qty in order_cart.items():
        inventory[item][1] -= qty

    sales.append((datetime.datetime.now(), order_details, total))
    summary = "\n".join(
        f"{name} x{qty} = ₹{cost:.2f}"
        for name, (qty, cost) in order_details.items()
    )
    messagebox.showinfo("Order Summary", f"{summary}\n\nTotal Bill: ₹{total:.2f}", parent=root)
    order_cart.clear()
    refresh_order_cart()
    refresh_inventory()
    show_sales()

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


def show_page(name):
    current_page[0] = name
    for frame in page_frames.values():
        frame.pack_forget()
    page_frames[name].pack(fill="both", expand=True)
    for button_name, button in nav_buttons.items():
        button.set_palette(palette(), button_name == name)


def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()


def choose_wallpaper():
    global wallpaper_image, wallpaper_color, wallpaper_source
    choice = messagebox.askyesnocancel(
        "Choose background",
        "Choose Yes to select an image, or No to choose a background color.",
        parent=root,
    )
    if choice is None:
        return
    if choice:
        path = filedialog.askopenfilename(
            parent=root,
            title="Choose wallpaper",
            filetypes=(
                ("Image files", "*.png *.gif *.ppm *.pgm *.jpg *.jpeg"),
                ("All files", "*"),
            ),
        )
        if not path:
            return
        try:
            wallpaper_source = path
            wallpaper_image = make_wallpaper_image()
            wallpaper_color = None
            apply_theme()
        except (tk.TclError, OSError, ValueError) as error:
            messagebox.showerror(
                "Unsupported image",
                f"This image could not be opened: {error}\n"
                "PNG, GIF, PPM and PGM work directly. JPG/JPEG requires Pillow.",
                parent=root,
            )
    else:
        selected = colorchooser.askcolor(parent=root, title="Choose background color")
        if selected and selected[1]:
            wallpaper_color = selected[1]
            wallpaper_image = None
            wallpaper_source = None
            apply_theme()


def make_wallpaper_image():
    """Create a cover-cropped wallpaper at the current content size."""
    global wallpaper_image
    if not wallpaper_source:
        return None
    width = max(main_area.winfo_width(), 760)
    height = max(main_area.winfo_height(), 480)
    if Image is not None:
        with Image.open(wallpaper_source) as source:
            source = source.convert("RGB")
            scale = max(width / source.width, height / source.height)
            size = (round(source.width * scale), round(source.height * scale))
            resampling = getattr(Image, "Resampling", Image)
            resized = source.resize(size, resampling.LANCZOS)
            left = (resized.width - width) // 2
            top = (resized.height - height) // 2
            cropped = resized.crop((left, top, left + width, top + height))
            return ImageTk.PhotoImage(cropped)

    if wallpaper_source.lower().endswith((".jpg", ".jpeg")):
        raise OSError("JPG/JPEG wallpapers need Pillow. Install it with: python3 -m pip install Pillow")
    original = tk.PhotoImage(file=wallpaper_source)
    # Tk's built-in image support cannot interpolate arbitrary sizes; use its
    # integer scaling while keeping the image centered in the page background.
    factor = max(1, min(width // max(original.width(), 1), height // max(original.height(), 1)))
    if factor > 1:
        return original.zoom(factor, factor)
    divisor = max(1, min(original.width() // width, original.height() // height))
    return original.subsample(divisor, divisor) if divisor > 1 else original


def on_window_resize(event):
    global wallpaper_resize_job
    if event.widget is not root or not wallpaper_source:
        return
    if wallpaper_resize_job is not None:
        root.after_cancel(wallpaper_resize_job)
    wallpaper_resize_job = root.after(140, refresh_wallpaper_size)


def refresh_wallpaper_size():
    global wallpaper_image, wallpaper_resize_job
    wallpaper_resize_job = None
    if not wallpaper_source:
        return
    try:
        wallpaper_image = make_wallpaper_image()
        for background in page_wallpaper_labels.values():
            background.configure(image=wallpaper_image)
    except (tk.TclError, OSError, ValueError) as error:
        messagebox.showerror("Wallpaper error", str(error), parent=root)


def palette():
    if dark_mode:
        return {
            "background": wallpaper_color or "#171b24", "surface": "#222834", "raised": "#303848",
            "text": "#f3f5f8", "muted": "#aab4c2", "accent": "#88a9ff",
            "border": "#455064", "input": "#343d4d", "glass": "#29313d",
            "shadow": "#11151d",
        }
    return {
        "background": wallpaper_color or "#e7edf3", "surface": "#ffffff",
        "raised": "#f7f9fc", "text": "#202938", "muted": "#687486",
        "accent": "#4269c7", "border": "#dbe2eb", "input": "#f5f7fa",
        "glass": "#f3f5f8", "shadow": "#cbd2dc",
    }


def apply_theme():
    p = palette()
    root.configure(bg=p["background"])
    main_area.configure(bg=p["background"])
    nav_bar.configure(bg=p["surface"])
    nav_container.configure(bg=p["surface"])
    brand.configure(bg=p["surface"], fg=p["text"])
    inventory_card_shadow.configure(bg=p["shadow"])
    inventory_card.configure(bg=p["glass"])
    for frame in page_frames.values():
        frame.configure(bg=p["background"])
        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=p["background"], fg=p["text"])
            elif isinstance(child, tk.Frame):
                child.configure(bg=p["background"])
    for entry in entry_widgets:
        entry.configure(
            bg=p["input"], fg=p["text"], insertbackground=p["text"],
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=p["border"], highlightcolor=p["accent"],
        )
    for widget in text_widgets:
        widget.configure(bg=p["glass"], fg=p["text"], insertbackground=p["text"],
                         relief="flat", bd=0, highlightthickness=1,
                         highlightbackground=p["border"])
    for label in label_widgets:
        label.configure(bg=p["background"], fg=p["text"])
    for button in button_widgets:
        button.apply_palette(p)
    for button_name, button in nav_buttons.items():
        button.set_palette(p, button_name == current_page[0])
    for background in page_wallpaper_labels.values():
        background.configure(
            image=wallpaper_image if wallpaper_image else "",
            bg=wallpaper_color or p["background"],
        )
        background.lower()
    settings_note.configure(bg=p["background"], fg=p["muted"])


def add_label(parent, text, **kwargs):
    kwargs.setdefault("font", ("Arial", 13))
    widget = tk.Label(parent, text=text, **kwargs)
    label_widgets.append(widget)
    return widget


class RoundedButton(tk.Canvas):
    """Clean pill-shaped button with a subtle drop shadow."""
    def __init__(self, parent, text, command, width=170, height=46, primary=False):
        super().__init__(parent, width=width, height=height, bd=0,
                         highlightthickness=0, cursor="hand2")
        self.text = text
        self.command = command
        self.primary = primary
        self.width = width
        self.height = height
        self.active = False
        self.hovered = False
        self._button_image = None
        self.colors = palette()
        self.configure(bg=self.colors["surface"])
        self.bind("<Button-1>", lambda _event: self.command())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.draw()

    def _on_enter(self, _event):
        self.hovered = True
        self.draw()

    def _on_leave(self, _event):
        self.hovered = False
        self.draw()

    def _rounded_rect(self, x1, y1, x2, y2, radius, fill):
        points = [x1 + radius, y1, x2 - radius, y1, x2, y1,
                  x2, y1 + radius, x2, y2 - radius, x2, y2,
                  x2 - radius, y2, x1 + radius, y2, x1, y2,
                  x1, y2 - radius, x1, y1 + radius, x1, y1]
        return self.create_polygon(points, smooth=True, splinesteps=24, fill=fill, outline="")

    def draw(self):
        self.delete("all")
        p = self.colors
        self.configure(bg=p["surface"])
        radius = self.height // 2
        is_emphasized = self.primary or self.active
        base = p["accent"] if is_emphasized else p["raised"]
        if self.hovered:
            base = p["accent"] if is_emphasized else p["border"]
        shadow = "#111827" if self.colors.get("dark") else "#8d9aab"
        if Image is not None:
            scale = 4
            image_width, image_height = self.width * scale, self.height * scale
            canvas_image = Image.new("RGBA", (image_width, image_height), p["surface"])
            shadow_layer = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            shadow_draw.rounded_rectangle(
                (2 * scale, 4 * scale, (self.width - 2) * scale, (self.height - 1) * scale),
                radius=radius * scale,
                fill=(*ImageColor.getrgb(shadow), 48),
            )
            canvas_image = Image.alpha_composite(canvas_image, shadow_layer)
            button_draw = ImageDraw.Draw(canvas_image)
            button_draw.rounded_rectangle(
                (1 * scale, 1 * scale, (self.width - 1) * scale, (self.height - 4) * scale),
                radius=radius * scale,
                fill=base,
            )
            resampling = getattr(Image, "Resampling", Image)
            canvas_image = canvas_image.convert("RGB").resize(
                (self.width, self.height), resampling.LANCZOS
            )
            self._button_image = ImageTk.PhotoImage(canvas_image)
            self.create_image(0, 0, image=self._button_image, anchor="nw")
        else:
            # Smooth polygon fallback when Pillow is unavailable.
            self._rounded_rect(2, 4, self.width - 2, self.height - 1, radius, shadow)
            self._rounded_rect(1, 1, self.width - 1, self.height - 4, radius, base)
        fg = "#ffffff" if is_emphasized else p["text"]
        self.create_text(self.width / 2, self.height / 2, text=self.text,
                         fill=fg, font=("Arial", 10, "bold"))

    def apply_palette(self, p):
        self.colors = dict(p)
        self.colors["dark"] = dark_mode
        self.draw()

    def set_palette(self, p, active):
        self.colors = dict(p)
        self.colors["dark"] = dark_mode
        self.active = active
        self.draw()


def make_action_button(parent, text, command, primary=False):
    button = RoundedButton(parent, text, command, primary=primary)
    button_widgets.append(button)
    return button

# --- GUI Setup ---
root = tk.Tk()
root.title("Cafe Management System")
try:
    root.state("zoomed")
except tk.TclError:
    root.geometry("1100x760")
root.minsize(760, 560)
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.bind("<Configure>", on_window_resize)

wallpaper_layer = tk.Label(root, bd=0)
wallpaper_layer.place_forget()

nav_bar = tk.Frame(root, padx=18, pady=12)
nav_bar.grid(row=0, column=0, sticky="ew")
nav_bar.columnconfigure(0, weight=1)
brand = tk.Label(nav_bar, text="☕  CAFE MANAGEMENT", font=("Arial", 14, "bold"))
brand.grid(row=0, column=0, sticky="w", padx=(0, 16))
nav_container = tk.Frame(nav_bar)
nav_container.grid(row=0, column=1, sticky="e")

main_area = tk.Frame(root, padx=28, pady=22)
main_area.grid(row=1, column=0, sticky="nsew")
main_area.rowconfigure(0, weight=1)
main_area.columnconfigure(0, weight=1)
current_page = ["Inventory"]
nav_buttons = {}

def create_page(name):
    frame = tk.Frame(main_area, padx=22, pady=20)
    page_frames[name] = frame
    # A page-owned image layer stays above the parent and below its controls.
    background = tk.Label(frame, image=wallpaper_image or "", bd=0,
                          bg=wallpaper_color or palette()["background"])
    background.place(x=0, y=0, relwidth=1, relheight=1)
    background.lower()
    page_wallpaper_labels[name] = background
    return frame

# Inventory
inventory_frame = create_page("Inventory")
add_label(inventory_frame, "Inventory", font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 14))
inventory_card_shadow = tk.Frame(inventory_frame, padx=0, pady=0)
inventory_card_shadow.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))
inventory_card = tk.Frame(inventory_card_shadow, padx=0, pady=0)
inventory_card.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 3))
inv_text = tk.Text(inventory_card, font=("Consolas", 14), wrap="word", padx=16, pady=14,
                   relief="flat", bd=0, highlightthickness=0)
inv_text.pack(fill="both", expand=True)
text_widgets.append(inv_text)

# Add Item
add_frame = create_page("Add Item")
add_label(add_frame, "Add an item", font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 18))
for caption in ("Item Name", "Price (₹)", "Quantity"):
    add_label(add_frame, caption, font=("Arial", 12, "bold")).pack(anchor="w", pady=(8, 4))
    entry = tk.Entry(add_frame, font=("Arial", 14), width=38)
    entry.pack(anchor="w", fill="x", ipady=9, pady=(0, 4))
    entry_widgets.append(entry)
    if caption == "Item Name":
        item_entry = entry
    elif caption == "Price (₹)":
        price_entry = entry
    else:
        qty_entry = entry
make_action_button(add_frame, "Add Item", add_item, primary=True).pack(anchor="w", pady=18)

# Delete Item
delete_frame = create_page("Delete Item")
add_label(delete_frame, "Remove an item", font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 18))
add_label(delete_frame, "Item name", font=("Arial", 12, "bold")).pack(anchor="w", pady=(8, 4))
delete_entry = tk.Entry(delete_frame, font=("Arial", 14), width=38)
delete_entry.pack(anchor="w", fill="x", ipady=9)
entry_widgets.append(delete_entry)
make_action_button(delete_frame, "Delete Item", delete_item, primary=True).pack(anchor="w", pady=18)

# Process Order
order_frame = create_page("Process Order")
add_label(order_frame, "Process an order", font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 18))
for caption in ("Item name", "Quantity"):
    add_label(order_frame, caption, font=("Arial", 12, "bold")).pack(anchor="w", pady=(8, 4))
    entry = tk.Entry(order_frame, font=("Arial", 14), width=38)
    entry.pack(anchor="w", fill="x", ipady=9)
    entry_widgets.append(entry)
    if caption == "Item name":
        order_item_entry = entry
    else:
        order_qty_entry = entry
make_action_button(order_frame, "Add to order", process_order, primary=True).pack(anchor="w", pady=14)
add_label(order_frame, "Current order", font=("Arial", 15, "bold")).pack(anchor="w", pady=(10, 6))
cart_text = tk.Text(order_frame, font=("Consolas", 12), height=8, wrap="word", padx=12, pady=10, state="disabled")
cart_text.pack(fill="both", expand=True)
text_widgets.append(cart_text)
total_label = add_label(order_frame, "Total: ₹0.00", font=("Arial", 15, "bold"))
total_label.pack(anchor="e", pady=(10, 6))
order_actions = tk.Frame(order_frame)
order_actions.pack(anchor="e")
make_action_button(order_actions, "Remove item", remove_cart_item).pack(side="left", padx=5)
make_action_button(order_actions, "Checkout order", checkout_order, primary=True).pack(side="left", padx=5)

# Sales Record
sales_frame = create_page("Sales Record")
add_label(sales_frame, "Sales record", font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 14))
sales_text = tk.Text(sales_frame, font=("Consolas", 14), wrap="word", padx=16, pady=14)
sales_text.pack(fill="both", expand=True)
text_widgets.append(sales_text)

# Settings
settings_frame = create_page("Settings")
add_label(settings_frame, "Settings", font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 8))
add_label(settings_frame, "Personalize the cafe workspace", font=("Arial", 12)).pack(anchor="w", pady=(0, 18))
make_action_button(settings_frame, "Choose Wallpaper", choose_wallpaper).pack(anchor="w", pady=7)
make_action_button(settings_frame, "Toggle Light / Dark", toggle_theme).pack(anchor="w", pady=7)
settings_note = tk.Label(settings_frame, text="Wallpaper images: PNG, GIF, PPM, PGM, JPG and JPEG (JPEG requires Pillow). You can also choose a solid color.", font=("Arial", 10))
settings_note.pack(anchor="w", pady=(16, 0))

page_names = ("Inventory", "Add Item", "Delete Item", "Process Order", "Sales Record", "Settings")
for name in page_names:
    button = RoundedButton(
        nav_container, name,
        lambda page=name: (current_page.__setitem__(0, page), show_page(page)),
        width=112 if name != "Process Order" else 132, height=40,
    )
    button.pack(side="left", padx=3)
    nav_buttons[name] = button

show_page("Inventory")
apply_theme()
refresh_inventory()
refresh_order_cart()
show_sales()
root.mainloop()
