import mysql.connector

db = mysql.connector.connect(
    host="10.101.0.27",
    username="evan_test",
    password="test_stage_pwd_23"
)

cursor = db.cursor()

print("Initializing database...")

cursor.execute("USE test_db")

lab_query = "CREATE TABLE IF NOT EXISTS Lab(id int NOT NULL, name varchar(50) NOT NULL, " \
            "description varchar(100) NOT NULL, PRIMARY KEY(id)) "

teacher_query = "CREATE TABLE IF NOT EXISTS Teacher(id int NOT NULL, first_name varchar(50) NOT " \
                "NULL, last_name varchar(50) NOT NULL, dept varchar(50), PRIMARY KEY(id)) "

course_query = "CREATE TABLE IF NOT EXISTS Course(id int NOT NULL, name varchar(50) NOT NULL, " \
               "number varchar(15), allocation bool DEFAULT 1, PRIMARY KEY(id)) "

cursor.execute(lab_query)
cursor.execute(teacher_query)
cursor.execute(course_query)

cursor.execute("SHOW TABLES")

print("Following tables exist in the database:")

for x in cursor:
    print(x)

