import sqlite3

def create_database():
    conn = sqlite3.connect('gesture_data.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS gesture_data
                      (data INTEGER, state TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
