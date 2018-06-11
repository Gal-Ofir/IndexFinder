from tkinter import *
import threading
import os
from IndexFinder import (DEFAULT_ASIN, find_indexation_for_terms, create_csv)
from tkFileDialog import askopenfilename, askdirectory

lock = threading.Lock()


class Application:

    def __init__(self):
        self.root = Tk()
        self.root.title("IndexFinder v0.01")
        self.root.geometry("500x200")
        self.button_frame = Frame(self.root, height=30, width=50)

        self.choose_file_btn = Button(self.button_frame, text="Choose File...")
        self.choose_file_btn.bind("<Button-1>", self.get_xls_file_path)
        self.start_btn = Button(self.button_frame, text="Start")
        self.start_btn.bind("<Button-1>", self.start_find_indexation)
        self.generate_csv_btn = Button(self.button_frame, text="Generate xlsx")
        self.generate_csv_btn.bind("<Button-1>", self.generate_csv)

        self.radio_btn_single_or_csv_value = IntVar()
        self.radio_btn_single_or_csv_btn = Checkbutton(self.root, text="Single Term only", variable=self.radio_btn_single_or_csv_value)
        self.radio_btn_single_or_csv_btn.bind("<Button-1>", self.radio_btn_toggle)

        self.single_term_frame = Frame(self.root)
        self.single_term_label = Label(self.single_term_frame, text="Single search term")
        self.single_term_entry = Entry(self.single_term_frame, width=25)

        self.single_term_frame.pack(anchor=N)
        self.single_term_label.pack()
        self.single_term_entry.pack()

        self.file_name_entry = Entry(self.root, width=60)
        self.file_name_entry.bind("<Button-1>", self.get_xls_file_path)

        self.button_frame.pack(side=BOTTOM)
        self.file_name_entry.pack(side=BOTTOM)
        self.choose_file_btn.pack(side=LEFT)
        self.start_btn.pack(side=RIGHT)

        self.radio_btn_single_or_csv_btn.pack(anchor=W)

        self.results = []
        self.status_label = Label(self.root, text="Waiting")
        self.asin_entry = Entry(self.root, justify='center')
        self.asin_entry.insert(END, DEFAULT_ASIN)
        self.status_label.pack()
        self.asin_entry.pack(side=BOTTOM)

        self.results_listener = threading.Thread(target=self.listen_to_results)

    def get_xls_file_path(self, event):
        if self.file_name_entry['state'] == 'normal':
            file_path = askopenfilename(initialdir=os.environ['USERPROFILE'])
            self.file_name_entry.delete(0, END)
            self.file_name_entry.insert(0, file_path)

    def start_find_indexation(self, event):
        if not self.radio_btn_single_or_csv_value.get():
            if threading.active_count() < 2 and self.file_name_entry.get():
                threading.Thread(target=find_indexation_for_terms, args=(self.results, self.status_label, None, self.asin_entry.get(), self.file_name_entry.get())).start()
                self.results_listener.start()
            else:
                top_level = Toplevel(self.root)
                label_warning = Label(top_level, text="A search is already in progress!")
                label_warning.pack()
        else:
            if threading.active_count() < 2 and self.single_term_entry.get():
                threading.Thread(target=find_indexation_for_terms, args=(self.results, self.status_label, [self.single_term_entry.get()], self.asin_entry.get(), None)).start()
            else:
                top_level = Toplevel(self.root)
                label_warning = Label(top_level, text="A search is already in progress!")
                label_warning.pack()

    def start(self):

        self.root.mainloop()

    def listen_to_results(self):
        while True:
            if self.results:
                with lock:
                    self.generate_csv_btn.pack(side=RIGHT)
                    print 'Generate CSV button enabled'
                    break

    def generate_csv(self, event):
        asin = self.asin_entry.get()
        work_dir = askdirectory(initialdir=os.environ['USERPROFILE'])
        path = os.path.join(work_dir, 'indexFinder', asin)
        threading.Thread(target=create_csv, args=(self.results, path)).start()

    def radio_btn_toggle(self, event):
        self.file_name_entry['state'] = 'normal' if self.radio_btn_single_or_csv_value.get() == 1 else 'disabled'

if __name__ == "__main__":

    Application().start()
