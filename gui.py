import tkinter as tk
import tkinter.filedialog as fd
from tkinter import font as tkfont
from pathlib import Path
import webbrowser
import configparser


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('500x300')
        self.title('InfiPLANNER PTP project generator')
        self.csv = ''
        self.gui()

    def gui(self):

        container = tk.Frame(self)

        self.frames = {}
        for page in (StartPage, PageOne, SettingsPage, HelpPage, AboutPage):
            page_name = page.__name__
            frame = page(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        menu_main = tk.Menu(self)
        self.config(menu=menu_main)

        menu_file = tk.Menu(menu_main, tearoff=0)
        menu_file.add_command(label='Start page', command=lambda: self.show_frame('StartPage'))
        menu_file.add_command(label='Update database')
        menu_file.add_command(label='Exit', command=quit)

        menu_settings = tk.Menu(menu_main, tearoff=0)
        menu_settings.add_command(label='General', command=lambda: self.show_frame('SettingsPage'))

        menu_help = tk.Menu(menu_main, tearoff=0)
        menu_help.add_command(label='Help', command=lambda: self.show_frame('HelpPage'))
        menu_help.add_command(label='About', command=lambda: self.show_frame('AboutPage'))

        menu_main.add_cascade(label='File', menu=menu_file)
        menu_main.add_cascade(label='Settings', menu=menu_settings)
        menu_main.add_cascade(label='Help', menu=menu_help)

        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.show_frame('SettingsPage')

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.tkraise()

    def upload_file(self):
        self.csv = fd.askopenfilename(defaultextension='.csv',
                                                filetypes=(('CSV', '*.csv'), ('All files', '*.*')))
        self.frames['StartPage'].update_file()

    def show_(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.tkraise()



class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.font_label = tkfont.Font(family='Helvetica', size=12, weight='bold')
        self.font_other = tkfont.Font(family='Helvetica', size=10)
        self.file_name = tk.StringVar()
        self.message = tk.StringVar()

        frame_empty_1 = tk.Frame(self)
        frame_empty_2 = tk.Frame(self)
        frame_empty_3 = tk.Frame(self)

        label_inform = tk.Label(frame_empty_1, text='Please upload a CSV file and click Next to continue', height=5, font=self.font_label)
        button_csv = tk.Button(frame_empty_2, text='Upload file', width=25, command=controller.upload_file, font=self.font_other)
        label_csv = tk.Label(frame_empty_2, textvariable=self.message, font=self.font_other)
        button_next = tk.Button(frame_empty_3, text='Next', width=25, command=self.check_file, font=self.font_other)

        label_inform.pack()
        button_csv.pack(pady=10)
        label_csv.pack()
        button_next.pack(side='right', padx=10, pady=10)
        frame_empty_1.pack()
        frame_empty_2.pack(fill='x')
        frame_empty_3.pack(side='bottom', fill='x')

    def update_file(self):
        self.file_name.set(f'{self.controller.csv}')
        self.message.set(f'{self.controller.csv}')

    def check_file(self):
        if self.controller.csv == '':
            self.message.set(f'ERROR: CSV file is not selected')
        else:
            self.controller.show_frame('PageOne')


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


class SettingsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.font_label = tkfont.Font(family='Helvetica', size=12, weight='bold')
        self.font_other = tkfont.Font(family='Helvetica', size=10)
        self.var_bd = tk.StringVar()

        frame_1 = tk.Frame(self, bg='red')
        frame_2 = tk.Frame(self, bg='blue')

        onevar = tk.BooleanVar(value=True)
        twovar = tk.BooleanVar(value=False)
        threevar = tk.BooleanVar(value=True)

        one_lbl = tk.Label(frame_1, text='One')
        two_lbl = tk.Label(frame_1, text='Two')
        three_lbl = tk.Label(frame_1, text='Three              ')
        one = tk.Checkbutton(frame_1, variable=onevar, onvalue=True)
        two = tk.Checkbutton(frame_1, variable=twovar, onvalue=True)
        three = tk.Checkbutton(frame_1, variable=threevar, onvalue=True)

        four_lbl = tk.Label(frame_2, text='FOUR')

        one_lbl.grid(column=0, row=0, sticky='w')
        one.grid(column=1, row=0)
        two_lbl.grid(column=0, row=1, sticky='w')
        two.grid(column=1, row=1)
        three_lbl.grid(column=0, row=2, sticky='w')
        three.grid(column=1, row=2)
        four_lbl.grid()

        frame_1.pack(expand=True, fill='both')
        frame_2.pack()



class HelpPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.font = tkfont.Font(family='Helvetica', size=8)
        self.readme = 'ERROR: Help file missing'
        self.readme_path = Path.cwd() / 'readme.txt'
        self.get_help()

        text_help = tk.Text(self, wrap='word', font=self.font)
        text_help.insert('1.0', f'{self.readme}')
        text_help.config(state='disable')

        scroll = tk.Scrollbar(self, command=text_help.yview)
        text_help.config(yscrollcommand=scroll.set)

        scroll.pack(side='right', fill='y')
        text_help.pack(side='top', fill='both', padx=1, pady=1)

    def get_help(self):
        with open(self.readme_path, 'r') as text:
            self.readme = ''.join(text.readlines())

class AboutPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.font_info = tkfont.Font(family='Helvetica', size=12)
        self.font_other = tkfont.Font(family='Helvetica', size=10)

        label_info = tk.Label(self, text='InfiPLANNER PTP project generator v 1.0.0', font=self.font_info)
        label_link = tk.Label(self, text='www.infiplanner.infinetwireless.com', fg='blue', cursor='hand2', font=self.font_other)
        label_link.bind('<Button-1>', lambda x: self.callback(r'https://infiplanner.infinetwireless.com/'))
        label_contacts = tk.Label(self, text='If you have any questions, don\'t hesitate to contact me:\r\ni.demchuk@infinet.ru', font=self.font_other)
        label_info.pack(side='top', fill='x', pady=10)
        label_link.pack(side='top', fill='x', pady=10)
        label_contacts.pack(side='bottom', fill='x', pady=10)

    def callback(self, url):
        webbrowser.open_new(url)


if __name__ == '__main__':
    app = Application()
    app.mainloop()