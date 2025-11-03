"""
Advanced Database Setup Script for Library Management System
Run this script to create the database and test the connection
"""

import mysql.connector
from mysql.connector import Error

def create_database():
    """Create the library_management database"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Change this if your MySQL has a password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS library_management")
            print("✅ Database 'library_management' created successfully!")
            
            # Show databases to confirm
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("\n📊 Available databases:")
            for db in databases:
                if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']:
                    print(f"   📁 {db[0]}")
                
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure MySQL server is running")
        print("2. Check if the username/password is correct")
        print("3. If using XAMPP, start MySQL service from XAMPP Control Panel")
        print("4. If using MySQL Workbench, ensure the service is started")

def test_connection_and_create_tables():
    """Test connection and create all necessary tables"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='library_management',
            user='root',
            password=''  # Change this if your MySQL has a password
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to library_management database!")
            
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"🔌 MySQL version: {version[0]}")
            
            # Create all tables
            print("\n📋 Creating database tables...")
            
            # Books table with enhanced fields
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
            
            # Borrowed books table with due dates and fines
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
                FOREIGN KEY (book_title) REFERENCES books(title)
            )
            """
            
            # Users table for user management
            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(15),
                class VARCHAR(50),
                section VARCHAR(10),
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('active', 'suspended', 'inactive') DEFAULT 'active'
            )
            """
            
            # Book categories table
            categories_table = """
            CREATE TABLE IF NOT EXISTS book_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT
            )
            """

            # Book reviews table
            reviews_table = """
            CREATE TABLE IF NOT EXISTS book_reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_title VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL,
                rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review_text TEXT,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_title) REFERENCES books(title),
                FOREIGN KEY (username) REFERENCES users(username)
            )
            """
            
            # Execute table creation
            cursor.execute(books_table)
            print("   ✅ Books table created")
            
            cursor.execute(borrowed_table)
            print("   ✅ Borrowed books table created")
            
            cursor.execute(users_table)
            print("   ✅ Users table created")
            
            cursor.execute(categories_table)
            print("   ✅ Book categories table created")

            cursor.execute(reviews_table)
            print("   ✅ Book reviews table created")
            
            # Insert default categories
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
            
            print("\n📚 Inserting default book categories...")
            for category, description in categories:
                check_query = "SELECT COUNT(*) FROM book_categories WHERE category_name = %s"
                cursor.execute(check_query, (category,))
                if cursor.fetchone()[0] == 0:
                    insert_query = "INSERT INTO book_categories (category_name, description) VALUES (%s, %s)"
                    cursor.execute(insert_query, (category, description))
                    print(f"   ✅ Added category: {category}")
            
            connection.commit()
            
            # Show table status
            print("\n📊 Database Tables Status:")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   📁 {table[0]}: {count} records")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Please check:")
        print("1. MySQL service is running")
        print("2. Database 'library_management' exists")
        print("3. Username and password are correct")

def verify_setup():
    """Verify the complete setup"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='library_management',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("\n🔍 Verifying setup...")
            
            # Check required tables exist
            required_tables = ['books', 'borrowed_books', 'users', 'book_categories']
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            
            all_tables_exist = True
            for table in required_tables:
                if table in existing_tables:
                    print(f"   ✅ Table '{table}' exists")
                else:
                    print(f"   ❌ Table '{table}' missing")
                    all_tables_exist = False
            
            if all_tables_exist:
                print("\n🎉 Setup verification successful!")
                print("   💡 Your library management system is ready to use!")
            else:
                print("\n⚠️  Setup incomplete - some tables are missing")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    print("🏛️" + "="*60 + "🏛️")
    print("    📚 ADVANCED LIBRARY MANAGEMENT DATABASE SETUP 📚")
    print("🏛️" + "="*60 + "🏛️")
    
    print("\n🚀 Step 1: Creating database...")
    create_database()
    
    print("\n🚀 Step 2: Testing connection and creating tables...")
    test_connection_and_create_tables()
    
    print("\n🚀 Step 3: Verifying setup...")
    verify_setup()
    
    print("\n" + "="*65)
    print("🎯 SETUP COMPLETE!")
    print("🚀 Run 'python lib.py' to start the library management system!")
    print("📖 Check README.md for detailed usage instructions")
    print("="*65)