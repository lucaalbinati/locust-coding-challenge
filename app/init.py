#!/usr/bin/env python

"""
init_db.py: A standalone script to initialize (drop & create) database tables.
WARNING: This will destroy all existing data in the configured database.
"""

from app import app, db, User, TestRun


def init_db():
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()

        # Seed some sample data
        demo_user = User(username="demo", password="demo123", full_name="Demo User")
        db.session.add(demo_user)

        test_run_demo = TestRun(name="Load Test #1")
        db.session.add(test_run_demo)

        db.session.commit()
        print("Database initialized, tables created, and demo data inserted.")

if __name__ == "__main__":
    init_db()
