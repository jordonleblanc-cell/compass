import tkinter as tk
from tkinter import ttk, messagebox, font
import urllib.request
import json
import threading
from datetime import datetime

# --- Configuration ---
DATA_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

class SupervisorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Supervisor Profile Dashboard")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f2f5")

        # Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Data Store
        self.raw_data = {}
        
        # UI Setup
        self.create_header()
        self.create_main_container()
        self.create_status_bar()

        # Load Data immediately
        self.load_data()

    def configure_styles(self):
        # Color Palette
        self.colors = {
            "primary": "#1a73e8",   # Google Blue
            "secondary": "#5f6368", # Grey
            "success": "#1e8e3e",   # Green
            "warning": "#f9ab00",   # Yellow
            "danger": "#d93025",    # Red
            "bg": "#f0f2f5",
            "card": "#ffffff"
        }
        
        # Configure Ttk Styles
        self.style.configure("Card.TFrame", background=self.colors["card"], relief="flat", borderwidth=0)
        self.style.configure("Header.TLabel", background=self.colors["primary"], foreground="white", font=("Helvetica", 16, "bold"))
        self.style.configure("Subheader.TLabel", background=self.colors["card"], foreground=self.colors["secondary"], font=("Helvetica", 12))
        self.style.configure("Metric.TLabel", background=self.colors["card"], foreground="#202124", font=("Helvetica", 24, "bold"))
        self.style.configure("MetricTitle.TLabel", background=self.colors["card"], foreground=self.colors["secondary"], font=("Helvetica", 10))
        
        # Progress Bar
        self.style.configure("Green.Horizontal.TProgressbar", background=self.colors["success"])
        self.style.configure("Yellow.Horizontal.TProgressbar", background=self.colors["warning"])
        self.style.configure("Red.Horizontal.TProgressbar", background=self.colors["danger"])

    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.colors["primary"], height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        title = tk.Label(header_frame, text="Supervisor Performance Analytics", 
                         bg=self.colors["primary"], fg="white", 
                         font=("Segoe UI", 18, "bold"))
        title.pack(side="left", padx=20, pady=10)

        refresh_btn = tk.Button(header_frame, text="↻ Refresh Data", 
                                bg="#1557b0", fg="white", relief="flat",
                                command=self.load_data, font=("Segoe UI", 10))
        refresh_btn.pack(side="right", padx=20, pady=10)

    def create_main_container(self):
        # Scrollable Main Canvas
        self.canvas = tk.Canvas(self.root, bg=self.colors["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Card.TFrame")
        self.scrollable_frame.configure(style="TFrame") # Reset to transparent-ish if needed or match bg

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=880) # Slightly less than window width
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        self.scrollbar.pack(side="right", fill="y")

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor="w", bg="#e0e0e0")
        status_bar.pack(side="bottom", fill="x")

    def load_data(self):
        self.status_var.set("Fetching data from API...")
        # Run in thread to prevent UI freezing
        thread = threading.Thread(target=self.fetch_data_thread)
        thread.daemon = True
        thread.start()

    def fetch_data_thread(self):
        try:
            req = urllib.request.Request(DATA_URL)
            req.add_header('User-Agent', 'Python-Supervisor-App')
            with urllib.request.urlopen(req) as response:
                data = response.read()
                json_data = json.loads(data)
                self.root.after(0, lambda: self.render_dashboard(json_data))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Failed to fetch data: {str(e)}"))

    def show_error(self, message):
        self.status_var.set("Error")
        messagebox.showerror("Connection Error", message)

    def clear_dashboard(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def render_dashboard(self, data):
        self.clear_dashboard()
        self.raw_data = data
        self.status_var.set(f"Data updated: {datetime.now().strftime('%H:%M:%S')}")

        # --- 1. Profile Header Card ---
        profile_frame = self.create_card(self.scrollable_frame)
        profile_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Try to find name/role fields dynamically
        name = data.get("name") or data.get("Supervisor") or data.get("fullName") or "Unknown Supervisor"
        role = data.get("role") or data.get("Title") or data.get("position") or "Supervisor"
        dept = data.get("department") or data.get("Department") or "General Operations"
        
        tk.Label(profile_frame, text=name, bg=self.colors["card"], font=("Segoe UI", 20, "bold"), fg="#202124").pack(anchor="w", padx=20, pady=(15, 0))
        tk.Label(profile_frame, text=f"{role} | {dept}", bg=self.colors["card"], font=("Segoe UI", 12), fg=self.colors["secondary"]).pack(anchor="w", padx=20, pady=(0, 15))

        # --- 2. Interpretation / AI Summary ---
        summary_frame = self.create_card(self.scrollable_frame)
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(summary_frame, text="Performance Interpretation", bg=self.colors["card"], font=("Segoe UI", 12, "bold"), fg=self.colors["primary"]).pack(anchor="w", padx=20, pady=(15, 10))
        
        interpretation_text = self.generate_interpretation(data)
        interp_label = tk.Label(summary_frame, text=interpretation_text, bg=self.colors["card"], font=("Segoe UI", 11), justify="left", wraplength=800)
        interp_label.pack(anchor="w", padx=20, pady=(0, 15))

        # --- 3. Key Metrics Grid ---
        metrics_container = tk.Frame(self.scrollable_frame, bg=self.colors["bg"])
        metrics_container.pack(fill="x", padx=20, pady=10)
        
        # Identify numeric metrics
        metrics = self.extract_metrics(data)
        
        # Create a grid layout for metrics
        row = 0
        col = 0
        MAX_COLS = 3
        
        for key, value in metrics.items():
            self.create_metric_card(metrics_container, key, value, row, col)
            col += 1
            if col >= MAX_COLS:
                col = 0
                row += 1

        # --- 4. Team / Subordinate List (if available) ---
        # Look for lists in the JSON
        list_key = None
        for k, v in data.items():
            if isinstance(v, list) and len(v) > 0:
                list_key = k
                break
        
        if list_key:
            list_frame = self.create_card(self.scrollable_frame)
            list_frame.pack(fill="x", padx=20, pady=10)
            
            tk.Label(list_frame, text=f"{list_key.title()}", bg=self.colors["card"], font=("Segoe UI", 12, "bold"), fg=self.colors["primary"]).pack(anchor="w", padx=20, pady=(15, 10))
            
            # Simple table for list items
            tree_columns = list(data[list_key][0].keys()) if isinstance(data[list_key][0], dict) else ["Value"]
            tree = ttk.Treeview(list_frame, columns=tree_columns, show="headings", height=5)
            
            for col_name in tree_columns:
                tree.heading(col_name, text=col_name.title())
                tree.column(col_name, width=100)
            
            for item in data[list_key]:
                if isinstance(item, dict):
                    values = [item.get(c, "") for c in tree_columns]
                    tree.insert("", "end", values=values)
                else:
                    tree.insert("", "end", values=[item])
            
            tree.pack(fill="x", padx=20, pady=(0, 20))

        # --- 5. Raw Data Dump (Collapsible) ---
        raw_frame = self.create_card(self.scrollable_frame)
        raw_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(raw_frame, text="Raw Database Output", bg=self.colors["card"], font=("Segoe UI", 10, "bold"), fg=self.colors["secondary"]).pack(anchor="w", padx=20, pady=(10, 5))
        
        raw_text = tk.Text(raw_frame, height=5, width=80, font=("Consolas", 9), relief="flat", bg="#f8f9fa")
        raw_text.insert("1.0", json.dumps(data, indent=2))
        raw_text.config(state="disabled")
        raw_text.pack(padx=20, pady=(0, 20), fill="x")

    def create_card(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame")
        # Add a subtle shadow or border effect simply by nesting or using padding
        return frame

    def create_metric_card(self, parent, title, value, row, col):
        card = tk.Frame(parent, bg="white", padx=15, pady=15)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title.replace("_", " ").upper(), bg="white", fg="#5f6368", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        
        # Value Display
        val_display = str(value)
        if isinstance(value, float):
            val_display = f"{value:.1f}"
        
        tk.Label(card, text=val_display, bg="white", fg="#202124", font=("Segoe UI", 24)).pack(anchor="w", pady=(5, 10))

        # Visual Indicator (Progress Bar)
        # Normalize value to 0-100 if possible
        normalized = 0
        is_percentage = False
        
        if isinstance(value, (int, float)):
            if value <= 1.0 and value > 0: # Likely 0.85 format
                normalized = value * 100
                is_percentage = True
            elif value <= 100 and value >= 0: # Likely 85 format
                normalized = value
                is_percentage = True
        
        if is_percentage:
            style_color = "Green.Horizontal.TProgressbar"
            if normalized < 50: style_color = "Red.Horizontal.TProgressbar"
            elif normalized < 75: style_color = "Yellow.Horizontal.TProgressbar"
            
            pb = ttk.Progressbar(card, orient="horizontal", length=100, mode="determinate", style=style_color)
            pb['value'] = normalized
            pb.pack(fill="x")
            
            # Suffix
            suffix = "%" if normalized > 1 else "" 
            tk.Label(card, text=f"Target: 100{suffix}", bg="white", fg="#aaa", font=("Segoe UI", 8)).pack(anchor="e", pady=(5,0))

    def extract_metrics(self, data):
        """Recursively find numeric values to display as metrics."""
        metrics = {}
        ignore_keys = ["id", "uid", "phone", "zip", "year"]
        
        for k, v in data.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if k.lower() not in ignore_keys:
                    metrics[k] = v
            elif isinstance(v, dict):
                # Flatten nested dicts slightly
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, (int, float)):
                         metrics[f"{k} {sub_k}"] = sub_v
        return metrics

    def generate_interpretation(self, data):
        """Generates a text summary of the data."""
        lines = []
        metrics = self.extract_metrics(data)
        
        # Sort metrics to find highs and lows
        highs = []
        lows = []
        
        for k, v in metrics.items():
            # Basic normalization logic
            score = v
            if v <= 1: score = v * 100
            
            if score > 80: highs.append(k)
            if score < 60: lows.append(k)
            
        if highs:
            lines.append(f"✓ Strengths: The supervisor is performing exceptionally well in {', '.join(highs)}.")
        if lows:
            lines.append(f"⚠ Attention Needed: Immediate improvement plans are recommended for {', '.join(lows)}.")
            
        if not lines:
            lines.append("Data loaded successfully. Review the detailed metrics below.")
            
        return "\n".join(lines)

if __name__ == "__main__":
    root = tk.Tk()
    app = SupervisorApp(root)
    root.mainloop()
