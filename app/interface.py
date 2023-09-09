import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from app.pool_for_comparison import PoolForComparison

class LoadPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Product matching")
        
        # Add button to trigger file selection
        self.load_button = tk.Button(self.root, text="Load Config", command=self.load_config_and_init_class)
        self.load_button.pack()
    
    def open_main_gui(self):
        if self.pool_object:
            GuiPoolForComparison(self)
        else:
            no_dataset = 'No config file loaded'
            messagebox.showerror(title='No config file', message=no_dataset)
        
    # Function to handle file selection
    def load_config_and_init_class(self):
        file_path = filedialog.askopenfilename(filetypes=[("YAML files", "*.yml")])
        if not file_path:
            return
        
        self.pool_object = PoolForComparison(file_path)
        self.open_main_gui()

class GuiPoolForComparison(tk.Toplevel):
    def __init__(self, obj:LoadPage):
        tk.Toplevel.__init__(self)
        self.title('Pool for Comparison')
        self.geometry("700x700")
        self.pool = obj.pool_object
        self.pool.create_pair_file()
        self.pool.remove_matched_from_tree()
        self.pool.get_unpaired()
        self.options = list(self.pool.describe_unpaired.keys())

        # Create a StringVar to hold the selected value
        selected_value = tk.StringVar(self)
        selected_value.set("Select group")  # default value
        # Create the dropdown menu
        dropdown = tk.OptionMenu(self, selected_value, self.options)
        dropdown.pack()
        # Create the 'Select' button
        select_button = tk.Button(self, text="Select", command=lambda: '')
        select_button.pack()
        

    



# Create Tkinter window and the app instance
if __name__ == '__main__':
    root = tk.Tk()
    app = LoadPage(root)
    root.mainloop()
