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
    "CodeHilite": "markdown.extensions.codehilite",
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
    def __init__(self, pattern: str, tag: str, property_: str):
        """
        初始化
        :param pattern: 正则表达式
        :param tag: html标签
        :param property_: html标签属性名称
        """
        super().__init__(pattern)
        self.tag = tag
        self.property = property_

    def handleMatch(self, match, match_line):
        tag = xml.etree.ElementTree.Element(self.tag)  # 创建标签
        tag.text = match.group(1)  # 设置标签内容
        tag.set(self.property, match.group(2))  # 设置标签属性

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
    ALERT_RE = r'(\d+(\.\d+)*)\s+(.*)'

    def test(self, parent, block):
        # 检查当前块是否匹配我们的正则表达式
        return bool(self.ALERT_RE.match(block))

    def run(self, parent, blocks):
        # 处理匹配的块
        block = blocks.pop(0)
        m = self.ALERT_RE.search(block)
        if m:
            before = block[:m.start()]  # 匹配之前的文本
            after = block[m.end():]  # 匹配之后的文本
            if before:
                # 如果匹配之前有文本，则创建一个新的段落来包含它
                p = etree.SubElement(parent, 'p')
                p.text = before.strip()
                # 创建包含警告内容的 div 元素
            div = etree.SubElement(parent, 'div', {'class': 'alert'})
            div.text = m.group(1).strip()
            # 如果匹配之后还有文本，则将其重新添加到块列表中以便后续处理
            if after.strip():
                blocks.insert(0, after)
        else:
            # 如果没有匹配，则保留原始块以便后续处理器处理
            return False


class BoxBlockProcessor(BlockProcessor):
        RE_FENCE_START = r'^ *!{3,} *\n' # start line, e.g., `   !!!! `
        RE_FENCE_END = r'\n *!{3,}\s*$'  # last non-blank line, e.g, '!!!\n  \n\n'

        def test(self, parent, block):
            return re.match(self.RE_FENCE_START, block)

        def run(self, parent, blocks):
            original_block = blocks[0]
            blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])

            # Find block with ending fence
            for block_num, block in enumerate(blocks):
                if re.search(self.RE_FENCE_END, block):
                    # remove fence
                    blocks[block_num] = re.sub(self.RE_FENCE_END, '', block)
                    # render fenced area inside a new div
                    e = etree.SubElement(parent, 'div')
                    e.set('style', 'display: inline-block; border: 1px solid red;')
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
        md.inlinePatterns.register(Syllabus(r'(\d+(\.\d+)*)\s+(.*)'), 'syllabus', 0)  # 渲染提纲


def main(text: str) -> Tuple[str, Dict[str, List[str]]]:
    md = Markdown(extensions=[Basic()] + list(Extensions.values()), safe_mode=False)
    return md.convert(text), md.Meta
