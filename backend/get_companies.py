import sqlite3
import json
conn = sqlite3.connect('backend/ppa.db')
c = conn.cursor()
c.execute("SELECT id, email, role FROM user")
rows = c.fetchall()
print(json.dumps(rows))
