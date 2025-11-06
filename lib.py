"""
Project: Student library management system
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import sys


class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self, host='localhost', database='library_management', user='root', password=''):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                autocommit=True,  # Enable autocommit by default
                use_pure=True,    # Use pure Python implementation
                buffered=True     # Use buffered cursors
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(buffered=True)
                print("Successfully connected to MySQL database")
                self.create_tables()
                return True
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Create books table
            books_table = """
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL UNIQUE,
                available BOOLEAN DEFAULT TRUE,
                total_copies INT DEFAULT 1,
                available_copies INT DEFAULT 1,
                category VARCHAR(100) DEFAULT 'General',
                author VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Create book categories table
            categories_table = """
            CREATE TABLE IF NOT EXISTS book_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT
            )
            """
            
            # Create users table for user management
            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                full_name VARCHAR(255) NOT NULL,
                class VARCHAR(50),
                section CHAR(1),
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('active', 'suspended', 'inactive') DEFAULT 'active'
            )
            """

            # Create borrowed_books table with due dates and ON DELETE CASCADE
            borrowed_table = """
            CREATE TABLE IF NOT EXISTS borrowed_books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(255) NOT NULL,
                book_title VARCHAR(255) NOT NULL,
                borrowed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date DATE NOT NULL,
                returned BOOLEAN DEFAULT FALSE,
                return_date TIMESTAMP NULL,
                fine_amount DECIMAL(10,2) DEFAULT 0.00,
                FOREIGN KEY (book_title) REFERENCES books(title) ON DELETE CASCADE,
                FOREIGN KEY (student_name) REFERENCES users(username) ON UPDATE CASCADE
            )
            """

            # Create book reviews table with proper foreign keys
            reviews_table = """
            CREATE TABLE IF NOT EXISTS book_reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_title VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL,
                rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review_text TEXT,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_title) REFERENCES books(title) ON DELETE CASCADE,
                FOREIGN KEY (username) REFERENCES users(username) ON UPDATE CASCADE
            )
            """
            
            # Create tables in the correct order to avoid foreign key issues
            self.cursor.execute(books_table)
            self.cursor.execute(categories_table)
            self.cursor.execute(users_table)
            self.cursor.execute(borrowed_table)
            self.cursor.execute(reviews_table)
            self.connection.commit()
            print("Database tables created successfully")
            
            # Insert default categories
            self.insert_default_categories()
            
        except Error as e:
            print(f"Error creating tables: {e}")
    
    def insert_default_categories(self):
        """Insert default book categories"""
        try:
            categories = [
                ('Fiction', 'Novels, short stories, and fictional works'),
                ('Non-Fiction', 'Biographies, history, science, etc.'),
                ('Science', 'Scientific books and research'),
                ('Technology', 'Computer science, engineering, etc.'),
                ('Literature', 'Classic literature and poetry'),
                ('Economics', 'Economic theories and business'),
                ('Education', 'Educational and academic books'),
                ('General', 'General purpose books')
            ]
            
            for category, description in categories:
                check_query = "SELECT COUNT(*) FROM book_categories WHERE category_name = %s"
                self.cursor.execute(check_query, (category,))
                if self.cursor.fetchone()[0] == 0:
                    insert_query = "INSERT INTO book_categories (category_name, description) VALUES (%s, %s)"
                    self.cursor.execute(insert_query, (category, description))
            
            self.connection.commit()
            
        except Error as e:
            print(f"Error inserting categories: {e}")
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection is closed")


class Library:
    def __init__(self, db_connection):
        self.db = db_connection
        # self.initialize_books()

    # def initialize_books(self):
    #     """Initialize default books in database if not present"""
    #     default_books = [
    #         ("vistas", "General", "John Doe"),
    #         ("invention", "Science", "Jane Smith"),
    #         ("rich&poor", "Economics", "Robert Kiyosaki"),
    #         ("indian", "Literature", "Shashi Tharoor"),
    #         ("macroeconomics", "Economics", "N. Gregory Mankiw"),
    #         ("microeconomics", "Economics", "Hal Varian")
    #     ]
        
    #     try:
    #         for book_title, category, author in default_books:
    #             # Check if book already exists
    #             check_query = "SELECT COUNT(*) FROM books WHERE title = %s"
    #             self.db.cursor.execute(check_query, (book_title,))
    #             count = self.db.cursor.fetchone()[0]
                
    #             if count == 0:
    #                 # Insert book if it doesn't exist
    #                 insert_query = """
    #                 INSERT INTO books (title, available, total_copies, available_copies, category, author) 
    #                 VALUES (%s, %s, %s, %s, %s, %s)
    #                 """
    #                 self.db.cursor.execute(insert_query, (book_title, True, 1, 1, category, author))
            
    #         self.db.connection.commit()
    #         print("Default books initialized in database")
            
    #     except Error as e:
    #         print(f"Error initializing books: {e}")

    def displayAvailableBooks(self):
        """Display all available books from database"""
        try:
            query = """
            SELECT title, author, category, available_copies, total_copies 
            FROM books WHERE available_copies > 0
            ORDER BY category, title
            """
            self.db.cursor.execute(query)
            books = self.db.cursor.fetchall()
            
            if len(books) == 0:
                return []
            
            result = []
            for book in books:
                title, author, category, available_copies, total_copies = book
                author = author or "Unknown"
                result.append({
                    'title': title,
                    'author': author,
                    'category': category,
                    'available': available_copies,
                    'total': total_copies
                })
            return result
            
        except Error as e:
            raise Exception(f"Error displaying books: {e}")

    def searchBooks(self, search_term):
        """Search books by title, author, or category"""
        try:
            query = """
            SELECT title, author, category, available_copies, total_copies 
            FROM books 
            WHERE title LIKE %s OR author LIKE %s OR category LIKE %s
            ORDER BY available_copies DESC, title
            """
            search_pattern = f"%{search_term}%"
            self.db.cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            books = self.db.cursor.fetchall()
            
            result = []
            for book in books:
                title, author, category, available_copies, total_copies = book
                author = author or "Unknown"
                result.append({
                    'title': title,
                    'author': author,
                    'category': category,
                    'available': available_copies,
                    'total': total_copies
                })
            return result
            
        except Error as e:
            raise Exception(f"Error searching books: {e}")

    def registerUser(self, username, full_name, class_name=None, section=None):
        """Register a new user in the system"""
        try:
            if not username or not full_name:
                return False, "Username and full name are required!"

            # Check if username already exists
            check_query = "SELECT COUNT(*) FROM users WHERE username = %s"
            self.db.cursor.execute(check_query, (username,))
            
            if self.db.cursor.fetchone()[0] > 0:
                return False, f"Username '{username}' already exists. Please choose a different username."
            
            # Insert new user
            insert_query = """
            INSERT INTO users (username, full_name, class, section) 
            VALUES (%s, %s, %s, %s)
            """
            self.db.cursor.execute(insert_query, (username, full_name, class_name, section))
            self.db.connection.commit()
            
            return True, {
                'username': username,
                'full_name': full_name,
                'class': class_name or 'Not provided',
                'section': section or 'Not provided'
            }
            
        except Error as e:
            return False, f"Error registering user: {e}"

    def checkUserExists(self, username):
        """Check if a user exists in the system"""
        try:
            check_query = "SELECT username, full_name, status FROM users WHERE username = %s"
            self.db.cursor.execute(check_query, (username,))
            result = self.db.cursor.fetchone()
            
            if not result:
                return False, None
            
            username_db, full_name, status = result
            
            if status != 'active':
                print(f"❌ User account '{username}' is {status}. Please contact the librarian.\n")
                return False, None
            
            return True, {"username": username_db, "full_name": full_name, "status": status}
            
        except Error as e:
            print(f"❌ Error checking user: {e}")
            return False, None

    def searchUsers(self, search_term):
        """Search users by username, full name, class, or section"""
        try:
            query = """
            SELECT username, full_name, class, section, registration_date, status,
                   (SELECT COUNT(*) FROM borrowed_books WHERE student_name = users.username AND returned = FALSE) as active_books
            FROM users 
            WHERE username LIKE %s 
               OR full_name LIKE %s
               OR class LIKE %s
               OR section LIKE %s
            ORDER BY registration_date DESC
            """
            search_pattern = f"%{search_term}%"
            self.db.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            users = self.db.cursor.fetchall()
            
            result = []
            for user in users:
                username, full_name, class_name, section, reg_date, status, active_books = user
                result.append({
                    'username': username,
                    'full_name': full_name,
                    'class': class_name or "N/A",
                    'section': section or "N/A",
                    'status': status,
                    'active_books': active_books
                })
            return result
            
        except Error as e:
            raise Exception(f"Error searching users: {e}")

    def listAllUsers(self):
        """List all registered users (Admin function)"""
        try:
            query = """
            SELECT username, full_name, class, section, registration_date, status,
                   (SELECT COUNT(*) FROM borrowed_books WHERE student_name = users.username AND returned = FALSE) as active_books
            FROM users 
            ORDER BY registration_date DESC
            """
            self.db.cursor.execute(query)
            users = self.db.cursor.fetchall()
            
            result = []
            for user in users:
                username, full_name, class_name, section, reg_date, status, active_books = user
                result.append({
                    'username': username,
                    'full_name': full_name,
                    'class': class_name or "N/A",
                    'section': section or "N/A",
                    'status': status,
                    'active_books': active_books
                })
            return result
            
        except Error as e:
            raise Exception(f"Error listing users: {e}")

    def borrowBook(self, name, bookname):
        """Borrow a book and update database with due date"""
        try:
            # First check if user exists and is active
            user_exists, user_info = self.checkUserExists(name)
            if not user_exists:
                raise Exception(f"User '{name}' is not registered in the system.\n"
                              "Please register first using the registration option.")
            
            # Check if book exists and is available
            check_query = "SELECT title, available_copies FROM books WHERE title = %s"
            self.db.cursor.execute(check_query, (bookname,))
            result = self.db.cursor.fetchone()
            
            if not result:
                raise Exception(f"Book '{bookname}' does not exist in the library.")
            
            if result[1] <= 0:
                raise Exception(f"Book '{bookname}' is currently not available. All copies are borrowed.")
            
            # Check if user already has this book
            user_has_book_query = """
            SELECT COUNT(*) FROM borrowed_books 
            WHERE student_name = %s AND book_title = %s AND returned = FALSE
            """
            self.db.cursor.execute(user_has_book_query, (name, bookname))
            if self.db.cursor.fetchone()[0] > 0:
                raise Exception(f"You already have '{bookname}' borrowed. Please return it first.")
            
            # Check if user has reached borrowing limit (max 3 books)
            user_books_query = """
            SELECT COUNT(*) FROM borrowed_books 
            WHERE student_name = %s AND returned = FALSE
            """
            self.db.cursor.execute(user_books_query, (name,))
            current_books = self.db.cursor.fetchone()[0]
            
            if current_books >= 3:
                raise Exception("You have reached the maximum borrowing limit (3 books).\n"
                              "Please return some books first.")
            
            # Calculate due date (7 days from now)
            due_date = (datetime.now() + timedelta(days=7)).date()
            
            # Update book availability
            update_query = "UPDATE books SET available_copies = available_copies - 1 WHERE title = %s"
            self.db.cursor.execute(update_query, (bookname,))
            
            # Record the borrowing
            borrow_query = """
            INSERT INTO borrowed_books (student_name, book_title, due_date) 
            VALUES (%s, %s, %s)
            """
            self.db.cursor.execute(borrow_query, (name, bookname, due_date))
            
            self.db.connection.commit()
            
            # Return success information
            return {
                'success': True,
                'book': bookname,
                'borrower': name,
                'due_date': due_date
            }
            
        except Error as e:
            self.db.connection.rollback()
            raise Exception(f"Error borrowing book: {e}")
        except Exception as e:
            self.db.connection.rollback()
            raise e

    def returnBook(self, name, bookname):
        """Return a book and update database with fine calculation"""
        try:
            # First check if user exists and is active
            user_exists, user_info = self.checkUserExists(name)
            if not user_exists:
                raise Exception(f"User '{name}' is not registered in the system.")
            
            # Check if the book exists in the library
            book_check_query = "SELECT COUNT(*) FROM books WHERE title = %s"
            self.db.cursor.execute(book_check_query, (bookname,))
            if self.db.cursor.fetchone()[0] == 0:
                raise Exception(f"Book '{bookname}' does not exist in the library.")
            
            # Check if the book was borrowed by this person
            check_query = """
            SELECT id, due_date, borrowed_date FROM borrowed_books 
            WHERE student_name = %s AND book_title = %s AND returned = FALSE
            """
            self.db.cursor.execute(check_query, (name, bookname))
            borrow_record = self.db.cursor.fetchone()
            
            if not borrow_record:
                raise Exception(f"No record found for {name} borrowing {bookname}.\n"
                              "Please check if the book title is correct and you have borrowed it.")
            
            borrow_id, due_date, borrowed_date = borrow_record
            return_date = datetime.now()
            
            # Calculate fine if overdue
            fine_amount = 0.0
            days_overdue = 0
            
            if return_date.date() > due_date:
                days_overdue = (return_date.date() - due_date).days
                fine_amount = days_overdue * 5.0  # ₹5 per day fine
            
            # Mark book as returned with return date and fine
            return_query = """
            UPDATE borrowed_books 
            SET returned = TRUE, return_date = %s, fine_amount = %s 
            WHERE id = %s
            """
            self.db.cursor.execute(return_query, (return_date, fine_amount, borrow_id))
            
            # Update book availability
            update_query = "UPDATE books SET available_copies = available_copies + 1 WHERE title = %s"
            self.db.cursor.execute(update_query, (bookname,))
            
            self.db.connection.commit()
            
            # Return success information
            return {
                'success': True,
                'book': bookname,
                'returner': name,
                'return_date': return_date.strftime('%Y-%m-%d %H:%M'),
                'days_overdue': days_overdue,
                'fine_amount': fine_amount
            }
            
        except Error as e:
            self.db.connection.rollback()
            raise Exception(f"Error returning book: {e}")
        except Exception as e:
            self.db.connection.rollback()
            raise e

    def renewBook(self, name, bookname):
        """Renew a borrowed book (extend due date by 7 days)"""
        try:
            # First check if user exists and is active
            user_exists, user_info = self.checkUserExists(name)
            if not user_exists:
                print(f"❌ User '{name}' is not registered in the system.\n")
                return
            
            # Check if the book is borrowed by this person and not overdue
            check_query = """
            SELECT id, due_date FROM borrowed_books 
            WHERE student_name = %s AND book_title = %s AND returned = FALSE
            """
            self.db.cursor.execute(check_query, (name, bookname))
            borrow_record = self.db.cursor.fetchone()
            
            if not borrow_record:
                print(f"❌ No active borrowing record found for {name} and {bookname}\n")
                return
            
            borrow_id, current_due_date = borrow_record
            
            # Check if book is overdue
            if datetime.now().date() > current_due_date:
                print(f"❌ Cannot renew overdue book. Please return {bookname} and pay the fine first.\n")
                return
            
            # Extend due date by 7 days
            new_due_date = current_due_date + timedelta(days=7)
            
            update_query = "UPDATE borrowed_books SET due_date = %s WHERE id = %s"
            self.db.cursor.execute(update_query, (new_due_date, borrow_id))
            
            self.db.connection.commit()
            
            print("✅ BOOK RENEWED SUCCESSFULLY!")
            print(f"📚 Book: {bookname}")
            print(f"📅 New Due Date: {new_due_date}")
            print()
            
        except Error as e:
            print(f"Error renewing book: {e}")

    def donateBook(self, bookname):
        """Donate a new book to the library"""
        try:
            # Check if book already exists
            check_query = "SELECT COUNT(*) FROM books WHERE title = %s"
            self.db.cursor.execute(check_query, (bookname,))
            count = self.db.cursor.fetchone()[0]
            
            if count > 0:
                print(f"{bookname} already exists in the library!\n")
                return
            
            # Add new book
            insert_query = "INSERT INTO books (title, available) VALUES (%s, %s)"
            self.db.cursor.execute(insert_query, (bookname, True))
            
            self.db.connection.commit()
            print("BOOK DONATED : THANK YOU VERY MUCH, HAVE A GREAT DAY AHEAD.\n")
            
        except Error as e:
            print(f"Error donating book: {e}")

    def getBorrowLogs(self):
        """Get complete history of all book borrowings"""
        try:
            query = """
            SELECT student_name, book_title, borrowed_date, due_date, returned, return_date, fine_amount,
                   DATEDIFF(CURDATE(), due_date) as days_overdue
            FROM borrowed_books 
            ORDER BY borrowed_date DESC
            """
            self.db.cursor.execute(query)
            logs = self.db.cursor.fetchall()
            
            result = []
            total_fines = 0
            
            for record in logs:
                student_name, book_title, borrowed_date, due_date, returned, return_date, fine_amount, days_overdue = record
                
                # Calculate status
                if returned:
                    status = "Returned"
                    return_str = return_date.strftime('%Y-%m-%d %H:%M') if return_date else "N/A"
                else:
                    if days_overdue and days_overdue > 0:
                        status = f"Overdue ({days_overdue}d)"
                    else:
                        status = "Active"
                    return_str = "N/A"
                
                total_fines += fine_amount or 0
                
                result.append({
                    'student': student_name,
                    'book': book_title,
                    'borrowed_date': borrowed_date.strftime('%Y-%m-%d %H:%M'),
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'status': status,
                    'return_date': return_str,
                    'fine': fine_amount or 0
                })
            
            return {'logs': result, 'total_fines': total_fines}
                
        except Error as e:
            raise Exception(f"Error getting borrow logs: {e}")

    def trackBooks(self):
        """Track all borrowed books from database"""
        try:
            query = """
            SELECT student_name, book_title, borrowed_date, due_date,
                   DATEDIFF(CURDATE(), due_date) as days_overdue
            FROM borrowed_books 
            WHERE returned = FALSE
            ORDER BY due_date
            """
            self.db.cursor.execute(query)
            borrowed_books = self.db.cursor.fetchall()
            
            result = []
            for record in borrowed_books:
                student_name, book_title, borrowed_date, due_date, days_overdue = record
                
                status = "On Time" if days_overdue is None or days_overdue <= 0 else f"OVERDUE ({days_overdue}d)"
                
                result.append({
                    'student': student_name,
                    'book': book_title,
                    'borrowed_date': borrowed_date.strftime('%Y-%m-%d'),
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'status': status
                })
            
            return result
                
        except Error as e:
            raise Exception(f"Error tracking books: {e}")

    def getUserLogs(self, username):
        """Get complete borrowing history for a specific user"""
        pass

    def add_book_review(self, username, book_title, rating, review_text=None):
        """Add a review and rating for a book"""
        try:
            if not 1 <= rating <= 5:
                return "Rating must be between 1 and 5!"
            
            insert_query = """
                INSERT INTO book_reviews (book_title, username, rating, review_text)
                VALUES (%s, %s, %s, %s)
            """
            self.db.cursor.execute(insert_query, (book_title, username, rating, review_text))
            self.db.connection.commit()
            return True
        except Error as e:
            return f"Error adding review: {str(e)}"

    def get_book_reviews(self, book_title):
        """Get all reviews for a specific book"""
        try:
            query = """
                SELECT username, rating, review_text, review_date
                FROM book_reviews
                WHERE book_title = %s
                ORDER BY review_date DESC
            """
            self.db.cursor.execute(query, (book_title,))
            reviews = self.db.cursor.fetchall()
            return reviews
        except Error as e:
            return []

    def get_top_rated_books(self, limit=5):
        """Get top rated books with their average ratings"""
        try:
            query = """
                SELECT b.title, b.author, b.category,
                    AVG(r.rating) as avg_rating,
                    COUNT(r.id) as num_reviews
                FROM books b
                LEFT JOIN book_reviews r ON b.title = r.book_title
                GROUP BY b.title, b.author, b.category
                HAVING num_reviews > 0
                ORDER BY avg_rating DESC, num_reviews DESC
                LIMIT %s
            """
            self.db.cursor.execute(query, (limit,))
            return self.db.cursor.fetchall()
        except Error as e:
            return []

    def getOverdueBooks(self):
        """Get all overdue books"""
        try:
            query = """
            SELECT student_name, book_title, borrowed_date, due_date,
                   DATEDIFF(CURDATE(), due_date) as days_overdue,
                   (DATEDIFF(CURDATE(), due_date) * 5) as fine_amount
            FROM borrowed_books 
            WHERE returned = FALSE AND due_date < CURDATE()
            ORDER BY days_overdue DESC
            """
            self.db.cursor.execute(query)
            overdue_books = self.db.cursor.fetchall()
            
            result = []
            total_fine = 0
            
            for record in overdue_books:
                student_name, book_title, borrowed_date, due_date, days_overdue, fine_amount = record
                total_fine += fine_amount
                
                result.append({
                    'student': student_name,
                    'book': book_title,
                    'borrowed_date': borrowed_date.strftime('%Y-%m-%d'),
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'days_overdue': days_overdue,
                    'fine': fine_amount
                })
            
            return {'books': result, 'total_fine': total_fine}
                
        except Error as e:
            raise Exception(f"Error getting overdue books: {e}")

    def removeBook(self, title):
        """Remove a book from the library"""
        try:
            # First check if book exists
            check_query = "SELECT * FROM books WHERE title = %s"
            self.db.cursor.execute(check_query, (title,))
            book = self.db.cursor.fetchone()
            
            if not book:
                return False, "Book not found"
                
            # Check if any copies are borrowed
            check_borrowed = "SELECT COUNT(*) FROM borrowed_books WHERE book_title = %s AND returned = FALSE"
            self.db.cursor.execute(check_borrowed, (title,))
            borrowed_count = self.db.cursor.fetchone()[0]
            
            if borrowed_count > 0:
                return False, "Cannot remove book - some copies are currently borrowed"
            
            try:
                # Explicitly disable autocommit and handle transaction manually
                self.db.connection.autocommit = False
                
                # First delete any existing reviews
                self.db.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                self.db.cursor.execute("DELETE FROM book_reviews WHERE book_title = %s", (title,))
                
                # Then delete borrow history
                self.db.cursor.execute("DELETE FROM borrowed_books WHERE book_title = %s", (title,))
                
                # Finally delete the book
                self.db.cursor.execute("DELETE FROM books WHERE title = %s", (title,))
                self.db.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                
                # Commit all changes
                self.db.connection.commit()
                
                # Re-enable autocommit
                self.db.connection.autocommit = True
                
                return True, "Book successfully removed"
                
            except Error as e:
                print(f"Error during book removal: {str(e)}")  # Debug log
                # Ensure rollback
                try:
                    self.db.connection.rollback()
                except Error as rollback_error:
                    print(f"Rollback error: {str(rollback_error)}")  # Debug log
                
                # Re-enable foreign key checks and autocommit in case of error
                try:
                    self.db.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                    self.db.connection.autocommit = True
                except Error as cleanup_error:
                    print(f"Cleanup error: {str(cleanup_error)}")  # Debug log
                
                return False, f"Database error: {str(e)}"
                
        except Error as e:
            print(f"Outer error during book removal: {str(e)}")  # Debug log
            # Final safety cleanup
            try:
                self.db.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                self.db.connection.autocommit = True
            except:
                pass
            return False, f"Failed to remove book: {str(e)}"

    def editBook(self, old_title, new_title, new_author, new_category, new_total_copies):
        """Edit book details"""
        try:
            # Check if book exists
            check_query = "SELECT available_copies, total_copies FROM books WHERE title = %s"
            self.db.cursor.execute(check_query, (old_title,))
            book = self.db.cursor.fetchone()
            
            if not book:
                return False, "Book not found"
            
            available_copies, total_copies = book
            borrowed_copies = total_copies - available_copies
            
            if new_total_copies < borrowed_copies:
                return False, f"Cannot reduce total copies below borrowed copies ({borrowed_copies})"
            
            # Calculate new available copies
            new_available_copies = new_total_copies - borrowed_copies
            
            # Update the book details
            update_query = """
                UPDATE books 
                SET title = %s, author = %s, category = %s, 
                    total_copies = %s, available_copies = %s 
                WHERE title = %s
            """
            self.db.cursor.execute(update_query, 
                (new_title, new_author, new_category, 
                 new_total_copies, new_available_copies, old_title))
            
            # Update borrowed_books table if title changed
            if old_title != new_title:
                update_borrowed = "UPDATE borrowed_books SET book_title = %s WHERE book_title = %s"
                self.db.cursor.execute(update_borrowed, (new_title, old_title))
            
            self.db.connection.commit()
            return True, "Book details updated successfully"
            
        except Error as e:
            return False, f"Failed to update book details: {str(e)}"

    def addNewBook(self, title, author, category, copies=1):
        """Add a new book to the library"""
        try:
            # Check if book already exists
            check_query = "SELECT COUNT(*) FROM books WHERE title = %s"
            self.db.cursor.execute(check_query, (title,))
            
            if self.db.cursor.fetchone()[0] > 0:
                # Book exists, update copies
                update_query = """
                UPDATE books 
                SET total_copies = total_copies + %s, available_copies = available_copies + %s
                WHERE title = %s
                """
                self.db.cursor.execute(update_query, (copies, copies, title))
                print(f"✅ Added {copies} more copies of '{title}' to the library!\n")
            else:
                # New book
                insert_query = """
                INSERT INTO books (title, author, category, total_copies, available_copies) 
                VALUES (%s, %s, %s, %s, %s)
                """
                self.db.cursor.execute(insert_query, (title, author, category, copies, copies))
                print(f"✅ New book '{title}' by {author} added to the library!\n")
            
            self.db.connection.commit()
            
        except Error as e:
            print(f"Error adding book: {e}")

    def removeUser(self, username):
        """Remove a user from the system"""
        try:
            # Check if user exists
            check_user = "SELECT COUNT(*) FROM users WHERE username = %s"
            self.db.cursor.execute(check_user, (username,))
            if self.db.cursor.fetchone()[0] == 0:
                return False, f"User '{username}' not found in the system."

            # Check if user has any borrowed books
            check_borrowed = """
            SELECT COUNT(*) FROM borrowed_books 
            WHERE student_name = %s AND returned = FALSE
            """
            self.db.cursor.execute(check_borrowed, (username,))
            active_books = self.db.cursor.fetchone()[0]
            
            if active_books > 0:
                return False, f"Cannot remove user '{username}'. They have {active_books} borrowed books. Please ensure all books are returned first."
            
            # Delete user from the users table
            delete_query = "DELETE FROM users WHERE username = %s"
            self.db.cursor.execute(delete_query, (username,))
            self.db.connection.commit()
            
            return True, f"User '{username}' has been successfully removed from the system."
            
        except Error as e:
            return False, f"Error removing user: {e}"

    def generateReports(self):
        """Generate library statistics and reports"""
        try:
            report_data = {}
            
            # Total books
            self.db.cursor.execute("SELECT COUNT(*), SUM(total_copies) FROM books")
            unique_books, total_copies = self.db.cursor.fetchone()
            total_copies = total_copies or 0
            
            # Available books
            self.db.cursor.execute("SELECT SUM(available_copies) FROM books")
            available_copies = self.db.cursor.fetchone()[0] or 0
            
            report_data['summary'] = {
                'unique_books': unique_books,
                'total_copies': total_copies,
                'available_copies': available_copies,
                'borrowed_copies': total_copies - available_copies
            }
            
            # Most popular books
            popular_query = """
            SELECT book_title, COUNT(*) as borrow_count
            FROM borrowed_books
            GROUP BY book_title
            ORDER BY borrow_count DESC
            LIMIT 5
            """
            self.db.cursor.execute(popular_query)
            popular_books = self.db.cursor.fetchall()
            report_data['popular_books'] = [
                {'title': title, 'count': count}
                for title, count in popular_books
            ]
            
            # Active borrowers
            active_query = """
            SELECT student_name, COUNT(*) as active_books
            FROM borrowed_books
            WHERE returned = FALSE
            GROUP BY student_name
            ORDER BY active_books DESC
            """
            self.db.cursor.execute(active_query)
            active_borrowers = self.db.cursor.fetchall()
            report_data['active_borrowers'] = [
                {'name': name, 'books': count}
                for name, count in active_borrowers
            ]
            
            return report_data
            
        except Error as e:
            raise Exception(f"Error generating reports: {e}")



def editBook(self, old_title, new_title, new_author, new_category, new_total_copies):
    """Edit book details"""
    try:
        # Check if book exists
        check_query = "SELECT available_copies, total_copies FROM books WHERE title = %s"
        self.db.cursor.execute(check_query, (old_title,))
        book = self.db.cursor.fetchone()
        
        if not book:
            return False, "Book not found"
        
        available_copies, total_copies = book
        borrowed_copies = total_copies - available_copies
        
        if new_total_copies < borrowed_copies:
            return False, f"Cannot reduce total copies below borrowed copies ({borrowed_copies})"
        
        # Calculate new available copies
        new_available_copies = new_total_copies - borrowed_copies
        
        # Update the book details
        update_query = """
            UPDATE books 
            SET title = %s, author = %s, category = %s, 
                total_copies = %s, available_copies = %s 
            WHERE title = %s
        """
        self.db.cursor.execute(update_query, 
            (new_title, new_author, new_category, 
             new_total_copies, new_available_copies, old_title))
        
        # Update borrowed_books table if title changed
        if old_title != new_title:
            update_borrowed = "UPDATE borrowed_books SET book_title = %s WHERE book_title = %s"
            self.db.cursor.execute(update_borrowed, (new_title, old_title))
        
        self.db.connection.commit()
        return True, "Book details updated successfully"
        
    except Error as e:
        return False, f"Failed to update book details: {str(e)}"
class Student():
    def registerUser(self):
        """Register a new user"""
        print("📝 User Registration")
        print("-" * 30)
        username = input("Enter username (unique): ")
        full_name = input("Enter full name: ")
        class_name = input("Enter class (e.g., I, II, III, etc.): ") or None
        section = input("Enter section (A, B, C, etc.): ") or None
        return username, full_name, class_name, section

    def requestBook(self):
        print("So, you want to borrow book!")
        self.book = input("Enter name of the book you want to borrow: ")
        return self.book

    def returnBook(self):
        print("So, you want to return book!")
        self.name = input("Enter your username: ")
        self.book = input("Enter name of the book you want to return: ")
        return self.name, self.book
    
    def renewBook(self):
        print("So, you want to renew book!")
        self.name = input("Enter your username: ")
        self.book = input("Enter name of the book you want to renew: ")
        return self.name, self.book

    def donateBook(self):
        print("Okay! you want to donate book!")
        self.book = input("Enter name of the book you want to donate: ")
        self.author = input("Enter author name (optional): ") or "Unknown"
        self.category = input("Enter category (Fiction/Non-Fiction/Science/Technology/Literature/Economics/Education/General): ") or "General"
        return self.book, self.author, self.category
    
    def addNewBook(self):
        print("Adding a new book to the library!")
        self.book = input("Enter book title: ")
        self.author = input("Enter author name: ")
        self.category = input("Enter category (Fiction/Non-Fiction/Science/Technology/Literature/Economics/Education/General): ") or "General"
        try:
            self.copies = int(input("Enter number of copies (default 1): ") or "1")
        except ValueError:
            self.copies = 1
        return self.book, self.author, self.category, self.copies

    def searchBooks(self):
        print("Search for books!")
        search_term = input("Enter book title, author, or category to search: ")
        return search_term
    
    def removeUser(self):
        print("❌ Remove user from the system")
        print("-" * 30)
        username = input("Enter username to remove: ")
        confirm = input(f"Are you sure you want to remove user '{username}'? (y/n): ")
        if confirm.lower() == 'y':
            return username
        return None


def setup_database():
    """Setup database connection with user input"""
    print("=== Database Configuration ===")
    host = input("Enter MySQL host (default: localhost): ") or "localhost"
    database = input("Enter database name (default: library_management): ") or "library_management"
    user = input("Enter MySQL username (default: root): ") or "root"
    password = input("Enter MySQL password: ")
    
    db = DatabaseConnection()
    if db.connect(host, database, user, password):
        return db
    else:
        print("Failed to connect to database. Exiting...")
        sys.exit(1)


def display_menu():
    """Display the main menu"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    📚 LIBRARY MANAGEMENT SYSTEM              ║
╠══════════════════════════════════════════════════════════════╣
║  1. 📖 List all available books                              ║
║  2. 🔍 Search books (by title/author/category)               ║
║  3. 📚 Borrow a book                                         ║
║  4. 📤 Return a book                                         ║
║  5. 🔄 Renew a book                                          ║
║  6. 💝 Donate/Add a book                                     ║
║  7. ➕ Add new book (Librarian)                              ║
║  8. � Track all borrowed books                              ║
║  9. ⚠️  View overdue books                                   ║
║ 10. 📊 Generate library reports                              ║
║ 11. � List all registered users (Admin)                     ║
║ 12. 📝 Register new user                                     ║
║ 13. ❌ Remove user                                           ║
║ 14. �🚪 Exit the library                                     
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    # Setup database connection
    db_connection = setup_database()
    
    # Initialize library with database connection
    Delhilibrary = Library(db_connection)
    student = Student()

    print("\n" + "="*70)
    print("🏛️  WELCOME TO MARY MATHA DIGITAL LIBRARY MANAGEMENT SYSTEM  🏛️")
    print("="*70)
    print("⚠️  NOTE: You must be a registered user to borrow/return books!")
    print("📝 Use option 13 to register if you're a new user.")

    try:
        while (True):
            display_menu()
            try:
                usr_response = int(input("👉 Enter your choice (1-15): "))

                if usr_response == 1:  # List available books
                    Delhilibrary.displayAvailableBooks()
                    
                elif usr_response == 2:  # Search books
                    search_term = student.searchBooks()
                    Delhilibrary.searchBooks(search_term)
                    
                elif usr_response == 3:  # Borrow books
                    student_name = input("Enter your username: ")
                    book_name = student.requestBook()
                    Delhilibrary.borrowBook(student_name, book_name)
                    
                elif usr_response == 4:  # Return books
                    student_name, book_name = student.returnBook()
                    Delhilibrary.returnBook(student_name, book_name)
                    
                elif usr_response == 5:  # Renew books
                    student_name, book_name = student.renewBook()
                    Delhilibrary.renewBook(student_name, book_name)
                    
                elif usr_response == 6:  # Donate books
                    book_name, author, category = student.donateBook()
                    Delhilibrary.addNewBook(book_name, author, category, 1)
                    
                elif usr_response == 7:  # Add new books (Librarian)
                    book_name, author, category, copies = student.addNewBook()
                    Delhilibrary.addNewBook(book_name, author, category, copies)
                    
                elif usr_response == 8:  # Track books
                    Delhilibrary.trackBooks()
                    
                elif usr_response == 9:  # Overdue books
                    Delhilibrary.getOverdueBooks()
                    
                elif usr_response == 10:  # Generate reports
                    Delhilibrary.generateReports()
                    
                elif usr_response == 11:  # List all users (Admin)
                    Delhilibrary.listAllUsers()
                    
                elif usr_response == 12:  # Register new user
                    username, full_name, class_name, section = student.registerUser()
                    Delhilibrary.registerUser(username, full_name, class_name, section)
                    
                elif usr_response == 13:  # Remove user
                    username = student.removeUser()
                    if username:
                        Delhilibrary.removeUser(username)
                    
                elif usr_response == 14:  # Exit
                    print("\n🙏 THANK YOU FOR USING MARY MATHA DIGITAL LIBRARY SYSTEM!")
                    print("📚 Happy Reading! 📚\n")
                    break
                    
                else:
                    print("❌ INVALID INPUT! Please enter a number between 1-14.\n")
                    
            except ValueError:
                print("❌ INVALID INPUT! Please enter a valid number.\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")
                
    finally:
        # Close database connection when exiting
        db_connection.close_connection()