from pathlib import Path
import pandas as pd


class Olist:
    """
    The Olist class provides methods to interact with Olist's e-commerce data.

    Methods:
        get_data():
            Loads and returns a dictionary where keys are dataset names (e.g., 'sellers', 'orders')
            and values are pandas DataFrames loaded from corresponding CSV files.
    """

    def __init__(self):
        self.data = None

    def get_data(self):
        """
        This function returns a Python dict.
        Its keys should be 'sellers', 'orders', 'order_items' etc...
        Its values should be pandas.DataFrames loaded from csv files
        """
        csv_path = Path("/Users/gechen/Projects/OlistDataAnalysis/OlistData/data/csv").expanduser()
        file_paths = list(csv_path.iterdir())
        file_names = [file.name for file in file_paths]
        key_name = [name.replace("_dataset.csv", "")
                 .replace(".csv", "")
                 .replace("olist_", "")
            for name in file_names]

        data={}
        for key, path in zip(key_name, file_paths):
            data[key] = pd.read_csv(path)

        self.data = data
        return self.data
