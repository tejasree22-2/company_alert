import psycopg2
    
DB_CONFIG = {
    "host": "localhost",
    "database": "init_postgresql",
    "user": "tejasree",
    "password": "tejasree@22",
    "port": "5432"
}
    
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
    
# USERS TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL
);
""")
    
# SUBSCRIPTIONS TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    is_paused BOOLEAN DEFAULT FALSE
);
""")
    
# COMPANIES TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    opening_date DATE
);
""")
    
conn.commit()
cur.close()
conn.close()
    
print("Tables created successfully!")
    








