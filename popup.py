"""
该文件修改自 https://github.com/PyPigStudio/PyPigPlayer。
"""

import tkinter
import tkinter.filedialog


ok = False
text = ''


def open(title: str, name: str = '', type: str = '') -> str:
    """
    打开文件。
    """
    tk = tkinter.Tk()
    tk.withdraw()
    if name and type:
        file = tkinter.filedialog.askopenfilename(
            title=title, filetypes=[(name, type)])
    else:
        file = tkinter.filedialog.askopenfilename(title=title)
    tk.destroy()
    return file


def folder(title: str) -> str:
    """
    打开文件夹。
    """
    tk = tkinter.Tk()
    tk.withdraw()
    folder = tkinter.filedialog.askdirectory(title=title)
    tk.destroy()
    return folder


def print(msg: str, title: str, okstr: str = '确认') -> None:
    """
    提示框。
    """
    tk = tkinter.Tk()
    tk.geometry('400x80')
    tk.resizable(0, 0)
    tk.title(title)
    tk.focus_force()

    tkinter.Label(tk, text=msg).pack(pady=5)
    tk.bind('<Return>', lambda x: tk.destroy())
    tkinter.Button(tk, text=okstr, command=tk.destroy,
                   width=10).pack(pady=5)

    tkinter.mainloop()


def save(title: str, default: str = None, name: str = '', type: str = '') -> str:
    """
    保存文件。
    """
    tk = tkinter.Tk()
    tk.withdraw()
    if name and type:
        file = tkinter.filedialog.asksaveasfilename(
            title=title, filetypes=[(name, type)], initialfile=default)
    else:
        file = tkinter.filedialog.asksaveasfilename(
            title=title, initialfile=default)
    tk.destroy()
    return file


def input(msg: str, title: str) -> str:
    """
    输入框。
    """
    global text
    text = ''

    tk = tkinter.Tk()
    tk.geometry('400x110')
    tk.resizable(0, 0)
    tk.title(title)

    tkinter.Label(tk, text=msg).pack(pady=5)
    inp = tkinter.Entry(tk, width=50)
    inp.focus_force()
    inp.pack(pady=5)

    def submit():
        global text
        text = inp.get()
        tk.destroy()

    tk.bind('<Return>', lambda x: submit())
    tkinter.Button(tk, text='确认', command=submit, width=10).pack(pady=5)
    tkinter.mainloop()
    return text


def yesno(msg: str, title: str, yesstr: str = '确认', nostr: str = '取消') -> bool:
    """
    确认框。
    """
    global ok
    ok = False
    tk = tkinter.Tk()
    tk.geometry('400x80')
    tk.resizable(0, 0)
    tk.title(title)
    tk.focus_force()

    tkinter.Label(tk, text=msg).pack(pady=5)

    def yes():
        global ok
        ok = True
        tk.destroy()

    tk.bind('<Return>', lambda x: yes())
    tkinter.Button(tk, text=yesstr, command=yes, width=10).pack(
        side='left', padx=5, pady=5)
    tkinter.Button(tk, text=nostr, command=tk.destroy,
                   width=10).pack(side='right', padx=5, pady=5)
    tkinter.mainloop()
    return ok
