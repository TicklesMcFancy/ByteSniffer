from tkinter import *
from tkinter import filedialog
from pathlib import Path
import json
import os
import re

class main_win(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("ByteSniffer")
        self.resizable(False,False)
        #self.geometry("500x400+300+300")

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

        self.file_name = StringVar()
        self.fTitle = Label(self.hold_b, textvariable=self.file_name)
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



    def file_find(self):

        _ = Path.cwd()
        file = filedialog.askopenfilename(initialdir=_,title="Search for clues...", filetypes=[("Text files", "txt")])

        self.file_name.set(file)

        file_stats = os.stat(self.file_name.get())
        disp = 'File Size in Bytes: {}'.format(file_stats.st_size)
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        self.text.insert('end',disp)
        self.text['state'] = 'disabled'

        self.results.clear()
        self.lOptions.set(' '.join(self.results.keys()))

    def file_read(self):
        self.text['state'] = 'normal'
        self.text.delete(1.0,'end')
        _bool = True
        _n = 0


        with open(self.file_name.get(), 'rb') as reader:
            while _bool:
                _f = reader.readline()

                _f = _f.decode()
                _n += len(_f)
                self.text.insert('end',_f)

                if not _f:
                    self.text['state'] = 'disabled'
                    break

    def file_search(self):
        var = self.fEntry.get()
        var = var.strip()

        self.results.clear()
        self.lOptions.set(' '.join(self.results.keys()))

        _line = 0
        _n = 0
        with open(self.file_name.get(), 'rb') as reader:
            while True:
                _line += 1

                _f = reader.readline()
                _f = _f.decode()
                _match = re.findall(var, _f)

                if _match:
                    #print(_f)
                    _sent = _f.split(var)
                    _byte_marker = len(_sent[0]) + _n
                    self.results[str(_byte_marker)] = _f

                    self.lOptions.set(' '.join(self.results.keys()))

                elif not _match:
                    pass

                _n += len(_f)

                if not _f:
                    break

        for byt in self.results.keys():
            sent = self.create_sentence(byt)
            self.results[byt] = sent


    def create_sentence(self, byte_index):
        with open(self.file_name.get(),'rb') as reader:
            punct = [b"!",b".",b"?"]
            reader.seek(int(byte_index))
            sent = []

            while reader.read(1) not in punct:
                reader.seek(-2,1)
            while True:
                _i = reader.read(1)
                sent.append(_i.decode())
                if _i in punct:
                    return ''.join(sent)
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
