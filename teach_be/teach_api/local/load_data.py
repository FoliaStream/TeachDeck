import csv, os
import psycopg
from dotenv import load_dotenv

load_dotenv()

# --- Teachers ---
# with psycopg.connect(os.environ['DATABASE_URL']) as conn:
#     with conn.cursor() as cur:
#         with open(f"{os.getcwd()}/teach_be/teach_api/local/teachers.csv", newline="", encoding="utf-8") as f:
#             for row in csv.DictReader(f):
#                 cur.execute(
#                     "INSERT INTO teachers (name, email, phone, password_hash) VALUES (%s, %s, %s, %s)",
#                     (row['name'], row['email'], row['phone'], row['password_hash']),
#                 )

# --- Students ---
# with psycopg.connect(os.environ['DATABASE_URL']) as conn:
#     with conn.cursor() as cur:
#         with open(f"{os.getcwd()}/teach_be/teach_api/local/students.csv", newline="", encoding="utf-8") as f:
#             for row in csv.DictReader(f):
#                 cur.execute(
#                     "INSERT INTO students (name, dob, email, phone, password_hash) VALUES (%s, %s, %s, %s, %s)",
#                     (row['name'], row['dob'], row['email'], row['phone'], row['password_hash']),
#                 )

# --- Classes ---
# with psycopg.connect(os.environ['DATABASE_URL']) as conn:
#     with conn.cursor() as cur:
#         with open(f"{os.getcwd()}/teach_be/teach_api/local/classes.csv", newline="", encoding="utf-8") as f:
#             for row in csv.DictReader(f):
#                 cur.execute(
#                     "SELECT id FROM teachers WHERE email = %s",
#                     (row['teacher_email'],),
#                 )
#                 teacher_id = cur.fetchone()[0]
#                 cur.execute(
#                     "INSERT INTO classes (name, teacher_id, level) VALUES (%s, %s, %s)",
#                     (row['name'], teacher_id, row['level']),
#                 )

# --- Enrollments ---
# with psycopg.connect(os.environ['DATABASE_URL']) as conn:
#     with conn.cursor() as cur:
#         with open(f"{os.getcwd()}/teach_be/teach_api/local/enrollments.csv", newline="", encoding="utf-8") as f:
#             for row in csv.DictReader(f):
#                 cur.execute(
#                     "SELECT id FROM students WHERE email = %s", (row['student_email'],)
#                 )
#                 student_id = cur.fetchone()[0]
#                 cur.execute(
#                     "SELECT id FROM classes WHERE name = %s", (row['class_name'],)
#                 )
#                 class_id = cur.fetchone()[0]
#                 cur.execute(
#                     "INSERT INTO enrollments (student_id, class_id) VALUES (%s, %s)",
#                     (student_id, class_id),
#                 )

# --- Activities ---
# with psycopg.connect(os.environ['DATABASE_URL']) as conn:
#     with conn.cursor() as cur:
#         with open(f"{os.getcwd()}/teach_be/teach_api/local/activities.csv", newline="", encoding="utf-8") as f:
#             for row in csv.DictReader(f):
#                 cur.execute(
#                     "SELECT id FROM classes WHERE name = %s", (row['class_name'],)
#                 )
#                 class_id = cur.fetchone()[0]
#                 cur.execute(
#                     "INSERT INTO activities (title, description, due_date, max_score, type, class_id) VALUES (%s, %s, %s, %s, %s, %s)", 
#                     (row['title'], row['description'], row['due_date'], row['max_score'], row['type'], class_id )
#                 )


# --- Submissions ---

# def clean(value):
#     if value == "":
#         return None
#     return value


# with psycopg.connect(os.environ['DATABASE_URL']) as conn:
#     with conn.cursor() as cur:
#         with open(f"{os.getcwd()}/teach_be/teach_api/local/submissions.csv", newline="", encoding="utf-8") as f:
#             for row in csv.DictReader(f):
#                 # lookup 1: student id from the email
#                 cur.execute(
#                     "SELECT id FROM students WHERE email = %s",
#                     (row['student_email'],),
#                 )
#                 student_id = cur.fetchone()[0]

#                 # lookup 2: activity id from the class name + activity title
#                 cur.execute(
#                     """
#                     SELECT a.id
#                     FROM activities a
#                     JOIN classes c ON c.id = a.class_id
#                     WHERE c.name = %s AND a.title = %s
#                     """,
#                     (row['class_name'], row['activity_title']),
#                 )
#                 activity_id = cur.fetchone()[0]

#                 # insert: empty cells become NULL through clean()
#                 cur.execute(
#                     """
#                     INSERT INTO submissions
#                         (activity_id, student_id, submitted_at, grade, feedback)
#                     VALUES (%s, %s, %s, %s, %s)
#                     """,
#                     (
#                         activity_id,
#                         student_id,
#                         clean(row['submitted_at']),
#                         clean(row['grade']),
#                         clean(row['feedback']),
#                     ),
#                 )

# --- Events ---
def clean(value):
    if value == "":
        return None
    return value
 

with psycopg.connect(os.environ['DATABASE_URL']) as conn:
    with conn.cursor() as cur:
        with open(f"{os.getcwd()}/teach_be/teach_api/local/events.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                # step 1: the student's id, from the email
                cur.execute(
                    "SELECT id FROM students WHERE email = %s",
                    (row['student_email'],),
                )
                student_id = cur.fetchone()[0]
 
                # step 2: the activity's id, from class name + activity title (a join)
                cur.execute(
                    """
                    SELECT a.id
                    FROM activities a
                    JOIN classes c ON c.id = a.class_id
                    WHERE c.name = %s AND a.title = %s
                    """,
                    (row['class_name'], row['activity_title']),
                )
                activity_id = cur.fetchone()[0]
 
                # step 3: the submission's id, from the (activity, student) pair
                cur.execute(
                    "SELECT id FROM submissions WHERE activity_id = %s AND student_id = %s",
                    (activity_id, student_id),
                )
                submission_id = cur.fetchone()[0]
 
                # step 4: insert the event; the timestamp comes from the file
                cur.execute(
                    """
                    INSERT INTO submission_events (submission_id, event_type, note, created_at)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (submission_id, row['event_type'], clean(row['note']), row['created_at']),
                )