from re import Match

from markdown.extensions import Extension, extra, admonition, meta, sane_lists, toc, wikilinks, codehilite

from pygments.formatters import HtmlFormatter

from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
from markdown.preprocessors import Preprocessor

from markdown.blockparser import BlockParser

from markdown import Markdown
from typing import *
import re
import lxml
import xml
import emoji

from .Define import Variable

try:  # 检测当前平台是否支持扩展语法
    from .Extra import *

    EXTRA_ABLE = True
except ModuleNotFoundError:  # 不支持扩展语法
    EXTRA_ABLE = False


class HighlightHtmlFormatter(HtmlFormatter):
    """
    用于给code highlight扩展添加语言类型
    """

    def __init__(self, lang_str='', **options):
        """
        初始化
        :param lang_str: 数据格式 {lang_prefix}{lang}
        :param options:
        """
        super().__init__(**options)
        self.lang_str = lang_str.split('-')[-1]

    def _wrap_code(self, source: str):
        yield 0, f'<code class="{self.lang_str}">'
        yield from source
        yield 0, '</code>'


Extensions = {
    '基本扩展': extra.ExtraExtension(fenced_code={'lang_prefix': ''}),
    '警告扩展': admonition.AdmonitionExtension(),
    '元数据': meta.MetaExtension(),
    '能列表': sane_lists.SaneListExtension(),
    '目录': toc.TocExtension(),
    '内部链接': wikilinks.WikiLinkExtension(),
    '代码高亮': codehilite.CodeHiliteExtension(guess_lang=False, pygments_formatter=HighlightHtmlFormatter),
}


class PreProcess(Preprocessor):
    """预处理"""
    def __init__(self, variable: Variable):
        super().__init__()
        self.variable = variable

    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        for line in lines:  # 逐行遍历
            for value in re.findall(r'\{\[(.+?)]}', line):  # 找到变量
                if value in self.variable:  # 变量已定义
                    line = re.sub(fr'\{{\[{value}]}}', self.variable[value], line)  # 替换变量为值
                else:
                    line = re.sub(fr'\{{\[{value}]}}', value, line)  # 不替换变量
            new_lines.append(line)
        return new_lines


class Simple(InlineProcessor):
    """
    可通过简单的正则表达式和HTML标签实现的样式
    """

    def __init__(self, pattern: str, tag: str):
        """
        初始化
        :param pattern: 正则表达式
        :param tag: html标签
        """
        super().__init__(pattern)
        self.tag = tag

    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[None, None, None]:
        """
        处理匹配
        :param m: re模块的匹配对象
        :param data: 被匹配的原始文本
        :return: 标签 匹配开始 匹配结束
        """
        tag = xml.etree.ElementTree.Element(self.tag)  # 创建标签
        tag.text = m.group(1)  # 获取匹配到的文本并设置为标签的内容

        return tag, m.start(), m.end()


class Nest(InlineProcessor):
    """
    需要嵌套HTML标签实现的样式
    """

    def __init__(self, pattern: str, outer_tag: str, inner_tag: str):
        """
        初始化
        :param pattern: 正则表达式
        :param outer_tag: 外层html标签
        :param inner_tag: 内层html标签
        """
        super().__init__(pattern)
        self.outer_tag = outer_tag
        self.inner_tag = inner_tag

    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[None, None, None]:
        """
        处理匹配
        :param m: re模块的匹配对象
        :param data: 被匹配的原始文本
        :return: 标签 匹配开始 匹配结束
        """
        outer_tag = xml.etree.ElementTree.Element(self.outer_tag)  # 创建外层标签
        inner_tag = xml.etree.ElementTree.SubElement(outer_tag, self.inner_tag)  # 创建内层标签
        outer_tag.text = m.group(1)  # 设置外层标签文本
        inner_tag.text = m.group(2)  # 设置内层标签文本

        return outer_tag, m.start(), m.end()


class ID(InlineProcessor):
    """
    需要对HTML标签设置ID实现的样式
    """

    def __init__(self, pattern: str, tag: str, property_: str, value: Union[str, bool] = None):
        """
        初始化
        :param pattern: 正则表达式
        :param tag: html标签
        :param property_: html标签属性名称
        :param value: html标签属性的值 不设置时为第二个匹配组,设置为整数时则为指定的匹配组,设置为字符串则为原始字符串
        """
        super().__init__(pattern)
        self.tag = tag
        self.property = property_
        self.value = value

    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[None, None, None]:
        """
        处理匹配
        :param m: re模块的匹配对象
        :param data: 被匹配的原始文本
        :return: 标签 匹配开始 匹配结束
        """
        tag = xml.etree.ElementTree.Element(self.tag)  # 创建标签
        tag.text = m.group(1)  # 设置标签内容
        tag.set(self.property, m.group(2) if self.value is None else self.value)  # 设置标签属性,属性的值默认为第二个匹配组

        return tag, m.start(), m.end()


class Emoji(InlineProcessor):
    """
    需要对HTML标签设置ID实现的样式
    """

    def __init__(self, pattern: str):
        """
        初始化
        :param pattern: 正则表达式
        """
        super().__init__(pattern)

    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[None, None, None]:
        """
        处理匹配
        :param m: re模块的匹配对象
        :param data: 被匹配的原始文本
        :return: 标签 匹配开始 匹配结束
        """
        return emoji.emojize(m.group(0)), m.start(), m.end()


class Syllabus(BlockProcessor):
    # 定义提纲的正则表达式
    syllabus_re = r'(\d+(\.\d+)*)\s+(.*)'

    def test(self, parent: xml.etree.ElementTree.Element, block: str) -> Match[str] | None | bool:
        """
        检查当前块是否匹配正则表达式
        :param parent: 当前块的Element对象
        :param block: 当前块的内容
        :return: 匹配成功与否
        """
        return re.match(self.syllabus_re, block)

    def run(self, parent: xml.etree.ElementTree.Element, blocks: List[str]) -> bool | None:
        """
        对匹配到的块进行处理
        :param parent: 当前块的Element对象
        :param blocks: 包含文本中剩余块的列表
        :return: 匹配成功与否
        """
        syllabus = re.match(self.syllabus_re, blocks[0])  # 匹配提纲的号和内容
        header = xml.etree.ElementTree.SubElement(parent, f'h{len(syllabus.group(1).split("."))}')  # 按照提纲号等级创建标题
        header.set('id', syllabus.group(1))  # 设置提纲ID
        header.text = syllabus.group(1) + ' ' + syllabus.group(3)  # 设置提纲内容
        blocks[0] = ''
        return False


class BoxBlock(BlockProcessor):
    def __init__(self, parser: BlockParser, re_start, re_end, style):
        """
        初始化
        :param parser: 块处理器
        :param re_start: 块的起始re表达式
        :param re_end: 块的终止re表达式
        :param style: 块的风格
        """
        super().__init__(parser)
        self.re_start = re_start  # start line, e.g., `   !!!!
        self.re_end = re_end  # last non-blank line, e.g, '!!!\n  \n\n'
        self.style = style

    def test(self, parent: xml.etree.ElementTree.Element, block: str) -> Match[str] | None | bool:
        """
        检查当前块是否匹配正则表达式
        :param parent: 当前块的Element对象
        :param block: 当前块的内容
        :return: 匹配成功与否
        """
        return re.match(self.re_start, block)

    def run(self, parent: xml.etree.ElementTree.Element, blocks: List[str]) -> bool | None:
        """
        对匹配到的块进行处理
        :param parent: 当前块的Element对象
        :param blocks: 包含文本中剩余块的列表
        :return: 匹配成功与否
        """
        original_block = blocks[0]
        blocks[0] = re.sub(self.re_start, '', blocks[0])

        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            if re.search(self.re_end, block):
                # remove fence
                blocks[block_num] = re.sub(self.re_end, '', block)
                # render fenced area inside a new div
                e = xml.etree.ElementTree.SubElement(parent, 'div')
                e.set('style', self.style)
                self.parser.parseBlocks(e, blocks[0:block_num + 1])
                # remove used blocks
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False


class _Anchor(InlineProcessor):
    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[None, None, None]:
        """
        处理匹配
        :param m: re模块的匹配对象
        :param data: 被匹配的原始文本
        :return: 标签 匹配开始 匹配结束
        """
        tag = xml.etree.ElementTree.Element('span')  # 创建标签
        tag.text = m.group(1)
        tag.set('id', m.group(1))  # 设置id

        return tag, m.start(), m.end()


class LinkLine(InlineProcessor):
    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[None, None, None]:
        """
        处理匹配
        :param m: re模块的匹配对象
        :param data: 被匹配的原始文本
        :return: 标签 匹配开始 匹配结束
        """
        tag = xml.etree.ElementTree.Element('a')  # 创建标签
        tag.set('href', '#' + m.group(1))  # 设置id
        tag.text = m.group(1)

        return tag, m.start(), m.end()


class CodeLine(Treeprocessor):
    """
    渲染单行代码
    """

    def __init__(self, variable: Variable):
        """
        初始化
        :param variable: 变量字典
        """
        super().__init__()
        self.variable = variable

    def run(self, root: xml.etree.ElementTree.Element):
        """
        渲染
        :param root: Element树
        """
        for code in root.findall('.//code'):  # 在所有段落中查找单行代码
            if re.match(r'\$[^$]*\$', code.text):  # 渲染Latex
                code.text = fr'\({code.text[1:-1]}\)'
                code.tag = 'p'
            elif re.match(r'¥[^$]*¥', code.text):  # 是数学函数(单行)
                if EXTRA_ABLE:  # 支持扩展语法
                    expression, range_ = re.findall(r'¥([^$]*)¥(€[^$]*€)?', code.text)[0]  # 分离表达式与范围(如果有)
                    x_r = (-10, 10)
                    y_r = (-20, 20)
                    if range_ != '':  # 定义了范围
                        ranges = range_[1:-1].split('|')
                        if len(ranges) in (1, 2):  # 定义的范围正确
                            x_r = tuple(int(i) for i in ranges[0].split(','))
                            if len(ranges) == 2:  # 定义了y范围
                                y_r = tuple(int(i) for i in ranges[1].split(','))
                    code.tag = 'img'
                    code.set('src', f"""data:image/png;base64,{(function_drawing(
                        function=lambda x: eval(expression.split('=')[1]), x_range=x_r, y_range=y_r
                    ))}""")  # 绘制函数图像
                    code.set('alt', 'Base64 函数图片')
                else:  # 不支持扩展语法
                    code.tag = 'span'
                    code.set('class', 'block')
                    code.text = '该平台不支持扩展语法'
            elif re.match(r'\{[^$]*}', code.text):  # 是强调
                code.tag = 'span'
                code.set('class', 'block')
                key = code.text[1:-1]  # 去掉两边的{}
                if key in self.variable:
                    code.text = self.variable[key]
                else:
                    code.text = key


class Pre(Extension):
    """预处理"""
    def __init__(self, variable: Variable):
        """
        初始化
        :param variable: 变量字典
        """
        super().__init__()
        self.variable = variable

    def extendMarkdown(self, md: Markdown):
        """
        添加扩展
        :param md: 转换器
        """
        md.registerExtension(self)  # 注册扩展
        md.preprocessors.register(PreProcess(self.variable), 'pre_process', 0)


class Basic(Extension):
    """
    渲染基本样式
    """

    def extendMarkdown(self, md: Markdown):
        """
        添加扩展
        :param md: 转换器
        """
        md.registerExtension(self)  # 注册扩展
        md.inlinePatterns.register(Simple(r'~~(.*?)~~', tag='s'), 'strikethrough', 176)  # ~~删除线~~
        md.inlinePatterns.register(Simple(r'~(.*?)~', tag='u'), 'underline', 177)  # ~下划线~
        md.inlinePatterns.register(Simple(r'==(.*?)==', tag='mark'), 'high_light', 178)  # ==高亮==
        md.inlinePatterns.register(Nest(
            r'\[(.*?)]\^\((.*?)\)', outer_tag='ruby', inner_tag='rt'), 'up', 179
        )  # [在文本的正上方添加一行小文本]^(主要用于标拼音)
        md.inlinePatterns.register(ID(
            r'\[(.*?)]-\((.*?)\)', tag='span', property_='title'), 'hide', 180
        )  # [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)
        md.inlinePatterns.register(Emoji(r':(.+?):'), 'emoji', 181)  # 将emoji短代码转换为emoji字符
        md.parser.blockprocessors.register(Syllabus(md.parser), 'syllabus', 182)  # 渲染提纲


class Box(Extension):
    """
    渲染外框
    """

    def extendMarkdown(self, md):
        """
        添加扩展
        :param md: 转换器
        """
        md.registerExtension(self)  # 注册扩展
        # 红框警告
        md.inlinePatterns.register(ID(
            r'!{3}(.+?)!{3}', tag='div', property_='style', value='display: inline-block; border: 1px solid red;'
        ), 'warning_in_line', 190)  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *!{3} *\n', r'\n *!{3}\s*$', 'display: inline-block; border: 1px solid red;'
        ), 'warning_box', 191)  # 块

        # 黄框提醒
        md.inlinePatterns.register(ID(
            r'!{2}(.+?)!{2}', tag='div', property_='style', value='display: inline-block; border: 1px solid yellow;'
        ), 'reminding_in_line', 192)  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *!-! *\n', r'\n *!-!\s*$', 'display: inline-block; border: 1px solid yellow;'
        ), 'reminding_box', 193)  # 块

        # 绿框安心
        md.inlinePatterns.register(ID(
            r',{3}(.+?),{3}', tag='div', property_='style', value='display: inline-block; border: 1px solid green;'
        ), 'reminding_in_line', 194)  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *,{3} *\n', r'\n *,{3}\s*$', 'display: inline-block; border: 1px solid green;'
        ), 'reminding_box', 195)  # 块

        # 蓝框怀疑
        md.inlinePatterns.register(ID(
            r',-,(.+?),{2}', tag='div', property_='style', value='display: inline-block; border: 1px solid blue;'
        ), 'reminding_in_line', 196)  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *,-, *\n', r'\n *,-,\s*$', 'display: inline-block; border: 1px solid blue;'
        ), 'reminding_box', 197)  # 块


class Anchor(Extension):
    def extendMarkdown(self, md: Markdown):
        """
        添加扩展
        :param md: 转换器
        """
        md.registerExtension(self)  # 注册扩展
        md.inlinePatterns.register(_Anchor(r'\{#([^{}#]+)}'), 'anchor', 0)  # 定义锚点
        md.inlinePatterns.register(LinkLine(r'\{([^{}#]+)}'), 'line_link', 0)  # 添加页内链接


class Code(Extension):
    def __init__(self, variable: Variable):
        """
        初始化
        :param variable: 变量字典
        """
        super().__init__()
        self.variable = variable

    def extendMarkdown(self, md: Markdown):
        """
        添加扩展
        :param md: 转换器
        """
        md.registerExtension(self)  # 注册扩展
        md.treeprocessors.register(CodeLine(variable=self.variable), 'code_line', 0)  # 渲染单行代码块


def main(text: str, variable: Variable = None) -> Tuple[str, Dict[str, Variable]]:
    """
    主函数
    :param text: 输入文本
    :param variable: 变量字典
    :return: 返回html与元数据字典
    """
    if variable is None:
        variable = {}
    md = Markdown(extensions=[Pre(variable=variable), Basic(), Box(), Anchor()] + list(Extensions.values()) + [Code(variable=variable)])
    return md.convert(text), md.Meta
