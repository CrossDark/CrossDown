from markdown.extensions import Extension, extra, admonition, meta, sane_lists, toc, wikilinks, codehilite

from pygments.formatters import HtmlFormatter

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


try:  # 检测当前平台是否支持扩展语法
    from .Extra import *
    EXTRA_ABLE = True
except ModuleNotFoundError:  # 不支持扩展语法
    EXTRA_ABLE = False


class HighlightHtmlFormatter(HtmlFormatter):
    def __init__(self, lang_str='', **options):
        super().__init__(**options)
        # lang_str has the value {lang_prefix}{lang}
        # specified by the CodeHilite's options
        self.lang_str = lang_str.split('-')[-1]

    def _wrap_code(self, source):
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


class _Anchor(InlineProcessor):
    def handleMatch(self, match, match_line):
        tag = xml.etree.ElementTree.Element('span')  # 创建标签
        tag.text = match.group(1)
        tag.set('id', match.group(1))  # 设置id

        return tag, match.start(), match.end()


class LinkLine(InlineProcessor):
    def handleMatch(self, match, match_line):
        tag = xml.etree.ElementTree.Element('a')  # 创建标签
        tag.set('href', '#' + match.group(1))  # 设置id
        tag.text = match.group(1)

        return tag, match.start(), match.end()


class CodeLine(Treeprocessor):
    def __init__(self, variable: Dict):
        super().__init__()
        self.variable = variable

    def run(self, root):
        for elem in root.iter('p'):  # 在所有段落中查找单行代码
            if elem.findall('code'):  # 找到单行代码
                for code in elem:
                    if re.match(r'\$[^$]*\$', code.text):  # 渲染Latex
                        if isinstance(elem.text, str):  # 这个段落还有其它内容
                            elem.text += fr'\({code.text[1:-1]}\){code.tail}'  # 插入latex
                        else:
                            elem.text = fr'\({code.text[1:-1]}\)'  # latex是段落中唯一的内容
                        elem.remove(code)
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


class CodeBlock(Treeprocessor):
    def run(self, root):
        for code in root.findall('p'):
            # 在这里处理 <pre> 标签
            # 例如，你可以添加属性或修改内容
            print(f'{code.text} | {code.tag}')


class Basic(Extension):  # TODO InlineProcessor 不能渲染一行中两个以上的元素(内置的扩展斜体和粗体的优先级好像是一样的)
    """
    渲染基本样式
    """

    def extendMarkdown(self, md):
        md.registerExtension(self)  # 注册扩展
        md.inlinePatterns.register(Simple(r'~~(.*?)~~', tag='s'), 'strikethrough', 1)  # ~~删除线~~
        md.inlinePatterns.register(Simple(r'~(.*?)~', tag='u'), 'underline', 2)  # ~下划线~
        md.inlinePatterns.register(Simple(r'==(.*?)==', tag='mark'), 'high_light', 3)  # ==高亮==
        md.inlinePatterns.register(Nest(
            r'\[(.*?)]\^\((.*?)\)', outer_tag='ruby', inner_tag='rt'), 'up', 4
        )  # [在文本的正上方添加一行小文本]^(主要用于标拼音)
        md.inlinePatterns.register(ID(
            r'\[(.*?)]-\((.*?)\)', tag='span', property_='title'), 'hide', 5
        )  # [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)
        md.inlinePatterns.register(Emoji(r':(.+?):'), 'emoji', 6)  # 将emoji短代码转换为emoji字符
        md.parser.blockprocessors.register(Syllabus(md.parser), 'syllabus', 11)  # 渲染提纲


class Box(Extension):
    """
    渲染外框
    """

    def extendMarkdown(self, md):
        md.registerExtension(self)  # 注册扩展
        # 红框警告
        md.inlinePatterns.register(ID(
            r'!{3}(.+?)!{3}', tag='div', property_='style', value='display: inline-block; border: 1px solid red;'
        ), 'warning_in_line', 20)  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *!{3} *\n', r'\n *!{3}\s*$', 'display: inline-block; border: 1px solid red;'
        ), 'warning_box', 175)  # 块

        # 黄框提醒
        md.inlinePatterns.register(ID(
            r'!-!(.+?)!-!', tag='div', property_='style', value='display: inline-block; border: 1px solid yellow;'
        ), 'reminding_in_line', 21)  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *!-! *\n', r'\n *!-!\s*$', 'display: inline-block; border: 1px solid yellow;'
        ), 'reminding_box', 176)  # 块

        # 绿框安心
        md.inlinePatterns.register(ID(
            r',{3}(.+?),{3}', tag='div', property_='style', value='display: inline-block; border: 1px solid green;'
        ), 'reminding_in_line', 22)  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *,{3} *\n', r'\n *,{3}\s*$', 'display: inline-block; border: 1px solid green;'
        ), 'reminding_box', 177)  # 块

        # 蓝框怀疑
        md.inlinePatterns.register(ID(
            r',-,(.+?),{2}', tag='div', property_='style', value='display: inline-block; border: 1px solid blue;'
        ), 'reminding_in_line', 23)  # 行内
        md.parser.blockprocessors.register(BoxBlock(
            md.parser, r'^ *,-, *\n', r'\n *,-,\s*$', 'display: inline-block; border: 1px solid blue;'
        ), 'reminding_box', 178)  # 块


class Anchor(Extension):
    def extendMarkdown(self, md: Markdown):
        md.registerExtension(self)  # 注册扩展
        md.inlinePatterns.register(_Anchor(r'\{#([^{}#]+)}'), 'anchor', 0)  # 定义锚点
        md.inlinePatterns.register(LinkLine(r'\{([^{}#]+)}'), 'line_link', 0)  # 添加页内链接


class Code(Extension):
    def __init__(self, variable: Dict):
        super().__init__()
        self.variable = variable

    def extendMarkdown(self, md: Markdown):
        md.registerExtension(self)  # 注册扩展
        md.treeprocessors.register(CodeLine(variable=self.variable), 'code_line', 0)  # 渲染单行代码块
        # md.treeprocessors.register(CodeBlock(), 'code_block', 1)  # 渲染多行代码块


def main(text: str, variable: Dict) -> Tuple[str, Dict[str, List[str]]]:
    md = Markdown(extensions=[Basic(), Box(), Anchor()] + list(Extensions.values()) + [Code(variable=variable)])
    return md.convert(text), md.Meta
