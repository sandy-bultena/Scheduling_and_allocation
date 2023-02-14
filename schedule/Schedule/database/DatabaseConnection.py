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

stream_query = "CREATE TABLE IF NOT EXISTS Stream(id int NOT NULL, number varchar(2) NOT NULL, " \
               "description varchar(50), PRIMARY KEY (id)) "

lab_block_query = "CREATE TABLE IF NOT EXISTS LabBlock(lab_id int NOT NULL, block_id int NOT NULL, " \
                  "PRIMARY KEY(lab_id, block_id), " \
                  "FOREIGN KEY(lab_id) REFERENCES Lab(id) ON DELETE CASCADE, " \
                  "FOREIGN KEY(block_id) REFERENCES Block(id) ON DELETE CASCADE)"

teacher_block_query = "CREATE TABLE IF NOT EXISTS TeacherBlock(teacher_id int NOT NULL, block_id " \
                      "int NOT NULL, " \
                      "PRIMARY KEY(teacher_id, block_id), " \
                      "FOREIGN KEY(teacher_id) REFERENCES Teacher(id) ON DELETE CASCADE, " \
                      "FOREIGN KEY(block_id) REFERENCES Block(id) ON DELETE CASCADE)"

schedule_teachers_query = "CREATE TABLE IF NOT EXISTS ScheduleTeacher(schedule_id int NOT NULL, " \
                          "teacher_id int NOT NULL, work_release decimal(4, 2) NOT NULL, " \
                          "PRIMARY KEY(schedule_id, teacher_id), FOREIGN KEY (schedule_id) " \
                          "REFERENCES Schedule(id) ON DELETE CASCADE, " \
                          "FOREIGN KEY (teacher_id) REFERENCES Teacher(id) ON DELETE CASCADE)"

stream_section_query = "CREATE TABLE IF NOT EXISTS StreamSection(stream_id int NOT NULL, " \
                       "section_id int NOT NULL, " \
                       "PRIMARY KEY(stream_id, section_id), " \
                       "FOREIGN KEY(stream_id) REFERENCES Stream(id) ON DELETE CASCADE, " \
                       "FOREIGN KEY(section_id) REFERENCES Section(id) ON DELETE CASCADE)"

cursor.execute(lab_query)
cursor.execute(teacher_query)
cursor.execute(course_query)
cursor.execute(timeslot_query)
cursor.execute(scenario_query)
cursor.execute(schedule_query)
cursor.execute(section_query)
cursor.execute(block_query)
cursor.execute(stream_query)
cursor.execute(lab_block_query)
cursor.execute(teacher_block_query)
cursor.execute(schedule_teachers_query)
cursor.execute(stream_section_query)

cursor.execute("SHOW TABLES")

print("Following tables exist in the database:")

for x in cursor:
    print(x)
