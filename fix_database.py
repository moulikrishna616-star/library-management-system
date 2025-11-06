"""
Script to verify and rebuild database tables with proper constraints
"""
import mysql.connector
from mysql.connector import Error

def verify_and_fix_database():
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host='localhost',
            database='library_management',
            user='root',
            password=''
        )
        cursor = connection.cursor()
        
        # Drop all tables in correct order to avoid FK constraint issues
        print("Dropping existing tables...")
        tables = ['borrowed_books', 'book_reviews', 'books', 'users', 'book_categories']
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"- Dropped {table}")
            except Error as e:
                print(f"Error dropping {table}: {e}")
        
        # Create tables in correct order
        print("\nCreating tables with proper constraints...")
        
        # Create books table
        books_table = """
        CREATE TABLE books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL UNIQUE,
            available BOOLEAN DEFAULT TRUE,
            total_copies INT DEFAULT 1,
            available_copies INT DEFAULT 1,
            category VARCHAR(100) DEFAULT 'General',
            author VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """
        cursor.execute(books_table)
        print("- Created books table")
        
        # Create users table
        users_table = """
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            class VARCHAR(50),
            section CHAR(1),
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('active', 'suspended', 'inactive') DEFAULT 'active'
        ) ENGINE=InnoDB;
        """
        cursor.execute(users_table)
        print("- Created users table")
        
        # Create book categories table
        categories_table = """
        CREATE TABLE book_categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT
        ) ENGINE=InnoDB;
        """
        cursor.execute(categories_table)
        print("- Created book_categories table")
        
        # Create borrowed_books table with proper FK constraints
        borrowed_table = """
        CREATE TABLE borrowed_books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(255) NOT NULL,
            book_title VARCHAR(255) NOT NULL,
            borrowed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date DATE NOT NULL,
            returned BOOLEAN DEFAULT FALSE,
            return_date TIMESTAMP NULL,
            fine_amount DECIMAL(10,2) DEFAULT 0.00,
            CONSTRAINT fk_borrowed_book FOREIGN KEY (book_title) 
                REFERENCES books(title) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fk_borrowed_student FOREIGN KEY (student_name) 
                REFERENCES users(username) ON DELETE RESTRICT ON UPDATE CASCADE
        ) ENGINE=InnoDB;
        """
        cursor.execute(borrowed_table)
        print("- Created borrowed_books table")
        
        # Create book reviews table with proper FK constraints
        reviews_table = """
        CREATE TABLE book_reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_title VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
            review_text TEXT,
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_review_book FOREIGN KEY (book_title) 
                REFERENCES books(title) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fk_review_user FOREIGN KEY (username) 
                REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB;
        """
        cursor.execute(reviews_table)
        print("- Created book_reviews table")
        
        # Verify foreign keys
        print("\nVerifying foreign key constraints...")
        
        check_fk_query = """
        SELECT TABLE_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_SCHEMA = 'library_management'
        AND REFERENCED_TABLE_NAME IS NOT NULL;
        """
        cursor.execute(check_fk_query)
        fks = cursor.fetchall()
        
        for fk in fks:
            print(f"- {fk[0]} -> {fk[2]} ({fk[1]})")
        
        connection.commit()
        print("\n✅ Database structure rebuilt successfully!")
        
    except Error as e:
        print(f"\n❌ Database error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verify_and_fix_database()