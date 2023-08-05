from app.setup_comparison import setup_comparison
import argparse


if __name__ == '__main__':

    # pass config file path
    parser = argparse.ArgumentParser(description='Path to config file')
    parser.add_argument('config_file_path', type=str)
    conf_file_path = parser.parse_args()
    print(conf_file_path)

    setup = setup_comparison(conf=conf_file_path.config_file_path)
    setup.set_input_files()
    setup.standardize_files()
    setup.create_json()
    setup.update_json(modified=True)
