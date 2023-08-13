from app.setup_comparison import setup_comparison
import argparse
import os


if __name__ == '__main__':

    # pass config file path
    parser = argparse.ArgumentParser(description='Path to config file')
    parser.add_argument('config_file_path', type=str)
    conf_file_path = parser.parse_args()
    # set class variables
    setup = setup_comparison(conf=conf_file_path.config_file_path)
    setup.set_input_files()
    # standardize files using dictionary
    setup.standardize_files()
    # create json file for output
    setup.create_json()
    # update json file with product tree
    setup.update_json(modified=True)
