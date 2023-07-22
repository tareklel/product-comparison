from app.setup_comparison import setup_comparison

if __name__ == '__main__':
    setup = setup_comparison()
    setup.find_files()
    setup.find_combinations()
