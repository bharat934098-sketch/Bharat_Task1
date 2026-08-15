import string
import secrets
import tkinter as tk
from tkinter import messagebox, ttk
import pyperclip


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Generator")
        self.root.geometry("460x640")
        self.root.resizable(False, False)

        # Apply a clean theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Session history (Max 5 passwords)
        self.history = []

        self.create_widgets()

    def create_widgets(self):
        # Header Label
        title_label = tk.Label(
            self.root, 
            text="🔐 Password Generator", 
            font=("Helvetica", 16, "bold"), 
            fg="#2c3e50"
        )
        title_label.pack(pady=12)

        # Options Frame
        opts_frame = ttk.LabelFrame(self.root, text=" Options ", padding=12)
        opts_frame.pack(fill="x", padx=20, pady=5)

        # Length Selector (Slider + Spinbox)
        tk.Label(
            opts_frame, 
            text="Password Length (Min: 8):", 
            font=("Helvetica", 10, "bold")
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.length_var = tk.IntVar(value=12)
        
        self.slider = ttk.Scale(
            opts_frame, 
            from_=8, 
            to=64, 
            variable=self.length_var, 
            command=self.sync_length_from_slider
        )
        self.slider.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        self.spinbox = ttk.Spinbox(
            opts_frame, 
            from_=8, 
            to=64, 
            textvariable=self.length_var, 
            width=5,
            command=self.sync_length_from_spinbox
        )
        self.spinbox.grid(row=1, column=1, sticky="w")
        opts_frame.columnconfigure(0, weight=1)

        # Checkboxes for Character Sets
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        self.exclude_ambiguous = tk.BooleanVar(value=True)

        ttk.Checkbutton(opts_frame, text="Include Uppercase (A-Z)", variable=self.use_upper).grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(opts_frame, text="Include Lowercase (a-z)", variable=self.use_lower).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(opts_frame, text="Include Numbers (0-9)", variable=self.use_digits).grid(row=4, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(opts_frame, text="Include Symbols (!@#$...)", variable=self.use_symbols).grid(row=5, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(opts_frame, text="Exclude Ambiguous (0, O, 1, l)", variable=self.exclude_ambiguous).grid(row=6, column=0, columnspan=2, sticky="w", pady=2)

        # Action Buttons Frame
        btn_frame = ttk.Frame(self.root, padding=5)
        btn_frame.pack(fill="x", padx=20, pady=5)

        self.gen_btn = ttk.Button(btn_frame, text="Generate Password", command=self.generate_password)
        self.gen_btn.grid(row=0, column=0, padx=3, pady=3, sticky="ew")

        self.copy_btn = ttk.Button(btn_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_btn.grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_fields)
        self.clear_btn.grid(row=0, column=2, padx=3, pady=3, sticky="ew")

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

        # Result Frame
        res_frame = ttk.LabelFrame(self.root, text=" Generated Password ", padding=10)
        res_frame.pack(fill="x", padx=20, pady=5)

        self.password_entry = ttk.Entry(res_frame, font=("Consolas", 12), justify="center")
        self.password_entry.pack(fill="x", pady=4)

        self.strength_label = tk.Label(res_frame, text="Strength: --", font=("Helvetica", 10, "bold"), fg="gray")
        self.strength_label.pack(anchor="w", pady=2)

        # Session History Frame
        hist_frame = ttk.LabelFrame(self.root, text=" Session History (Last 5) ", padding=10)
        hist_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        self.history_listbox = tk.Listbox(hist_frame, font=("Consolas", 10), height=5)
        self.history_listbox.pack(fill="both", expand=True)

    def sync_length_from_slider(self, val):
        self.length_var.set(int(float(val)))

    def sync_length_from_spinbox(self):
        try:
            val = int(self.spinbox.get())
            if val < 8:
                val = 8
            elif val > 64:
                val = 64
            self.length_var.set(val)
        except ValueError:
            self.length_var.set(8)

    def generate_password(self):
        length = self.length_var.get()
        if length < 8:
            messagebox.showerror("Invalid Input", "Minimum password length must be 8.")
            return

        # Prepare Pools
        pools = []
        if self.use_upper.get():
            pools.append(string.ascii_uppercase)
        if self.use_lower.get():
            pools.append(string.ascii_lowercase)
        if self.use_digits.get():
            pools.append(string.digits)
        if self.use_symbols.get():
            pools.append(string.punctuation)

        # Require at least 2 character types
        if len(pools) < 2:
            messagebox.showwarning("Selection Error", "Please select at least 2 character types.")
            return

        # Handle Ambiguous Characters
        if self.exclude_ambiguous.get():
            ambiguous_chars = {"0", "O", "1", "l"}
            cleaned_pools = []
            for pool in pools:
                cleaned = "".join([c for c in pool if c not in ambiguous_chars])
                cleaned_pools.append(cleaned)
            pools = cleaned_pools

        # Guarantee at least one character from each selected pool
        password_chars = [secrets.choice(pool) for pool in pools]

        # Combine all allowed characters for remaining positions
        full_pool = "".join(pools)
        remaining_length = length - len(password_chars)
        
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(full_pool))

        # Securely shuffle using Fisher-Yates algorithm with secrets.randbelow
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

        password = "".join(password_chars)

        # Update Display
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

        # Copy to Clipboard Automatically
        pyperclip.copy(password)

        # Calculate Strength
        self.update_strength(length, len(pools))

        # Update Session History
        self.update_history(password)

    def update_strength(self, length, type_count):
        if length >= 14 and type_count >= 3:
            self.strength_label.config(text="Strength: Strong 🟢", fg="green")
        elif length >= 10 and type_count >= 2:
            self.strength_label.config(text="Strength: Medium 🟡", fg="#d35400")
        else:
            self.strength_label.config(text="Strength: Weak 🔴", fg="red")

    def update_history(self, password):
        self.history.insert(0, password)
        if len(self.history) > 5:
            self.history.pop()

        self.history_listbox.delete(0, tk.END)
        for pwd in self.history:
            self.history_listbox.insert(tk.END, pwd)

    def copy_to_clipboard(self):
        pwd = self.password_entry.get()
        if pwd:
            pyperclip.copy(pwd)
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        else:
            messagebox.showwarning("Empty Field", "No password available to copy.")

    def clear_fields(self):
        self.password_entry.delete(0, tk.END)
        self.strength_label.config(text="Strength: --", fg="gray")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()