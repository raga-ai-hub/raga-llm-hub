"""
Helper functions
"""

import hashlib
import json
import uuid

import numpy as np


def generate_fingerprint(input_data):
    """
    A function to generate a SHA-256 fingerprint from input data, which can be either a string or a JSON-formatted string.
    The function takes input_data as a parameter and returns the hexadecimal representation of the generated digest.
    """
    # If the input_data is not a string, convert it to a JSON-formatted string
    if not isinstance(input_data, str):
        input_data = json.dumps(input_data, sort_keys=True)

    # Encode the input data to bytes, ensuring consistent encoding
    input_bytes = input_data.encode("utf-8")

    # Create a SHA-256 hash object
    hasher = hashlib.sha256()

    # Pass the bytes to the hasher
    hasher.update(input_bytes)

    # Return the hexadecimal representation of the digest
    return hasher.hexdigest()


class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for numpy data types"""

    def default(self, obj):
        try:
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return super(NumpyEncoder, self).default(obj)
        except TypeError:
            print(f"Type not handled: {type(obj)}")
            raise


def generate_unique_name():
    """
    Generate a unique name for the test.

    Returns:
        str: A unique name for the test.
    """
    return str(uuid.uuid4())
