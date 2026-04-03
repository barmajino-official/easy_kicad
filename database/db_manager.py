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
                    cat.name as category_name,
                    cat.shorthand,
                    sub.name as subcategory_name,
                    c.description,
                    c.manufacturer,
                    c.mfr_part_no,
                    c.is_mirrored
                FROM components c
                JOIN subcategories sub ON c.subcategory_id = sub.id
                JOIN categories cat ON sub.category_id = cat.id
                WHERE c.lcsc_id = ?
            """
            cursor.execute(query, (lcsc_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'lcsc_id': row['lcsc_id'],
                    'category_name': row['category_name'],
                    'shorthand': row['shorthand'],
                    'subcategory_name': row['subcategory_name'],
                    'description': row['description'],
                    'manufacturer': row['manufacturer'],
                    'mfr_part_no': row['mfr_part_no'],
                    'is_mirrored': row['is_mirrored']
                }
            return None
        except Exception as e:
            logging.error(f"Database error: {e}")
            return None

    def mark_mirrored(self, lcsc_id: str):
        """
        Mark a component as mirrored in the database.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE components SET is_mirrored = 1 WHERE lcsc_id = ?", (lcsc_id,))
            conn.commit()
        except Exception as e:
            logging.error(f"Marking mirrored error for {lcsc_id}: {e}")

    def search_components(self, term: str):
        """
        Search for components matching a term in lcsc_id, mfr_part_no, or description.
        Returns a list of matching LCSC IDs.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            search_pattern = f"%{term}%"
            
            query = """
                SELECT lcsc_id 
                FROM components 
                WHERE lcsc_id LIKE ? 
                   OR mfr_part_no LIKE ? 
                   OR description LIKE ?
            """
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            results = cursor.fetchall()
            return [row['lcsc_id'] for row in results]
        except Exception as e:
            logging.error(f"Search error: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
