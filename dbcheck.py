import sqlite3

conn = sqlite3.connect('stroop_efficiency.db')
c = conn.cursor()
c.execute("SELECT * FROM efficiency")
for row in c.fetchall():
    print(row)
conn.close()
