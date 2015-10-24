#coding=utf-8
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog,messagebox

import os
import threading
import subprocess
import time

tk=Tk()
tk.title('pyMatcher by xmcp')
tk.rowconfigure(1,weight=1)
tk.columnconfigure(0,weight=1)

exefn=None
data=[]
timeout=None
timeoutvar=IntVar(value=1000)
output={}

def psize(size):
    b=size%1024
    k=int(size/1024)%1024
    m=int(size/1024/1024)
    if m and k:
        return '%d %d %d 字节'%(m,k,b)
    elif k:
        return '%d %d 字节'%(k,b)
    else:
        return '%d 字节'%b

def getresult(*_):
    name=tree.focus()
    if name in output:
        messagebox.showinfo(name,'您的输出：\n\n%s'%(output[name]))

def exeget():
    fn=filedialog.askopenfilename(
        title='打开程序文件...',
        filetypes=[('EXE Files','*.exe')],
    )
    if fn and os.path.isfile(fn):
        global exefn
        exefn=fn
        exebtn['text']='EXE ✓'
        tk.title('pyMatcher [ %s ]'%os.path.basename(fn))
        if exefn and data:
            jgbtn.state(['!disabled'])
    elif fn:
        messagebox.showerror('pyMatcher','程序文件不存在')

def dtget():
    dtdir=filedialog.askdirectory(title='选择数据目录')
    if dtdir and os.path.isdir(dtdir):
        global data
        os.chdir(dtdir)
        for infn in os.listdir():
            tmp=os.path.splitext(infn)
            if tmp[1]=='.in' and os.path.isfile(tmp[0]+'.out'):
                with open(infn,'r') as inf, open(tmp[0]+'.out','r') as outf:
                    dt=[tmp[0],inf.read(),outf.read()]
                    tree.insert('','end',tmp[0],text='%s (%s -> %s)'%\
                        (tmp[0],psize(len(dt[1])),psize(len(dt[2]))))
                    data.append(dt)
        dtbtn['text']='数据 ✓'
        if exefn and data:
            jgbtn.state(['!disabled'])
    elif dtdir:
        messagebox.showerror('pyMatcher','数据目录不存在')

def judge():
    def real_judge():
        def killer():
            nonlocal killed
            killed=True
            p.kill()
        
        for name,i,o in data:
            tree.item(name,values=['正在运行...','...'])
            killed=False
            if timeout:
                timer=threading.Timer(timeout,killer)
            
            t1=time.time()
            p=subprocess.Popen(
                executable=exefn,args=[],shell=True,
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if timeout:
                timer.start()

            try:
                pout,perr=p.communicate(i.encode('gbk','ignore'))
            except OSError:
                tree.item(name,values=['无法发送STDIN',''])
                continue
            
            pout=pout.decode('gbk','ignore')
            ret=p.wait()
            output[name]=pout
            if timeout:
                timer.cancel()
            t2=time.time()

            t=int(1000*(t2-t1))
            if killed:
                tree.item(name,values=['运行超时',t])
            elif ret:
                tree.item(name,values=['返回值为%d'%ret,t])
            elif perr:
                tree.item(name,values=['STDERR不为空',t])
            elif not pout:
                tree.item(name,values=['没有输出',t])
            elif o.rstrip()==pout.rstrip():
                tree.item(name,values=['通过',t])
            elif [x.rstrip() for x in o.rstrip().split('\n')]\
                ==[x.rstrip() for x in pout.rstrip().split('\n')]:
                tree.item(name,values=['通过（格式错误）',t])
            else:
                tree.item(name,values=['结果错误',t])

    def wrapper():
        try:
            real_judge()
        except Exception as e:
            messagebox.showerror('pyMatcher',repr(e))
            raise
        finally:
            jgbtn.state(['!disabled'])

    global timeout
    timeout=timeoutvar.get()/1000
    if timeout<0:
        messagebox.showerror('pyMatcher','延时错误')
        return

    global output
    output={}

    exebtn.state(['disabled'])
    dtbtn.state(['disabled'])
    jgbtn.state(['disabled'])
    threading.Thread(target=wrapper).start()

f=Frame(tk)
f.grid(row=0,column=0,sticky='we')
f.columnconfigure(2,weight=1)

exebtn=Button(f,text='EXE ×',command=exeget)
exebtn.grid(row=0,column=0)

dtbtn=Button(f,text='数据 ×',command=dtget)
dtbtn.grid(row=0,column=1)

Label(f,text=' ').grid(row=0,column=2)

Label(f,text='超时(ms):').grid(row=0,column=3)
timeoutentry=Entry(f,textvariable=timeoutvar)
timeoutentry.grid(row=0,column=4)
timeoutentry.bind('<Return>',lambda *_:jgbtn.invoke())

jgbtn=Button(f,text='评测',command=judge,state='disabled')
jgbtn.grid(row=0,column=5)

tf=Frame(tk)
tf.grid(row=1,column=0,sticky='nswe')
tf.rowconfigure(0,weight=1)
tf.columnconfigure(0,weight=1)

tree=Treeview(tf,columns=('result','time'))
tree.grid(row=0,column=0,sticky='nswe')
sbar=Scrollbar(tf,orient=VERTICAL,command=tree.yview)
tree.configure(yscrollcommand=sbar.set)
sbar.grid(row=0,column=1,sticky='ns')

tree.bind('<Double-Button-1>',getresult)
tree.column('#0',width=400)
tree.column('result',width=100)
tree.heading('result',text='结果')
tree.column('time',width=100,anchor='e')
tree.heading('time',text='时间')

mainloop()
