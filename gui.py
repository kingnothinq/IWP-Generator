import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
from tkinter import font as tkfont
from pathlib import Path
import webbrowser
from configparser import ConfigParser


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('450x460')
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
        self.font_btn_path = tkfont.Font(family='Helvetica', size=3)
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

        self.font_bold = tkfont.Font(size=10, weight='bold')

        self.cfg = ConfigParser(comment_prefixes='/', allow_no_value=True)
        self.cfg_path = Path('config.ini')
        self.cfg.read(self.cfg_path)

        self.var_region = tk.StringVar(value=self.cfg.get('Settings', 'region'))

        self.var_weigh_xg1000 = tk.StringVar(value=self.cfg.get('Settings', 'weight_xg1000'))
        self.var_weigh_xg = tk.StringVar(value=self.cfg.get('Settings', 'weight_xg500'))
        self.var_weigh_quanta = tk.StringVar(value=self.cfg.get('Settings', 'weight_quanta'))
        self.var_weigh_e5000 = tk.StringVar(value=self.cfg.get('Settings', 'weight_e5000'))
        self.var_weigh_r5000_pro = tk.StringVar(value=self.cfg.get('Settings', 'weight_r5000_pro'))
        self.var_weigh_r5000_lite = tk.StringVar(value=self.cfg.get('Settings', 'weight_r5000_lite'))
        self.var_weigh_excl = tk.StringVar(value=self.cfg.get('Settings', 'weight_exclude'))

        self.var_pr_req_freq = tk.StringVar(value=self.cfg.get('Project', 'req_freq'))
        self.var_pr_req_bw = tk.StringVar(value=self.cfg.get('Project', 'req_bw'))
        self.var_pr_req_cap = tk.StringVar(value=self.cfg.get('Project', 'req_cap'))
        self.var_pr_req_avb = tk.StringVar(value=self.cfg.get('Project', 'req_avb'))
        self.var_pr_req_excl = tk.StringVar(value=self.cfg.get('Project', 'req_exclude'))

        if self.cfg.get('Database', 'db_path') == 'default':
            self.var_db_fld_txt = tk.StringVar(value=(Path.cwd() / 'devices.db'))
        else:
            self.var_db_fld_txt = tk.StringVar(value=Path(self.cfg.get('Database', 'db_path')))

        if self.cfg.get('Database', 'xls_path') == 'default':
            self.var_xls_path_txt = tk.StringVar(value=(Path.cwd() / 'devices.xlsx'))
        else:
            self.var_xls_path_txt = tk.StringVar(value=Path(self.cfg.get('Database', 'xls_path')))

        if self.cfg.get('Output', 'output_folder') == 'default':
            self.var_out_fld_txt = tk.StringVar(value=(Path.cwd() / 'Output'))
        else:
            self.var_out_fld_txt = tk.StringVar(value=Path(self.cfg.get('Output', 'output_folder')))

        self.var_out_kmz = tk.StringVar(value=Path(self.cfg.get('Output', 'kmz_name')))
        self.var_out_bom = tk.StringVar(value=Path(self.cfg.get('Output', 'bom_name')))

        self.gui()

    def gui(self):

        # Left indent
        self.empty_lbl_1 = tk.Label(self, text=' ')

        self.empty_lbl_1.grid(column=0, row=0, sticky='w')

        # Global settings (Upper)
        self.set_gb_lbl = tk.Label(self, text='Global settings', font=self.font_bold)
        self.set_gb_weigh_xg1000_lbl = tk.Label(self, text='Weight XG 1000')
        self.set_gb_weigh_xg500_lbl = tk.Label(self, text='Weight XG')
        self.set_gb_weigh_quanta_lbl = tk.Label(self, text='Weight Quanta')
        self.set_gb_weigh_e5000_lbl = tk.Label(self, text='Weight Evolution')
        self.set_gb_weigh_r5000_pro_lbl = tk.Label(self, text='Weight R5000 Pro')
        self.set_gb_weigh_r5000_lite_lbl = tk.Label(self, text='Weight R5000 Lite')
        self.set_gb_weigh_excl_lbl = tk.Label(self, text='Weight Exclude')
        self.set_gb_region_lbl = tk.Label(self, text='Region')

        self.set_gb_weigh_xg1000_ent = tk.Entry(self, textvariable=self.var_weigh_xg1000, width=15)
        self.set_gb_weigh_xg_ent = tk.Entry(self, textvariable=self.var_weigh_xg, width=15)
        self.set_gb_weigh_quanta_ent = tk.Entry(self, textvariable=self.var_weigh_quanta, width=15)
        self.set_gb_weigh_e5000_ent = tk.Entry(self, textvariable=self.var_weigh_e5000, width=15)
        self.set_gb_weigh_r5000_pro_ent = tk.Entry(self, textvariable=self.var_weigh_r5000_pro, width=15)
        self.set_gb_weigh_r5000_lite_ent = tk.Entry(self, textvariable=self.var_weigh_r5000_lite, width=15)
        self.set_gb_weigh_excl_ent = tk.Entry(self, textvariable=self.var_weigh_excl, width=15)

        self.set_gb_lbl.grid(column=1, row=0, sticky='w', columnspan=2, padx=2, pady=2)
        self.set_gb_weigh_xg1000_lbl.grid(column=1, row=1, sticky='w', padx=2, pady=2)
        self.set_gb_weigh_xg500_lbl.grid(column=1, row=2, sticky='w', padx=2, pady=2)
        self.set_gb_weigh_quanta_lbl.grid(column=1, row=3, sticky='w', padx=2, pady=2)
        self.set_gb_weigh_e5000_lbl.grid(column=1, row=4, sticky='w', padx=2, pady=2)
        self.set_gb_weigh_r5000_pro_lbl.grid(column=1, row=5, sticky='w', padx=2, pady=2)
        self.set_gb_weigh_r5000_lite_lbl.grid(column=1, row=6, sticky='w', padx=2, pady=2)
        self.set_gb_weigh_excl_lbl.grid(column=1, row=7, sticky='w', padx=2, pady=2)
        self.set_gb_region_lbl.grid(column=1, row=8, sticky='w', padx=2, pady=2)

        self.set_gb_weigh_xg1000_ent.grid(column=2, row=1, sticky='w')
        self.set_gb_weigh_xg_ent.grid(column=2, row=2, sticky='w')
        self.set_gb_weigh_quanta_ent.grid(column=2, row=3, sticky='w')
        self.set_gb_weigh_e5000_ent.grid(column=2, row=4, sticky='w')
        self.set_gb_weigh_r5000_pro_ent.grid(column=2, row=5, sticky='w')
        self.set_gb_weigh_r5000_lite_ent.grid(column=2, row=6, sticky='w')
        self.set_gb_weigh_excl_ent.grid(column=2, row=7, sticky='w')

        # Deilimeter between Global and Project
        self.empty_lbl_2 = tk.Label(self, text=' ')

        self.empty_lbl_2.grid(column=3, row=0, sticky='w')

        # Project settings (Lower)
        self.set_pr_lbl = tk.Label(self, text='Project settings', font=self.font_bold)
        self.set_pr_req_freq_lbl = tk.Label(self, text='Frequency range')
        self.set_pr_req_bw_lbl = tk.Label(self, text='Bandwidth')
        self.set_pr_req_cap_lbl = tk.Label(self, text='Capacity')
        self.set_pr_req_avb_lbl = tk.Label(self, text='Availability')
        self.set_pr_req_exclude_lbl = tk.Label(self, text='Exclude devices')

        self.freq_list = ['3', '4', '5', '6', '70']
        self.set_pr_req_freq_cmbx = ttk.Combobox(self, values=self.freq_list, textvariable=self.var_pr_req_freq, width=15)
        self.set_pr_req_bw_ent = tk.Entry(self, textvariable=self.var_pr_req_bw, width=18)
        self.set_pr_req_cap_ent = tk.Entry(self, textvariable=self.var_pr_req_cap, width=18)
        self.avb_list = ['99.90', '99.99']
        self.set_pr_req_avb_cmbx = ttk.Combobox(self, values=self.avb_list, textvariable=self.var_pr_req_avb, width=15)
        self.set_pr_req_excl_xg1000_chbx = tk.Checkbutton(self, text='XG 1000')
        self.set_pr_req_excl_xg_chbx = tk.Checkbutton(self, text='XG')
        self.set_pr_req_excl_quanta_chbx = tk.Checkbutton(self, text='Quanta')
        self.set_pr_req_excl_e5000_chbx = tk.Checkbutton(self, text='Evolution')
        self.set_pr_req_excl_r5000_pro_chbx = tk.Checkbutton(self, text='R5000 Pro')
        self.set_pr_req_excl_r5000_lite_chbx = tk.Checkbutton(self, text='R5000 Lite')

        self.set_pr_lbl.grid(column=4, row=0, sticky='w', columnspan=2, padx=2, pady=2)
        self.set_pr_req_freq_lbl.grid(column=4, row=1, sticky='w', padx=2, pady=2)
        self.set_pr_req_bw_lbl.grid(column=4, row=2, sticky='w', padx=2, pady=2)
        self.set_pr_req_cap_lbl.grid(column=4, row=3, sticky='w', padx=2, pady=2)
        self.set_pr_req_avb_lbl.grid(column=4, row=4, sticky='w', padx=2, pady=2)
        self.set_pr_req_exclude_lbl.grid(column=4, row=5, sticky='w', padx=2, pady=2)

        self.set_pr_req_freq_cmbx.grid(column=5, row=1, sticky='w', columnspan=2, padx=2, pady=2)
        self.set_pr_req_bw_ent.grid(column=5, row=2, sticky='w', columnspan=2, padx=2, pady=2)
        self.set_pr_req_cap_ent.grid(column=5, row=3, sticky='w', columnspan=2, padx=2, pady=2)
        self.set_pr_req_avb_cmbx.grid(column=5, row=4, sticky='w', columnspan=2, padx=2, pady=2)
        self.set_pr_req_excl_xg1000_chbx.grid(column=4, row=6, sticky='w')
        self.set_pr_req_excl_xg_chbx.grid(column=4, row=7, sticky='w')
        self.set_pr_req_excl_quanta_chbx.grid(column=4, row=8, sticky='w')
        self.set_pr_req_excl_e5000_chbx.grid(column=5, row=6, sticky='w')
        self.set_pr_req_excl_r5000_pro_chbx.grid(column=5, row=7, sticky='w')
        self.set_pr_req_excl_r5000_lite_chbx.grid(column=5, row=8, sticky='w')

        # Database settings
        self.set_db_lbl = tk.Label(self, text='Database settings', font=self.font_bold)
        self.set_db_fld_lbl = tk.Label(self, text='Database folder')
        self.set_db_btn = tk.Button(self, text='Set', command=self.choose_db_fld, width=12, height=1)
        self.set_db_txt = tk.Text(self, wrap='word', width=25, height=3, bg='whitesmoke')
        self.set_db_txt.insert('1.0', f'{self.var_db_fld_txt.get()}')
        self.set_db_txt.config(state='disable')
        self.set_xls_fld_lbl = tk.Label(self, text='XLS file')
        self.set_xls_btn = tk.Button(self, text='Choose', command=self.choose_xls, width=12, height=1)
        self.set_xls_txt = tk.Text(self, wrap='word', width=25, height=3, bg='whitesmoke')
        self.set_xls_txt.insert('1.0', f'{self.var_xls_path_txt.get()}')
        self.set_xls_txt.config(state='disable')
        self.set_db_upd_btn = tk.Button(self, text='Update database', command=self.update_db, width=16, height=1)

        self.set_db_lbl.grid(column=1, row=9, sticky='w', columnspan=2, padx=2, pady=2)
        self.set_db_fld_lbl.grid(column=1, row=10, sticky='w', padx=2, pady=2)
        self.set_db_btn.grid(column=2, row=10, sticky='e', padx=2, pady=2)
        self.set_db_txt.grid(column=1, row=11, sticky='nsew', columnspan=2, rowspan=3, padx=2, pady=2)
        self.set_db_lbl.grid(column=1, row=9, sticky='w', padx=2, pady=2)
        self.set_xls_fld_lbl.grid(column=1, row=15, sticky='w', padx=2, pady=2)
        self.set_xls_btn.grid(column=2, row=15, sticky='w', padx=2, pady=2)
        self.set_xls_txt.grid(column=1, row=16, sticky='nsew', columnspan=2, rowspan=3, padx=2, pady=2)
        self.set_db_upd_btn.grid(column=1, row=20, sticky='w', columnspan=2, padx=2, pady=2)

        # Output settings
        self.set_out_lbl = tk.Label(self, text='Output settings', font=self.font_bold)
        self.set_out_fld_lbl = tk.Label(self, text='Output folder')
        self.set_out_btn = tk.Button(self, text='Set', command=self.choose_out_fld, width=12, height=1)
        self.set_out_txt = tk.Text(self, wrap='word', width=25, height=3, bg='whitesmoke')
        self.set_out_txt.insert('1.0', f'{self.var_out_fld_txt.get()}')
        self.set_out_txt.config(state='disable')
        self.set_out_kmz_lbl = tk.Label(self, text='KMZ name')
        self.set_out_kmz_ent = tk.Entry(self, textvariable=self.var_out_kmz, width=18)
        self.set_out_bom_lbl = tk.Label(self, text='BOM name')
        self.set_out_bom_ent = tk.Entry(self, textvariable=self.var_out_bom, width=18)

        self.set_out_lbl.grid(column=4, row=9, sticky='w', columnspan=2, padx=2, pady=2)
        self.set_out_fld_lbl.grid(column=4, row=10, sticky='w', padx=2, pady=2)
        self.set_out_btn.grid(column=5, row=10, sticky='e', padx=2, pady=2)
        self.set_out_txt.grid(column=4, row=11, sticky='nsew', columnspan=2, rowspan=3, padx=2, pady=2)
        self.set_out_kmz_lbl.grid(column=4, row=15, sticky='w', padx=2, pady=2)
        self.set_out_kmz_ent.grid(column=5, row=15, sticky='w', padx=2, pady=2)
        self.set_out_bom_lbl.grid(column=4, row=16, sticky='w', padx=2, pady=2)
        self.set_out_bom_ent.grid(column=5, row=16, sticky='w', padx=2, pady=2)

        # Save button
        self.save_btn = tk.Button(self, text='Save', width=25, command=self.save)

        self.save_btn.grid(column=4, row=20, sticky='e', columnspan=2, padx=2, pady=2)

        self.grid()


    def choose_db_fld(self):
        self.var_db_fld_txt.set(fd.askdirectory())

    def choose_out_fld(self):
        self.var_out_fld_txt.set(fd.askdirectory())

    def choose_xls(self):
        self.var_xls_path_txt.set(fd.askopenfilename(defaultextension='.xlsx',
                                                     filetypes=(('XLSX', '*.xlsx'),
                                                                ('XLS', '*.xls'),
                                                                ('All files', '*.*'))))


    def update_db(self):
        pass

    def save(self):
        pass



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