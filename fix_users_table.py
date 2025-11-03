import mysql.connector

def fix_users_table():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='library_management',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Drop foreign key constraints first
            cursor.execute("""
                ALTER TABLE book_reviews
                DROP FOREIGN KEY IF EXISTS book_reviews_ibfk_2
            """)
            
            # Now we can safely drop and recreate users table
            cursor.execute("DROP TABLE IF EXISTS users")
            
            users_table = """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                full_name VARCHAR(255) NOT NULL,
                class VARCHAR(50),
                section VARCHAR(10),
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('active', 'suspended', 'inactive') DEFAULT 'active'
            )
            """
            cursor.execute(users_table)
            connection.commit()
            print("✅ Users table recreated successfully!")
            
            cursor.close()
            connection.close()
            
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_users_table()