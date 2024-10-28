from markdown.extensions import Extension, extra, admonition, meta, sane_lists, toc, wikilinks, codehilite, legacy_attrs

from pymdownx.extra import ExtraExtension
from pymdownx.arithmatex import ArithmatexExtension
from pymdownx.emoji import EmojiExtension
from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.admonition import AdmonitionExtension
from pymdownx.blocks.details import DetailsExtension
from pymdownx.blocks.html import HTMLExtension
from pymdownx.blocks.tab import TabExtension
from pymdownx.caret import InsertSupExtension
from pymdownx.critic import CriticExtension
from pymdownx.highlight import HighlightExtension
from pymdownx.inlinehilite import InlineHiliteExtension
from pymdownx.keys import KeysExtension
from pymdownx.mark import MarkExtension
from pymdownx.progressbar import ProgressBarExtension
from pymdownx.smartsymbols import SmartSymbolsExtension
from pymdownx.superfences import SuperFencesCodeExtension, fence_div_format
from pymdownx.tasklist import TasklistExtension
from pymdownx.tilde import DeleteSubExtension
from pymdownx.fancylists import FancyListExtension
from pymdownx.saneheaders import SaneHeadersExtension

from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
from markdown.preprocessors import Preprocessor
from markdown.blockparser import BlockParser
from markdown import Markdown

from typing import *
import re
import xml

from .Define import Variable


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

    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[
        None, None, None]:
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

    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[
        None, None, None]:
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

    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[
        None, None, None]:
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


class _Anchor(InlineProcessor):
    def handleMatch(self, m: Match[str], data: str) -> Tuple[xml.etree.ElementTree.Element, int, int] | Tuple[
        None, None, None]:
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
                code.tag = 'span'
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
        md.preprocessors.register(PreProcess(self.variable), 'pre_process', 1000)


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
        md.inlinePatterns.register(Nest(
            r'\[(.*?)]\^\((.*?)\)', outer_tag='ruby', inner_tag='rt'), 'up', 179
        )  # [在文本的正上方添加一行小文本]^(主要用于标拼音)
        md.inlinePatterns.register(ID(
            r'\[(.*?)]-\((.*?)\)', tag='span', property_='title'), 'hide', 180
        )  # [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)
        md.parser.blockprocessors.register(Syllabus(md.parser), 'syllabus', 182)  # 渲染提纲


class Anchor(Extension):
    def extendMarkdown(self, md: Markdown):
        """
        添加扩展
        :param md: 转换器
        """
        md.registerExtension(self)  # 注册扩展
        md.inlinePatterns.register(_Anchor(r'\{{#([^{}#]+)}}'), 'anchor', 0)  # 定义锚点
        md.inlinePatterns.register(LinkLine(r'\{{([^{}#]+)}}'), 'line_link', 0)  # 添加页内链接


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
        # md.treeprocessors.register(CodeLine(variable=self.variable), 'code_line', 0)  # 渲染单行代码块
        # md.treeprocessors.register(CodeBlock(), 'code_block', 1000)  # 渲染多行代码块


Extensions = {
    # 自带
    '元数据': meta.MetaExtension(),
    '目录': toc.TocExtension(),
    '内部链接': wikilinks.WikiLinkExtension(),
    '属性设置': legacy_attrs.LegacyAttrExtension(),

    # pymdownx
    '基本扩展': ExtraExtension(configs={
        superfences: {
            custom_fences: [  # 渲染mermaid
                {
                    'name': 'mermaid',
                    'class': 'mermaid',
                    'format': fence_div_format
                }
            ]
        }
    }),
    '超级数学': ArithmatexExtension(),
    'EMOJI': EmojiExtension(),
    '块扩展': BlocksExtension(),
    '警告': AdmonitionExtension(),
    '详情': DetailsExtension(),
    'HTML': HTMLExtension(),
    '标签': TabExtension(),
    '批评': CriticExtension(),
    '代码高亮': HighlightExtension(),
    '行内高亮': InlineHiliteExtension(),
    '按键风格': KeysExtension(),
    '高亮': MarkExtension(),
    '进度条': ProgressBarExtension(),
    '高级符号': SmartSymbolsExtension(),
    '任务列表': TasklistExtension(clickable_checkbox=True),
    '下标': DeleteSubExtension(),
    '上标': InsertSupExtension(),
    '高级列表': FancyListExtension(),
    '高级标题': SaneHeadersExtension(),

    # 自定义
    '基本风格': Basic(),
}


def main(text: str, variable: Variable = None) -> Tuple[str, Variable]:
    """
    主函数
    :param text: 输入文本
    :param variable: 变量字典
    :return: 返回html与元数据字典
    """
    if variable is None:
        variable = {}
    md = Markdown(extensions=list(Extensions.values()))
    return md.convert(text), md.Meta
