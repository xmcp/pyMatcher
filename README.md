# pyMatcher

如果你自己写了一（几）道题，找了些数据想对拍，Cena、Lemon之流可能并不适合你，因为创建比赛、加题、加选手、设编译参数一系列操作往往都比较麻烦。

pyMatcher 把这个流程简化为了：

- 把自己的 EXE 拖进窗口里（因为直接是EXE，所以连编译选项都不用设了）
- 把数据那个文件夹拖到窗口里
- 点【评测】按钮

![image](https://user-images.githubusercontent.com/6646473/27003330-d0ce0daa-4e26-11e7-9cd6-00c7d42eb6ab.png)

惊不惊喜？刺不刺激？

还支持对比你的输出文件：

![image](https://user-images.githubusercontent.com/6646473/27003344-32f14146-4e27-11e7-95c2-8e42a6814c33.png)

顺便还会自动检测“改完代码忘编译”、“忘删 freopen”、“忘删 system("pause")”三个常见的制杖情况并弹窗警(chao)告(feng)。

作为一个超·轻量级的评测软件，pyMatcher **现在不支持、之后也不会支持**：
- 一切非 Windows 系统和扩展名!=.exe 的选手程序
- 导入多个选手
- 导出成绩
- 检测内存超限和危险系统调用
- Special Judge 和交互库
- 输入文件的扩展名!=.in，或输出文件的扩展名 ∉ {.out, .ans, .std}，或输入输出文件名除扩展名以外不完全相同 的数据
- 在评测过程中显示魔性的动画（Cena 说的就是你）

运行环境是 Python 3.x，不想装环境的话也可以 [下载 Build 版本](http://s.xmcp.ml/matcher.7z)，仅 2.5MB，解压即用。
