import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD")
)

cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS testdb")
cursor.execute("USE testdb")

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    role VARCHAR(255),
    salary INT
)
""")

cursor.execute("""
INSERT INTO employees (name, role, salary) VALUES
('Alice', 'Engineer', 70000),
('Bob', 'Manager', 85000),
('Charlie', 'Analyst', 60000)
""")

conn.commit()
cursor.close()
conn.close()

print("DB and table initialized.")
