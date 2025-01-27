import datetime

from config import DATABASE_URI, JWT_SECRET_KEY
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configure Flask app with SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure JWT
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)

db = SQLAlchemy(app)


###################################
# MODELS
###################################


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    access_token = db.Column(db.String(500), nullable=True)

    def __init__(self, username, password, full_name):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.full_name = full_name

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class TestRun(db.Model):
    __tablename__ = "test_runs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())


class CPUUsage(db.Model):
    __tablename__ = "cpu_usage"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_run_id = db.Column(db.Integer, db.ForeignKey("test_runs.id"), nullable=False)
    usage_percent = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now())

    # Relationship
    test_run = db.relationship(
        "TestRun",
        backref=db.backref("cpu_entries", lazy=True, cascade="all, delete-orphan"),
    )


###################################
# ROUTES
###################################


@app.route("/initdb", methods=["GET"])
def initdb():
    """
    A helper route to create or re-create the database tables.
    Not recommended for production usage directly as a route.
    """
    db.drop_all()
    db.create_all()

    # Optionally, create a demo user:
    demo_user = User(username="demo", password="demo123", full_name="Demo User")
    db.session.add(demo_user)

    # Optionally, create a demo test run:
    test_run_demo = TestRun(name="Load Test #1")
    db.session.add(test_run_demo)

    db.session.commit()
    return jsonify({"message": "Database tables created and demo data added."}), 200


@app.route("/login", methods=["POST"])
def login():
    """
    Authenticates the user with username and password.
    Returns the access_token if successful.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.username)

    user.access_token = access_token
    db.session.commit()

    return jsonify({"full_name": user.full_name, "access_token": access_token}), 200


@app.route("/test_runs/<int:test_run_id>/cpu_usage", methods=["POST"])
@jwt_required()
def create_cpu_usage(test_run_id):
    """
    Creates a CPU usage record linked to a specific test run (by ID).
    """
    test_run = TestRun.query.get(test_run_id)
    if not test_run:
        return jsonify({"message": "Test run not found"}), 404

    data = request.get_json()
    usage_percent = data.get("usage_percent")

    if usage_percent is None:
        return jsonify({"message": "Missing usage_percent in request"}), 400

    cpu_entry = CPUUsage(
        test_run_id=test_run_id,
        usage_percent=usage_percent,
    )
    db.session.add(cpu_entry)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "CPU usage data created",
                "cpu_usage_id": cpu_entry.id,
                "test_run_id": cpu_entry.test_run_id,
                "usage_percent": cpu_entry.usage_percent,
            }
        ),
        201,
    )


@app.route("/test_runs/<int:test_run_id>/cpu_usage", methods=["GET"])
@jwt_required()
def read_cpu_usage(test_run_id):
    """
    Returns all CPU usage entries for a specified test run (by ID).
    """
    test_run = TestRun.query.get(test_run_id)
    if not test_run:
        return jsonify({"message": "Test run not found"}), 404

    cpu_entries = CPUUsage.query.filter_by(test_run_id=test_run_id).all()

    output = []
    for entry in cpu_entries:
        output.append(
            {
                "id": entry.id,
                "usage_percent": entry.usage_percent,
                "timestamp": entry.timestamp.isoformat(),
            }
        )

    return (
        jsonify(
            {
                "test_run_id": test_run_id,
                "test_run_name": test_run.name,
                "cpu_usage": output,
            }
        ),
        200,
    )


if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True, host="0.0.0.0", port=8888)
