import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
from app.pool_for_comparison import PoolForComparison, ComparePool
from PIL import Image, ImageTk


class LoadPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Product matching")

        # Add button to trigger file selection
        self.load_button = tk.Button(
            self.root, text="Load Config", command=self.load_config_and_init_class)
        self.load_button.pack()

    def open_main_gui(self):
        if self.pool_object:
            GuiPoolForComparison(self)
        else:
            no_dataset = 'No config file loaded'
            messagebox.showerror(title='No config file', message=no_dataset)

    # Function to handle file selection
    def load_config_and_init_class(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yml")])
        if not file_path:
            return

        self.pool_object = PoolForComparison(file_path)
        self.open_main_gui()


class GuiPoolForComparison(tk.Toplevel):
    def __init__(self, obj: LoadPage):
        tk.Toplevel.__init__(self)
        self.title('Pool for Comparison')
        self.geometry("1300x700")
        self.pool = obj.pool_object
        self.pool.create_pair_file()
        self.pool.remove_matched_from_tree()
        self.pool.get_unpaired()
        self.options = list(self.pool.describe_unpaired.keys())

        # Create a StringVar to hold the selected value
        selected_value = tk.StringVar(self)
        selected_value.set("Select group")  # default value
        # Create the dropdown menu
        dropdown = tk.OptionMenu(self, selected_value, *self.options)
        dropdown.pack()
        # Create the 'Select' button
        select_button = tk.Button(
            self, text="Select", command=lambda: self.select_group(selected_value.get()))
        select_button.pack()

    def select_group(self, selected_value):
        print(selected_value)
        if self.pool.file['images_dest']:
            self.pool.start_compare_pool(selected_value, self.pool.file['images_dest'])
        else:
            self.pool.start_compare_pool(selected_value)
        
        GuiComparePool(self.pool.comparepool)


class GuiComparePool(tk.Toplevel):
    def __init__(self, obj: ComparePool):
        tk.Toplevel.__init__(self)
        self.obj = obj
        self.title('Compare Pool')
        self.geometry("1300x900")
        self.obj.select_compare_a()
        self.obj.select_compare_b()
        self.group_name = tk.Label(self, text=self.obj.group_name)
        self.group_name.grid(sticky='w', row=0, column=1)

        self.next_button = tk.Button(
            self, text='Next Compare Group', command=lambda: '')
        self.save_close_button = tk.Button(
            self, text='Save and Close', command=lambda: '')
        self.next_button.grid(sticky='w', row=0, column=2)
        self.save_close_button.grid(sticky='w', row=0, column=3)

        # add for spacing
        empty_frame = tk.Frame(self, height=20, width=20)
        empty_frame.grid(sticky='w', row=1, column=1)

        # get compare a products
        self.pool_name_a = tk.Label(self, text=self.obj.first_group_key)
        self.compare_a_name = tk.Label(
            self, text=next(iter(self.obj.compare_a)))
        self.compare_a_description = tk.Label(
            self, text=self.obj.compare_a[next(iter(self.obj.compare_a))])

        self.pool_name_a.grid(sticky='w', row=2, column=1)
        self.compare_a_name.grid(sticky='w', row=3, column=1)
        self.compare_a_description.grid(sticky='w', row=4, column=1)


        # get image for compare a
        self.image_a = self.get_images(self.obj.first_group_key, next(iter(self.obj.compare_a)))
        self.image1_label = tk.Label(self, image=self.image_a)


        self.image1_label.grid(sticky='w', row=5, column=1)


        # add for spacing 2
        empty_frame2 = tk.Frame(self, height=20, width=20)
        empty_frame2.grid(sticky='w', row=6, column=0)

        self.pool_name_b = tk.Label(self, text=self.obj.second_group_key)
        self.pool_name_b.grid(sticky='w', row=7, column=1)

        # Loop through the dictionary and create radio buttons
        radio_selected_key = tk.StringVar()
        # Frame for radio buttons (using pack)

        # Create a canvas and a vertical scrollbar
        self.canvas_scroll = tk.Canvas(self, width=900, height=500)

        self.canvas_scroll.grid(sticky='w', row=8, column=1)
        self.scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas_scroll.yview)

        # Configure the canvas
        self.canvas_scroll.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(sticky='ns', row=8, column=0)

        # Frame inside canvas with radio
        self.frame1 = tk.Frame(self.canvas_scroll)
        self.frame1.grid(sticky='w', row=0, column=0)
        for key, value in self.obj.product_b_list.items():
            tk.Radiobutton(self.frame1,
                           text=key,
                           variable=radio_selected_key,
                           value=key).pack(anchor='w')
            tk.Label(self.frame1, text=value, wraplength=900).pack(anchor='w')

        self.canvas_scroll.create_window(
            (0, 0), window=self.frame1, anchor="nw")

        # Update the scrollregion after configuring the interior frame
        self.frame1.update_idletasks()
        self.canvas_scroll.config(scrollregion=self.canvas_scroll.bbox("all"))

        # Add a button to print the selected value
        self.radio_select = tk.Button(
            self, text="Match products", command='')

        self.radio_select.grid(sticky='w', row=9, column=1)

    def get_image_files(self, directory, extensions=['.jpg', '.png', '.gif']):
        return [os.path.join(directory, f) for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) and any(f.lower().endswith(ext) for ext in extensions)]

    def get_images(self, group, key):

        images_dest = self.obj.args[0][0][group]
        image_dir = [os.path.join(images_dest, d) for d in  os.listdir(images_dest) if os.path.isdir(os.path.join(images_dest, d)) and key in d][0]
        # get images path from list
        images = self.get_image_files(image_dir)
        print(images)
        image = Image.open(images[0])
        image = image.resize((200, 200))
        photo = ImageTk.PhotoImage(image)
        return photo




        


# Create Tkinter window and the app instance
if __name__ == '__main__':
    root = tk.Tk()
    app = LoadPage(root)
    # initiate steps after to continue testing
    app.pool_object = PoolForComparison(
        'app/tests/resources/pool_for_comparison_gui.yml')
    pool = GuiPoolForComparison(app)
    pool.select_group(
        'crawl_date.2023-06-18.country.sa.gender.women.brand.Burberry.category.shoes.site')
    root.mainloop()
