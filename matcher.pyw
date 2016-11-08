#coding=utf-8
__author__='xmcp'
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
    b=size%1024
    k=int(size/1024)%1024
    m=int(size/1024/1024)
    if m and k:
        return '%d %d %d 字节'%(m,k,b)
    elif k:
        return '%d %d 字节'%(k,b)
    else:
        return '%d 字节'%b

def addpanel():
    timeoutvar=IntVar(value=1000)
    msg=StringVar(value='加载中...')

    exefn=None
    sourcefn=None
    data=[]
    timeout=None
    inputt={}
    output={}
    acoutput={}

    b=Frame(tk)
    b.rowconfigure(1,weight=1)
    b.columnconfigure(0,weight=1)
    book.add(b,text=' 新评测 ')
    
    def getresult(*_):
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
        
        name=tree.focus()
        if name in acoutput and name in output:
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

            data0=inputt[name].splitlines()
            data1=output[name].splitlines()
            data2=acoutput[name].splitlines()
            len1=len(data1)
            len2=len(data2)

            threading.Thread(target=init0).start()
            threading.Thread(target=init12).start()
        
    def exeget():
        global init_exe_path
        fn=filedialog.askopenfilename(
            title='打开程序文件...',
            filetypes=[('选手程序文件','*.exe')],
            initialdir=init_exe_path,
        )
        if fn and os.path.isfile(fn):
            nonlocal exefn, sourcefn
            exefn=fn
            init_exe_path=os.path.split(fn)[0]
            if os.path.isfile(os.path.splitext(fn)[0]+'.cpp'):
                sourcefn=os.path.splitext(fn)[0]+'.cpp'
            else:
                sourcefn=None
            exebtn['text']='程序 ✓'
            book.tab(b,text=' %s '%os.path.basename(exefn))
            if data:
                jgbtn.state(['!disabled'])
                msg.set('请输入时间限制，然后点击评测按钮')
                addpanel()
            else:
                msg.set('请选择数据目录')
        elif fn:
            messagebox.showerror('pyMatcher','程序文件不存在')

    def dtget():
        global init_data_path
        def outfn(basename):
            return basename+'.out' if os.path.isfile(basename+'.out') else \
                basename+'.ans' if os.path.isfile(basename+'.ans') else None

        dtdir=filedialog.askdirectory(
            title='选择数据目录',
            initialdir=init_data_path,
        )
        if dtdir and os.path.isdir(dtdir):
            data.clear()
            inputt.clear()
            acoutput.clear()
            tree.delete(*tree.get_children())
            init_data_path=dtdir
            
            os.chdir(dtdir)
            fns=os.listdir()
            maxfnlen=max((len(x) for x in fns))
            for infn in sorted(fns,key=lambda x: x.rjust(maxfnlen,' ')):
                inbase,inext=os.path.splitext(infn)
                out=outfn(inbase)
                if inext=='.in' and out:
                    with open(infn,'r') as inf, open(out,'r') as outf:
                        dt=[inbase,inf.read(),outf.read()]
                        tree.insert('','end',inbase,text='%s (%s -> %s)'%\
                            (inbase,psize(len(dt[1])),psize(len(dt[2])))
                        )
                        data.append(dt)
                        acoutput[inbase]=dt[2]
            if data:
                dtbtn['text']='数据 ✓'
                if exefn:
                    jgbtn.state(['!disabled'])
                    msg.set('请输入时间限制，然后点击评测按钮')
                    addpanel()
                else:
                    msg.set('请选择选手程序')
            else:
                messagebox.showerror('pyMatcher',
                    '没有找到数据\n'
                    '输入文件的扩展名应为 .in；输出文件的扩展名应为 .out 或 .ans，且文件名需和输入文件对应'
                )
        elif dtdir:
            messagebox.showerror('pyMatcher','数据目录不存在')

    def judge():
        def real_judge():
            def killer():
                nonlocal killed
                killed=True
                p.kill()

            datacnt=len(data)
            accnt=0
            judgeanyway=False
            
            for pos,val in enumerate(data):
                msg.set('正在评测 %d/%d...'%(pos+1,datacnt))
                name,i,o=val
                tree.item(name,values=['正在运行...','...'])
                tree.see(name)
                inputt[name]=i

                killed=False
                if timeout:
                    timer=threading.Timer(timeout,killer)
                 
                p=subprocess.Popen(
                    executable=exefn,args=[],shell=True,
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                t1=time.time()
                if timeout:
                    timer.start()

                try:
                    pout,perr=p.communicate(i.encode('gbk','ignore'))
                except OSError:
                    tree.item(name,values=['× 无法发送STDIN',''])
                    continue
                
                pout=pout.decode('gbk','ignore')
                ret=p.wait()

                t2=time.time()
                if timeout:
                    timer.cancel()
                tree.item(name,values=['正在评测...','...'])
                output[name]=pout

                if not o.endswith('\n'): o+='\n'
                if not pout.endswith('\n'): pout+='\n'
                t=int(1000*(t2-t1))
                if not judgeanyway and pout and '请按任意键继续' in pout:
                    if not messagebox.askyesno('pyMatcher',
                        '您可能忘记移除 system("pause") 语句\n仍然继续评测吗？'):
                        msg.set('评测已中断')
                        tree.item(name,values=['评测中断','...'])
                        book.tab(b,text=' %s '%os.path.basename(exefn))
                        return
                    else:
                        judgeanyway=True
                
                if killed or t>timeout*1000:
                    tree.item(name,values=['× 运行超时',t])
                elif ret:
                    tree.item(name,values=['× 返回值为%d'%ret,t])
                elif perr:
                    tree.item(name,values=['× STDERR不为空',t])
                elif not pout:
                    tree.item(name,values=['× 没有输出',t])
                elif [x.rstrip() for x in o.rstrip().splitlines()]==\
                    [x.rstrip() for x in pout.rstrip().splitlines()]:
                    tree.item(name,values=['✓ 通过',t])
                    accnt+=1
                elif [x.replace(' ','').replace('\t','') for x in o.strip().split('\n')]==\
                    [x.replace(' ','').replace('\t','') for x in pout.strip().split('\n')]:
                    tree.item(name,values=['✓ 通过（格式错误）',t])
                    accnt+=1
                else:
                    tree.item(name,values=['× 结果错误',t])

            if datacnt==accnt:
                msg.set('您通过了全部 %d 组数据'%datacnt)
            else:
                msg.set('您通过了 %d 组数据中的 %d 组，双击错误项查看详情'%(datacnt,accnt))
            book.tab(b,text=' %s ( %d / %d ) '%(os.path.basename(exefn),accnt,datacnt))

        def wrapper():
            try:
                timeoutentry.state(['disabled'])
                real_judge()
            except Exception as e:
                messagebox.showerror('pyMatcher',repr(e))
                raise
            finally:
                timeoutentry.state(['!disabled'])
                jgbtn.state(['!disabled'])

        nonlocal timeout
        timeout=timeoutvar.get()/1000
        if timeout<0:
            messagebox.showerror('pyMatcher','延时错误')
            return

        if sourcefn and os.stat(sourcefn).st_mtime>os.stat(exefn).st_mtime:
            if not messagebox.askyesno('pyMatcher',
                '源代码修改时间新于选手程序修改时间\n您可能忘记编译新修改的代码\n仍然继续评测吗？'):
                return
            else:
                shutil.copystat(sourcefn,exefn)

        msg.set('正在启动评测...')
        nonlocal output
        output={}

        for name in tree.get_children():
            tree.item(name,values=['','...'])

        exebtn.state(['disabled'])
        dtbtn.state(['disabled'])
        jgbtn.state(['disabled'])
        book.tab(b,text=' %s …… '%os.path.basename(exefn))
        threading.Thread(target=wrapper).start()

    f=Frame(b)
    f.grid(row=0,column=0,sticky='we',pady=2)
    f.columnconfigure(2,weight=1)

    exebtn=Button(f,text='程序 ×',command=exeget)
    exebtn.grid(row=0,column=0,padx=2)

    dtbtn=Button(f,text='数据 ×',command=dtget)
    dtbtn.grid(row=0,column=1)

    Label(f,text=' ').grid(row=0,column=2)

    Label(f,text='超时(ms):').grid(row=0,column=3,padx=2)
    timeoutentry=Entry(f,textvariable=timeoutvar,width=8)
    timeoutentry.grid(row=0,column=4)
    timeoutentry.bind('<Return>',lambda *_:jgbtn.invoke())

    jgbtn=Button(f,text='评测',command=judge,state='disabled')
    jgbtn.grid(row=0,column=5,padx=2)

    tf=Frame(b)
    tf.grid(row=1,column=0,sticky='nswe')
    tf.rowconfigure(0,weight=1)
    tf.columnconfigure(0,weight=1)

    tree=Treeview(tf,columns=('result','time'),selectmode='browse',height=12)
    tree.grid(row=0,column=0,sticky='nswe')
    sbar=Scrollbar(tf,orient=VERTICAL,command=tree.yview)
    tree.configure(yscrollcommand=sbar.set)
    sbar.grid(row=0,column=1,sticky='ns')

    tree.bind('<Double-Button-1>',getresult)
    tree.column('#0',width=400)
    tree.column('result',width=125)
    tree.heading('result',text='结果')
    tree.column('time',width=75,anchor='e')
    tree.heading('time',text='时间')

    msgf=Frame(b)
    msgf.grid(row=2,column=0,pady=2,sticky='we')
    msgf.columnconfigure(0,weight=1)

    Label(msgf,textvariable=msg).grid(row=0,column=0,padx=5,sticky='we')
    Button(msgf,text='关于本程序',command=about).grid(row=0,column=1,padx=2)

    msg.set('请选择选手程序和数据目录')

book=Notebook(tk)
book.grid(row=0,column=0,sticky='nswe')
book.rowconfigure(0,weight=1)
book.columnconfigure(0,weight=1)

addpanel()
mainloop()
