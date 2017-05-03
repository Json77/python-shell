#start with python

##简单规则
###数和运算
1. 无大整数溢出
2. 浮点数优先，除法python2取整，python3用//取整，浮点算法转换为二进制。
3. 可以用”+“实现字符串相连。


### 块和缩进

1. ”:“表示开始一个块，块的行缩进，if-elif-else每个后面都要":"

### 循环语句

1. while可以有else从句
2. for循环，for i in [序列]，可以跟else从句，在循环结束后执行一次，除非有break
3. continue跳过

### 函数

1. 函数里的变量是局部的，不能影响外面的同名变量，如果需要，加global。
2. 可以在定义时传默认值，但是必须先定义没有默认值的形参，再加有默认值的。
3. 关键参数在调用时用名字，可以忽略顺序和处理默认值。

### 文档字符串

1. `print printMax.__doc__`，第一个逻辑行的字符串。
2. 文档字符串的惯例是一个多行字符串，它的首行以大写字母开始，句号结尾。第二行是空行，从第三行开始是详细的描述。 强烈建议 你在你的函数中使用文档字符串时遵循这个惯例。
3. 同help和pydoc。



### 序列

1. range生成序列，`range(1,5)`给出序列`[1, 2, 3, 4]`，默认地，`range`的步长为1。如果我们为`range`提供第三个数，那么它将成为步长。例如，`range(1,5,2)`给出`[1,3]`。记住，range 向上 延伸到第二个数，即它**不**包含第二个数。
2. 序列可以用负数，代表倒数第几个。
3. 切片操作，数是可选的，':'是必须的，开始位置包含，结束位置不包含。
4. 序列操作可以同样用在列表、元组、字符串上

### 模块

1. py程序本身是模块，调用里面的函数和变量用"."，用`if __name__ == __main__`标志自身。

### 对象、参考、绑定

1. A = ['a', 'b', 'c']，B = A，赋值列表类似于指针，A或B改了两个名字对应的都会改。如果B = A[:]作切片，B改了A就不会改。即赋值语句对复杂对象不创建拷贝，切片创建。

### 字符串

1. `name.startswith('Swa')`以开头

2. `'a' in name`字符串包含

3. `name.find('war')`返回字符串在另一个字符串里的位置，-1没找到。

4. ```python
   delimiter = '_*_'
   mylist = ['Brazil', 'Russia', 'India', 'China']
   print delimiter.join(mylist)
   ```

   得到`Brazil_*_Russia_*_India_*_China`分隔整理。

5. `r'str'`自然字符串


## 序列整体操作

- map(fun,list)，对list按位执行fun函数：

```python
#比如，把这个list所有数字转为字符串：
>>> map(str, [1, 2, 3, 4, 5, 6, 7, 8, 9])
['1', '2', '3', '4', '5', '6', '7', '8', '9']
```

- reduce(f, [x1, x2, x3, x4]) = f(f(f(x1, x2), x3), x4)，累计运算

```python
#如果要把序列[1, 3, 5, 7, 9]变换成整数13579，reduce就可以派上用场：
>>> def fn(x, y):
...   return x * 10 + y
>>> reduce(fn, [1, 3, 5, 7, 9])
13579
#把str转换为int的函数：
def char2num(s):
  return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[s]
def str2int(s):
  return reduce(lambda x,y: x*10+y, map(char2num, s))
```

- zip([seql, ...])接受一系列可迭代对象作为参数，将对象中对应的元素打包成一个个tuple（元组），然后返回由这些tuples组成的list（列表）。若传入参数的长度不等，则返回list的长度和参数中长度最短的对象相同。

```python
#zip打包解包列表和倍数
>>> a = [1, 2, 3]
>>> b = ['a', 'b', 'c']
>>> z = zip(a, b)
>>> z
[(1, 'a'), (2, 'b'), (3, 'c')]
>>> zip(*z)
[(1, 2, 3), ('a', 'b', 'c')]
#使用zip合并相邻的列表项

>>> a = [1, 2, 3, 4, 5, 6]
>>> zip(*([iter(a)] * 2))
[(1, 2), (3, 4), (5, 6)]

>>> group_adjacent = lambda a, k: zip(*([iter(a)] * k))
>>> group_adjacent(a, 3)
[(1, 2, 3), (4, 5, 6)]
>>> group_adjacent(a, 2)
[(1, 2), (3, 4), (5, 6)]
>>> group_adjacent(a, 1)
[(1,), (2,), (3,), (4,), (5,), (6,)]

>>> zip(a[::2], a[1::2])
[(1, 2), (3, 4), (5, 6)]

>>> zip(a[::3], a[1::3], a[2::3])
[(1, 2, 3), (4, 5, 6)]

>>> group_adjacent = lambda a, k: zip(*(a[i::k] for i in range(k)))
>>> group_adjacent(a, 3)
[(1, 2, 3), (4, 5, 6)]
>>> group_adjacent(a, 2)
[(1, 2), (3, 4), (5, 6)]
>>> group_adjacent(a, 1)
[(1,), (2,), (3,), (4,), (5,), (6,)]

#使用zip和iterators生成滑动窗口 (n -grams) 
>>> from itertools import islice
>>> def n_grams(a, n):
...     z = (islice(a, i, None) for i in range(n))
...     return zip(*z)
...
>>> a = [1, 2, 3, 4, 5, 6]
>>> n_grams(a, 3)
[(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]
>>> n_grams(a, 2)
[(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
>>> n_grams(a, 4)
[(1, 2, 3, 4), (2, 3, 4, 5), (3, 4, 5, 6)]

#使用zip反转字典
>>> m = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
>>> m.items()
[('a', 1), ('c', 3), ('b', 2), ('d', 4)]
>>> zip(m.values(), m.keys())
[(1, 'a'), (3, 'c'), (2, 'b'), (4, 'd')]
>>> mi = dict(zip(m.values(), m.keys()))
>>> mi
{1: 'a', 2: 'b', 3: 'c', 4: 'd'}
```



## 列表操作

- 定义一个列表类，list = ['a', 'b', 'c', 'd']，列表也是一个序列。


- 获取列表长度：len(list)获取个数，4
- list.append()，可以增加字符串。
- list.sort()，可以排列字符串，按首字母顺序，影响列表，即列表是可变的，字符串是不变的。
- del list[0]删除列表中的第一个。还有list.pop(n)，删除索引第n个（从0开始），默认删最后一个，list.remove(str)删除内容，默认第一个。[-1]可以表示最后一个元素。
- list.index(x,n)，从列表中下标n开始找出第一个匹配x的索引位置。
- sum(list)，获取一个列表的和。

### 元组

1. 元组不可变，list = ('a', 'b', 'c', 'd')，也是一个序列
2. len(list)获取个数，4
3. new_list = ('e', 'f', list)，元组之内的元组不会失去它的身份。len(newlist)为3
4. 可以用`new_list[2][2]`来索引b
5. 空元组list = ()，含有一个元素的元组list = (2, )
6. 使用元组输出`print '%s is %d years old' % (name, age)`(s%表示字符串，d%表示整数)

### 字典

1. 键值对`d = {key1 : value1, key2 : value2 }`，键用不可变对象（一般字符串），没有顺序，属于dict类
2. 添加用赋值`ab['Guido'] = 'guido@python.org'`
3. 删除用`del ab['Spammer']`
4. 打印指定值`print "Swaroop's address is %s" % ad['Swaroop']`
5. 打印表`print 'Contact %s at %s' % (name, address)`
6. 用in操作检验键值存在`if 'Guido' in ab:`或者用dict类has_key。

##内建函数

- id(对象)：获取地址

- type(对象)：获取类型

- divmod(a,b)：返回商和余数

- round(a,b)：取b位四舍五入

- str(a),repr(a)：转为字符串

- `raw_input('Enter an integer : ')`打印一个字符串，返回输入的字符串

- range(a,b,c):生成序列，起a，终b（不包括b），c为步长

- len():取字符串长度，取序列个数

- `dir`函数来列出模块定义的标识符。标识符有函数、类和变量。定义a会出现在dir()中，del a会删除。

- print可以在行尾加','消除自动打印的换行。

- isinstance(x,int)可以判断一个变量是否是已知的类型，第二个参数也可以是（int,list,float）这样的列表，返回true或false。

- abs()返回数字的绝对值。

  ​

  ​



##模块函数
- `from __future__ import division`浮点除法，用/都能得到浮点数结果
- `import math`math模块，math.pi，dir(math)


- from math import copysign as sign，sign(s,y)将y的正负号给x返回。
- `import sys`模块，它在`sys.path`变量中所列目录中寻找`sys.py`模块。如果找到了这个文件，这个模块的主块中的语句将被运行，然后这个模块将能够被你 使用 。执行python命令后面跟着的内容被作为参数传递给程序。Python为我们把它存储在`sys.argv`变量中，变量从0开始计数，`'using_sys.py'`是`sys.argv[0]`。



# python实用

## 文件操作

### 在文件中查找指定值1

> 类似cat file | grep key | awk -F ' ' ''${print 2}''，操作一个固定格式的表文件

```python
def pick_ip_info(filename, ip, info_num):
    with open(filename, 'r') as fobj:
        for line in fobj:
            dat_in = line.split()
            if dat_in[0] == ip:
                return dat_in[info_num]
```

with open打开的文件会自动关，open的则需要close，打开后是一个object，split用来分隔字符串，查到第1个是key的，返回第info_num个值。split()函数用法，split(str, num)，str是分隔符，默认空格，num分隔次数

### 在文件中查找正则表达式

> 同样类似cat file | grep str | wc -l

```python
import re
def find_str_in_file(filename, string):
    count = 0 
    with open(filename, 'r') as fobj:
        for line in fobj.readlines():
            if re.search(string, line):
                count = count + 1 
    return count
```

需要用到re作正则表达式匹配，这里string为正则表达式，查到就count+1。

### 在文件中查找指定位置的值并作替换

> 类似cat file | grep str | sed -i "s/a/b/h" file

```python
import os
import shutil
import tempfile
def modify_os_table(os_table, ip_addr, rate_value, rate_descript):
    tmp_rate = pick_ip_info(os_table, ip_addr, 2)
    if rate_value == tmp_rate:
        return 0
    out_file = tempfile.mktemp()
    fout = open(out_file, 'w')
    with open(os_table, 'r') as fin:
        for line in fin:
            dat_in = line.split()
            if dat_in[0] == ip_addr:
                dat_in[1] = rate_value
                dat_in[2] = rate_descript
                dat_out = ' '.join(dat_in)
            else:
                dat_out = ' '.join(dat_in)
            fout.writelines(dat_out+'\n')

    fout.close()
    shutil.move(out_file, os_table)
```

根据ip_addr找第二个参数rate，找到建一个临时文件。tempfile模块，mktemp创建一个临时文件路径，但是不创建具体文件，mkstemp创建一个文件元组，mkdtemp创建一个临时目录。open()函数打开文件，后面是权限。split函数分隔字符串，join函数连接字符串，前面是分隔符，后面是一个对象（元组或列表）。wrtie()函数和writelines()写字符串，要自己加换行。open()打开的要close()关闭，shutil进行文件移动，拷贝等操作，注意参数类型。

### 只显示字母与数字

```python
def OnlyCharNum(s,oth=''):
    s2 = s.lower();
    fomart = 'abcdefghijklmnopqrstuvwxyz0123456789'
    for c in s2:
        if not c in fomart:
            s = s.replace(c,'');
    return s;
 
print(OnlyStr("a000 aa-b"))
```

## 字符串操作

```python
sStr1 = '12345'
sStr2 = '123bc'
# 去空格及特殊符号
s.strip().lstrip().rstrip(',')
# 连接
sStr1 += sStr2
print sStr1
# 复制
sStr1 = 'strcpy'
sStr2 = sStr1
sStr1 = 'strcpy2'
print sStr2
# 比较指定位，去掉n全比
n = 3
print cmp(sStr1[0:n],sStr2[0:n])
# 1中查找2
nPos = sStr1.index(sStr2)
print nPos
# 扫描1中是否包含2
print len(sStr1 and sStr2)
# 长度 len
# 大小写转换
sStr1 = sStr1.upper()
# 追加指定长度，所有指定长度用[0:n]
n = 3
sStr1 += sStr2[0:n]
# 颠倒字符串
sStr1 = sStr1[::-1]
# 查找
print sStr1.find(sStr2)
```



## 正则表达式

### re模块常用函数

> 从字符串的开头开始匹配

```python
re.match(pattern, string, flags)
m = re.match(r"(\w+)\s", text)
```

参数分别是正则表达式，字符串，标志位。

> 查找符合的第一个

```python
re.search(pattern, string, flags)
m = re.search(r'\shan(ds)ome\s', text)
```

> 替换字符串

```python
re.sub(pattern, repl, string, count)
text = "JGood is a handsome boy, he is cool, clever, and so on..."
print re.sub(r'\s+', '-', text)
```

第二个为替换为repl，count为替换个数，默认0，每个都换

> 用正则表达式分隔

```python
re.split(r'\s+', text)
```

是否打印分隔符的问题，见

```python
import re
r1 = re.compile('\W+')
print r1.split('192.168.1.1')
print re.split('(\W+)','192.168.1.1')
print re.split('(\W+)','192.168.1.1',1)
```

输出

```python
['192', '168', '1', '1']
['192', '.', '168', '.', '1', '.', '1']
['192', '.', '168.1.1']
```

> 获取所有符合的

```python
re.findall(r'\w*oo\w*', text)
```

> 建立模板

```python
regex = re.compile(r'\w*oo\w*')
print regex.findall(text)   #查找所有包含'oo'的单词
print regex.sub(lambda m: '[' + m.group(0) + ']', text) #将字符串中含有'oo'的单词用[]括起来。
```

flags定义包括：

re.I：忽略大小写

re.L：表示特殊字符集 \w, \W, \b, \B, \s, \S 依赖于当前环境

re.M：多行模式

re.S：’ . ’并且包括换行符在内的任意字符（注意：’ . ’不包括换行符）

re.U： 表示特殊字符集 \w, \W, \b, \B, \d, \D, \s, \S 依赖于 Unicode 字符属性数据库

### lambda表达式简化单行函数

简化单行函数，可以用for in if完成的不要用lambda，内部不要再包含循环，

对比

```python
>>> foo = [2, 18, 9, 22, 17, 24, 8, 12, 27]
>>>
>>> print filter(lambda x: x % 3 == 0, foo)
[18, 9, 24, 12, 27]
>>>
>>> print map(lambda x: x * 2 + 10, foo)
[14, 46, 28, 54, 44, 58, 26, 34, 64]
>>>
>>> print reduce(lambda x, y: x + y, foo)
139
```

和

```python
print [x * 2 + 10 for x in foo]
print [x for x in foo if x % 3 == 0]
```

## 异常处理

> 用户定义异常，引发异常，和异常处理

```python
#!/usr/bin/python
# Filename: raising.py

class ShortInputException(Exception):
    '''A user-defined exception class.'''
    def __init__(self, length, atleast):
        Exception.__init__(self)
        self.length = length
        self.atleast = atleast

try:
    s = raw_input('Enter something --> ')
    if len(s) < 3:
        raise ShortInputException(len(s), 3)
    # Other work can continue as usual here
except EOFError:
    print '\nWhy did you do an EOF on me?'
except ShortInputException, x:
    print 'ShortInputException: The input was of length %d, \
          was expecting at least %d' % (x.length, x.atleast)
else:
    print 'No exception was raised.' 
```

## 字典处理

> 对字典按键、值排序

```python
sorted(dic.keys())
sorted(dic.items(), key=lamda item:item[0]) #选取符合格式的第一个值作为比较
```

> 两个列表组成一个字典

```python
dic = dict(zip(num, word))
```

## lambda模板操作

> 按字符中的数字排列字符串

```python
def order2(sentence):
    return " ".join(sorted(sentence.split(), key=lambda x: int(filter(str.isdigit, x))))
#输入"is2 Thi1s T4est 3a"输出"Thi1s is2 3a T4est"
```

###  

# 正则表达式全部符号

| 字符          | 描述                                       |
| ----------- | ---------------------------------------- |
| \           | 将下一个字符标记为一个特殊字符、或一个原义字符、或一个 向后引用、或一个八进制转义符。例如，'n' 匹配字符 "n"。'\n' 匹配一个换行符。序列 '\\' 匹配 "\" 而 "\(" 则匹配 "("。 |
| ^           | 匹配输入字符串的开始位置。如果设置了 RegExp 对象的 Multiline 属性，^ 也匹配 '\n' 或 '\r' 之后的位置。 |
| $           | [匹配输入字符串的结束位置。如果设置了](undefined)RegExp 对象的 Multiline 属性，$ 也匹配 '\n' 或 '\r' 之前的位置。 |
| *           | [匹配前面的子表达式零次或多次。例如，](undefined)zo* 能匹配 "z" 以及 "zoo"。* 等价于{0,}。 |
| +           | [匹配前面的子表达式一次或多次。例如，](undefined)'zo+' 能匹配 "zo" 以及 "zoo"，但不能匹配 "z"。+ 等价于 {1,}。 |
| ?           | [匹配前面的子表达式零次或一次。例如，](undefined)"do(es)?" 可以匹配 "do" 或 "does" 中的"do" 。? 等价于 {0,1}。 |
| {n}         | [n  ](undefined)是一个非负整数。匹配确定的 n 次。例如，'o{2}' 不能匹配 "Bob" 中的 'o'，但是能匹配 "food" 中的两个 o。 |
| {n,}        | n 是一个非负整数。至少匹配n 次。例如，'o{2,}' 不能匹配 "Bob" 中的 'o'，但能匹配 "foooood" 中的所有 o。'o{1,}' 等价于 'o+'。'o{0,}' 则等价于 'o*'。  {n,m}  m 和 n 均为非负整数，其中n <= m。最少匹配 n 次且最多匹配 m 次。例如，"o{1,3}" 将匹配 "fooooood" 中的前三个 o。'o{0,1}' 等价于 'o?'。请注意在逗号和两个数之间不能有空格。 |
| x\\{m\\}    | 重复字符x，m次，如：'0\{5\}'匹配包含5个o的行。            |
| x\\{m,\\}   | 重复字符x,至少m次，如：'o\{5,\}'匹配至少有5个o的行。        |
| x\\{m,n\\}  | 重复字符x，至少m次，不多于n次，如：'o\{5,10\}'匹配5--10个o的行。 |
| ?           | [当该字符紧跟在任何一个其他限制符](undefined) (*, +, ?, {n}, {n,}, {n,m}) 后面时，匹配模式是非贪婪的。非贪婪模式尽可能少的匹配所搜索的字符串，而默认的贪婪模式则尽可能多的匹配所搜索的字符串。例如，对于字符串 "oooo"，'o+?' 将匹配单个 "o"，而 'o+' 将匹配所有 'o'。 |
| .           | 匹配除 "\n" 之外的任何单个字符。要匹配包括 '\n' 在内的任何字符，请使用象 '[.\n]' 的模式。 |
| (pattern)   | 匹配pattern 并获取这一匹配。所获取的匹配可以从产生的 Matches 集合得到，在VBScript 中使用 SubMatches 集合，在JScript 中则使用 $0…$9 属性。要匹配圆括号字符，请使用 '\(' 或 '\)'。 |
| (?:pattern) | [匹配](undefined) pattern 但不获取匹配结果，也就是说这是一个非获取匹配，不进行存储供以后使用。这在使用 "或" 字符 (\|) 来组合一个模式的各个部分是很有用。例如， 'industr(?:y\|ies) 就是一个比 'industry\|industries' 更简略的表达式。 |
| (?=pattern) | [正向预查，在任何匹配](undefined) pattern 的字符串开始处匹配查找字符串。这是一个非获取匹配，也就是说，该匹配不需要获取供以后使用。例如，'Windows (?=95\|98\|NT\|2000)' 能匹配 "Windows 2000" 中的 "Windows" ，但不能匹配 "Windows 3.1" 中的 "Windows"。预查不消耗字符，也就是说，在一个匹配发生后，在最后一次匹配之后立即开始下一次匹配的搜索，而不是从包含预查的字符之后开始。 |
| (?!pattern) | 负向预查，在任何不匹配 pattern 的字符串开始处匹配查找字符串。这是一个非获取匹配，也就是说，该匹配不需要获取供以后使用。例如'Windows (?!95\|98\|NT\|2000)' 能匹配 "Windows 3.1" 中的 "Windows"，但不能匹配 "Windows 2000" 中的 "Windows"。预查不消耗字符，也就是说，在一个匹配发生后，在最后一次匹配之后立即开始下一次匹配的搜索，而不是从包含预查的字符之后开始。 |
| x\|y        | [匹配](undefined) x 或 y。例如，'z\|food' 能匹配 "z" 或 "food"。'(z\|f)ood' 则匹配 "zood" 或 "food"。 |
| [xyz]       | [字符集合。匹配所包含的任意一个字符。例如，](undefined) '[abc]' 可以匹配 "plain" 中的 'a'。 |
| [^xyz]      | [负值字符集合。匹配未包含的任意字符。例如，](undefined) '[^abc]' 可以匹配 "plain" 中的'p'。 |
| [a-z]       | [字符范围。匹配指定范围内的任意字符。例如，](undefined)'[a-z]' 可以匹配 'a' 到 'z' 范围内的任意小写字母字符。 |
| [^a-z]      | [负值字符范围。匹配任何不在指定范围内的任意字符。例如，](undefined)'[^a-z]' 可以匹配任何不在 'a' 到 'z' 范围内的任意字符。 |
| \b          | [匹配一个单词边界，也就是指单词和空格间的位置。例如，](undefined) 'er\b' 可以匹配"never" 中的 'er'，但不能匹配 "verb" 中的 'er'。'\bgrep\b'只匹配grep |
| \B          | [匹配非单词边界。](undefined)'er\B' 能匹配 "verb" 中的 'er'，但不能匹配 "never" 中的 'er'。 |
| \cx         | [匹配由](undefined) x 指明的控制字符。例如， \cM 匹配一个 Control-M 或回车符。x 的值必须为 A-Z 或 a-z 之一。否则，将 c 视为一个原义的 'c' 字符。 |
| \d          | [匹配一个数字字符。等价于](undefined) [0-9]。         |
| \D          | [匹配一个非数字字符。等价于](undefined)\[^0-9\]。      |
| \f          | [匹配一个换页符。等价于](undefined) \x0c 和 \cL。     |
| \n          | [匹配一个换行符。等价于](undefined) \x0a 和 \cJ。     |
| \r          | [匹配一个回车符。等价于](undefined) \x0d 和 \cM。     |
| \s          | [匹配任何空白字符，包括空格、制表符、换页符等等。等价于](undefined) [ \f\n\r\t\v]。 |
| \S          | [匹配任何非空白字符。等价于](undefined) [^ \f\n\r\t\v]。 |
| \t          | [匹配一个制表符。等价于](undefined) \x09 和 \cI。     |
| \v          | [匹配一个垂直制表符。等价于](undefined) \x0b 和 \cK。   |
| \w          | [匹配包括下划线的任何单词字符。等价于](undefined)'[A-Za-z0-9_]'。 |
| \W          | [匹配任何非单词字符。等价于](undefined) '[^A-Za-z0-9_]'。 |
| \xn         | [匹配](undefined) n，其中 n 为十六进制转义值。十六进制转义值必须为确定的两个数字长。例如，'\x41' 匹配 "A"。'\x041' 则等价于 '\x04' & "1"。正则表达式中可以使用 ASCII 编码。 |
| \num        | [匹配](undefined) num，其中 num 是一个正整数。对所获取的匹配的引用。例如，'(.)\1' 匹配两个连续的相同字符。 |
| \n          | [标识一个八进制转义值或一个向后引用。如果](undefined) \n 之前至少 n 个获取的子表达式，则 n 为向后引用。否则，如果 n 为八进制数字 (0-7)，则 n 为一个八进制转义值。 |
| \nm         | [标识一个八进制转义值或一个向后引用。如果](undefined) \nm 之前至少有 nm 个获得子表达式，则 nm 为向后引用。如果 \nm 之前至少有 n 个获取，则 n 为一个后跟文字 m 的向后引用。如果前面的条件都不满足，若 n 和 m 均为八进制数字 (0-7)，则 \nm 将匹配八进制转义值 nm。 |
| \nml        | [如果](undefined) n 为八进制数字 (0-3)，且 m 和 l 均为八进制数字 (0-7)，则匹配八进制转义值 nml。 |
| \un         | [匹配](undefined) n，其中 n 是一个用四个十六进制数字表示的 Unicode 字符。例如， \u00A9 匹配版权符号 (?)。 |
| \\(..\\)    | 标记匹配字符，如'\(love\)'，love被标记为1。            |
| \\<         | 锚定单词的开始，如:'\<grep'匹配包含以grep开头的单词的行。      |
| \\>         | 锚定单词的结束，如'grep\>'匹配包含以grep结尾的单词的行。       |

匹配POSIX字符

[:alnum:]    #文字数字字符   

[:alpha:]    #文字字符   

[:digit:]    #数字字符   

[:graph\:]    #非空字符（非空格、控制字符）   

[:lower:]    #小写字符   

[:cntrl:]    #控制字符   

[:print:]    #非空字符（包括空格）   

[:punct:]    #标点符号   

[:space:]    #所有空白字符（新行，空格，制表符）   

[:upper:]    #大写字符   

[:xdigit:]   #十六进制数字（0-9，a-f，A-F）


















模块函数：



.split()分隔
用法str.split(str="", num=string.count(str))
str -- 分隔符，默认为空格。
num -- 分割次数。
返回分割后的字符串列表

.strip(rm)
只要开头结尾的字符在删除序列内，删除字符，空则删除空白符（'\n','\r','\t',''）

r''表示读取

.open(path, 'r')	#只读模式打开	（rd）
.close()			#对应关闭文件

.readline() #按行读取，使用readlines效率更高，readlines自动将内容分析成一个行的列表

list.append()	#添加到list后面

.lower()		#全部转化为小写

commands.getoutput(cmd)		#执行cmd命令，返回输出路径
commands.getstatus(cmd)		#执行cmd命令，返回输出值
commands.getstatusoutput(cmd)		#执行cmd命令，返回输出值和输出路径，两个值赋给两个值

.endswith()  #以字符串结尾

名称过滤函数
def name_fileter(name_list, suffix):
    '''根据后缀过滤list'''
    def match_name(name):
        if name.lower().endswith(suffix.lower()):				#name里所有的大写字符转换为小写，以suffix转换为小写结尾
            return True
        return False
    return filter(match_name, name_list)						#filter，自定一个函数，以此过滤需要过滤的列，返回True,False,filter可以将结果为True的组成一个list返回。

os.path.isfile()		#是否是普通文件
os.path.basename(source_file)		#取文件名
os.path.join(target_dir, file_name)			#在路径后连接文件或目录
os.path.isdir(mnt_dir):
os.path.ismount(mnt_dir)
os.rmdir(mnt_dir)
os.path.exists(mnt_dir):
os.makedirs(mnt_dir)
os.listdir()			#列出内容
os.system()				#执行其他命令或脚本

shutil.copy(source_file, target_dir)		#拷贝文件
shutil.rmtree(path)							#移除目录

cmd = "umount %s" %(mnt_dir)				#执行的命令，%s代替参数

if __name__ == "__main__"
__name__，
如果是放在Modules模块中，就表示是模块的名字；
如果是放在Classs类中，就表示类的名字；
脚本的主模块的名字，始终都叫做__main__。

options,args = getopt.getopt(sys.argv[1:],"hp:i:",["help","ip=","port="])			#用于执行命令行代码
“hp:i:”
短格式 --- h 后面没有冒号：表示后面不带参数，p：和 i：后面有冒号表示后面需要参数
["help","ip=","port="]
长格式 --- help后面没有等号=，表示后面不带参数，其他三个有=，表示后面需要参数
返回值 options 是个包含元祖的列表，每个元祖是分析出来的格式信息，比如 [('-i','127.0.0.1'),('-p','80')] ;
args 是个列表，包含那些没有‘-’或‘--’的参数，比如：['55','66']
注意：定义命令行参数时，要先定义带'-'选项的参数，再定义没有‘-’的参数

getopt.GetoptError

try和except#尝试可能出错的语句，except处理异常。
try:
……
except Exception as e:
	print(e)						#捕捉异常并将异常输出


hv_dic = {each: common.get_rpm_info(os.path.join(G_HV_RPMS_DIR, each)).name for each in hv_list}	#dic格式

模块
import paramiko 仅需要在本地上安装相应的软件（python以及PyCrypto），对远程服务器没有配置要求，对于连接多台服务器，进行复杂的连接操作特别有帮助。

get()语法：dict.get(key, default=None)
参数
key -- 字典中要查找的键。
default -- 如果指定键的值不存在时，返回该默认值值。

正则表达式，import re
re.match ：只从字符串的开始与正则表达式匹配，匹配成功返回matchobject，否则返回none；
re.search ：将字符串的所有字串尝试与正则表达式匹配，如果所有的字串都没有匹配成功，返回none，否则返回matchobject；（re.search相当于perl中的默认行为）



pdb调试：
import pdb
在需要加断点的地方加pdb.set.trace()
(Pdb) l #打印近几行的数据
(Pdb) import os #可以载入模块
(Pdb) import commands #载入执行shell命令的模块
(Pdb) p os.listdir('/tmp') #可以在python当前显示目录，p为打印参数/变量
(Pdb) out = commands.getoutput('cat /tmp/package-installs.json') 
#用command模块可以执行shell命令并获得输出
(Pdb) p out  #同样打印出参数信息
(Pdb) for each in out: print each #还可以循环打印







