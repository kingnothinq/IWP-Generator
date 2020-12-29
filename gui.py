import tkinter as tk
import tkinter.filedialog as fd
import webbrowser
from configparser import ConfigParser
from pathlib import Path
from re import compile
from tkinter import font as tkfont
from tkinter import ttk

from csvhandler import handle
from dbupdater import update_database


class Application(tk.Tk):
    """Main class for GUI application."""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('450x460')
        self.title('InfiPLANNER project generator')

        self.container = tk.Frame(self)

        self.frames = {}
        for page in (MainPage, SettingsPage, HelpPage, AboutPage):
            page_name = page.__name__
            frame = page(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.menu_main = tk.Menu(self)
        self.config(menu=self.menu_main)

        self.menu_file = tk.Menu(self.menu_main, tearoff=0)
        self.menu_file.add_command(label='Main page', command=lambda: self.show_frame('MainPage'))
        self.menu_file.add_command(label='Exit', command=self.destroy)

        self.menu_settings = tk.Menu(self.menu_main, tearoff=0)
        self.menu_settings.add_command(label='General', command=lambda: self.show_frame('SettingsPage'))

        self.menu_help = tk.Menu(self.menu_main, tearoff=0)
        self.menu_help.add_command(label='Help', command=lambda: self.show_frame('HelpPage'))
        self.menu_help.add_command(label='About', command=lambda: self.show_frame('AboutPage'))

        self.menu_main.add_cascade(label='File', menu=self.menu_file)
        self.menu_main.add_cascade(label='Settings', menu=self.menu_settings)
        self.menu_main.add_cascade(label='Help', menu=self.menu_help)

        self.gui()

    def gui(self):
        """Show GUI (Window)."""

        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_frame('MainPage')

    def show_frame(self, page_name):
        """Show a frame for the given page name"""

        frame = self.frames[page_name]
        frame.tkraise()


class MainPage(tk.Frame):
    """Main Page."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.font_lbl = tkfont.Font(family='Arial', size=12, weight='bold')
        self.font_result = tkfont.Font(family='Arial', size=15, weight='bold')
        self.font_btn = tkfont.Font(family='Arial', size=15, weight='bold')

        self.var_csv_path = tk.StringVar()

        self.frame = tk.Frame(self)

        self.info_lbl = tk.Label(self, text='Please upload a CSV file and click Start to continue', font=self.font_lbl)
        self.csv_upl_btn = tk.Button(self, text='Upload file', width=30, height=3,
                                     command=self.upload_file, font=self.font_btn)
        self.csv_path_txt = tk.Text(self, wrap='word', width=30, height=3, bg='Gray94', relief='flat')
        self.csv_path_txt.config(state='disabled')
        self.start_btn = tk.Button(self, text='Start', width=30, height=5,
                                   command=self.generate_project, font=self.font_btn)
        self.start_txt = tk.Text(self, wrap='word', width=30, height=3, bg='Gray94',
                                 relief='flat', font=self.font_result)
        self.start_txt.config(state='disabled')
        self.gui()

    def gui(self):
        """Show GUI (Window)."""

        self.info_lbl.pack(fill='x', padx=10, pady=10)
        self.csv_upl_btn.pack(padx=10, pady=10)
        self.csv_path_txt.pack(padx=10, pady=10)
        self.start_txt.pack(padx=10, pady=10)
        self.start_btn.pack(side='bottom', padx=30, pady=30)
        self.frame.pack()

        self.grid()

    def upload_file(self):
        """Set path to the xlsx file."""

        self.var_csv_path.set(fd.askopenfilename(defaultextension='.csv',
                                                 filetypes=(('CSV', '*.csv'), ('All files', '*.*'))))
        self.csv_path_txt.config(state='normal')
        self.csv_path_txt.delete('0.0', 'end')
        self.csv_path_txt.insert('0.0', f'{self.var_csv_path.get()}')
        self.csv_path_txt.tag_add('center', '0.0', 'end')
        self.csv_path_txt.tag_config('center', justify='center')
        self.csv_path_txt.config(state='disabled')

    def generate_project(self):
        """Start csvhandler."""
        try:
            handle(Path(self.var_csv_path.get()))
            self.start_txt.config(state='normal', fg='green')
            self.start_txt.delete('0.0', 'end')
            self.start_txt.insert('0.0', f'Project has been successfully generated')
            self.start_txt.tag_add('center', '0.0', 'end')
            self.start_txt.tag_config('center', justify='center')
            self.start_txt.config(state='disabled')
        except:
            self.start_txt.config(state='normal', fg='red')
            self.start_txt.delete('0.0', 'end')
            self.start_txt.insert('0.0', f'Error')
            self.start_txt.tag_add('center', '0.0', 'end')
            self.start_txt.tag_config('center', justify='center')
            self.start_txt.config(state='disabled')


class SettingsPage(tk.Frame):
    """Settings Page."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.font_bold = tkfont.Font(size=10, weight='bold')

        self.cfg = ConfigParser(comment_prefixes='/', allow_no_value=True)
        self.cfg_path = Path('config.ini')
        self.cfg.read(self.cfg_path)

        # Global settings variables
        self.var_region = tk.StringVar(value=self.cfg.get('Settings', 'region'))

        self.var_weigh_xg1000 = tk.IntVar(value=self.cfg.get('Settings', 'weight_xg1000'))
        self.var_weigh_xg500 = tk.IntVar(value=self.cfg.get('Settings', 'weight_xg500'))
        self.var_weigh_quanta = tk.IntVar(value=self.cfg.get('Settings', 'weight_quanta'))
        self.var_weigh_e5000 = tk.IntVar(value=self.cfg.get('Settings', 'weight_e5000'))
        self.var_weigh_r5000_pro = tk.IntVar(value=self.cfg.get('Settings', 'weight_r5000_pro'))
        self.var_weigh_r5000_lite = tk.IntVar(value=self.cfg.get('Settings', 'weight_r5000_lite'))
        self.var_weigh_excl = tk.IntVar(value=self.cfg.get('Settings', 'weight_exclude'))

        # Project settings variables
        self.var_pr_req_freq = tk.IntVar(value=self.cfg.get('Project', 'req_freq'))
        self.var_pr_req_bw = tk.IntVar(value=self.cfg.get('Project', 'req_bw'))
        self.var_pr_req_cap = tk.IntVar(value=self.cfg.get('Project', 'req_cap'))
        self.var_pr_req_avb = tk.StringVar(value=self.cfg.get('Project', 'req_avb'))
        self.var_pr_req_excl = tk.StringVar(value=self.cfg.get('Project', 'req_exclude'))
        self.var_pr_req_excl_xg1000 = tk.BooleanVar()
        self.var_pr_req_excl_xg500 = tk.BooleanVar()
        self.var_pr_req_excl_quanta = tk.BooleanVar()
        self.var_pr_req_excl_e5000 = tk.BooleanVar()
        self.var_pr_req_excl_r5000_pro = tk.BooleanVar()
        self.var_pr_req_excl_r5000_lite = tk.BooleanVar()
        self.text_to_var()

        # Database settings variables
        if self.cfg.get('Database', 'db_path') == 'default':
            self.var_db_path = tk.StringVar(value=(Path.cwd() / 'devices.db'))
            self.var_db_fld_chng = tk.BooleanVar(value=False)
        else:
            self.var_db_path = tk.StringVar(value=Path(self.cfg.get('Database', 'db_path')))
            self.var_db_fld_chng = tk.BooleanVar(value=True)

        if self.cfg.get('Database', 'xls_path') == 'default':
            self.var_xls_path = tk.StringVar(value=(Path.cwd() / 'devices.xlsx'))
            self.var_xls_chng = tk.BooleanVar(value=False)
        else:
            self.var_xls_path = tk.StringVar(value=Path(self.cfg.get('Database', 'xls_path')))
            self.var_xls_chng = tk.BooleanVar(value=True)

        # Output settings variables
        if self.cfg.get('Output', 'output_folder') == 'default':
            self.var_out_fld_path = tk.StringVar(value=(Path.cwd() / 'Output'))
            self.var_out_fld_chng = tk.BooleanVar(value=False)
        else:
            self.var_out_fld_path = tk.StringVar(value=Path(self.cfg.get('Output', 'output_folder')))
            self.var_out_fld_chng = tk.BooleanVar(value=True)

        if self.cfg.get('Output', 'kmz_name') == 'default':
            self.var_out_kmz = tk.StringVar(value='default')
        else:
            self.var_out_kmz = tk.StringVar(value=Path(self.cfg.get('Output', 'kmz_name')))

        if self.cfg.get('Output', 'bom_name') == 'default':
            self.var_out_bom = tk.StringVar(value='default')
        else:
            self.var_out_bom = tk.StringVar(value=Path(self.cfg.get('Output', 'bom_name')))

        # Left indent
        self.empty_lbl_1 = tk.Label(self, text=' ')

        # Global settings widgets
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
        self.set_gb_weigh_xg_ent = tk.Entry(self, textvariable=self.var_weigh_xg500, width=15)
        self.set_gb_weigh_quanta_ent = tk.Entry(self, textvariable=self.var_weigh_quanta, width=15)
        self.set_gb_weigh_e5000_ent = tk.Entry(self, textvariable=self.var_weigh_e5000, width=15)
        self.set_gb_weigh_r5000_pro_ent = tk.Entry(self, textvariable=self.var_weigh_r5000_pro, width=15)
        self.set_gb_weigh_r5000_lite_ent = tk.Entry(self, textvariable=self.var_weigh_r5000_lite, width=15)
        self.set_gb_weigh_excl_ent = tk.Entry(self, textvariable=self.var_weigh_excl, width=15)
        self.region_list = ['rus', 'eng']
        self.set_gb_region_cmbx = ttk.Combobox(self, values=self.region_list, textvariable=self.var_region, width=12)

        # Delimeter between Global and Project
        self.empty_lbl_2 = tk.Label(self, text=' ')

        # Project settings
        self.set_pr_lbl = tk.Label(self, text='Project settings', font=self.font_bold)
        self.set_pr_req_freq_lbl = tk.Label(self, text='Frequency range')
        self.set_pr_req_bw_lbl = tk.Label(self, text='Bandwidth')
        self.set_pr_req_cap_lbl = tk.Label(self, text='Capacity')
        self.set_pr_req_avb_lbl = tk.Label(self, text='Availability')
        self.set_pr_req_exclude_lbl = tk.Label(self, text='Exclude devices')

        self.freq_list = [3, 4, 5, 6, 70]
        self.set_pr_req_freq_cmbx = ttk.Combobox(self, values=self.freq_list,
                                                 textvariable=self.var_pr_req_freq, width=15)
        self.set_pr_req_bw_ent = tk.Entry(self, textvariable=self.var_pr_req_bw, width=18)
        self.set_pr_req_cap_ent = tk.Entry(self, textvariable=self.var_pr_req_cap, width=18)
        self.avb_list = ['99.90', '99.99']
        self.set_pr_req_avb_cmbx = ttk.Combobox(self, values=self.avb_list,
                                                textvariable=self.var_pr_req_avb, width=15)
        self.set_pr_req_excl_xg1000_chbx = tk.Checkbutton(self, text='XG 1000',
                                                          variable=self.var_pr_req_excl_xg1000)
        self.set_pr_req_excl_xg_chbx = tk.Checkbutton(self, text='XG',
                                                      variable=self.var_pr_req_excl_xg500)
        self.set_pr_req_excl_quanta_chbx = tk.Checkbutton(self, text='Quanta',
                                                          variable=self.var_pr_req_excl_quanta)
        self.set_pr_req_excl_e5000_chbx = tk.Checkbutton(self, text='Evolution',
                                                         variable=self.var_pr_req_excl_e5000)
        self.set_pr_req_excl_r5000_pro_chbx = tk.Checkbutton(self, text='R5000 Pro',
                                                             variable=self.var_pr_req_excl_r5000_pro)
        self.set_pr_req_excl_r5000_lite_chbx = tk.Checkbutton(self, text='R5000 Lite',
                                                              variable=self.var_pr_req_excl_r5000_lite)

        # Database settings
        self.set_db_lbl = tk.Label(self, text='Database settings', font=self.font_bold)
        self.set_db_fld_lbl = tk.Label(self, text='Database file')
        self.set_db_btn = tk.Button(self, text='Choose', command=self.choose_db_fld, width=12, height=1)
        self.set_db_txt = tk.Text(self, wrap='word', width=25, height=3, bg='Gray94', relief='flat')
        self.set_db_txt.insert('0.0', f'{self.var_db_path.get()}')
        self.set_db_txt.config(state='disable')
        self.set_xls_fld_lbl = tk.Label(self, text='XLS file')
        self.set_xls_btn = tk.Button(self, text='Choose', command=self.choose_xls, width=12, height=1)
        self.set_xls_txt = tk.Text(self, wrap='word', width=25, height=3, bg='Gray94', relief='flat')
        self.set_xls_txt.insert('0.0', f'{self.var_xls_path.get()}')
        self.set_xls_txt.config(state='disable')
        self.set_db_upd_btn = tk.Button(self, text='Update database', command=self.update_db, width=16, height=1)

        # Output settings
        self.set_out_lbl = tk.Label(self, text='Output settings', font=self.font_bold)
        self.set_out_fld_lbl = tk.Label(self, text='Output folder')
        self.set_out_btn = tk.Button(self, text='Set', command=self.choose_out_fld, width=12, height=1)
        self.set_out_txt = tk.Text(self, wrap='word', width=25, height=3, bg='Gray94', relief='flat')
        self.set_out_txt.insert('1.0', f'{self.var_out_fld_path.get()}')
        self.set_out_txt.config(state='disable')
        self.set_out_kmz_lbl = tk.Label(self, text='KMZ name')
        self.set_out_kmz_ent = tk.Entry(self, textvariable=self.var_out_kmz, width=18)
        self.set_out_bom_lbl = tk.Label(self, text='BOM name')
        self.set_out_bom_ent = tk.Entry(self, textvariable=self.var_out_bom, width=18)

        # Save button
        self.save_btn = tk.Button(self, text='Save', width=16, command=self.save)

        self.gui()

    def gui(self):
        """Show GUI (SettingsPage)."""

        # Left indent
        self.empty_lbl_1.grid(column=0, row=0, sticky='w')

        # Global settings widgets
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
        self.set_gb_region_cmbx.grid(column=2, row=8, sticky='w')

        # Delimeter between Global and Project
        self.empty_lbl_2.grid(column=3, row=0, sticky='w')

        # Project settings
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
        self.set_out_lbl.grid(column=4, row=9, sticky='w', columnspan=2, padx=2, pady=2)
        self.set_out_fld_lbl.grid(column=4, row=10, sticky='w', padx=2, pady=2)
        self.set_out_btn.grid(column=5, row=10, sticky='e', padx=2, pady=2)
        self.set_out_txt.grid(column=4, row=11, sticky='nsew', columnspan=2, rowspan=3, padx=2, pady=2)
        self.set_out_kmz_lbl.grid(column=4, row=15, sticky='w', padx=2, pady=2)
        self.set_out_kmz_ent.grid(column=5, row=15, sticky='w', padx=2, pady=2)
        self.set_out_bom_lbl.grid(column=4, row=16, sticky='w', padx=2, pady=2)
        self.set_out_bom_ent.grid(column=5, row=16, sticky='w', padx=2, pady=2)

        # Save button
        self.save_btn.grid(column=4, row=20, sticky='e', columnspan=2, padx=2, pady=2)

        self.grid()

    def choose_db_fld(self):
        """Set path to the database."""

        self.var_db_path.set(fd.askopenfilename(defaultextension='.db',
                                                filetypes=(('DB', '*.db'),
                                                                ('JSON', '*.json'),
                                                                ('All files', '*.*'))))
        self.set_db_txt.config(state='normal')
        self.set_db_txt.delete('0.0', 'end')
        self.set_db_txt.insert('0.0', f'{self.var_db_path.get()}')
        self.set_db_txt.config(state='disabled')
        self.var_db_fld_chng.set(True)

    def choose_out_fld(self):
        """Set path to the output folder."""

        self.var_out_fld_path.set(fd.askdirectory())
        self.set_out_txt.config(state='normal')
        self.set_out_txt.delete('0.0', 'end')
        self.set_out_txt.insert('0.0', f'{self.var_out_fld_path.get()}')
        self.set_out_txt.config(state='disabled')
        self.var_out_fld_chng.set(True)

    def choose_xls(self):
        """Set path to the xlsx file."""

        self.var_xls_path.set(fd.askopenfilename(defaultextension='.xlsx',
                                                 filetypes=(('XLSX', '*.xlsx'),
                                                                ('XLS', '*.xls'),
                                                                ('All files', '*.*'))))
        self.set_xls_txt.config(state='normal')
        self.set_xls_txt.delete('0.0', 'end')
        self.set_xls_txt.insert('0.0', f'{self.var_xls_path.get()}')
        self.set_xls_txt.config(state='disabled')
        self.var_xls_chng.set(True)

    def text_to_var(self):
        """Get req_exclude variable and parse it."""

        # Patterns for var_pr_req_excl
        self.pattern_xg1000 = compile(r'(xg1000)')
        self.pattern_xg500 = compile(r'(xg500)')
        self.pattern_quanta = compile(r'(quanta)')
        self.pattern_e5000 = compile(r'(e5000)')
        self.pattern_r5000_pro = compile(r'(r5000_pro)')
        self.pattern_r5000_lite = compile(r'(r5000_lite)')

        if self.pattern_xg1000.search(self.var_pr_req_excl.get().lower()) is not None:
            self.var_pr_req_excl_xg1000.set(True)
        if self.pattern_xg500.search(self.var_pr_req_excl.get().lower()) is not None:
            self.var_pr_req_excl_xg500.set(True)
        if self.pattern_quanta.search(self.var_pr_req_excl.get().lower()) is not None:
            self.var_pr_req_excl_quanta.set(True)
        if self.pattern_e5000.search(self.var_pr_req_excl.get().lower()) is not None:
            self.var_pr_req_excl_e5000.set(True)
        if self.pattern_r5000_pro.search(self.var_pr_req_excl.get().lower()) is not None:
            self.var_pr_req_excl_r5000_pro.set(True)
        if self.pattern_r5000_lite.search(self.var_pr_req_excl.get().lower()) is not None:
            self.var_pr_req_excl_r5000_lite.set(True)

    def var_to_text(self):
        """Get exlclude variables and make req_exclude."""

        self.temp_var_pr_req_excl = []
        if self.var_pr_req_excl_xg1000.get() is True:
            self.temp_var_pr_req_excl.append('xg1000')
        if self.var_pr_req_excl_xg500.get() is True:
            self.temp_var_pr_req_excl.append('xg500')
        if self.var_pr_req_excl_quanta.get() is True:
            self.temp_var_pr_req_excl.append('quanta')
        if self.var_pr_req_excl_e5000.get() is True:
            self.temp_var_pr_req_excl.append('e5000')
        if self.var_pr_req_excl_r5000_pro.get() is True:
            self.temp_var_pr_req_excl.append('r5000_pro')
        if self.var_pr_req_excl_r5000_lite.get() is True:
            self.temp_var_pr_req_excl.append('r5000_lite')
        if len(self.temp_var_pr_req_excl) == 0:
            self.temp_var_pr_req_excl.append('none')
        return ', '.join(self.temp_var_pr_req_excl)

    def update_db(self):
        """Update database (dbupdater.py)."""

        try:
            self.db_upd_ok_lbl = tk.Label(self, text='OK', fg='green', font=self.font_bold)
            self.db_upd_error_lbl = tk.Label(self, text='ERROR', fg='red', font=self.font_bold)

            update_database(self.var_db_path.get(), self.var_xls_path.get())

            self.db_upd_error_lbl.grid_forget()
            self.db_upd_ok_lbl.grid(column=2, row=20, sticky='e', padx=2, pady=2)
        except:
            self.db_upd_ok_lbl.grid_forget()
            self.db_upd_error_lbl.grid(column=2, row=20, sticky='e', padx=2, pady=2)

    def save(self):
        """Save configuration file (config.ini)."""

        try:
            self.db_save_ok_lbl = tk.Label(self, text='OK       ', fg='green', font=self.font_bold)
            self.db_save_error_lbl = tk.Label(self, text='ERROR', fg='red', font=self.font_bold)

            # Set global settings
            if self.var_region.get() in ['rus', 'eng']:
                self.cfg.set('Settings', 'region', self.var_region.get())
            else:
                raise

            self.cfg.set('Settings', 'weight_xg1000', str(self.var_weigh_xg1000.get()))
            self.cfg.set('Settings', 'weight_xg500', str(self.var_weigh_xg500.get()))
            self.cfg.set('Settings', 'weight_quanta', str(self.var_weigh_quanta.get()))
            self.cfg.set('Settings', 'weight_quanta_70', str(self.var_weigh_quanta.get()))
            self.cfg.set('Settings', 'weight_e5000', str(self.var_weigh_e5000.get()))
            self.cfg.set('Settings', 'weight_r5000_pro', str(self.var_weigh_r5000_pro.get()))
            self.cfg.set('Settings', 'weight_r5000_lite', str(self.var_weigh_r5000_lite.get()))
            self.cfg.set('Settings', 'weight_exclude', str(self.var_weigh_excl.get()))

            # Set project settings
            if self.var_pr_req_freq.get() in [3, 4, 5, 6, 70]:
                self.cfg.set('Project', 'req_freq', str(self.var_pr_req_freq.get()))
            else:
                raise

            if self.var_pr_req_bw.get() > 0:
                self.cfg.set('Project', 'req_bw', str(self.var_pr_req_bw.get()))
            else:
                raise

            if self.var_pr_req_cap.get() > 0:
                self.cfg.set('Project', 'req_cap', str(self.var_pr_req_cap.get()))
            else:
                raise

            if self.var_pr_req_avb.get() in ['99.90', '99.99']:
                self.cfg.set('Project', 'req_avb', self.var_pr_req_avb.get())
            else:
                raise

            self.cfg.set('Project', 'req_exclude', self.var_to_text())

            # Set database settings
            if self.var_db_fld_chng.get() is False or len(self.var_db_path.get()) == 0:
                self.cfg.set('Database', 'db_path', 'default')
            else:
                self.cfg.set('Database', 'db_path', self.var_db_path.get())

            if self.var_xls_chng.get() is False or len(self.var_xls_path.get()) == 0:
                self.cfg.set('Database', 'xls_path', 'default')
            else:
                self.cfg.set('Database', 'xls_path', self.var_xls_path.get())

            # Output settings
            if self.var_out_fld_chng.get() is False or len(self.var_out_fld_path.get()) == 0:
                self.cfg.set('Output', 'output_folder', 'default')
            else:
                self.cfg.set('Output', 'output_folder', self.var_out_fld_path.get())

            self.cfg.set('Output', 'kmz_name', self.var_out_kmz.get())
            self.cfg.set('Output', 'bom_name', self.var_out_bom.get())

            with open(self.cfg_path, 'w') as config_file:
                self.cfg.write(config_file)

            self.db_save_error_lbl.grid_forget()
            self.db_save_ok_lbl.grid(column=4, row=20, sticky='w', padx=2, pady=2)
        except:
            self.db_save_ok_lbl.grid_forget()
            self.db_save_error_lbl.grid(column=4, row=20, sticky='w', padx=2, pady=2)


class HelpPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.font_help_txt = tkfont.Font(family='Arial', size=8)
        self.font_help_err = tkfont.Font(family='Arial', size=10, weight='bold')

        self.var_readme_path = Path.cwd() / 'readme.txt'
        self.var_help_txt = tk.StringVar()

        self.frame = tk.Frame(self)

        self.gui()

    def gui(self):
        """Show GUI (HelpPage)."""

        try:
            if self.var_readme_path.is_file() is True:
                with open(self.var_readme_path, 'r') as self.readme_text:
                    self.var_help_txt = ''.join(self.readme_text.readlines())
            else:
                raise

            self.help_txt = tk.Text(self, wrap='word', font=self.font_help_txt)
            self.help_txt.insert('0.0', f'{self.var_help_txt}')
            self.help_txt.config(state='disable')
            self.help_scrl = tk.Scrollbar(self, command=self.help_txt.yview)
            self.help_scrl.pack(side='right', fill='y')
            self.help_txt.pack(side='top', expand='yes', fill='both', padx=1, pady=1)
            self.frame.pack()
        except:
            self.help_err_lbl = tk.Label(self, text='Help file missing', fg='red', font=self.font_help_err)
            self.help_err_lbl.pack(anchor='center', fill='both', expand='yes')
            self.frame.pack()

        self.grid()

class AboutPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.font_info = tkfont.Font(family='Arial', size=12)
        self.font_other = tkfont.Font(family='Arial', size=10)

        self.frame = tk.Frame(self)

        # General information
        self.info_lbl = tk.Label(self, text='InfiPLANNER project generator v 1.0.0', font=self.font_info)
        self.info_link_lbl = tk.Label(self, text='www.infiplanner.infinetwireless.com',
                                      fg='blue', cursor='hand2', font=self.font_other)

        self.info_link_lbl.bind('<Button-1>', lambda x: self.callback(r'https://infiplanner.infinetwireless.com/'))

        # Contacts
        self.contacts_lbl = tk.Label(self, text=f'If you have any questions, don\'t hesitate to contact '
                                                f'me:\r\ni.demchuk@infinet.ru', font=self.font_other)

        self.gui()

    def gui(self):
        """Show GUI (AboutPage)."""

        self.info_lbl.pack(side='top', fill='x')
        self.info_link_lbl.pack(side='top', fill='x')
        self.contacts_lbl.pack(side='bottom', fill='x')
        self.frame.pack()

        self.grid()

    def callback(self, url):
        webbrowser.open_new(url)


if __name__=='__main__':
    app = Application()
    app.mainloop()
