"""
DBManager: Manage the SQLite database for storing evaluation results.
"""

import datetime
import json
import sqlite3

from .utils.utils import NumpyEncoder


class TrackManager:
    """
    Class for managing the database.
    """

    def __init__(self, db_path, tracker_name):
        """
        Initializes a new instance of the class with the specified database path.
        Parameters:
            db_path (str): The path to the database file.
        """
        self.conn = sqlite3.connect(db_path)
        self._initialize_database(tracker_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _initialize_database(self, tracker_name):
        """Initialize the SQLite database and create required tables if they don't exist."""
        with self.conn as conn:
            cursor = conn.cursor()
            create_command = (
                "CREATE TABLE IF NOT EXISTS "
                + tracker_name
                + " (time_id INTEGER PRIMARY KEY,details TEXT)"
            )
            cursor.execute(create_command)
        print("Table created", tracker_name)
        print("command used", create_command)

    def _check_eval_name_exists(self, tracker_name):
        """Check if a tracker_name already exists in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM " + tracker_name)
        return cursor.fetchall() is not None

    def execute_query(self, query, params=(), fetchone=False):
        """Execute a database query safely."""
        try:
            with self.conn as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetchone:
                    return cursor.fetchone()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            raise

    def save_run_details(self, tracker_name, final_results):
        """Save or append the details of the current test run to the database with a timestamp."""
        details = json.dumps(final_results, indent=4, cls=NumpyEncoder)
        timestamp = datetime.datetime.now().isoformat()
        details_with_timestamp = {"timestamp": timestamp, "details": details}
        #    "INSERT INTO test_runs (eval_name, details) VALUES (?, ?)",
        #           (eval_name, json.dumps([details_with_timestamp], indent=4)),
        self.execute_query(
            "INSERT INTO " + tracker_name + "(details) VALUES (?)",
            (json.dumps([details_with_timestamp], indent=4),),
        )

        print(
            f"Test run details saved/updated under TRACKER name '{tracker_name}' with timestamp {timestamp}."
        )

    def retrieve_run_details(self, tracker_name):
        """Retrieve and print details of a previous test run by tracker_name."""
        details = self.execute_query(
            "SELECT details FROM " + tracker_name,
            fetchone=True,
        )
        if details:
            print(json.dumps(json.loads(details[0]), indent=4))
        else:
            print(f"No test run found for tracker name '{tracker_name}'.")

    def __load_previous_eval(self, tracker_name):
        """Load details of a previous test run by tracker_name, raising exception if not found."""
        details = self.execute_query(
            "SELECT details FROM " + tracker_name,
            fetchone=True,
        )
        if not details:
            raise ValueError(f"No test run found for tracker name '{tracker_name}'.")

        final_results = json.loads(details[0])
        print(f"Loaded test run for eval name '{tracker_name}'.")
        return final_results
