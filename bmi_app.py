import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Database Setup Name
DB_NAME = "bmi_records.db"

def initialize_database():
    """Initializes the SQLite database and creates the records table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to initialize database: {e}")

class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced BMI Calculator")
        self.root.geometry("500x650")
        self.root.minsize(450, 600)
        
        # Configure Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        initialize_database()
        self.create_widgets()

    def create_widgets(self):
        """Creates and places all GUI widgets in the main window."""
        # Title Label
        title_label = tk.Label(self.root, text="BMI Tracker & Analyzer", font=("Helvetica", 18, "bold"), fg="#2c3e50")
        title_label.pack(pady=15)

        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text=" User Details ", padding=15)
        input_frame.pack(fill="x", padx=20, pady=10)

        # Name Input
        tk.Label(input_frame, text="User Name:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=8)
        self.name_entry = ttk.Entry(input_frame, font=("Helvetica", 10), width=25)
        self.name_entry.grid(row=0, column=1, pady=8, padx=10)

        # Weight Input
        tk.Label(input_frame, text="Weight (kg):", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=8)
        self.weight_entry = ttk.Entry(input_frame, font=("Helvetica", 10), width=25)
        self.weight_entry.grid(row=1, column=1, pady=8, padx=10)

        # Height Input
        tk.Label(input_frame, text="Height (m):", font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", pady=8)
        self.height_entry = ttk.Entry(input_frame, font=("Helvetica", 10), width=25)
        self.height_entry.grid(row=2, column=1, pady=8, padx=10)

        # Result Display Frame
        self.result_frame = ttk.LabelFrame(self.root, text=" Results ", padding=15)
        self.result_frame.pack(fill="x", padx=20, pady=10)

        self.bmi_label = tk.Label(self.result_frame, text="BMI: --", font=("Helvetica", 12, "bold"))
        self.bmi_label.pack(anchor="w", pady=2)

        self.category_label = tk.Label(self.result_frame, text="Category: --", font=("Helvetica", 12, "bold"))
        self.category_label.pack(anchor="w", pady=2)

        # Action Buttons Frame
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill="x", padx=10)

        # Row 1 Buttons
        ttk.Button(btn_frame, text="Calculate BMI", command=self.calculate_bmi).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="View History", command=self.view_history).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="Show Graph", command=self.show_trend_graph).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Row 2 Buttons
        ttk.Button(btn_frame, text="Clear Fields", command=self.clear_fields).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="Exit", command=self.root.quit).grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

    def validate_inputs(self):
        """Validates inputs for being empty, non-numeric, or <= 0."""
        name = self.name_entry.get().strip()
        weight_str = self.weight_entry.get().strip()
        height_str = self.height_entry.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "User Name cannot be empty.")
            return None, None, None

        try:
            weight = float(weight_str)
            if weight <= 0:
                raise ValueError("Weight must be greater than zero.")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid weight! Please enter a valid positive number.")
            return None, None, None

        try:
            height = float(height_str)
            if height <= 0:
                raise ValueError("Height must be greater than zero.")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid height! Please enter a valid positive number.")
            return None, None, None

        return name, weight, height

    def classify_bmi(self, bmi):
        """Classifies the BMI value into standard health categories."""
        if bmi < 18.5:
            return "Underweight", "#3498db"  # Blue
        elif 18.5 <= bmi <= 24.9:
            return "Normal", "#2ecc71"       # Green
        elif 25 <= bmi <= 29.9:
            return "Overweight", "#f1c40f"   # Yellow/Orange
        else:
            return "Obese", "#e74c3c"        # Red

    def calculate_bmi(self):
        """Calculates BMI, displays visual feedback, and saves record to database."""
        name, weight, height = self.validate_inputs()
        if not name:
            return

        bmi = weight / (height ** 2)
        bmi_rounded = round(bmi, 2)
        category, color = self.classify_bmi(bmi_rounded)

        # Update UI feedback
        self.bmi_label.config(text=f"BMI: {bmi_rounded}")
        self.category_label.config(text=f"Category: {category}", fg=color)

        # Save record to database
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bmi_logs (name, weight, height, bmi, category)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, bmi_rounded, category))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not save record: {e}")

    def view_history(self):
        """Opens a new window showing historical logs for the user."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a User Name to view history.")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title(f"BMI History - {name}")
        history_window.geometry("500, 350")

        # Treeview Widget for tabular layout
        columns = ("ID", "Weight", "Height", "BMI", "Category", "Date")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=75, anchor="center")

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, weight, height, bmi, category, date 
                FROM bmi_logs WHERE name = ? ORDER BY date DESC
            """, (name,))
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                tree.insert("", "end", values=row)

            if not rows:
                messagebox.showinfo("No Records", f"No history found for user: {name}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve history: {e}")

    def show_trend_graph(self):
        """Plots a Matplotlib trend graph for the specified user."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a User Name to plot the trend graph.")
            return

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, bmi FROM bmi_logs WHERE name = ? ORDER BY date ASC
            """, (name,))
            data = cursor.fetchall()
            conn.close()

            if not data:
                messagebox.showinfo("No Data", f"No records available to plot for {name}.")
                return

            dates = [row[0] for row in data]
            bmis = [row[1] for row in data]

            # Create Matplotlib Figure
            graph_window = tk.Toplevel(self.root)
            graph_window.title(f"BMI Trend Graph - {name}")
            graph_window.geometry("600, 400")

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(dates, bmis, marker="o", color="#2980b9", linestyle="-", linewidth=2)
            ax.set_title(f"BMI Trend over Time for {name}")
            ax.set_xlabel("Date & Time")
            ax.set_ylabel("BMI Value")
            plt.xticks(rotation=45, ha="right")
            ax.grid(True, linestyle="--", alpha=0.6)
            fig.tight_layout()

            # Embed plot into Tkinter window
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load graph data: {e}")

    def clear_fields(self):
        """Clears all input entries and result displays."""
        self.name_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.bmi_label.config(text="BMI: --")
        self.category_label.config(text="Category: --", fg="black")

if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()
