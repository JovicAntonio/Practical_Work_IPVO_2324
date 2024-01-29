import sqlite3
import psycopg2

# SQLite connection
sqlite_conn = sqlite3.connect('db.sqlite3')
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL connection
postgres_conn = psycopg2.connect(
    database="pgdb",
    user="postgres_user",
    password="postgres_password",
    host="postgres",
    port="5432"
)
postgres_cursor = postgres_conn.cursor()

# Retrieve data from SQLite
sqlite_cursor.execute("SELECT * FROM student_files_studentfile")
data_to_replicate = sqlite_cursor.fetchall()

postgres_cursor.execute("CREATE TABLE student_files_studentfile (title varchar(100), file varchar(512), studentFirstName varchar(100), studentLastName varchar(100), thesisDefenseDate date, thesisType varchar(100), thesisDefensePlace varchar(100), wordCount int, fileSize int)")
postgres_conn.commit()

for row in data_to_replicate:
    postgres_cursor.execute(
        "INSERT INTO student_files_studentfile (title, file, studentFirstName, studentLastName, thesisDefenseDate, thesisType, thesisDefensePlace, wordCount, fileSize) VALUES (%s, %s, ...)",
        row
    )

postgres_conn.commit()
postgres_conn.close()
sqlite_conn.close()


if __name__ == "__main__":
    log_file = f'/app/logs/replication_log_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'

    try:
        with open(log_file, 'a') as log:
            log.write(f"Replication started at {datetime.now()}\n")

            log.write(f"Replication completed successfully at {datetime.now()}\n")

    except Exception as e:
        with open(log_file, 'a') as log:
            log.write(f"Error during replication at {datetime.now()}: {str(e)}\n")