import os 
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text 
from sqlalchemy.exc import IntegrityError

load_dotenv()

app = Flask(__name__)
CORS(app)

engine = create_engine(os.environ['DATABASE_URL'])


# --- GET ALL METHODS ---
@app.get("/teachers")
def db_teachers():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM teachers")).mappings().all()
    return jsonify([dict(r) for r in rows])

@app.get("/students")
def db_students():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM students")).mappings().all()
    return jsonify([dict(r) for r in rows])

@app.get("/classes")
def db_classes():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM classes")).mappings().all()
    return jsonify([dict(r) for r in rows])

@app.get("/enrollments")
def db_enrollments():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM enrollments")).mappings().all()
    return jsonify([dict(r) for r in rows])

@app.get("/activities")
def db_activities():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM activities")).mappings().all()
    return jsonify([dict(r) for r in rows])

@app.get("/submissions")
def db_submissions():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM submissions")).mappings().all()
    return jsonify([dict(r) for r in rows])

@app.get("/submission_events")
def db_submissions_events():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM submission_events")).mappings().all()
    return jsonify([dict(r) for r in rows])



# --- POST ALL METHODS ---

ALLOWED = {
    None: {"completed"},
    "completed": {"received", "not_received"},
    "not_received": {"completed"},
    "received": {"feedback_given"},
    "feedback_given": set(),
}

@app.post("/submissions/<int:submission_id>/events")
def add_event(submission_id):
    data = request.get_json() or {}
    event_type = data.get("event_type")
    note = data.get("note")

    with engine.begin() as conn:
        # 1. does the submission exist, and is it homework?
        sub = conn.execute(text("""
        SELECT a.type
        FROM submissions s
        JOIN activities a ON a.id = s.activity_id
        WHERE s.id = :id"""),
        {"id":submission_id}).mappings().first()
        if sub is None:
            return jsonify({"error":"Submission not found"}), 404
        if sub["type"] != "assignment":
            return jsonify({"error": "Exams have no delivery workflow"}), 409

        # 2. What is the current state? (the latest event)
        last = conn.execute(text("""
        SELECT event_type
        FROM submission_events
        WHERE submission_id = :id
        ORDER BY created_at DESC, id DESC
        LIMIT 1
        """), {"id": submission_id}).mappings().first()
        current = last["event_type"] if last else None

        # 3. is the requested move allowed from here?
        if event_type not in ALLOWED[current]:
            return jsonify({"error": f"'{event_type} is not allowed after '{current}'"}), 409

        # 4. store the event
        new = conn.execute(text("""
        INSERT INTO submission_events (submission_id, event_type, note)
        VALUES (:id, :event_type, :note)
        RETURNING id, submission_id, event_type, note, created_at
        """), {"id":submission_id, "event_type":event_type, "note":note}).mappings().first()
    
    return jsonify(dict(new)), 201


# Submissions POST

@app.post("/activities")
def create_activity():
    data = request.get_json() or {}

    required = ['class_id', 'title', 'description', 'due_date', 'max_score', 'type']
    missing = [k for k in required if data.get(k) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    
    try:
        with engine.begin() as conn:
            activity = conn.execute(text("""
                INSERT INTO activities (class_id, title, description, due_date, max_score, type)
                VALUES (:class_id, :title, :description, :due_date, :max_score, :type)
                RETURNING id, class_id, title, description, due_date, max_score, type
            """), data).mappings().first()

            created = conn.execute(text("""
                INSERT INTO submissions (activity_id, student_id)
                SELECT :activity_id, e.student_id
                FROM enrollments e
                WHERE e.class_id = :class_id
            """), {"activity_id": activity['id'], "class_id":data['class_id']})
    except IntegrityError:
        return jsonify({"error": "Invalid data: does the class exist, and is type 'assignment' or 'exam'?"}), 400
    
    result = dict(activity)
    result['submissions_created'] = created.rowcount
    return jsonify(result), 201


if __name__ == "__main__":
    app.run(debug=True)