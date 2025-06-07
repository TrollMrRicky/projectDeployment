import sqlite3
import csv
from pathlib import Path

def create_database(csv_file_path, db_name='learning.db', table_name='Flashcard'):
    """
    Creates a SQLite database from a CSV file
    
    Args:
        csv_file_path (str): Path to the CSV file
        db_name (str): Name of the SQLite database file
        table_name (str): Name of the table to create
    """
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect("databasestuff/learning.db")
    cursor = conn.cursor()
    
    # Read CSV file to get headers and data
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)  # Get column headers from first row
        data_rows = [row for row in csv_reader]  # Get all data rows
        
    for i in data_rows:
        print(i)
        cursor.execute(f"""
            INSERT INTO Flashcard (Definition, Reading, Sentence, SentenceTranslation, WordID) VALUES ("{i[0]}", "{i[1]}", "{i[2]}", "{i[3]}", {i[4]});
        """)    

    # Commit changes and close connection
    conn.commit()
    conn.close()

path = r"C:\Users\ricky\Documents\GitHub\4-Ricky-Clipsham\SE Project - Ricky Clipsham\databasestuff\lyricmapping.csv"
create_database(path)