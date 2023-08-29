import psycopg2


conn = psycopg2.connect(dbname="budgetunidb", user="budgetunidb_user", password="Ba6AF9eekpJ4AdbSPjbxyea69aRa2lka", host="dpg-cjggv341ja0c73cru58g-a.frankfurt-postgres.render.com", port="5432")
cur = conn.cursor()
conn.autocommit = True