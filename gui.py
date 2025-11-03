"""
Library Management System GUI
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from lib import Library, DatabaseConnection
import mysql.connector

class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mary Matha Digital Library Management System")
        self.root.geometry("800x600")
        
        # Setup database connection
        self.db = DatabaseConnection()
        if not self.db.connect():
            messagebox.showerror("Error", "Failed to connect to database!")
            self.root.destroy()
            return
        
        # Initialize library
        self.library = Library(self.db)
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.create_books_tab()
        self.create_user_tab()
        self.create_reports_tab()
        
        # Add exit button
        exit_btn = ttk.Button(root, text="Exit", command=self.on_closing)
        exit_btn.pack(pady=5)
        
        # Bind closing event
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_books_tab(self):
        books_frame = ttk.Frame(self.notebook)
        self.notebook.add(books_frame, text="Books Management")
        
        # Search section
        search_frame = ttk.LabelFrame(books_frame, text="Search Books")
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_books).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Show All", command=self.show_all_books).pack(side='left', padx=5)
        
        # Books list
        list_frame = ttk.LabelFrame(books_frame, text="Books List")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for books
        columns = ('title', 'author', 'category', 'available', 'total')
        self.books_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        self.books_tree.heading('title', text='Title')
        self.books_tree.heading('author', text='Author')
        self.books_tree.heading('category', text='Category')
        self.books_tree.heading('available', text='Available')
        self.books_tree.heading('total', text='Total')
        
        # Define columns
        self.books_tree.column('title', width=200)
        self.books_tree.column('author', width=150)
        self.books_tree.column('category', width=100)
        self.books_tree.column('available', width=70)
        self.books_tree.column('total', width=70)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.books_tree.yview)
        self.books_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.books_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        buttons_frame = ttk.Frame(books_frame)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Borrow Book", command=self.borrow_book).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Return Book", command=self.return_book).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Renew Book", command=self.renew_book).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Donate Book", command=self.donate_book).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Add New Book", command=self.add_new_book).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Edit Book", command=self.edit_book).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Remove Book", command=self.remove_book).pack(side='left', padx=5)

    def create_user_tab(self):
        user_frame = ttk.Frame(self.notebook)
        self.notebook.add(user_frame, text="User Management")
        
        # Search section
        search_frame = ttk.LabelFrame(user_frame, text="Search Users")
        search_frame.pack(fill='x', padx=5, pady=5)
        
        # Search bar
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.user_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.user_search_var)
        search_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Bind the entry to search on key release (real-time search without popups)
        search_entry.bind('<KeyRelease>', self.search_users_realtime)
        
        # Search and Show All buttons
        ttk.Button(search_frame, text="Search", command=lambda: self.search_users(None, show_popup=True)).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Show All", command=self.refresh_users).pack(side='left', padx=5)
        
        # User registration section
        reg_frame = ttk.LabelFrame(user_frame, text="User Registration")
        reg_frame.pack(fill='x', padx=5, pady=5)
        
        # Registration fields
        fields_frame = ttk.Frame(reg_frame)
        fields_frame.pack(fill='x', padx=5, pady=5)
        
        labels = ['Username:', 'Full Name:', 'Class:', 'Section:']
        self.reg_vars = {}
        
        for i, label in enumerate(labels):
            ttk.Label(fields_frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky='e')
            self.reg_vars[label] = tk.StringVar()
            ttk.Entry(fields_frame, textvariable=self.reg_vars[label]).grid(row=i, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Button(reg_frame, text="Register User", command=self.register_user).pack(pady=5)
        
        # User list section
        list_frame = ttk.LabelFrame(user_frame, text="Registered Users")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for users
        columns = ('username', 'full_name', 'class', 'section', 'status')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        self.users_tree.heading('username', text='Username')
        self.users_tree.heading('full_name', text='Full Name')
        self.users_tree.heading('class', text='Class')
        self.users_tree.heading('section', text='Section')
        self.users_tree.heading('status', text='Status')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.users_tree.yview)
        self.users_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.users_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Button frame
        button_frame = ttk.Frame(user_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Refresh Users List", 
                  command=self.refresh_users).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Remove User", 
                  command=self.remove_user).pack(side='left', padx=5)

    def create_reports_tab(self):
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Reports text area
        self.reports_text = scrolledtext.ScrolledText(reports_frame, wrap=tk.WORD, height=20)
        self.reports_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(reports_frame)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Library Statistics", command=self.show_statistics).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Top Rated Books", command=self.show_top_rated).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Overdue Books", command=self.show_overdue).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Current Borrows", command=self.show_borrowed).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Borrow History", command=self.show_borrow_logs).pack(side='left', padx=5)

    # Functionality methods
    def search_books(self):
        search_term = self.search_var.get()
        # Clear current items
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        try:
            books = self.library.searchBooks(search_term)
            for book in books:
                self.books_tree.insert('', 'end', values=(
                    book['title'],
                    book['author'],
                    book['category'],
                    book['available'],
                    book['total']
                ))
                
            if not books:
                messagebox.showinfo("Search Results", "No books found matching your search.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_all_books(self):
        # Clear current items
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
            
        try:
            books = self.library.displayAvailableBooks()
            for book in books:
                self.books_tree.insert('', 'end', values=(
                    book['title'],
                    book['author'],
                    book['category'],
                    book['available'],
                    book['total']
                ))
                
            if not books:
                messagebox.showinfo("Books", "No books available in the library.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def borrow_book(self):
        # Create dialog for borrowing
        dialog = tk.Toplevel(self.root)
        dialog.title("Borrow Book")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="📚 Borrow a Book", 
                 font=('Helvetica', 12, 'bold')).pack(pady=(0,20))
        
        # Input fields frame
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=5)
        
        # Username
        username_frame = ttk.Frame(fields_frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="Username:*", width=15).pack(side=tk.LEFT)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=username_var, width=30)
        username_entry.pack(side=tk.LEFT)
        
        # Book Title
        book_frame = ttk.Frame(fields_frame)
        book_frame.pack(fill=tk.X, pady=5)
        ttk.Label(book_frame, text="Book Title:*", width=15).pack(side=tk.LEFT)
        book_var = tk.StringVar()
        book_entry = ttk.Entry(book_frame, textvariable=book_var, width=30)
        book_entry.pack(side=tk.LEFT)
        
        # Required fields note
        ttk.Label(main_frame, text="* Required fields", 
                 font=('Helvetica', 8)).pack(pady=(10,0), anchor=tk.W)
        
        def submit():
            username = username_var.get().strip()
            book_title = book_var.get().strip()
            
            if not username or not book_title:
                messagebox.showerror("Error", "Both username and book title are required!")
                return
            
            try:
                result = self.library.borrowBook(username, book_title)
                if result['success']:
                    message = (
                        f"✅ BOOK ISSUED SUCCESSFULLY!\n\n"
                        f"📚 Book: {result['book']}\n"
                        f"👤 Borrower: {result['borrower']}\n"
                        f"📅 Due Date: {result['due_date']}\n\n"
                        f"⚠️  Please return the book on time to avoid fines."
                    )
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                    self.show_all_books()  # Refresh the books list
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="OK", command=submit, 
                  width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", 
                  command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def return_book(self):
        # Create dialog for returning
        dialog = tk.Toplevel(self.root)
        dialog.title("Return Book")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="📚 Return a Book", 
                 font=('Helvetica', 12, 'bold')).pack(pady=(0,20))
        
        # Input fields frame
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=5)
        
        # Username
        username_frame = ttk.Frame(fields_frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="Username:*", width=15).pack(side=tk.LEFT)
        username_var = tk.StringVar()
        ttk.Entry(username_frame, textvariable=username_var, width=30).pack(side=tk.LEFT)
        
        # Book Title
        book_frame = ttk.Frame(fields_frame)
        book_frame.pack(fill=tk.X, pady=5)
        ttk.Label(book_frame, text="Book Title:*", width=15).pack(side=tk.LEFT)
        book_var = tk.StringVar()
        ttk.Entry(book_frame, textvariable=book_var, width=30).pack(side=tk.LEFT)
        
        # Required fields note
        ttk.Label(main_frame, text="* Required fields", 
                 font=('Helvetica', 8)).pack(pady=(10,0), anchor=tk.W)
        
        def submit():
            username = username_var.get().strip()
            book_title = book_var.get().strip()
            
            if not username or not book_title:
                messagebox.showerror("Error", "Both username and book title are required!")
                return
            
            try:
                result = self.library.returnBook(username, book_title)
                if result['success']:
                    message = f"✅ BOOK RETURNED SUCCESSFULLY!\n\n"
                    message += f"📚 Book: {result['book']}\n"
                    message += f"👤 Returned by: {result['returner']}\n"
                    message += f"📅 Return Date: {result['return_date']}\n\n"
                    
                    if result['fine_amount'] > 0:
                        message += f"⚠️  OVERDUE: {result['days_overdue']} days late\n"
                        message += f"💰 Fine Amount: ₹{result['fine_amount']:.2f}"
                    else:
                        message += "✅ Returned on time - No fine!"
                    
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                    self.show_all_books()  # Refresh the books list
                    
                    # Ask for review
                    if messagebox.askyesno("Book Review", 
                                         "Would you like to rate and review this book?"):
                        self.submit_review(username, book_title)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="OK", command=submit, 
                  width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", 
                  command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def renew_book(self):
        # Create dialog for renewing
        dialog = tk.Toplevel(self.root)
        dialog.title("Renew Book")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="📚 Renew a Book", 
                 font=('Helvetica', 12, 'bold')).pack(pady=(0,20))
        
        # Input fields frame
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=5)
        
        # Username
        username_frame = ttk.Frame(fields_frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="Username:*", width=15).pack(side=tk.LEFT)
        username_var = tk.StringVar()
        ttk.Entry(username_frame, textvariable=username_var, width=30).pack(side=tk.LEFT)
        
        # Book Title
        book_frame = ttk.Frame(fields_frame)
        book_frame.pack(fill=tk.X, pady=5)
        ttk.Label(book_frame, text="Book Title:*", width=15).pack(side=tk.LEFT)
        book_var = tk.StringVar()
        ttk.Entry(book_frame, textvariable=book_var, width=30).pack(side=tk.LEFT)
        
        # Required fields note
        ttk.Label(main_frame, text="* Required fields", 
                 font=('Helvetica', 8)).pack(pady=(10,0), anchor=tk.W)
        
        def submit():
            username = username_var.get().strip()
            book_title = book_var.get().strip()
            
            if not username or not book_title:
                messagebox.showerror("Error", "Both username and book title are required!")
                return
            
            try:
                self.library.renewBook(username, book_title)
                messagebox.showinfo("Success", f"Book '{book_title}' has been successfully renewed for 7 more days!")
                dialog.destroy()
                self.show_all_books()  # Refresh the books list
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="OK", command=submit, 
                  width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", 
                  command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def add_new_book(self):
        # Create dialog for adding new book
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Book (Librarian)")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title frame
        ttk.Label(main_frame, text="➕ Add New Book", 
                 font=('Helvetica', 12, 'bold')).pack(pady=(0,20))
        
        # Input fields frame
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=5)
        
        # Book Title
        title_frame = ttk.Frame(fields_frame)
        title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(title_frame, text="Book Title:*", width=15).pack(side=tk.LEFT)
        title_var = tk.StringVar()
        ttk.Entry(title_frame, textvariable=title_var, width=30).pack(side=tk.LEFT)
        
        # Author
        author_frame = ttk.Frame(fields_frame)
        author_frame.pack(fill=tk.X, pady=5)
        ttk.Label(author_frame, text="Author:*", width=15).pack(side=tk.LEFT)
        author_var = tk.StringVar()
        ttk.Entry(author_frame, textvariable=author_var, width=30).pack(side=tk.LEFT)
        
        # Category
        category_frame = ttk.Frame(fields_frame)
        category_frame.pack(fill=tk.X, pady=5)
        ttk.Label(category_frame, text="Category:*", width=15).pack(side=tk.LEFT)
        category_var = tk.StringVar(value="General")
        categories = ["Fiction", "Non-Fiction", "Science", "Technology", 
                     "Literature", "Economics", "Education", "General"]
        category_combo = ttk.Combobox(category_frame, textvariable=category_var, 
                                    values=categories, width=27, state="readonly")
        category_combo.pack(side=tk.LEFT)
        
        # Number of Copies
        copies_frame = ttk.Frame(fields_frame)
        copies_frame.pack(fill=tk.X, pady=5)
        ttk.Label(copies_frame, text="Copies:", width=15).pack(side=tk.LEFT)
        copies_var = tk.StringVar(value="1")
        ttk.Spinbox(copies_frame, from_=1, to=100, textvariable=copies_var, 
                   width=5).pack(side=tk.LEFT)
        
        # Required fields note
        ttk.Label(main_frame, text="* Required fields", 
                 font=('Helvetica', 8)).pack(pady=(10,0), anchor=tk.W)
        
        def submit():
            title = title_var.get().strip()
            author = author_var.get().strip()
            category = category_var.get()
            
            try:
                copies = int(copies_var.get())
                if copies < 1:
                    raise ValueError("Number of copies must be at least 1")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            
            if not title or not author:
                messagebox.showerror("Error", "Book title and author are required!")
                return
            
            try:
                self.library.addNewBook(title, author, category, copies)
                messagebox.showinfo("Success", f"Successfully added {copies} copies of '{title}' to the library!")
                dialog.destroy()
                self.show_all_books()  # Refresh the books list
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Add Book", command=submit, 
                  width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", 
                  command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Center the dialog on screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def donate_book(self):
        # Create dialog for donation
        dialog = tk.Toplevel(self.root)
        dialog.title("Donate Book")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        
        # Make dialog modal (user must interact with it before using main window)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title frame
        ttk.Label(main_frame, text="📚 Donate a Book", font=('Helvetica', 12, 'bold')).pack(pady=(0,20))
        
        # Input fields frame
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=5)
        
        # Book Title
        title_frame = ttk.Frame(fields_frame)
        title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(title_frame, text="Book Title:*", width=15).pack(side=tk.LEFT)
        title_var = tk.StringVar()
        ttk.Entry(title_frame, textvariable=title_var, width=30).pack(side=tk.LEFT)
        
        # Author
        author_frame = ttk.Frame(fields_frame)
        author_frame.pack(fill=tk.X, pady=5)
        ttk.Label(author_frame, text="Author:", width=15).pack(side=tk.LEFT)
        author_var = tk.StringVar()
        ttk.Entry(author_frame, textvariable=author_var, width=30).pack(side=tk.LEFT)
        
        # Category
        category_frame = ttk.Frame(fields_frame)
        category_frame.pack(fill=tk.X, pady=5)
        ttk.Label(category_frame, text="Category:", width=15).pack(side=tk.LEFT)
        category_var = tk.StringVar(value="General")
        categories = ["Fiction", "Non-Fiction", "Science", "Technology", 
                     "Literature", "Economics", "Education", "General"]
        category_combo = ttk.Combobox(category_frame, textvariable=category_var, 
                                    values=categories, width=27, state="readonly")
        category_combo.pack(side=tk.LEFT)
        
        # Required fields note
        ttk.Label(main_frame, text="* Required field", 
                 font=('Helvetica', 8)).pack(pady=(10,0), anchor=tk.W)
        
        def submit():
            title = title_var.get().strip()
            author = author_var.get().strip()
            category = category_var.get()
            
            if not title:
                messagebox.showerror("Error", "Book title is required!")
                return
            
            try:
                self.library.addNewBook(title, author or "Unknown", category)
                messagebox.showinfo("Success", f"Book '{title}' has been successfully donated!, thank you for your contribution.")
                dialog.destroy()
                self.show_all_books()  # Refresh the books list
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="OK", command=submit, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", 
                  command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Center the dialog on screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def remove_user(self):
        # Get selected user
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user to remove")
            return
            
        # Get user details
        user_values = self.users_tree.item(selected[0])['values']
        if not user_values:
            return
            
        username = user_values[0]
        
        # Create dialog for user removal
        dialog = tk.Toplevel(self.root)
        dialog.title("Remove User")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with warning icon
        ttk.Label(main_frame, text="⚠️ Remove User", 
                 font=('Helvetica', 12, 'bold')).pack(pady=(0,20))
        
        # Warning message
        warning_text = ("Warning: This action cannot be undone.\n"
                       "User must return all borrowed books before removal.")
        ttk.Label(main_frame, text=warning_text, 
                 foreground='red').pack(pady=(0,20))
        
        # User info
        user_info = f"Username: {username}\nFull Name: {user_values[1]}"
        ttk.Label(main_frame, text=user_info).pack(pady=10)
        
        def submit():
            # Ask for confirmation
            if not messagebox.askyesno("Confirm Removal", 
                                     f"Are you sure you want to remove user '{username}'?\n"
                                     "This action cannot be undone!"):
                return
            
            try:
                success, message = self.library.removeUser(username)
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                    self.refresh_users()  # Refresh the users list
                else:
                    messagebox.showerror("Error", message)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Remove", command=submit, 
                  width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", 
                  command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def register_user(self):
        try:
            username = self.reg_vars['Username:'].get().strip()
            full_name = self.reg_vars['Full Name:'].get().strip()
            class_name = self.reg_vars['Class:'].get().strip()
            section = self.reg_vars['Section:'].get().strip()
            
            success, result = self.library.registerUser(username, full_name, class_name, section)
            
            if success:
                self.refresh_users()
                messagebox.showinfo("Success", 
                    f"✅ User '{result['username']}' registered successfully!\n\n"
                    f"👤 Full Name: {result['full_name']}\n"
                    f"📚 Class: {result['class']}\n"
                    f"📝 Section: {result['section']}\n\n"
                    f"🎉 User can now borrow books from the library!")
                
                # Clear fields
                for var in self.reg_vars.values():
                    var.set('')
            else:
                messagebox.showerror("Error", result)
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_users_realtime(self, event=None):
        """Real-time search for users without popup messages"""
        search_term = self.user_search_var.get().strip()
        
        # Clear current items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            if search_term:
                users = self.library.searchUsers(search_term)
            else:
                users = self.library.listAllUsers()
                
            for user in users:
                self.users_tree.insert('', 'end', values=(
                    user['username'],
                    user['full_name'],
                    user['class'],
                    user['section'],
                    user['status']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_users(self, event=None, show_popup=False):
        """Search for users based on search bar input with optional popup"""
        search_term = self.user_search_var.get().strip()
        
        # Clear current items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            if search_term:
                users = self.library.searchUsers(search_term)
            else:
                users = self.library.listAllUsers()
                
            for user in users:
                self.users_tree.insert('', 'end', values=(
                    user['username'],
                    user['full_name'],
                    user['class'],
                    user['section'],
                    user['status']
                ))
                
            # Only show popup when explicitly requested (via Search button)
            if show_popup and not users:
                if search_term:
                    messagebox.showinfo("Search Results", "No users found matching your search.")
                else:
                    messagebox.showinfo("Users", "No users registered in the system.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_users(self):
        # Clear current items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            users = self.library.listAllUsers()
            for user in users:
                self.users_tree.insert('', 'end', values=(
                    user['username'],
                    user['full_name'],
                    user['class'],
                    user['section'],
                    user['status']
                ))
                
            if not users:
                messagebox.showinfo("Users", "No users registered in the system.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def submit_review(self, username, book_title):
        """Open dialog for submitting book review"""
        review_dialog = tk.Toplevel(self.root)
        review_dialog.title("Book Review")
        review_dialog.geometry("400x400")
        review_dialog.resizable(False, False)
        review_dialog.transient(self.root)
        review_dialog.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(review_dialog, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="⭐ Rate and Review Book", 
                 font=('Helvetica', 12, 'bold')).pack(pady=(0,20))
        
        # Book info
        ttk.Label(main_frame, text=f"Book: {book_title}").pack(pady=5)
        
        # Rating
        rating_frame = ttk.Frame(main_frame)
        rating_frame.pack(pady=10)
        ttk.Label(rating_frame, text="Rating (1-5 stars):").pack(side=tk.LEFT, padx=5)
        rating_var = tk.StringVar(value="5")
        rating_combo = ttk.Combobox(rating_frame, textvariable=rating_var, 
                                  values=["1", "2", "3", "4", "5"], width=5)
        rating_combo.pack(side=tk.LEFT)
        
        # Review text
        ttk.Label(main_frame, text="Write your review (optional):").pack(pady=(10,5))
        review_text = tk.Text(main_frame, height=5, width=40)
        review_text.pack(pady=5)
        
        def submit():
            try:
                rating = int(rating_var.get())
                review = review_text.get("1.0", tk.END).strip()
                if not review:
                    review = None
                    
                result = self.library.add_book_review(username, book_title, rating, review)
                if result is True:
                    messagebox.showinfo("Success", "Thank you for your review!")
                    review_dialog.destroy()
                else:
                    messagebox.showerror("Error", str(result))
            except ValueError:
                messagebox.showerror("Error", "Please select a valid rating (1-5)")
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        ttk.Button(buttons_frame, text="Submit Review", command=submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", 
                  command=review_dialog.destroy).pack(side=tk.LEFT, padx=5)

    def show_top_rated(self):
        """Display top rated books in the reports area"""
        try:
            self.reports_text.delete(1.0, tk.END)
            top_books = self.library.get_top_rated_books(5)
            
            self.reports_text.insert(tk.END, "⭐ TOP RATED BOOKS ⭐\n")
            self.reports_text.insert(tk.END, "=" * 60 + "\n\n")
            
            if top_books:
                for book in top_books:
                    title, author, category, avg_rating, num_reviews = book
                    rating_str = f"{avg_rating:.1f}/5.0" if avg_rating else "No rating"
                    self.reports_text.insert(tk.END, f"📚 Book:{title}\n")
                    self.reports_text.insert(tk.END, f"   Author: {author}\n")
                    self.reports_text.insert(tk.END, f"   Category: {category}\n")
                    self.reports_text.insert(tk.END, f"   Rating: {rating_str} ({num_reviews} reviews)\n")
                    
                    # Get detailed reviews
                    reviews = self.library.get_book_reviews(title)
                    if reviews:
                        self.reports_text.insert(tk.END, "\n   Recent Reviews:\n")
                        for review in reviews[:3]:  # Show only 3 most recent reviews
                            username, rating, review_text, review_date = review
                            self.reports_text.insert(tk.END, f"   • {username} - {rating}⭐\n")
                            if review_text:
                                self.reports_text.insert(tk.END, f"     \"{review_text}\"\n")
                    self.reports_text.insert(tk.END, "\n" + "-"*50 + "\n\n")
            else:
                self.reports_text.insert(tk.END, "No book ratings yet.\n")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_statistics(self):
        try:
            self.reports_text.delete(1.0, tk.END)
            report_data = self.library.generateReports()
            
            # Format and display the report
            self.reports_text.insert(tk.END, "📊 LIBRARY STATISTICS REPORT\n")
            self.reports_text.insert(tk.END, "=" * 60 + "\n\n")
            
            # Summary
            summary = report_data['summary']
            self.reports_text.insert(tk.END, f"📚 Total Unique Books: {summary['unique_books']}\n")
            self.reports_text.insert(tk.END, f"📖 Total Book Copies: {summary['total_copies']}\n")
            self.reports_text.insert(tk.END, f"✅ Available Copies: {summary['available_copies']}\n")
            self.reports_text.insert(tk.END, f"📋 Borrowed Copies: {summary['borrowed_copies']}\n\n")
            
            # Popular books
            if report_data['popular_books']:
                self.reports_text.insert(tk.END, "🏆 TOP 5 MOST BORROWED BOOKS:\n")
                for i, book in enumerate(report_data['popular_books'], 1):
                    self.reports_text.insert(tk.END, f"{i}. {book['title']} ({book['count']} times)\n")
                self.reports_text.insert(tk.END, "\n")
            
            # Active borrowers
            if report_data['active_borrowers']:
                self.reports_text.insert(tk.END, "👥 ACTIVE BORROWERS:\n")
                for borrower in report_data['active_borrowers']:
                    self.reports_text.insert(tk.END, f"• {borrower['name']}: {borrower['books']} book(s)\n")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_overdue(self):
        try:
            self.reports_text.delete(1.0, tk.END)
            data = self.library.getOverdueBooks()
            
            if not data['books']:
                self.reports_text.insert(tk.END, "✅ NO OVERDUE BOOKS!\n")
                return
            
            self.reports_text.insert(tk.END, f"⚠️  {len(data['books'])} OVERDUE BOOKS:\n")
            self.reports_text.insert(tk.END, "-" * 100 + "\n")
            self.reports_text.insert(tk.END, f"{'Student':<20} {'Book Title':<25} {'Due Date':<12} {'Days Late':<10} {'Fine':<10}\n")
            self.reports_text.insert(tk.END, "-" * 100 + "\n")
            
            for book in data['books']:
                fine_str = f"₹{book['fine']:.2f}"
                self.reports_text.insert(tk.END, 
                    f"{book['student']:<20} {book['book']:<25} {book['due_date']:<12} "
                    f"{book['days_overdue']:<10} {fine_str:<10}\n"
                )
            
            self.reports_text.insert(tk.END, "-" * 100 + "\n")
            self.reports_text.insert(tk.END, f"Total Outstanding Fines: ₹{data['total_fine']:.2f}\n")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_borrowed(self):
        try:
            self.reports_text.delete(1.0, tk.END)
            books = self.library.trackBooks()
            
            if not books:
                self.reports_text.insert(tk.END, "✅ NO BOOKS ARE CURRENTLY ISSUED!\n")
                return
            
            self.reports_text.insert(tk.END, f"📊 {len(books)} BOOKS ARE CURRENTLY BORROWED:\n")
            self.reports_text.insert(tk.END, "-" * 90 + "\n")
            self.reports_text.insert(tk.END, f"{'Student':<20} {'Book Title':<25} {'Borrowed Date':<15} {'Due Date':<12} {'Status':<15}\n")
            self.reports_text.insert(tk.END, "-" * 90 + "\n")
            
            for book in books:
                self.reports_text.insert(tk.END,
                    f"{book['student']:<20} {book['book']:<25} {book['borrowed_date']:<15} "
                    f"{book['due_date']:<12} {book['status']:<15}\n"
                )
            
            self.reports_text.insert(tk.END, "-" * 90 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def edit_book(self):
        # Get selected book
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to edit")
            return
        
        # Get book details
        book_values = self.books_tree.item(selected[0])['values']
        if not book_values:
            return
        
        # Create dialog for editing
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Book")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="📚 Edit Book Details", 
                 font=('Helvetica', 12, 'bold')).pack(pady=(0,20))
        
        # Input fields frame
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=5)
        
        # Book details
        details = {
            'Title': book_values[0],
            'Author': book_values[1],
            'Category': book_values[2],
            'Total Copies': book_values[4]
        }
        
        variables = {}
        for label, value in details.items():
            frame = ttk.Frame(fields_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{label}:*", width=15).pack(side=tk.LEFT)
            var = tk.StringVar(value=value)
            variables[label] = var
            ttk.Entry(frame, textvariable=var, width=30).pack(side=tk.LEFT)
        
        def submit():
            try:
                # Validate input
                new_title = variables['Title'].get().strip()
                new_author = variables['Author'].get().strip()
                new_category = variables['Category'].get().strip()
                try:
                    new_total = int(variables['Total Copies'].get())
                    if new_total < 1:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Total copies must be a positive number")
                    return
                
                if not all([new_title, new_author, new_category]):
                    messagebox.showerror("Error", "All fields are required")
                    return
                
                # Update book
                success, message = self.library.editBook(
                    book_values[0], new_title, new_author, 
                    new_category, new_total
                )
                
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                    self.show_all_books()  # Refresh book list
                else:
                    messagebox.showerror("Error", message)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update book: {str(e)}")
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        ttk.Button(buttons_frame, text="Update", command=submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def remove_book(self):
        # Get selected book
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to remove")
            return
        
        # Get book details
        book_values = self.books_tree.item(selected[0])['values']
        if not book_values:
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Remove", 
            f"Are you sure you want to remove '{book_values[0]}' from the library?"):
            return
        
        try:
            success, message = self.library.removeBook(book_values[0])
            if success:
                messagebox.showinfo("Success", message)
                self.show_all_books()  # Refresh book list
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove book: {str(e)}")

    def show_borrow_logs(self):
        try:
            self.reports_text.delete(1.0, tk.END)
            result = self.library.getBorrowLogs()
            logs = result['logs']
            total_fines = result['total_fines']
            
            if not logs:
                self.reports_text.insert(tk.END, "✅ NO BORROWING HISTORY FOUND!\n")
                return
            
            self.reports_text.insert(tk.END, "📚 COMPLETE BORROWING HISTORY:\n")
            self.reports_text.insert(tk.END, "-" * 110 + "\n")
            self.reports_text.insert(tk.END,
                f"{'Student':<20} {'Book Title':<25} {'Borrowed':<20} {'Due':<12} "
                f"{'Status':<12} {'Returned':<20} {'Fine':<8}\n"
            )
            self.reports_text.insert(tk.END, "-" * 110 + "\n")
            
            for log in logs:
                self.reports_text.insert(tk.END,
                    f"{log['student']:<20} {log['book']:<25} {log['borrowed_date']:<20} "
                    f"{log['due_date']:<12} {log['status']:<12} {log['return_date']:<20} "
                    f"₹{log['fine']:<7.2f}\n"
                )
            
            self.reports_text.insert(tk.END, "-" * 110 + "\n")
            self.reports_text.insert(tk.END, f"\n💰 Total Fines Accrued: ₹{total_fines:.2f}\n")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.db.close_connection()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()