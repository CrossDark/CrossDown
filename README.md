Title:   My Document
Summary: A brief description of my document.
Authors: Waylan Limberg
         John Doe
Date:    October 2, 2007
blank-value: 
base_url: http://example.com

[TOC]

# CrossDown
自制的markdown，添加了一些自定义的语法
效果请见[README.html](https://github.com/CrossDark/CrossDown/blob/main/README.html)

1 基本语法

1.1 标题

# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题

1.2 样式

1.2.1 *斜体*

1.2.2 **粗体**

1.2.3 ***粗斜体***

1.2.4 ~下划线~

1.2.5 ~~删除线~~

1.2.6 ==高亮==

1.2.7 [在文本的正上方添加一行小文本]^(主要用于标拼音)

1.2.8 [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)

1.2.9 分割线

---
___
***

1.3 链接

1.3.1 普通链接

[链接文本](链接地址)

[CrossDark](https://crossdark.com)

<https://crossdark.net/>

1.3.2 图片

![链接图片](链接地址)

![sea](https://crossdark.com/wp-content/uploads/2024/05/1715259682-sea.jpg)

1.3.3 变量链接

[链接文本][变量]

[变量]: https://crossdark.com

2 变量

2.1 定义

{变量名} = 值

2.2 赋值

{变量名} {锚点名}

提纲的编号已经自动配置为了锚点,可直接使用{2}

2.3 添加锚点

{#锚点名}

3 代码块

3.1 `单行`

3.1.1 LaTex

`$CO_2$`

`$H_2O$`

3.1.2 函数

`¥y=x*2+1¥`  // 不定义范围

`¥y=x**2¥€-50,50€`  // 定义了x范围

`¥y=x**3¥€-50,50|-100,100€`  // 定义了y范围

3.2 多行

3.2.1 YAML

`
A:
    1. a
    2. b
    3. c
B:
    - a
    - b
    - c
`

3.2.2 Python

`python
print('CrossDown')
`

3.2.3 Mermaid

`mermaid
graph LR
    A-->B
    A-->C
    B-->D
    C-->D
`

4 转义

\\ 

\a 

\*

5 引用

> 一级引用
>> 二级引用
>>> 三级引用
>>>> 四级引用
>>>>> 五级引用
>>>>>> 六级引用
> 
> 引文内添加*斜体***粗体**~下划线~~~删除线~~==高亮==

6 提纲

6.1 提纲号

以数字和点组成,通过空格与提纲名分隔,例如:

6.1.1 提纲号示例

点不能出现在开头或结尾,例如

.6.1.2 错误示范

6.1.3. 错误示范

不能出现两个及以上连续的点,例如:

6..1...4 错误示范

提纲号会被自动配置为锚点,可直接使用{6}{6.1}

7 注释

7.1 强注释

|=
无论如何都会被移除
`放在代码块里也没用`
=|

7.2 弱注释

<!-- 这是注释 -->

只有在 // 后面才会被移除

`// 代码中的注释弱不会被移除`

8 列表

8.1 有序列表
1. a
2. b
3. c
4. d

8.2 无序列表
- A
- B
- C
- D

9 表格

| 表头1  | 表头2  | 表头3  |  
|:----:|:----:|:----:|  
| 单元格1 | 单元格2 | 单元格3 |  
| 单元格4 | 单元格5 | 单元格6 |

10 警告

!!! 这是一条警告

11 Emoji

:person_biking:

:grinning_face_with_big_eyes:

12 扩展语法

12.1 警告

!!! danger "Don't try this at home"
