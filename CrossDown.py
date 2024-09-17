from typing import *
import re

import markdown


class Header:
    def __init__(self, text: str):
        self.text = text

    def __call__(self, *args, **kwargs):
        """
        渲染标题
        # 一级标题
        ## 二级标题
        ### 三级标题
        #### 四级标题
        ##### 五级标题
        ###### 六级标题
        :return: 处理后的文本
        """
        h6 = re.sub(r'###### (.*?)\n', r'<h6>\1</h6>\n', self.text)  # H6
        h5 = re.sub(r'##### (.*?)\n', r'<h5>\1</h5>\n', h6)  # H5
        h4 = re.sub(r'#### (.*?)\n', r'<h4>\1</h4>\n', h5)  # H4
        h3 = re.sub(r'### (.*?)\n', r'<h3>\1</h3>\n', h4)  # H3
        h2 = re.sub(r'## (.*?)\n', r'<h2>\1</h2>\n', h3)  # H2
        h1 = re.sub(r'# (.*?)\n', r'<h1>\1</h1>\n', h2)  # H1
        return h1


class Style:
    """
    渲染字体样式
    """

    def __init__(self, text: str):
        """
        初始化
        :param text: cd文本
        """
        self.text = text

    def italic(self):
        """
        *斜体*
        :return:
        """
        self.text = re.sub(r'\*([^*\n]+)\*', r'<i>\1</i>', self.text)

    def bold(self):
        """
        **粗体**
        :return:
        """
        self.text = re.sub(r'\*\*([^*\n]+)\*\*', r'<b>\1</b>', self.text)

    def underline(self):
        """
        ~下划线~
        :return:
        """
        self.text = re.sub(r'~([^~\n]+)~', r'<u>\1</u>', self.text)

    def strikethrough(self):
        """
        ~~删除线~~
        :return:
        """
        self.text = re.sub(r'~~([^~\n]+)~~', r'<s>\1</s>', self.text)

    def highlight(self):
        """
        ==高亮==
        :return:
        """
        self.text = re.sub(r'==([^=\n]+)==', r'<mark>\1</mark>', self.text)

    def up(self):
        """
        [在文本的正上方添加一行小文本]^(主要用于标拼音)
        :return:
        """
        self.text = re.sub(r'\[(.*?)]\^\((.*?)\)', r'<ruby>\1<rt>\2</rt></ruby>', self.text)

    def hide(self):
        """
        [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)
        :return:
        """
        self.text = re.sub(r'\[(.*?)]-\((.*?)\)', r'<span title="\2">\1</span>', self.text)

    def split_line(self):
        """
        添
        ***
        加
        ___
        分
        ---
        隔
        :return:
        """
        self.text = re.sub(r'([*_-]){3}\n', r'<hr>', self.text)

    def __call__(self, *args, **kwargs):
        """
        一键运行
        :param args:
        :param kwargs:
        :return:
        """
        # self.bold()
        # self.italic()
        self.strikethrough()
        self.underline()
        self.highlight()
        self.up()
        self.hide()
        # self.split_line()
        return self.text


class Link:
    """
    添加链接
    """

    def __init__(self, text: str):
        """
        初始化
        :param text: cd文本
        """
        self.text = text

    def image(self):
        """
        ![链接图片](链接地址)
        :return:
        """
        self.text = re.sub(r'!\[([^\[\]\n]+)]\(([^()\n]+)\)', r'<img src="\2" alt="\1">', self.text)

    def link(self):
        """
        [链接文本](链接地址)
        :return:
        """
        self.text = re.sub(r'\[([^\[\]\n]+)]\(([^()\n]+)\)', r'<a href="\2">\1</a>', self.text)

    def __call__(self, *args, **kwargs):
        """
        一键运行
        :param args:
        :param kwargs:
        :return:
        """
        self.image()
        self.link()
        return self.text


class Value:
    """
    定义: {变量名} = 值
    赋值: {变量或锚点名}
    锚点: {#锚点名}
    """
    def __init__(self, text: str):
        self.text = text
        self.values = {
            key: value for key, value in re.findall(r'\{([^{}#]+)} ?= ?(.+?)(?=\n|$)', text)
        }  # 从text中提取所有变量并转换成字典
        self.anchor = re.findall(r'\{#([^{}#]+)}', text)

    def __call__(self, *args, **kwargs) -> Tuple[str, Dict[str, str]]:
        """
        将所有变量赋值并移除变量定义
        :param args:
        :param kwargs:
        :return: 赋值后的正文
        """
        text = self.text
        for item in self.anchor:
            text = re.sub(r'\{#(' + item + ')}', r'<span id="\1"></span>', text)  # 添加锚点
            text = re.sub(r'\{' + item + '}', fr'<a href="#{item}">{item}</a>', text)  # 添加页内链接
        for k, v in self.values.items():
            text = re.sub(r'\{' + k + '} ?= ?(.+?)(?=\n|$)', '', text)  # 移除变量的定义
            text = re.sub(r'\{' + k + '}', fr'{v}', text)  # 给变量赋值
        return text, self.values


class CodeBlock:
    def __init__(self, text: str):
        """
        找出`代码块`并移除代码标识
        :param text: 输入的文本
        """
        self.codes = [i for i in re.findall(r'`([^`]*)`', text) if i != '']  # 找出代码快
        self.text = re.sub(r'``', '', text)  # 移除代码标识`

    def __call__(self, *args, **kwargs):
        """
        临时移除代码块
        :param args:
        :param kwargs:
        :return: 不含代码的文本
        """
        for index, item in enumerate(self.codes):  # 替换代码块为-@@-(ID)-@@-
            self.text = re.sub(fr'`{re.escape(item)}`', f'\0\1{index}\1\0', self.text)  # 同时转译特殊字符
        return self.text

    def rendering(self, values: Dict[str, str]):
        """
        渲染代码
        :param values: 变量字典
        :return:
        """
        for index, code in enumerate(self.codes):
            if re.match(r'\{[^$]*}', code):  # 是变量
                # 给变量赋值
                key = re.findall(r'\{([^}]+)}', code)[0]  # 查找变量名
                code = re.sub(r'\{' + key + '}', fr'{values[key]}', code)
                self.codes[index] = code  # 给变量赋值
            if re.search(r'\n', code):  # 是多行代码
                head = re.findall(r'(.*?)\n', code)[0]
                if head in ('', 'yaml'):
                    self.codes[index] = f'<pre><code class="language-yaml">{code}</code></pre>'
                elif head in ('shell', 'python'):
                    self.codes[index] = f'<pre><code class="language-{head}">{re.sub(f"({head})", "", code)}</code></pre>'
                elif head in ('mermaid',):
                    self.codes[index] = f'<div class="{head}">{re.sub(f"({head})", "", code)}</div>'
            elif re.match(r'\$[^$]*\$', code):  # 是LaTex代码(单行)
                self.codes[index] = re.sub(fr'\$([^$]*)\$', r'<p>\(\1\)</p>', code)
            else:  # 是突出块
                self.codes[index] = f'<span class="block">{code}</span>'

    def restore(self, new_text: str):
        """
        将渲染好的代码重新放回处理好的正文
        :param new_text: 处理好的正文
        :return: 加上代码的文章
        """
        for index, item in enumerate(self.codes):
            new_text = re.sub(f'\0\1{index}\1\0', f'{item}', new_text, flags=re.DOTALL)
        return new_text


class Escape:  # TODO 还有点问题
    """
    转义\后字符
    """

    def __init__(self, text: str):
        """
        找出转义符并转义
        :param text: 输入的文本
        """
        self.text = text
        self.escapes = {
            i: f'\0\1\2{i}\2\1\0' for i in re.findall(r'(\\.)', text)
        }   # 找出要转义的字符

    def __call__(self, *args, **kwargs):
        """
        临时移除代码块
        :param args:
        :param kwargs:
        :return: 不含代码的文本
        """
        for index, item in self.escapes.items():  # 替换代码块为\0\1\2(id)\2\1\0
            self.text = re.sub(fr'{re.escape(index)}', re.escape(item), self.text)  # 同时转译特殊字符
            print(item)
        return self.text

    def back(self, text):
        """
        将被转义的字符放回文本中
        :param text: 新文本
        :return: 放回转义字符的文本
        """
        for index, item in self.escapes.items():  # 替换\0\1\2(id)\2\1\0为转义字符
            print(item)
            self.text = re.sub(item, '', text)  # 同时转译特殊字符
        return self.text

    def restore(self, new_text: str):
        """
        将渲染好的代码重新放回处理好的正文
        :param new_text: 处理好的正文
        :return: 加上代码的文章
        """
        for index, item in enumerate(self.escapes):
            new_text = re.sub(fr'-@@-{index}-@@-', f'{item}', new_text, flags=re.DOTALL)
        return new_text


class Cite:
    """
    > 渲染引用 --[引用来源]
    """
    def __init__(self, text):
        self.text = text

    def __call__(self, *args, **kwargs) -> str:
        self.text = re.sub('> (.*?) --\[(.*?)]\n', r'<blockquote>\1<footer><cite>\2</cite></footer></blockquote>', self.text)  # 渲染有来源的引用
        self.text = re.sub('> (.*?)\n', r'<blockquote>\1</blockquote>\n', self.text)  # 渲染没有来源的引用
        return self.text


class Syllabus:
    """
    1. 找到提纲
    1.1 找到符合若干个‘数字+点+数字’且首尾都是数字的行
    """
    def __init__(self, text):
        self.text = text
        self.syllabus = {tuple(num.split('.')): txt for num, txt in re.findall(r'([\.|\d]+) ([^ ]+?)\n', self.text) if not num.endswith('.')}  # 找出提纲

    def __call__(self, *args, **kwargs):
        for num, txt in self.syllabus.items():
            self.text = re.sub(f'{".".join(num)} {re.escape(txt)}', f'{"#" * len(num)}{".".join(num)} {txt}{{#' + '.'.join(num) + f'}}\n', self.text)  # 按照层级为提纲添加不同等级的标题并创建锚点
        return self.text


class Basic:
    def __init__(self, text: str):
        self.text: str = text

    @staticmethod
    def strong_annotation(text: str) -> str:
        """
        移除|=强注释=|
        :param text: 原始文本
        :return: 移除强注释后的文本
        """
        return re.sub('\|=[\s\S]*=\|', '', text, re.DOTALL)

    @staticmethod
    def week_annotation(text: str) -> str:
        """
        移除 // 弱注释
        :param text: 原始文本
        :return: 移除弱注释后的文本
        """
        return re.sub('// .*?\n', '\n', text)

    def paragraph(self):
        """
        为普通的行套上<p>段落标签</p>
        """
        # TODO 有点问题
        self.text = re.sub(r'<p>(<.+?>.*?<.+?>)</p>\n',
                           r'\1\n',  # 移除已被标签包裹的行的额外的<p>标签
                           '\n'.join(
                               [
                                   f'<p>{line}</p>' if not re.search('\0.+?\0', line) else line  # 识别-@@-n-@@-并保留
                                   for line in self.text.splitlines()  # 把所有非空的行都套上<p>标签
                                   if not re.search(r'^\s*\n?$', line)  # 识别空行或空白行
                               ]
                           )
                           )

    def __call__(self, *args, **kwargs):
        self.paragraph()
        return self.text


def add_indent_to_string(input_string: str, indent_spaces: int = 4):
    """
    给字符串中的每一行前面加上缩进。
    :param input_string: 原始字符串，可以包含多行。
    :param indent_spaces: 每行前面要添加的空格数，默认为4。
    :return: 带缩进的新字符串。
    """
    # 使用字符串的splitlines()方法分割原始字符串为行列表
    lines = input_string.splitlines()

    # 遍历行列表，给每行前面加上相应的缩进，并重新组合成字符串
    indented_string = "\n".join(f"{' ' * indent_spaces}{line}" for line in lines)

    return indented_string


def body(text: str) -> Tuple[str, Dict[str, str]]:
    """
    渲染正文部分
    :param text: 输入正文
    :return: 输出渲染后的正文
    """
    escape = Escape(text)  # 转义
    text = escape()
    text = Basic.week_annotation(text)  # 移除弱注释
    text = Syllabus(text)()  # 渲染提纲
    text, values = Value(text)()  # 提取变量并赋值到文本中
    # text = Header(text)()  # 渲染标题
    text = Style(text)()  # 渲染字体样式
    # text = Link(text)()  # 渲染特殊功能
    # text = Cite(text)()  # 渲染引用
    # text = Basic(text)()  # 渲染基础格式
    text = markdown.markdown(text, extensions=['markdown.extensions.extra'])  # 渲染标准markdown
    text = escape.back(text)  # 放回被转义的字符

    # text = Basic.paragraph(text)  # 渲染段落
    return text, values


def main(origen: str):
    # 预处理、
    origen = Basic.strong_annotation(origen)  # 移除强注释
    code_block = CodeBlock(origen)  # 获取代码内容
    text = code_block()  # 暂时移除代码
    # 处理正文
    text, values = body(text)
    # 后处理
    code_block.rendering(values)  # 渲染代码
    return code_block.restore(text)  # 放回代码


if __name__ == '__main__':
    with open('README.md', encoding='utf-8') as test:
        cd = main(test.read())
    with open('README.html', 'w', encoding='utf-8') as html:
        html.write(f"""<!DOCTYPE html>  
<html lang="zh-CN">  
<head>  
    <meta charset="UTF-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  
    <title>CrossDown</title>  
    <script type="text/javascript" async
      src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
    <link href="https://cdn.jsdelivr.net/npm/prismjs/themes/prism.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/prismjs/prism.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs/components/prism-yaml.min.js"></script>
    <style>  
    .block {{  
        background-color: grey; /* 灰色背景 */  
        color: white; /* 白色文字 */  
    }}
    </style> 
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <!-- 可以在这里添加其他元数据和CSS链接 -->  
</head>  
<body>
    <script>  
        mermaid.initialize({{startOnLoad:true}});  
    </script>
    {add_indent_to_string(cd, 4)}
</body>  
</html>
""")
