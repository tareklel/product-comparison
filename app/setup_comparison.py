import os
import glob


class setup_comparison:
    """
    get and organize products to compare
    """

    def __init__(self, input_path='input/', output_path='output/'):
        self.input_path = input_path
        self.output_path = output_path

    def read_files(self):
        """
        Read all csvs in input folder
        """
        try:
            self.csv_files = glob.glob(os.path.join(self.input_path, '*.csv'))
            if not self.csv_files:
                raise FileNotFoundError("No CSV files found in the specified directory.")
        except OSError as e:
            print(f"Error reading directory: {e}")
        
