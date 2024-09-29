import time
from typing import *
import re
import emoji
import markdown

try:  # 检测当前平台是否支持扩展语法
    import CrossMore

    EXTRA_ABLE = True
except ModuleNotFoundError:
    EXTRA_ABLE = False

__all__ = [
    'main',  # 主函数
    'indent',  # 添加空格
    'body',  # 主题函数
    'Style',  # 风格
    'Value',  # 变量
    'CodeBlock',  # 代码块
    'Syllabus',  # 提纲
    'Basic',  # 基础
    'HEAD',
    'BODY',
]
__version__ = '0.11.2'
__author__ = 'CrossDark'
__email__ = 'liuhanbo333@icloud.com'
__source__ = 'https://crossdark.net/'
__license__ = """MIT"""

HEAD = (
    '<script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"></script>',
    '<link href="https://cdn.jsdelivr.net/npm/prismjs/themes/prism.css" rel="stylesheet" />',
    '<script src="https://cdn.jsdelivr.net/npm/prismjs/prism.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/prismjs/components/prism-yaml.min.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>',
    '<style>',
    '   .block {',
    '   background-color: grey; /* 灰色背景 */',
    '   color: white; /* 白色文字 */',
    '}',
    '</style>'
)

BODY = (
    '<script>',
    '   mermaid.initialize({{startOnLoad:true}});',
    '</script>',
    '<script>',
    '   document.addEventListener("DOMContentLoaded", function() {',
    '   emojify.run();',
    '});',
    '</script>',
)


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

    def __call__(self, *args, **kwargs) -> str:
        """
        一键运行
        :param args:
        :param kwargs:
        :return: 处理后的文本
        """
        self.strikethrough()
        self.underline()
        self.highlight()
        self.up()
        self.hide()
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

    def __call__(self, *args, **kwargs) -> str:
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
                    self.codes[
                        index] = f'<pre><code class="language-{head}">{re.sub(f"({head})", "", code)}</code></pre>'
                elif head in ('mermaid',):
                    self.codes[index] = f'<div class="{head}">{re.sub(f"({head})", "", code)}</div>'
            elif re.match(r'\$[^$]*\$', code):  # 是LaTex代码(单行)
                self.codes[index] = re.sub(fr'\$([^$]*)\$', r'<p>\(\1\)</p>', code)
            elif re.match(r'¥[^$]*¥', code):  # 是数学函数(单行)
                if EXTRA_ABLE:
                    expression, range_ = re.findall(r'¥([^$]*)¥(€[^$]*€)?', code)[0]  # 分离表达式与范围(如果有)
                    x_r = (-10, 10)
                    y_r = (-20, 20)
                    if range_ != '':  # 定义了范围
                        ranges = range_[1:-1].split('|')
                        if len(ranges) in (1, 2):  # 定义的范围正确
                            x_r = tuple(int(i) for i in ranges[0].split(','))
                            if len(ranges) == 2:  # 定义了y范围
                                y_r = tuple(int(i) for i in ranges[1].split(','))
                    self.codes[index] = CrossMore.function_drawing(  # 绘制函数图像
                        function=lambda x: eval(expression.split('=')[1]), x_range=x_r, y_range=y_r
                    )

                else:
                    self.codes[index] = '<mark>该平台不支持扩展语法</mark>'
            else:  # 是突出块
                self.codes[index] = f'<span class="block">{code}</span>'

    def restore(self, new_text: str) -> str:
        """
        将渲染好的代码重新放回处理好的正文
        :param new_text: 处理好的正文
        :return: 加上代码的文章
        """
        for index, item in enumerate(self.codes):
            new_text = re.sub(f'\0\1{index}\1\0', f'{item}', new_text, flags=re.DOTALL)
        return new_text


class Syllabus:
    """
    1. 找到提纲
    2 找到符合若干个‘数字+点+数字’且首尾都是数字的行
    每个提纲编号全文只能出现一次
    """

    def __init__(self, text: str):
        self.text = text

    def __call__(self, *args, **kwargs) -> str:
        return '\n'.join([
            (lambda match, origen:
             re.sub(f'^({match.groups()[0]})',  # 按照提纲等级添加#和锚点
                    fr'{"#" * len(match.groups()[0].split("."))} \1{{#' + match.groups()[0] + '}', origen)
             if match is not None else origen)  # 对于不是提纲的行,直接返回原始字符
            ((lambda x: re.match(r'^([\d.]+) ', x)  # 判断是否是提纲
            if not any((x.startswith('.'),  # 以.开头
                        re.search('\. ', x) is not None,  # 存在.+空格
                        re.search('\.{2,}', x),  # 存在连续的.
                        ))
            else None)(line), line)  # 排除.在提纲号开头或结尾的情况
            for line in self.text.splitlines()  # 分割并遍历文本的每一行
        ])


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


def indent(input_: Union[str, List, Tuple], indent_spaces: int = 4) -> str:
    """
    给字符串中的每一行前面加上缩进。
    :param input_: 原始字符串，可以包含多行。
    :param indent_spaces: 每行前面要添加的空格数，默认为4。
    :return: 带缩进的新字符串。
    """
    # 使用字符串的splitlines()方法分割原始字符串为行列表,如果是可迭代对象则直接遍历
    # 遍历行列表，给每行前面加上相应的缩进，并重新组合成字符串
    return "\n".join(
        f"{' ' * indent_spaces}{line}" for line in (lambda x: x.splitlines() if isinstance(x, str) else x)(input_))


def body(text: str) -> Tuple[str, Dict[str, str]]:
    """
    渲染正文部分
    :param text: 输入正文
    :return: 输出渲染后的正文
    """
    text = Basic.week_annotation(text)  # 移除弱注释
    text = Syllabus(text)()  # 渲染提纲
    text, values = Value(text)()  # 提取变量并赋值到文本中
    text = Style(text)()  # 渲染字体样式
    text = markdown.markdown(text, extensions=[
        'markdown.extensions.extra',  # 扩展语法
        'markdown.extensions.codehilite',  # 语法高亮拓展
        'markdown.extensions.toc',  # 自动生成目录
        'markdown.extensions.admonition',  # 警告扩展
        'markdown.extensions.meta',  # 元数据
    ])  # 渲染标准markdown
    text = emoji.emojize(text)  # 渲染Emoji
    return text, values


def main(origen: str):
    # 预处理
    origen = Basic.strong_annotation(origen)  # 移除强注释
    code_block = CodeBlock(origen)  # 获取代码内容
    text = code_block()  # 暂时移除代码
    # 处理正文
    text, values = body(text)
    # 后处理
    code_block.rendering(values)  # 渲染代码
    return code_block.restore(text)  # 放回代码


if __name__ == '__main__':
    # 开始计时
    start_time = time.perf_counter_ns()
    # 主程序
    with open('README.md', encoding='utf-8') as test:
        cd = main(test.read())
    with open('README.html', 'w', encoding='utf-8') as html:
        html.write(f"""<!DOCTYPE html>  
<html lang="zh-CN">  
<head>  
    <meta charset="UTF-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  
    <title>UTF-8编码示例</title>  
{indent(HEAD)}
    <!-- 可以在这里添加其他元数据和CSS链接 -->  
</head>  
<body>
{indent(BODY)}
{indent(cd, 4)}
</body>  
</html>
""")
    # 停止计时
    end_time = time.perf_counter_ns()
    # 输出用时
    print("运行时间: {:.9f} 秒".format((end_time - start_time) / 1e9))
