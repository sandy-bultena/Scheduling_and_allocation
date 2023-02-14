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

timeslot_query = "CREATE TABLE IF NOT EXISTS TimeSlot(id int NOT NULL, day char(3) NOT NULL, " \
                 "duration decimal(3,1) NOT NULL, start varchar(5) NOT NULL, movable bool DEFAULT " \
                 "1, unavailable_lab_id int, PRIMARY KEY(id), FOREIGN KEY(unavailable_lab_id) " \
                 "REFERENCES Lab(id))"

scenario_query = "CREATE TABLE IF NOT EXISTS Scenario(id int NOT NULL, name varchar(50), " \
                 "description varchar(1000), year int, PRIMARY KEY(id)) "

schedule_query = "CREATE TABLE IF NOT EXISTS Schedule(id int NOT NULL, name varchar(50) NOT NULL, " \
                 "description varchar(100), " \
                 "semester varchar(11) NOT NULL, official boolean NOT NULL, scenario_id int NOT " \
                 "NULL, PRIMARY KEY(id), " \
                 "FOREIGN KEY (scenario_id) REFERENCES Scenario(id) ON DELETE CASCADE ON UPDATE " \
                 "CASCADE) "

section_query = "CREATE TABLE IF NOT EXISTS Section(id int NOT NULL, name varchar(50), " \
                "number varchar(15), hours decimal(4,2) DEFAULT 1.5, num_students int DEFAULT 0, " \
                "course_id " \
                "int NOT NULL, schedule_id int NOT NULL, PRIMARY KEY(id), FOREIGN KEY(course_id) " \
                "REFERENCES Course(id) ON DELETE CASCADE, FOREIGN KEY(schedule_id) REFERENCES " \
                "Schedule(id) ON DELETE CASCADE)"

block_query = "CREATE TABLE IF NOT EXISTS Block(id int NOT NULL, section_id int NOT NULL, " \
              "timeslot_id int " \
              "NOT NULL, " \
              "PRIMARY KEY(id), FOREIGN KEY(section_id) REFERENCES Section(id) ON DELETE CASCADE " \
              "ON UPDATE CASCADE, " \
              "FOREIGN KEY(timeslot_id) REFERENCES TimeSlot(id))"

cursor.execute(lab_query)
cursor.execute(teacher_query)
cursor.execute(course_query)
cursor.execute(timeslot_query)
cursor.execute(scenario_query)
cursor.execute(schedule_query)
cursor.execute(section_query)
cursor.execute(block_query)

cursor.execute("SHOW TABLES")

print("Following tables exist in the database:")

for x in cursor:
    print(x)
