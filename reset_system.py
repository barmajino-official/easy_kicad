import sqlite3
import os
import shutil
import argparse

def reset_system(db_path, output_dir):
    print(f"🧹 Starting System Reset...")
    
    # 1. Reset Database
    if os.path.exists(db_path):
        try:
            print(f"🛰️ Resetting 'is_mirrored' flags in {db_path}...")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE components SET is_mirrored = 0")
            conn.commit()
            print(f"✅ Database reset successful ({cursor.rowcount} parts updated).")
            conn.close()
        except Exception as e:
            print(f"❌ Database reset failed: {e}")
    else:
        print(f"⚠️ Database not found at {db_path}. Skipping DB reset.")

    # 2. Clear Output Files
    if os.path.exists(output_dir):
        try:
            print(f"📂 Clearing output directory: {output_dir}...")
            # We don't delete the folder itself, just its contents
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'❌ Failed to delete {file_path}. Reason: {e}')
            print(f"✅ Output directory cleared.")
        except Exception as e:
            print(f"❌ Failed to clear output directory: {e}")
    else:
        print(f"⚠️ Output directory {output_dir} not found. Skipping FS reset.")

    print("✨ Reset Complete! You are ready for a fresh bulk download.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="database/easy_kicad_catalog.db")
    parser.add_argument("--output", default="outputFile")
    args = parser.parse_args()
    
    reset_system(args.db, args.output)
