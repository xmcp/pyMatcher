#coding=utf-8
LICENSE='''
            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.

'''

from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog,messagebox

import os, shutil
import sys
import threading
import subprocess
import time

tk=Tk()
tk.title('pyMatcher')
tk.rowconfigure(0,weight=1)
tk.columnconfigure(0,weight=1)

init_exe_path=os.path.expanduser('~/desktop')
init_data_path=os.path.expanduser('~/desktop')

def about():
    tl=Toplevel(tk)
    tl.title('关于 pyMatcher 评测程序')
    tl.resizable(False,False)
    tl.focus_force()

    t=Text(tl,font='Consolas -14',height=20,width=69,background='#eee')
    t.insert('end','\n  Source code available at https://github.com/xmcp/pyMatcher\n\n')
    t.insert('end',LICENSE)
    t.insert('end','\n\n  Copyright (C) 2015 xmcp')
    t['state']='disabled'
    t.grid(row=0,column=0,sticky='nswe')

def psize(size):
    b=size%1000
    k=int(size/1000)%1000
    m=int(size/1000/1000)
    if m and k:
        return '%d %3d %3d 字节'%(m,k,b)
    elif k:
        return '%d %3d 字节'%(k,b)
    else:
        return '%d 字节'%b

_cur_panel=None
def addpanel():
    global _cur_panel
    if not _cur_panel or (_cur_panel.exebtn and _cur_panel.data) or _cur_panel._deleted:
        _cur_panel=Panel()

class Panel:
    def __init__(self):
        self.timeoutvar=IntVar(value=1000)
        self.msg=StringVar(value='加载中...')

        self.exefn=None
        self.sourcefn=None
        self.data=[]
        self.timeout=None
        self.inputt={}
        self.output={}
        self.acoutput={}
        self._deleted=False

        self.b=Frame(tk)
        self.b.rowconfigure(1,weight=1)
        self.b.columnconfigure(0,weight=1)
        book.add(self.b,text=' 新评测 ')

        f = Frame(self.b)
        f.grid(row=0, column=0, sticky='we', pady=2)
        f.columnconfigure(2, weight=1)

        self.exebtn = Button(f, text='程序 ×', command=self.exeget)
        self.exebtn.grid(row=0, column=0, padx=2)

        self.dtbtn = Button(f, text='数据 ×', command=self.dtget)
        self.dtbtn.grid(row=0, column=1)

        Label(f, text=' ').grid(row=0, column=2)

        Label(f, text='超时(ms):').grid(row=0, column=3, padx=2)
        self.timeoutentry = Entry(f, textvariable=self.timeoutvar, width=8)
        self.timeoutentry.grid(row=0, column=4)
        self.timeoutentry.bind('<Return>', lambda *_: self.jgbtn.invoke())

        self.jgbtn = Button(f, text='评测', command=self.judge, state='disabled')
        self.jgbtn.grid(row=0, column=5, padx=2)

        tf = Frame(self.b)
        tf.grid(row=1, column=0, sticky='nswe')
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)

        self.tree = Treeview(tf, columns=('result', 'time'), selectmode='browse', height=12)
        self.tree.grid(row=0, column=0, sticky='nswe')
        sbar = Scrollbar(tf, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sbar.set)
        sbar.grid(row=0, column=1, sticky='ns')

        self.tree.bind('<Double-Button-1>', self.getresult)
        self.tree.column('#0', width=400)
        self.tree.column('result', width=125)
        self.tree.heading('result', text='结果')
        self.tree.column('time', width=75, anchor='e')
        self.tree.heading('time', text='时间')

        msgf = Frame(self.b)
        msgf.grid(row=2, column=0, pady=2, sticky='we')
        msgf.columnconfigure(0, weight=1)

        Label(msgf, textvariable=self.msg).grid(row=0, column=0, padx=5, sticky='we')
        Button(msgf, text='关于本程序', command=about).grid(row=0, column=1)
        Button(msgf, text='X', width=3, command=self._delpanel).grid(row=0, column=2, padx=2)

        self.msg.set('请选择选手程序和数据目录')

    def _delpanel(self):
        book.forget(self.b)
        self._deleted=True
        self.b.destroy()
        addpanel()

    def getresult(self,*_):
        def scrollall(*_):
            t1.yview(*_)
            t2.yview(*_)
        def callback1(a,*_):
            sbar.set(a,*_)
            t2.yview_moveto(a)
        def callback2(a,*_):
            sbar.set(a,*_)
            t1.yview_moveto(a)

        def breaker(event):
            if event.keysym not in ('Alt_L','Alt_R','F4'):
                return 'break'

        def init12():
            for pos in range(max(len1,len2)):
                if pos<len1:
                    t1.insert('end','%d\t'%(pos+1),'lineno')
                    if pos>=len2:
                        t1.insert('end',data1[pos]+'↓\n','bad' if data1[pos].rstrip() else 'soso')
                        t2.insert('end','~\t','lineno')
                        t2.insert('end','\n')
                    else:
                        t2.insert('end','%d\t'%(pos+1),'lineno')
                        t2.insert('end',data2[pos]+'↓\n')
                        if data1[pos].rstrip()==data2[pos].rstrip():
                            t1.insert('end',data1[pos]+'↓\n','good')
                        elif data1[pos].replace(' ','').replace('\t','')==\
                            data2[pos].replace(' ','').replace('\t',''):
                            t1.insert('end',data1[pos]+'↓\n','soso')
                        else:
                            t1.insert('end',data1[pos]+'↓\n','bad')
                else:
                    t1.insert('end','~\t','lineno')
                    t1.insert('end','\n','bad' if data2[pos].rstrip() else 'soso')
                    t2.insert('end','%d\t'%(pos+1),'lineno')
                    t2.insert('end',data2[pos]+'↓\n')

        def init0():
            for pos in range(len(data0)):
                t0.insert('end','%d\t'%pos,'lineno')
                t0.insert('end',data0[pos]+'↓\n')
        
        name=self.tree.focus()
        if name in self.acoutput and name in self.output:
            tl=Toplevel(tk)
            tl.title(name)
            tl.rowconfigure(1,weight=1)
            tl.columnconfigure(0,weight=1)
            tl.columnconfigure(2,weight=1)
            tl.columnconfigure(4,weight=1)
            tl.focus_force()

            Label(tl,text='输入').grid(row=0,column=0)
            Label(tl,text='程序输出').grid(row=0,column=2)
            Label(tl,text='正确输出').grid(row=0,column=4)

            t0=Text(tl,font='Consolas -12',width=40)
            t0.grid(row=1,column=0,sticky='nswe')
            tmpbar=Scrollbar(tl,orient=VERTICAL,command=t0.yview)
            tmpbar.grid(row=1,column=1,sticky='ns')
            t0['yscrollcommand']=tmpbar.set
            t0.tag_config('lineno',foreground='#555',background='#ddd')
            t0.bind('<KeyPress>',breaker)
            
            t1=Text(tl,font='Consolas -12',width=40)
            t1.grid(row=1,column=2,sticky='nswe')
            t1.tag_config('good',foreground='#333',background='#bdf0b6')
            t1.tag_config('bad',foreground='#333',background='#f2bcbc')
            t1.tag_config('soso',foreground='#333',background='#b7cbf7')
            t1.tag_config('lineno',foreground='#555',background='#ddd')
            t1.bind('<KeyPress>',breaker)

            sbar=Scrollbar(tl,orient=VERTICAL)
            sbar.grid(row=1,column=3,sticky='ns')
            
            t2=Text(tl,font='Consolas -12',width=40)
            t2.grid(row=1,column=4,sticky='nswe')
            t2.tag_config('lineno',foreground='#555',background='#ddd')
            t2.bind('<KeyPress>',breaker)

            t1['yscrollcommand']=callback1
            t2['yscrollcommand']=callback2
            sbar['command']=scrollall

            data0=self.inputt[name].splitlines()
            data1=self.output[name].splitlines()
            data2=self.acoutput[name].splitlines()
            len1=len(data1)
            len2=len(data2)

            threading.Thread(target=init0).start()
            threading.Thread(target=init12).start()
        
    def exeget(self,fn=None):
        global init_exe_path
        if fn is None:
            fn=filedialog.askopenfilename(
                title='打开程序文件...',
                filetypes=[('选手程序文件','*.exe')],
                initialdir=init_exe_path,
            )
        if fn and os.path.isfile(fn):
            self.exefn=fn
            init_exe_path=os.path.split(fn)[0]
            if os.path.isfile(os.path.splitext(fn)[0]+'.cpp'):
                self.sourcefn=os.path.splitext(fn)[0]+'.cpp'
            else:
                self.sourcefn=None
            self.exebtn['text']='程序 ✓'
            book.tab(self.b,text=' %s '%os.path.basename(self.exefn))
            if self.data:
                self.jgbtn.state(['!disabled'])
                self.msg.set('请输入时间限制，然后点击评测按钮')
                addpanel()
            else:
                self.msg.set('请选择数据目录')
        elif fn:
            messagebox.showerror('pyMatcher','程序文件不存在')

    def dtget(self,dtdir=None):
        global init_data_path
        def outfn(basename):
            return basename+'.out' if os.path.isfile(basename+'.out') else \
                basename+'.ans' if os.path.isfile(basename+'.ans') else None

        if dtdir is None:
            dtdir=filedialog.askdirectory(
                title='选择数据目录',
                initialdir=init_data_path,
            )
        if dtdir and os.path.isdir(dtdir):
            self.data.clear()
            self.inputt.clear()
            self.acoutput.clear()
            self.tree.delete(*self.tree.get_children())
            init_data_path=dtdir
            
            os.chdir(dtdir)
            fns=os.listdir('.')
            maxfnlen=max((len(x) for x in fns))
            for infn in sorted(fns,key=lambda x: x.rjust(maxfnlen,' ')):
                inbase,inext=os.path.splitext(infn)
                out=outfn(inbase)
                if inext=='.in' and out:
                    with open(infn,'r') as inf, open(out,'r') as outf:
                        dt=[inbase,inf.read(),outf.read()]
                        self.tree.insert('','end',inbase,text='%s (%s -> %s)'%\
                            (inbase,psize(len(dt[1])),psize(len(dt[2])))
                        )
                        self.data.append(dt)
                        self.acoutput[inbase]=dt[2]
            if self.data:
                self.dtbtn['text']='数据 ✓'
                if self.exefn:
                    self.jgbtn.state(['!disabled'])
                    self.msg.set('请输入时间限制，然后点击评测按钮')
                    addpanel()
                else:
                    self.msg.set('请选择选手程序')
            else:
                messagebox.showerror('pyMatcher',
                    '没有找到数据\n'
                    '输入文件的扩展名应为 .in；输出文件的扩展名应为 .out 或 .ans，且文件名需和输入文件对应'
                )
        elif dtdir:
            messagebox.showerror('pyMatcher','数据目录不存在')

    def judge(self):
        def real_judge():
            def killer():
                nonlocal killed
                killed=True
                p.kill()

            datacnt=len(self.data)
            accnt=0
            judgeanyway=False
            
            for pos,val in enumerate(self.data):
                self.msg.set('正在评测 %d/%d...'%(pos+1,datacnt))
                name_, i, o=val
                self.tree.item(name_, values=['正在运行...', '...'])
                self.tree.see(name_)
                self.inputt[name_]=i

                killed=False
                if timeout:
                    timer=threading.Timer(timeout,killer)
                 
                p=subprocess.Popen(
                    executable=self.exefn,args=[],shell=True,
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                t1=time.time()
                if timeout:
                    timer.start()

                try:
                    pout,perr=p.communicate(i.encode('gbk','ignore'))
                except OSError:
                    self.tree.item(name_, values=['× 无法发送STDIN', ''])
                    continue
                
                pout=pout.decode('gbk','ignore')
                ret=p.wait()

                t2=time.time()
                if timeout:
                    timer.cancel()
                self.tree.item(name_, values=['正在评测...', '...'])
                self.output[name_]=pout

                if not o.endswith('\n'): o+='\n'
                if not pout.endswith('\n'): pout+='\n'
                t=int(1000*(t2-t1))
                if not judgeanyway and pout and '请按任意键继续' in pout:
                    if not messagebox.askyesno('pyMatcher',
                        '您可能忘记移除 system("pause") 语句\n仍然继续评测吗？'):
                        self.msg.set('评测已中断')
                        self.tree.item(name_, values=['评测中断', '...'])
                        book.tab(self.b,text=' %s '%os.path.basename(self.exefn))
                        return
                    else:
                        judgeanyway=True
                
                if killed or t>timeout*1000:
                    self.tree.item(name_, values=['× 运行超时', t])
                elif ret:
                    self.tree.item(name_, values=['× 返回值为%d' % ret, t])
                elif perr:
                    self.tree.item(name_, values=['× STDERR不为空', t])
                elif not pout:
                    self.tree.item(name_, values=['× 没有输出', t])
                elif [x.rstrip() for x in o.rstrip().splitlines()]==\
                    [x.rstrip() for x in pout.rstrip().splitlines()]:
                    self.tree.item(name_, values=['✓ 通过', t])
                    accnt+=1
                elif [x.replace(' ','').replace('\t','') for x in o.strip().split('\n')]==\
                        [x.replace(' ','').replace('\t','') for x in pout.strip().split('\n')]:
                    self.tree.item(name_, values=['✓ 通过（格式错误）', t])
                    accnt+=1
                else:
                    self.tree.item(name_, values=['× 结果错误', t])

            if datacnt==accnt:
                self.msg.set('您通过了全部 %d 组数据'%datacnt)
            else:
                self.msg.set('您通过了 %d 组数据中的 %d 组，双击错误项查看详情'%(datacnt,accnt))
            book.tab(self.b,text=' %s ( %d / %d ) '%(os.path.basename(self.exefn),accnt,datacnt))

        def wrapper():
            try:
                self.timeoutentry.state(['disabled'])
                real_judge()
            except Exception as e:
                messagebox.showerror('pyMatcher',repr(e))
                raise
            finally:
                self.exebtn.state(['!disabled'])
                self.dtbtn.state(['!disabled'])
                self.timeoutentry.state(['!disabled'])
                self.jgbtn.state(['!disabled'])

        timeout=self.timeoutvar.get()/1000
        if timeout<0:
            messagebox.showerror('pyMatcher','延时错误')
            return

        if self.sourcefn and os.stat(self.sourcefn).st_mtime>os.stat(self.exefn).st_mtime:
            if not messagebox.askyesno('pyMatcher',
                '源代码修改时间新于选手程序修改时间\n您可能忘记编译新修改的代码\n仍然继续评测吗？'):
                return
            else:
                shutil.copystat(self.sourcefn,self.exefn)

        self.msg.set('正在启动评测...')
        self.output={}

        for name in self.tree.get_children():
            self.tree.item(name,values=['','...'])

        self.exebtn.state(['disabled'])
        self.dtbtn.state(['disabled'])
        self.jgbtn.state(['disabled'])
        book.tab(self.b,text=' %s …… '%os.path.basename(self.exefn))
        threading.Thread(target=wrapper).start()

book=Notebook(tk)
book.grid(row=0,column=0,sticky='nswe')
book.rowconfigure(0,weight=1)
book.columnconfigure(0,weight=1)
book.enable_traversal()

addpanel()

args=sys.argv[1:]
for exefn,datadir,timeout in list(zip(args[::3],args[1::3],args[2::3])):
    p=Panel()
    p.exeget(exefn)
    p.dtget(datadir)
    p.timeoutvar.set(timeout)
    book.select(p.b)

mainloop()
