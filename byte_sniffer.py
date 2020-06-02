from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from pathlib import Path
import sqlite3
import json
import os
import re
import time

class Database_Toplevel(Toplevel):
    def __init__(self, root):
        Toplevel.__init__(self)
        self.root = root
        self.d_base = None
        self.title("Save to Database")
        self.geometry("400x250+300+300")
        self.resizable(False,False)
        self.transient(root)

        self._frame = Frame(self)
        self._frame.pack(side="top", expand=True, fill="both")

        _ = Path.cwd()
        self.d_base = filedialog.askopenfilename(initialdir=_, title="Save to Database", filetypes=[("Database", "db")])
        if not self.d_base:
            self.d_base = ''.join([str(_),"/",root.filename,".db"])
        self.f_label = LabelFrame(self._frame, text= "Selected Database:")
        self.f_label.grid(row=0,column=0, padx=2, sticky="E,W")
        self.db_label = Label(self.f_label, text=self.d_base)
        self.db_label.pack(side="top", expand=False)

        self.t_label = LabelFrame(self._frame, text= "Select a Table:")
        self.t_label.grid(row=1, column=0, padx=2, pady=2,sticky="N,E,S,W")
        self.tablevar = StringVar()

        with sqlite3.connect(self.d_base) as conn:
            cur = conn.cursor()
            tables = [i[0] for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table';") if i[0] != "sqlite_sequence"]
            self.tablevar.set(' '.join([*tables, 'Create']))

        self.t_list = Listbox(self.t_label, listvariable = self.tablevar)
        self.t_list.pack(side="left", expand=True, fill ="x")

        self.t_submit = Button(self._frame, text='Submit', command=self.submit_table)
        self.t_submit.grid(row=0,column=1, padx=2, pady=2, sticky = "E,W")

    def submit_table(self):
        with sqlite3.connect(self.d_base) as conn:
            cur = conn.cursor()
            opt = self.t_list.curselection()
            opt_lit = self.t_list.get(opt[0])


            #Create is last option so we check to see if that's selected
            if opt[0] == self.t_list.size() - 1:

                sql = '''CREATE TABLE {table_variable}(
                    BYTE_MARK INT NOT NULL,
                    FILE_NAME CHAR NOT NULL,
                    SENTENCE CHAR NOT NULL
                )'''.format(table_variable=self.root._search)
                cur.execute(sql)
                conn.commit()
                for item in self.root.results:

                    sql = '''INSERT INTO {} (BYTE_MARK, FILE_NAME, SENTENCE)
                        VALUES (? , ? , ?)'''.format(self.root._search)

                    cur.execute(sql, (int(item),self.root.filename, self.root.results[item]))

                conn.commit()
            else:
                for item in self.root.results:

                    sql = '''INSERT INTO {} (BYTE_MARK, FILE_NAME, SENTENCE)
                        VALUES (? , ? , ?)'''.format(opt_lit)

                    cur.execute(sql, (int(item),self.root.filename, self.root.results[item]))

                conn.commit()
            self.destroy()
            #print(opt_2)

class main_win(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("ByteSniffer")
        self.resizable(False,False)
        #self.geometry("500x400+300+300")
        self.filename = str()
        self._search = str()
        self.results = {}

        self.hold_u = Frame(self)
        self.hold_u.pack(side='top',expand=True, fill='both')

        self.text = Text(self.hold_u, wrap="word", state="disabled")
        self.text.grid(row=0,column=1,sticky="N,S,E,W")


        self.lOptions = StringVar()
        self.fResults = Listbox(self.hold_u, listvariable=self.lOptions)
        self.fResults.grid(row=0,column=0, sticky="N,S,E,W")
        self.fResults.bind('<Double-1>', self.on_click)

        self.hold_b = Frame(self)
        self.hold_b.pack(side="bottom",expand=True, fill="x")

        self.file_label = StringVar()
        self.fTitle = Label(self.hold_b, textvariable=self.file_label)
        self.fTitle.grid(row=0,column=1,pady=2,padx=2,ipady=1,ipadx=2,sticky='E,W')

        self.fOpen = Button(self.hold_b, text='Open', command=self.file_find)
        self.fOpen.grid(row=0,column=0,pady=2,padx=2,ipadx=2,ipady=1, sticky='E,W')

        self.fRead = Button(self.hold_b, text='Read', command=self.file_read)
        self.fRead.grid(row=0,column=2,pady=2,padx=2,ipadx=2,ipady=1,sticky='E,W')

        self.fEntry = Entry(self.hold_b, width=30)
        self.fEntry.grid(row=0,column=3,padx=2,pady=2)

        self.fSearch = Button(self.hold_b, text='Search', command=self.file_search)
        self.fSearch.grid(row=0,column=4,pady=2,padx=2,ipadx=2,ipady=1,sticky='W,E')

        self.fSave = Button(self.hold_b, text='Save Results', command= self.save)
        self.fSave.grid(row=0,column=5,pady=2,padx=2,ipadx=2,ipady=1,sticky="E,W")

        self.fDatabase = Button(self.hold_b, text='To Database', command= self.save_to_database)
        self.fDatabase.grid(row=0,column=6, pady=2, padx=2, ipadx=2, ipady=1, sticky="E,W")

    def save_to_database(self):
        w = Database_Toplevel(self)


    def file_find(self):

        _ = Path.cwd()
        file = filedialog.askopenfilename(initialdir=_,title="Search for clues...", filetypes=[("Text files", "txt")])
        self.filename = file.split('/')
        self.filename = self.filename[-1].split('.')
        self.filename = self.filename[0]
        self.file_label.set(file)

        file_stats = os.stat(self.file_label.get())
        disp = 'File Size in Bytes: {}'.format(file_stats.st_size)
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        self.text.insert('end',disp)
        self.text['state'] = 'disabled'

        self.results.clear()
        self.lOptions.set(' '.join(self.results.keys()))

    def file_read(self):
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')

        with open(self.file_label.get(), 'rb', 16384) as reader:
            while True:
                _f = reader.read(8192)

                _f = _f.decode()
                self.text.insert('end',_f)

                if not _f:
                    self.text['state'] = 'disabled'
                    break

    def file_search(self):
        self.text['state'] = 'normal'
        self.text.delete(1.0,'end')
        self.text['state'] = 'disabled'
        start = time.time()
        var = self.fEntry.get()
        var = var.strip()

        u_var = ''.join([var[0].upper(), var[1:]])
        l_var = ''.join([var[0].lower(), var[1:]])

        self._search = l_var
        self.results.clear()
        self.lOptions.set(' '.join(self.results.keys()))

        byt = 0
        with open(self.file_label.get(), 'rb',16384) as reader:

            while True:
                _r = reader.read(8192)
                #byt += len(_r)

                _r = _r.decode()
                #here we remove '\n' has len(1)
                _f = [i if u_var or l_var in i else len(i) for i in _r.split('\n')]

                if _f:
                    _f = iter(_f)
                    while True:
                        try:
                            _iter_f = next(_f)
                            if isinstance(_iter_f, int):
                                byt += _iter_f
                                #This should be to compensate for .split('\n')
                                byt += 1

                            elif isinstance(_iter_f, str):
                                _iter_str = iter(_iter_f.split(' '))
                                #Chunk through our string objects
                                while True:
                                    try:
                                        _next = next(_iter_str)
                                        if l_var in _next.lower():
                                            self.results[str(byt)] = str()
                                            self.lOptions.set(' '.join(self.results.keys()))

                                            pass
                                        else:
                                            #remember the space we lost when split

                                            pass
                                        byt += len(_next) + 1
                                    except StopIteration:
                                        break

                        except StopIteration:
                            byt -= 1
                            break
                elif not _f:
                    pass

                if not _r:
                    break
        self.create_sentence()
        self.text['state'] = 'normal'
        self.text.insert('end',"\n----{:.9f} Seconds----".format((time.time()-start)))
        self.text.insert('end','\nNumber of Results:{}'.format((len(self.results.keys()))))
        self.text['state'] = 'disabled'

    def create_sentence(self):
        with open(self.file_label.get(),'rb') as reader:
            punct = [b"!",b".",b"?"]
            for byt_indx in self.results.keys():
                reader.seek(int(byt_indx))
                sent = []

                while reader.read(1) not in punct:
                    try:
                        reader.seek(-2,1)
                    except OSError:
                        break
                while True:
                    _i = reader.read(1)
                    sent.append(_i.decode())
                    if _i in punct:
                        self.results[byt_indx] = ''.join(sent)
                        break

    def save(self):
        name = self.file_name.get() + '_search.txt'
        with open(name, 'w') as json_writer:
            json.dump(self.results, json_writer)

    def on_click(self, host):
        key = self.fResults.curselection()
        key = self.fResults.get(key[0])
        value = self.results[key]

        self.text['state'] = 'normal'
        self.text.delete(1.0,'end')

        self.text.insert('end', value)
        self.text['state'] = 'disabled'



if __name__=='__main__':

    main = main_win()
    main.mainloop()

