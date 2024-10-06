from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import Pattern as Pattern_
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
from markdown import Markdown
from typing import *
import re
import xml
import emoji

Extensions = {
    "Extra": "markdown.extensions.extra",
    "Abbreviations": "markdown.extensions.abbr",
    "Attribute Lists": "markdown.extensions.attr_list",
    "Definition Lists": "markdown.extensions.def_list",
    "Fenced Code Blocks": "markdown.extensions.fenced_code",
    "Footnotes": "markdown.extensions.footnotes",
    "Tables": "markdown.extensions.tables",
    # "Smart Strong": "markdown.extensions.smart_strong",
    "Admonition": "markdown.extensions.admonition",
    # "CodeHilite": "markdown.extensions.codehilite",
    # "HeaderId": "markdown.extensions.headerid",
    "Meta-Data": "markdown.extensions.meta",
    "New Line to Break": "markdown.extensions.nl2br",
    "Sane Lists": "markdown.extensions.sane_lists",
    "SmartyPants": "markdown.extensions.smarty",
    "Table of Contents": "markdown.extensions.toc",
    "WikiLinks": "markdown.extensions.wikilinks",
}

try:  # 检测当前平台是否支持扩展语法
    import Extra

    Extensions += Extra.EXTRA
except ModuleNotFoundError:
    EXTRA_ABLE = False


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

    def handleMatch(self, match, match_line):
        tag = xml.etree.ElementTree.Element(self.tag)  # 创建标签
        tag.text = match.group(1)  # 获取匹配到的文本并设置为标签的内容

        return tag, match.start(), match.end()


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

    def handleMatch(self, match, match_line):
        outer_tag = xml.etree.ElementTree.Element(self.outer_tag)  # 创建外层标签
        inner_tag = xml.etree.ElementTree.SubElement(outer_tag, self.inner_tag)  # 创建内层标签
        outer_tag.text = match.group(1)  # 设置外层标签文本
        inner_tag.text = match.group(2)  # 设置内层标签文本

        return outer_tag, match.start(), match.end()


class ID(InlineProcessor):
    """
    需要对HTML标签设置ID实现的样式
    """

    def __init__(self, pattern: str, tag: str, property_: str, value: Union[str, bool, int] = None):
        """
        初始化
        :param pattern: 正则表达式
        :param tag: html标签
        :param property_: html标签属性名称
        :param value: html标签属性的值
        """
        super().__init__(pattern)
        self.tag = tag
        self.property = property_
        self.value = value

    def handleMatch(self, match, match_line):
        tag = xml.etree.ElementTree.Element(self.tag)  # 创建标签
        tag.text = match.group(1)  # 设置标签内容
        tag.set(self.property, match.group(2) if self.value is None else self.value)  # 设置标签属性,属性的值默认为第二个匹配组

        return tag, match.start(), match.end()


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

    def handleMatch(self, match, match_line):
        return emoji.emojize(match.group(0)), match.start(), match.end()


class Syllabus_(InlineProcessor):
    """
        需要对HTML标签设置ID实现的样式
        """

    def __init__(self, pattern: str):
        """
        初始化
        :param pattern: 正则表达式
        """
        super().__init__(pattern)

    def handleMatch(self, match, match_line):
        tag = xml.etree.ElementTree.Element(f'h{len(match.group(1).split("."))}')  # 创建标签
        tag.text = match.group(1) + ' ' + match.group(3)  # 设置标签内容
        tag.set('id', match.group(1))  # 设置标签属性

        return tag, match.start(), match.end()


class Syllabus(BlockProcessor):
    # 定义提纲的正则表达式
    syllabus_re = r'(\d+(\.\d+)*)\s+(.*)'

    def test(self, parent, block):
        # 检查当前块是否匹配我们的正则表达式
        return re.match(self.syllabus_re, block)

    def run(self, parent, blocks):
        syllabus = re.match(self.syllabus_re, blocks[0])  # 匹配提纲的号和内容
        header = xml.etree.ElementTree.SubElement(parent, f'h{len(syllabus.group(1).split("."))}')  # 按照提纲号等级创建标题
        header.set('id', syllabus.group(1))  # 设置提纲ID
        header.text = syllabus.group(1) + ' ' + syllabus.group(3)  # 设置提纲内容
        blocks[0] = ''
        return False


class BoxBlock(BlockProcessor):
    def __init__(self, parser, re_start, re_end, style):
        super().__init__(parser)
        self.re_start = re_start  # start line, e.g., `   !!!!
        self.re_end = re_end  # last non-blank line, e.g, '!!!\n  \n\n'
        self.style = style

    def test(self, parent, block):
        return re.match(self.re_start, block)

    def run(self, parent, blocks):
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


class Basic(Extension):
    """
    渲染基本样式
    """

    def extendMarkdown(self, md):
        md.registerExtension(self)  # 注册扩展
        md.inlinePatterns.register(Simple(r'~~(.*?)~~', tag='s'), 'strikethrough', 0)  # ~~删除线~~
        md.inlinePatterns.register(Simple(r'~(.*?)~', tag='u'), 'underline', 0)  # ~下划线~
        md.inlinePatterns.register(Simple(r'==(.*?)==', tag='mark'), 'high_light', 0)  # ==高亮==
        md.inlinePatterns.register(Nest(
            r'\[(.*?)]\^\((.*?)\)', outer_tag='ruby', inner_tag='rt'), 'up', 0
        )  # [在文本的正上方添加一行小文本]^(主要用于标拼音)
        md.inlinePatterns.register(ID(
            r'\[(.*?)]-\((.*?)\)', tag='span', property_='title'), 'hide', 0
        )  # [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)
        md.inlinePatterns.register(Emoji(r':(.+?):'), 'emoji', 0)  # 将emoji短代码转换为emoji字符
        md.parser.blockprocessors.register(Syllabus(md.parser), 'syllabus', 11)  # 渲染提纲


class Box(Extension):
    """
    渲染外框
    """

    def extendMarkdown(self, md):
        md.registerExtension(self)  # 注册扩展
        # 红框警告
        md.inlinePatterns.register(ID(
            r'!{3,}(.+?)!{3,}', tag='div', property_='style', value='display: inline-block; border: 1px solid red;'
        ), 'warning_in_line', 0
        )  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *!{3,} *\n', r'\n *!{3,}\s*$', 'display: inline-block; border: 1px solid red;'
        ), 'warning_box', 175)  # 块
        # 黄框提醒
        md.inlinePatterns.register(ID(
            r'!{2,}(.+?)!{2,}', tag='div', property_='style', value='display: inline-block; border: 1px solid yellow;'
        ), 'reminding_in_line', 0
        )  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *!{2,} *\n', r'\n *!{2,}\s*$', 'display: inline-block; border: 1px solid yellow;'
        ), 'reminding_box', 175)  # 块


class Anchor(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)  # 注册扩展
        md.inlinePatterns.register(ID(
            r'\{#([^{}#]+)}', tag='span', property_='id'), 'hide', 0
        )  # 定义锚点


def main(text: str) -> Tuple[str, Dict[str, List[str]]]:
    md = Markdown(extensions=[Basic(), Box(), Anchor()] + list(Extensions.values()), safe_mode=False)
    return md.convert(text), md.Meta
