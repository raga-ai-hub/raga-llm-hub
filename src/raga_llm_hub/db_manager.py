"""
DBManager: Manage the SQLite database for storing evaluation results.
"""

import datetime
import json
import sqlite3

from .utils.utils import NumpyEncoder


class DBManager:
    """
    Class for managing the database.
    """

    def __init__(self, db_path):
        """
        Initializes a new instance of the class with the specified database path.
        Parameters:
            db_path (str): The path to the database file.
        """
        self.conn = sqlite3.connect(db_path)
        self._initialize_database()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _initialize_database(self):
        """Initialize the SQLite database and create required tables if they don't exist."""
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS test_runs (
                    eval_name TEXT PRIMARY KEY,
                    details TEXT
                )
            """
            )

    def _check_eval_name_exists(self, eval_name):
        """Check if an eval_name already exists in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM test_runs WHERE eval_name=?", (eval_name,))
        return cursor.fetchone() is not None

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

    def save_run_details(self, eval_name, final_results):
        """Save or append the details of the current test run to the database with a timestamp."""
        details = json.dumps(final_results, indent=4, cls=NumpyEncoder)
        timestamp = datetime.datetime.now().isoformat()
        details_with_timestamp = {"timestamp": timestamp, "details": details}

        existing_details = self.execute_query(
            "SELECT details FROM test_runs WHERE eval_name=?",
            (eval_name,),
            fetchone=True,
        )
        if existing_details:
            existing_details_list = json.loads(existing_details[0])
            existing_details_list.append(details_with_timestamp)
            updated_details_json = json.dumps(existing_details_list, indent=4)
            self.execute_query(
                "UPDATE test_runs SET details=? WHERE eval_name=?",
                (updated_details_json, eval_name),
            )
        else:
            self.execute_query(
                "INSERT INTO test_runs (eval_name, details) VALUES (?, ?)",
                (eval_name, json.dumps([details_with_timestamp], indent=4)),
            )

        print(
            f"Test run details saved/updated under eval name '{eval_name}' with timestamp {timestamp}."
        )

    def retrieve_run_details(self, eval_name):
        """Retrieve and print details of a previous test run by eval_name."""
        details = self.execute_query(
            "SELECT details FROM test_runs WHERE eval_name=?",
            (eval_name,),
            fetchone=True,
        )
        if details:
            print(json.dumps(json.loads(details[0]), indent=4))
        else:
            print(f"No test run found for eval name '{eval_name}'.")

    def __load_previous_eval(self, eval_name):
        """Load details of a previous test run by eval_name, raising exception if not found."""
        details = self.execute_query(
            "SELECT details FROM test_runs WHERE eval_name=?",
            (eval_name,),
            fetchone=True,
        )
        if not details:
            raise ValueError(f"No test run found for eval name '{eval_name}'.")

        final_results = json.loads(details[0])
        print(f"Loaded test run for eval name '{eval_name}'.")
        return final_results
