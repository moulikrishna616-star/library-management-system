"""
Excel import/export utilities for the Library Management System.

Functions:
 - export_database_to_excel(db_conn, filepath, tables=None)
 - import_database_from_excel(db_conn, filepath)

This module uses pandas + openpyxl to read/write .xlsx files and
mysql-connector to interact with the database.
"""
from typing import List
import pandas as pd
import numpy as np
from mysql.connector import Error
from datetime import datetime


DEFAULT_TABLES = [
    'books',
    'users',
    'borrowed_books',
    'book_categories',
    'book_reviews'
]


def export_database_to_excel(db_conn, filepath: str, tables: List[str] = None):
    """Export selected database tables into a single Excel workbook.

    Args:
        db_conn: DatabaseConnection instance (expected to have .cursor)
        filepath: path to .xlsx file to write
        tables: list of table names to export; defaults to DEFAULT_TABLES
    """
    if tables is None:
        tables = DEFAULT_TABLES

    cursor = db_conn.cursor
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                cols = cursor.column_names
                df = pd.DataFrame(rows, columns=cols)
                # Ensure sheet name length and characters are acceptable
                sheet_name = table[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            except Error:
                # skip tables that don't exist or on error
                continue
        # ExcelWriter context manager will save/close the file on exit.


def import_database_from_excel(db_conn, filepath: str):
    """Import data from an Excel workbook into the database.

    Each sheet name is treated as a target table. Rows are inserted using
    INSERT ... ON DUPLICATE KEY UPDATE to avoid duplicate-key failures.

    Note: This is a best-effort importer. It assumes columns in sheets match
    the corresponding table columns. Primary key columns (e.g., id) are not
    updated.
    """
    xls = pd.read_excel(filepath, sheet_name=None)
    cursor = db_conn.cursor
    conn = db_conn.connection

    def _normalize_value(v):
        """Convert pandas / numpy types to Python native types acceptable by mysql-connector."""
        # pandas NA handling
        if pd.isna(v):
            return None

        # pandas Timestamp -> python datetime
        if isinstance(v, pd.Timestamp):
            try:
                return v.to_pydatetime()
            except Exception:
                # Fallback: convert via Python datetime constructor
                return datetime(v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond)

        # numpy scalar -> python native
        if isinstance(v, np.generic):
            return v.item()

        # bool/int/float/str/datetime.date/datetime.datetime pass through
        return v

    for sheet_name, df in xls.items():
        table = sheet_name
        if df.empty:
            continue

        # Normalize column names to strings
        cols = [str(c) for c in df.columns]

        # Prepare insert parts
        columns_str = ','.join([f"`{c}`" for c in cols])
        placeholders = ','.join(['%s'] * len(cols))

        # Build ON DUPLICATE KEY UPDATE (skip id if present)
        update_cols = [c for c in cols if c.lower() not in ('id',)]
        if update_cols:
            update_str = ','.join([f"`{c}`=VALUES(`{c}`)" for c in update_cols])
            query = f"INSERT INTO `{table}` ({columns_str}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_str}"
        else:
            query = f"INSERT INTO `{table}` ({columns_str}) VALUES ({placeholders})"

        try:
            for _, row in df.iterrows():
                values = []
                for c in cols:
                    v = row[c]
                    values.append(_normalize_value(v))

                cursor.execute(query, tuple(values))
            conn.commit()
        except Exception as e:
            conn.rollback()
            # Re-raise with context to show which sheet failed
            raise Exception(f"Failed to import sheet '{sheet_name}': {e}")
