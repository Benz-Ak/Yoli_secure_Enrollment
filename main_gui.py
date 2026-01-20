import customtkinter as ctk
from tkinter import messagebox, ttk

class YoliSecureApp(ctk.CTk):
    def __init__(self, cipher_tool, db_controller, backup_manager):
        super().__init__()

        self.cipher = cipher_tool
        self.db = db_controller
        self.backup = backup_manager

        # Window Configuration
        self.title("YOLI SECURE ENROLLMENT - ADMINISTRATION")
        self.geometry("1100x650")
        ctk.set_appearance_mode("dark")
        
        # Grid Layout (Sidebar + Main)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- TABLE STYLE (TREEVIEW) ---
        self.setup_table_style()

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="🛡️ YOLI SECURE", font=("Impact", 24)).pack(pady=30)
        
        ctk.CTkButton(self.sidebar, text="Enrollment", command=self.show_enrollment).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Database", command=self.show_database).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Maintenance", command=self.show_backup).pack(pady=10, padx=20)

        # Main Container
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.show_enrollment()

    def setup_table_style(self):
        """Configures the table style to increase row height."""
        style = ttk.Style()
        style.theme_use("clam") # Required to modify row height
        style.configure("Treeview", 
                        rowheight=45, # INCREASED ROW HEIGHT
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b",
                        bordercolor="#333333",
                        borderwidth=0,
                        font=("Arial", 11))
        style.configure("Treeview.Heading", 
                        background="#333333", 
                        foreground="white", 
                        font=("Arial", 12, "bold"),
                        rowheight=40)
        style.map("Treeview", background=[('selected', '#1f538d')]) # Selection Blue

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # --- VIEW 1: ENROLLMENT FORM ---
    def show_enrollment(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="New Student (Encrypted Enrollment)", font=("Arial", 22, "bold")).pack(pady=20)
        
        self.ent_name = ctk.CTkEntry(self.main_frame, placeholder_text="Full Name", width=400, height=45); self.ent_name.pack(pady=10)
        self.ent_course = ctk.CTkEntry(self.main_frame, placeholder_text="Course/Major", width=400, height=45); self.ent_course.pack(pady=10)
        self.ent_email = ctk.CTkEntry(self.main_frame, placeholder_text="Email Address", width=400, height=45); self.ent_email.pack(pady=10)
        self.ent_phone = ctk.CTkEntry(self.main_frame, placeholder_text="Phone Number", width=400, height=45); self.ent_phone.pack(pady=10)

        ctk.CTkButton(self.main_frame, text="Save with AES-GCM", fg_color="#27ae60", 
                     height=45, width=250, command=self.handle_save).pack(pady=30)

    def handle_save(self):
        # Using improved logic from DBController
        res = self.db.save_student(self.ent_name.get(), self.ent_course.get(), self.ent_email.get(), self.ent_phone.get())
        if res == "DUPLICATE":
            messagebox.showwarning("Duplicate", "This email is already used by another student.")
        elif res is True:
            messagebox.showinfo("Success", "Data encrypted and saved successfully!")
            self.show_enrollment()
        else:
            messagebox.showerror("Error", "A technical error occurred during insertion.")

    # --- VIEW 2: DATABASE WITH ACTION BUTTONS ---
    def show_database(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Registry Management (Live Decryption)", font=("Arial", 22, "bold")).pack(pady=15)

        # Horizontal Container
        table_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        table_container.pack(expand=True, fill="both", padx=15, pady=10)

        # Table
        cols = ("Name", "Course", "Email", "Phone")
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings")
        for c in cols: 
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150)
        
        # Scrollbar
        scroll = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side="left", expand=True, fill="both")
        scroll.pack(side="right", fill="y")

        # Action Sidebar (RIGHT)
        action_bar = ctk.CTkFrame(self.main_frame, height=60)
        action_bar.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(action_bar, text="🔄 Refresh", width=120, fg_color="gray", command=self.refresh_table).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(action_bar, text="✏️ Edit", width=120, fg_color="#3498db", command=self.open_edit_window).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(action_bar, text="🗑️ Delete", width=120, fg_color="#e74c3c", command=self.handle_delete).pack(side="left", padx=10, pady=10)

        self.refresh_table()

    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        data = self.db.get_all_students()
        if data:
            for s in data:
                self.tree.insert("", "end", values=(s['full_name'], s['course'], s['email'], s['phone']))

    def handle_delete(self):
        selected = self.tree.selection()
        if not selected: return messagebox.showwarning("Warning", "Please select a row.")
        
        email = self.tree.item(selected)['values'][2]
        if messagebox.askyesno("Confirmation", f"Do you want to permanently delete student {email}?"):
            if self.db.delete_student(email):
                messagebox.showinfo("Deleted", "Data deleted successfully.")
                self.refresh_table()

    def open_edit_window(self):
        selected = self.tree.selection()
        if not selected: return messagebox.showwarning("Warning", "Select a student.")
        
        vals = self.tree.item(selected)['values']
        
        # Pop-up Window
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Secure Modification")
        edit_win.geometry("400x450")
        edit_win.attributes("-topmost", True)

        ctk.CTkLabel(edit_win, text="Update Information", font=("Arial", 18, "bold")).pack(pady=20)
        en_name = ctk.CTkEntry(edit_win, width=300, height=40); en_name.insert(0, vals[0]); en_name.pack(pady=5)
        en_course = ctk.CTkEntry(edit_win, width=300, height=40); en_course.insert(0, vals[1]); en_course.pack(pady=5)
        en_phone = ctk.CTkEntry(edit_win, width=300, height=40); en_phone.insert(0, vals[3]); en_phone.pack(pady=5)

        def save_changes():
            if self.db.update_student(vals[2], en_name.get(), en_course.get(), en_phone.get()):
                messagebox.showinfo("Success", "Data re-encrypted and updated successfully!")
                edit_win.destroy()
                self.refresh_table()

        ctk.CTkButton(edit_win, text="Save Changes", height=40, command=save_changes).pack(pady=25)

    # --- VIEW 3: MAINTENANCE ---
    def show_backup(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Maintenance & Security", font=("Arial", 22, "bold")).pack(pady=30)
        
        ctk.CTkButton(self.main_frame, text="💾 Generate Encrypted Backup (.enc)", width=300, height=50,
                     command=lambda: [self.backup.create_encrypted_backup(), messagebox.showinfo("Backup", "Backup created successfully!")]).pack(pady=10)
        
        ctk.CTkButton(self.main_frame, text="🔍 Test Backup Integrity", fg_color="orange", width=300, height=50,
                     command=lambda: self.backup.restore_from_file("students_backup.enc", self.cipher)).pack(pady=10)