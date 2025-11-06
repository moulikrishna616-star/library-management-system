# Advanced Library Management System with MySQL Integration

## 🚀 Latest Update: User Registration System

### 👤 User Management (NEW)
- **Mandatory Registration**: Users must register before borrowing books
- **User Verification**: All library operations verify user existence
- **User Profiles**: Store user details including contact information
- **Admin Functions**: List and manage all registered users

### 📅 Due Date System
- **7-day borrowing period**: All books must be returned within 7 days
- **Automatic due date calculation**: System calculates due date when book is borrowed
- **Due date tracking**: Shows due dates for all borrowed books

### 💰 Fine Management
- **Overdue fines**: $5 per day for late returns
- **Automatic calculation**: System calculates fines based on return date
- **Fine tracking**: Records all fines in database

### 👤 User Log System
- **Complete borrowing history**: View all books a user has borrowed
- **Current borrowed books**: See what books user currently has
- **Return history**: Track when books were returned and any fines paid
- **User search**: Search by username to get complete logs

### 📊 Advanced Tracking & Reports
- **Overdue book tracking**: See all overdue books and fines
- **Library statistics**: Total books, available copies, popular books
- **Active borrowers**: See who has books currently borrowed
- **Comprehensive reports**: Detailed analytics and insights

### 🔍 Enhanced Search & Management
- **Book search**: Search by title, author, or category
- **Book categories**: Organized categories for better management
- **Multiple copies**: Support for multiple copies of same book
- **Borrowing limits**: Maximum 3 books per user
- **Book renewal**: Extend due date by 7 days (if not overdue)

## 📋 Complete Feature List

### 🏛️ Main Features
1. **📖 List Available Books**: Shows all books with author, category, and availability
2. **🔍 Search Books**: Search by title, author, or category
3. **📚 Borrow Books**: Borrow with automatic due date and limit checking
4. **📤 Return Books**: Return with fine calculation for overdue books
5. **🔄 Renew Books**: Extend borrowing period by 7 days
6. **💝 Donate Books**: Add books to library collection
7. **➕ Add New Books**: Librarian function to add multiple copies
8. **👤 User Logs**: Complete borrowing history for any user
9. **📋 Track Borrowed Books**: See all currently borrowed books with due dates
10. **⚠️ Overdue Books**: Track overdue books and fines
11. **📊 Library Reports**: Comprehensive statistics and analytics
12. **🚪 Exit**: Clean database connection closure

### 🗄️ Database Schema

#### Books Table
```sql
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    available BOOLEAN DEFAULT TRUE,
    total_copies INT DEFAULT 1,
    available_copies INT DEFAULT 1,
    category VARCHAR(100) DEFAULT 'General',
    author VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Borrowed Books Table
```sql
CREATE TABLE borrowed_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    book_title VARCHAR(255) NOT NULL,
    borrowed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE NOT NULL,
    returned BOOLEAN DEFAULT FALSE,
    return_date TIMESTAMP NULL,
    fine_amount DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (book_title) REFERENCES books(title)
);
```

#### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(15),
    address TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('active', 'suspended', 'inactive') DEFAULT 'active'
);
```

#### Book Categories Table
```sql
CREATE TABLE book_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);
```

## 📚 Book Categories
- **Fiction**: Novels, short stories, and fictional works
- **Non-Fiction**: Biographies, history, science, etc.
- **Science**: Scientific books and research
- **Technology**: Computer science, engineering, etc.
- **Literature**: Classic literature and poetry
- **Economics**: Economic theories and business
- **Education**: Educational and academic books
- **General**: General purpose books

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
Run the database setup script:
```bash
py excel_utlils. py
py fix_users_table. py
py 
python setup_database.py
```

### 3. Run the Application
```bash
python lib.py
```

## 💡 Usage Examples

### 📖 Borrowing Process
1. User selects "Borrow a book"
2. Enters their name
3. Enters book title
4. System checks availability and borrowing limits
5. Sets due date (7 days from borrow date)
6. Updates database and shows confirmation with due date

### 📤 Return Process
1. User selects "Return a book"
2. Enters their name and book title
3. System verifies the borrowing record
4. Calculates any overdue fines
5. Updates database and shows return confirmation

### 👤 User Log Example
```
👤 USER LOGS FOR: john_doe

📚 CURRENTLY BORROWED BOOKS:
Book Title               Borrowed Date   Due Date     Status
Python Programming      2025-10-20      2025-10-27   On Time
Data Structures         2025-10-22      2025-10-29   On Time

📖 RECENT BORROWING HISTORY:
Book Title               Borrowed    Due Date    Returned    Fine
Machine Learning         2025-10-10  2025-10-17  2025-10-19  $10.00
Web Development         2025-10-05  2025-10-12  2025-10-11  $0.00
```

## ⚠️ Important Rules

### 📋 Borrowing Rules
- **Maximum 3 books** per user at any time
- **7-day borrowing period** for all books
- **No duplicate borrowing** - cannot borrow same book twice
- **Name verification required** for returns

### 💰 Fine System
- **$5 per day** for overdue books
- **No renewal** for overdue books
- **Fines recorded** in database for tracking

### 🔄 Renewal Rules
- **7-day extension** from current due date
- **Only for non-overdue books**
- **One renewal** per borrowing (can be extended)

## 🛠️ Troubleshooting

### Database Connection Issues
1. Ensure MySQL server is running
2. Check username/password credentials
3. Verify database exists
4. Check port 3306 is accessible

### Common Errors
- **Book not found**: Check exact spelling
- **User not found**: Verify name matches borrowing record
- **Borrowing limit**: Return books before borrowing new ones
- **Overdue renewal**: Return book and reborrow instead

## 🎯 Future Enhancements
- User registration system
- Email notifications for due dates
- Book reservation system
- Digital library integration
- Mobile app interface
- Barcode scanning

- Advanced reporting dashboard
