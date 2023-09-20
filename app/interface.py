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
        self.options = list(self.pool.describe_unpaired)

        # Create a StringVar to hold the selected value
        self.selected_value = tk.StringVar(self)
        self.selected_value.set("Select group")  # default value
        # Create the dropdown menu
        self.dropdown = tk.OptionMenu(self, self.selected_value, *self.options)
        self.dropdown.pack()
        # Create the 'Select' button
        select_button = tk.Button(
            self, text="Select", command=lambda: self.select_group(selected_value.get()))
        select_button.pack()

        print_matched = tk.Button(
            self, text="Print Matched", command=self.print_matched)
        print_matched.pack()

        consolidate = tk.Button(
            self, text="Consolidate and Save", command=self.consolidate_and_save)
        consolidate.pack()

    def select_group(self, selected_value):
        if any(selected_value in d for d in self.pool.matched):
            print('Group matched has already been saved')
        if self.pool.file['images_dest']:
            self.pool.start_compare_pool(
                selected_value, self.pool.file['images_dest'])
        else:
            self.pool.start_compare_pool(selected_value)

        GuiComparePool(self.pool)
    
    def print_matched(self):
        print(self.pool.matched)
    
    def consolidate_and_save(self):
        self.pool.consolidate_matched()
        self.pool.save_pair_df()
        # Create a StringVar to hold the selected value
        self.dropdown['menu'].delete(0, 'end')
        self.selected_value.set("Select group")  # default value
        # Create the dropdown menu
        for option in self.options:
            self.dropdown['menu'].add_command(label=option, command = tk._setit(self.selected_value, option))


class GuiComparePool(tk.Toplevel):
    def __init__(self, pool: ComparePool):
        tk.Toplevel.__init__(self)
        self.pool = pool
        self.obj = self.pool.comparepool
        self.title('Compare Pool')
        self.geometry("1300x900")
        self.obj.select_compare_a()
        self.obj.select_compare_b()

        # Create a canvas and a vertical scrollbar
        self.canvas = tk.Canvas(self)
        self.main_scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.main_scrollbar.pack(side="left", fill="y")

        # Configure the canvas
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.main_scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        # Create a frame inside the canvas and add it to the canvas window
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.group_name = tk.Label(self.frame, text=self.obj.group_name)
        self.group_name.grid(sticky='w', row=0, column=1)

        self.next_button = tk.Button(
            self.frame, text='Next Compare Product', command=self.next_compare_product)
        self.save_close_button = tk.Button(
            self.frame, text='Save and Close', command=self.save_close)
        self.next_button.grid(sticky='w', row=0, column=3)
        self.save_close_button.grid(sticky='w', row=0, column=4)

        # add for spacing
        empty_frame = tk.Frame(self.frame, height=20, width=20)
        empty_frame.grid(sticky='w', row=1, column=1)

        # get compare a products
        self.pool_name_a = tk.Label(self.frame, text=self.obj.first_group_key)
        self.compare_a_name = tk.Label(
            self.frame, text=next(iter(self.obj.compare_a)))
        self.compare_a_description = tk.Label(
            self.frame, text=self.obj.compare_a[next(iter(self.obj.compare_a))], wraplength=600)

        self.pool_name_a.grid(sticky='w', row=2, column=1)
        self.compare_a_name.grid(sticky='w', row=3, column=1)
        self.compare_a_description.grid(sticky='w', row=4, column=1)

        # get image for compare a
        self.image_a = self.get_images(
            self.obj.first_group_key, next(iter(self.obj.compare_a)))
        if self.image_a:
            self.image1_label = tk.Label(self.frame, image=self.image_a)
            self.image1_label.grid(sticky='w', row=4, column=2)

        # add for spacing 2
        empty_frame2 = tk.Frame(self.frame, height=20, width=20)
        empty_frame2.grid(sticky='w', row=6, column=0)

        self.pool_name_b = tk.Label(self.frame, text=self.obj.second_group_key)
        self.pool_name_b.grid(sticky='w', row=7, column=1)

        # Loop through the dictionary and create radio buttons
        self.radio_selected_key = tk.StringVar()
        # Frame for radio buttons (using pack)

        # Create a canvas and a vertical scrollbar
        self.canvas_compare2 = tk.Canvas(self.frame, width=700, height=500)

        self.canvas_compare2.grid(sticky='w', row=8, column=1)
        self.compare_2_scrollbar = tk.Scrollbar(
            self.frame, orient="vertical", command=self.canvas_compare2.yview)

        # Configure the canvas
        self.canvas_compare2.config(
            yscrollcommand=self.compare_2_scrollbar.set)
        self.compare_2_scrollbar.grid(sticky='ns', row=8, column=0)

        # Frame inside canvas with radio
        self.frame1 = tk.Frame(self.canvas_compare2)
        self.frame1.grid(sticky='w', row=0, column=0)
        self.image2_dict = {}
        for i, (key, value) in enumerate(self.obj.product_b_list.items()):
            tk.Radiobutton(self.frame1,
                           text=key,
                           variable=self.radio_selected_key,
                           value=key).grid(sticky='ns', row=i * 2, column=0)
            tk.Label(self.frame1, text=value, wraplength=600).grid(
                sticky='ns', row=i * 2 + 1, column=0)
            # get image for compare a
            image_b = self.get_images(
                self.obj.second_group_key, key)
            if image_b:
                self.image2_dict[key] = image_b
                self.imageb_label = tk.Label(
                    self.frame1, image=self.image2_dict[key])
                self.imageb_label.grid(sticky='ns', row=i * 2 + 1, column=1)

        self.canvas_compare2.create_window(
            (0, 0), window=self.frame1, anchor="nw")

        # Update the scrollregion after configuring the interior frame
        self.frame1.update_idletasks()
        self.canvas_compare2.config(
            scrollregion=self.canvas_compare2.bbox("all"))

        # Add a button to print the selected value
        self.radio_select = tk.Button(
            self.frame, text="Match products", command=lambda: self.match_products(self.radio_selected_key.get()))

        self.radio_select.grid(sticky='w', row=0, column=2)

    def get_image_files(self, directory, extensions=['.jpg', '.png', '.gif']):
        return [os.path.join(directory, f) for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) and any(f.lower().endswith(ext) for ext in extensions)]

    def get_images(self, group, key):

        images_dest = self.obj.args[0][0][group]
        image_dir = [os.path.join(images_dest, d) for d in os.listdir(
            images_dest) if os.path.isdir(os.path.join(images_dest, d)) and key in d]
        if image_dir:
            image_dir = image_dir[0]
        else:
            return None
        # get images path from list
        images = self.get_image_files(image_dir)
        image = Image.open(images[0])
        image = image.resize((100, 100))
        photo = ImageTk.PhotoImage(image)
        return photo

    def next_compare_product(self):
        """Change compare product a"""
        self.obj.select_next_a()
        self.compare_a_name.config(text=next(iter(self.obj.compare_a)))
        self.compare_a_description.config(
            text=self.obj.compare_a[next(iter(self.obj.compare_a))], wraplength=600)

        # get image for compare a
        self.image_a = self.get_images(
            self.obj.first_group_key, next(iter(self.obj.compare_a)))
        if self.image_a:
            self.image1_label.config(image=self.image_a)
    
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
    
    def match_products(self, product):
        self.obj.select_match(product)
        self.clear_frame(self.frame1)
        self.image2_dict = {}
        self.next_compare_product()
        for i, (key, value) in enumerate(self.obj.product_b_list.items()):
            tk.Radiobutton(self.frame1,
                           text=key,
                           variable=self.radio_selected_key,
                           value=key).grid(sticky='ns', row=i * 2, column=0)
            tk.Label(self.frame1, text=value, wraplength=600).grid(
                sticky='ns', row=i * 2 + 1, column=0)
            # get image for compare a
            image_b = self.get_images(
                self.obj.second_group_key, key)
            if image_b:
                self.image2_dict[key] = image_b
                self.imageb_label = tk.Label(
                    self.frame1, image=self.image2_dict[key])
                self.imageb_label.grid(sticky='ns', row=i * 2 + 1, column=1)
    
    def save_close(self):
        self.pool.update_matched()
        self.destroy()


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
