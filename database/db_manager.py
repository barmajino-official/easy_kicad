import sqlite3
import os
import logging

class DBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default path relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "easykicadprovition.db")
        
        self.db_path = db_path
        self.conn = None

    def connect(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def get_part_metadata(self, lcsc_id):
        """
        Fetch category, subcategory, and description for a given LCSC ID.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    c.lcsc_id,
                    cat.category_name,
                    sub.subcategory_name,
                    c.description,
                    c.manufacturer,
                    c.mfr_part_no
                FROM components c
                JOIN subcategories sub ON c.subcategory_id = sub.id
                JOIN categories cat ON sub.category_id = cat.id
                WHERE c.lcsc_id = ?
            """
            cursor.execute(query, (lcsc_id,))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            logging.error(f"Database error: {e}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
