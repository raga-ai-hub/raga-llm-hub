"""
Test Data for testing the package
"""

import pkgutil
import warnings

import toml


def get_data(test_name, num_samples=1):
    """
    Retrieves data for the given test name and number of samples from a TOML file.

    Args:
        test_name (str): The name of the test.
        num_samples (int, optional): Number of samples to retrieve. Defaults to 1.

    Returns:
        dict: A dictionary containing response data for the test.
    """

    raw_data = pkgutil.get_data(
        "raga_llm_hub", f"tests/test_data/data_files/{test_name}.toml"
    )

    if raw_data is not None:  # Check if data was successfully loaded
        data_str = raw_data.decode("utf-8")  # Decode bytes to string
        data = toml.loads(data_str)
    else:
        raise FileNotFoundError(f"Could not find data for {test_name}.")

    actual_samples = len(data.keys())
    if actual_samples < num_samples:
        warnings.warn(
            f"Requested {num_samples} test samples, but only {actual_samples} are available."
        )

    response_data = {}
    for _, values in data.items():
        for key, data in values.items():
            if key not in response_data:
                response_data[key] = []

            if len(response_data[key]) >= num_samples:
                break

            response_data[key].append(data)

    return response_data


# if __name__ == "__main__":
#     data_folder_path = "data_files"
#     test_data = get_data("relevancy_test", 1)
#     print(test_data)
