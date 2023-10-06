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
        self.select_group_button = "Select group"

        # Create a StringVar to hold the selected value
        self.selected_value = tk.StringVar(self)
        self.selected_value.set(self.select_group_button)  # default value
        # Create the dropdown menu
        self.dropdown = tk.OptionMenu(self, self.selected_value, *self.options)
        self.dropdown.pack()

        # Label to display the selected item
        self.label_text = tk.StringVar()
        self.info_label = tk.Label(self, textvar=self.label_text)
        self.info_label.pack(pady=20)

        # attach trace to selected value
        self.selected_value.trace("w", self.dropdown_info)

        # Create the 'Select' button
        # select_button = tk.Button(
        #    self, text="Select", command=lambda: self.select_group(list(self.selected_value.get())[0]))
        select_button = tk.Button(
            self, text="Select", command=lambda: self.select_group(self.selected_value.get()))
        select_button.pack()

        print_matched = tk.Button(
            self, text="Print Matched", command=self.print_matched)
        print_matched.pack()

        consolidate = tk.Button(
            self, text="Consolidate and Save", command=self.consolidate_and_save)
        consolidate.pack()

    def dropdown_info(self, *args):
        if self.selected_value.get() == self.select_group_button:
            self.label_text.set('')
        else:
            info = self.pool.describe_unpaired[(self.selected_value.get())]
            self.label_text.set(info)

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
        self.selected_value.set(self.select_group_button)  # default value
        del self.pool.pair_df
        self.pool.create_pair_file()
        self.pool.remove_matched_from_tree()
        self.pool.get_unpaired()
        self.options = list(self.pool.describe_unpaired)
        # Create the dropdown menu
        for option in self.options:
            self.dropdown['menu'].add_command(
                label=option, command=tk._setit(self.selected_value, option))


class GuiComparePool(tk.Toplevel):
    def __init__(self, pool: ComparePool):
        tk.Toplevel.__init__(self)
        self.pool = pool
        self.obj = self.pool.comparepool
        self.title('Compare Pool')
        self.geometry("1500x900")
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

        # press m to match
        self.bind("<n>", lambda event: self.next_compare_product())

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

        self.frame2 = tk.Frame(self.canvas)
        self.canvas.create_window((0, 300), window=self.frame2, anchor="nw")

        # add for spacing 2
        #empty_frame2 = tk.Frame(self.frame, height=20, width=20)
        #empty_frame2.grid(sticky='w', row=6, column=0)

        self.pool_name_b = tk.Label(self.frame2, text=self.obj.second_group_key)
        self.pool_name_b.grid(sticky='w', row=7-6, column=1)

        # Loop through the dictionary and create radio buttons
        self.radio_selected_key = tk.StringVar()
        # Frame for radio buttons (using pack)

        # Create a canvas and a vertical scrollbar
        self.canvas_compare2 = tk.Canvas(self.frame2, width=1200, height=500)

        self.canvas_compare2.grid(sticky='w', row=8-6, column=1)
        self.compare_2_scrollbar = tk.Scrollbar(
            self.frame2, orient="vertical", command=self.canvas_compare2.yview)

        # Configure the canvas
        self.canvas_compare2.config(
            yscrollcommand=self.compare_2_scrollbar.set)
        self.compare_2_scrollbar.grid(sticky='ns', row=8-6, column=0)

        # Frame inside canvas with radio
        self.frame1 = tk.Frame(self.canvas_compare2)
        self.frame1.grid(sticky='w', row=0, column=0)
        self.image2_dict = {}

        self.sort_product_b_list_refresh()

        self.canvas_compare2.create_window(
            (0, 0), window=self.frame1, anchor="nw")

        # Update the scrollregion after configuring the interior frame
        self.frame1.update_idletasks()
        self.canvas_compare2.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas_compare2.config(
            scrollregion=self.canvas_compare2.bbox("all"))

        # Add a button to match products
        self.radio_select = tk.Button(
            self.frame, text="Match products", command=lambda: self.match_products(self.radio_selected_key.get()))
        self.radio_select.grid(sticky='w', row=0, column=2)

        # press m to match
        self.bind("<m>", lambda event: self.match_products(
            self.radio_selected_key.get()))

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
        image = image.resize((200, 200))
        photo = ImageTk.PhotoImage(image)
        return photo

    def next_compare_product(self):
        """Change compare product a"""
        self.obj.select_next_a()
        self.compare_a_name.config(text=next(iter(self.obj.compare_a)))
        self.compare_a_description.config(
            text=self.obj.compare_a[next(iter(self.obj.compare_a))], wraplength=600)

        self.sort_product_b_list_refresh()

        # get image for compare a
        self.image_a = self.get_images(
            self.obj.first_group_key, next(iter(self.obj.compare_a)))
        if self.image_a:
            self.image1_label.config(image=self.image_a)

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def match_products(self, product):
        if product not in self.obj.product_b_list:
            # display message that product not in list
            self.obj.select_match(product)
            return
        # otherwise match products and display new product list
        self.obj.select_match(product)
        self.clear_frame(self.frame1)
        self.next_compare_product()
        self.sort_product_b_list_refresh()

    def sort_product_b_list_refresh(self):
        """
        sort and refresh product_b_list based on latest product_a
        """
        for widget in self.frame1.winfo_children():
            widget.destroy()

        if not self.obj.product_b_list:
            return

        # sort product_b_list based on number of words from text a in text b, most similar on top
        self.obj.product_b_list = {k: v for k, v in sorted(self.obj.product_b_list.items(),
                                                           key=lambda item: self.match_percentage(
                                                           str(item[1]), str(self.obj.compare_a[next(iter(self.obj.compare_a))])),
                                                           reverse=True)}

        # add in the products to the radio button including imagery
        for i, (key, value) in enumerate(self.obj.product_b_list.items()):
            tk.Radiobutton(self.frame1,
                           text=key,
                           variable=self.radio_selected_key,
                           value=key).grid(sticky='ns', row=i//3 * 2, column=i % 3 * 2)
            tk.Label(self.frame1, text=value, wraplength=200).grid(
                sticky='ns', row=i//3 * 2 + 1, column=i % 3 * 2)
            # get image for compare a
            if key in self.image2_dict:
                self.imageb_label = tk.Label(
                    self.frame1, image=self.image2_dict[key])
                self.imageb_label.grid(sticky='ns', row=i // 3 * 2 + 1, column=i % 3 * 2 + 1)
            else:
                try:
                    image_b = self.get_images(
                        self.obj.second_group_key, key)
                except IndexError:
                    image_b = None
                if image_b:
                    self.image2_dict[key] = image_b
                    self.imageb_label = tk.Label(
                        self.frame1, image=self.image2_dict[key])
                    self.imageb_label.grid(sticky='ns', row=i // 3 * 2 + 1, column=i % 3 * 2 + 1)
        self.canvas_compare2.yview_moveto(0)

    def match_percentage(self, str1, str2):
        set1 = set(str1.split())
        set2 = set(str2.split())

        matching_words = set1.intersection(set2)
    
        if not set:  # Prevent division by zero
            return 0.0  # or other suitable value
        
        return (len(matching_words) / len(set1)) * 100


    def save_close(self):
        self.pool.update_matched()
        self.destroy()

    def _on_mousewheel(self, event):
        self.canvas_compare2.yview_scroll(-event.delta, "units")
