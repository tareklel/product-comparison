import os
import glob
import csv
import yaml
import json
import pandas as pd


class setup_comparison:
    """
    get and organize products to compare
    """

    def __init__(self, conf='conf/inspecting.yml'):

        with open(conf, 'r') as file:
            conf_dict = yaml.safe_load(file)
            self.data = conf_dict['data_config']
            self.input_path = conf_dict['input_path']
            self.output_path = conf_dict['output_path']
            self.dictionary_dir = conf_dict['dictionary_dir']
            self.reference = conf_dict['reference']
            self.standard = conf_dict['standard']
            self.conf = conf_dict

    def find_files(self, path, ext):
        """
        Find all csvs in input folder
        """
        try:
            csv_files = glob.glob(os.path.join(path, f'*.{ext}'))
            if not csv_files:
                raise FileNotFoundError(
                    "No CSV files found in the specified directory.")
            return csv_files
        except OSError as e:
            print(f"Error reading directory: {e}")

    def set_input_files(self, path=None, ext='csv'):
        if not path:
            path = self.input_path

        self.input_files = self.find_files(self.input_path, ext)

    def map_df(self, df: pd.DataFrame, compare_df: pd.DataFrame, to_replace: str,
               replacement_col: str, reference_col: str
               ):
        """
        This function replaces values in 'df' based on a mapping defined in 'compare_df'. 
        'reference_col' is the column in 'df' that is compared with the columns in 'compare_df'.
        If a match is found, the corresponding value in 'to_replace' column is replaced using the mapping from 'compare_df'.
        """
        for compare in df[reference_col].unique():
            if compare in compare_df.columns:
                compare_mapping = compare_df.set_index(
                    compare)[replacement_col].to_dict()
                condition = df[reference_col] == compare
                df.loc[condition, to_replace] = df.loc[condition,
                                                       to_replace].replace(compare_mapping)
        return df

    def standardize_files(self, dictionary_dir=None, reference=None, standard=None):
        """
        Standardize input files, add standardized file objects.

        Parameters:
        - dictionary_dir: Path to the directory containing dictionary CSV files.
        - reference: Column name in the input data to be used as a reference for standardization.
        - standard: Column name in the dictionary data that contains the standard values.
        """

        if not dictionary_dir:
            dictionary_dir = self.dictionary_dir
        if not reference:
            reference = self.reference
        if not standard:
            standard = self.standard
        # Get dictionary files
        dict_files = self.find_files(dictionary_dir, 'csv')

        # Get input files
        input_files = self.input_files

        # Iterate over each input file
        for input_file in input_files:
            df = pd.read_csv(input_file)

            # Apply each dictionary to the input file
            for dict_file in dict_files:
                # Get category to replace from dictionary filename
                replacement_category = os.path.basename(
                    os.path.splitext(dict_file)[0])

                # Load dictionary data
                compare_df = pd.read_csv(dict_file)

                # Apply mapping to the data
                df = self.map_df(
                    df, compare_df, replacement_category, standard, reference)

            # Add standardized DataFrame to 'modified' attribute
            if not hasattr(self, 'modified'):
                self.modified = {}

            # Prepare modified dictionary name
            modified_dict_name = f"{os.path.basename(os.path.splitext(input_file)[0])}-modified"

            self.modified[modified_dict_name] = df

    def find_combinations(self, order: list, df: pd.DataFrame, dictionary: dict):
        """
        return nested dictionary tree with all products from files 
        """
        for _, row in df.iterrows():
            curr_dict = dictionary
            for key in order[:-1]:
                if key not in curr_dict:
                    curr_dict[key] = {}
                curr_dict = curr_dict[key]
                if str(row[key]) not in curr_dict:
                    curr_dict[str(row[key])] = {}
                curr_dict = curr_dict[str(row[key])]

            curr_dict[order[-1]] = row[order[-1]]

        return dictionary

    def create_json(self, file_json: str = None):
        if not file_json:
            input_files = [x.split('/')[-1].split('.')[0]
                           for x in self.input_files]
            files = "_".join(input_files)
            self.file_json = self.conf['tree_path']+'/'+files+'.json'
            file_json = self.file_json
        # Create an empty dictionary
        data = {}

        # Use the json.dump method to write the empty dictionary to a file
        if not os.path.exists(file_json):
            with open(file_json, 'w') as f:
                json.dump(data, f)

    def update_json(self, file_json: str=None, modified: bool=True):
        if not file_json:
            file_json = self.file_json
        with open(file_json, 'r') as f:
            dict = json.load(f)

        if modified:
            for df in self.modified.values():
                dict = self.find_combinations(
                    self.data['inpsection_order'], df, dict)
        else:
            for input_file in self.input_files:
                df = pd.read_csv(input_file)
                dict = self.find_combinations(
                    self.data['inpsection_order'], df, dict)

        with open(file_json, 'w') as f:
            json.dump(dict, f)

        return None
