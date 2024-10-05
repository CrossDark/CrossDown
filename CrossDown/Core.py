import xml
import emoji
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import Pattern as Pattern_
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import InlineProcessor
from markdown import Markdown
from typing import *
import re

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
    def __init__(self, pattern: str, tag: str, key: str, value: str):
        """
        初始化
        :param pattern: 正则表达式
        :param tag: html标签
        :param key: html标签属性
        :param value: html标签属性的值
        """
        super().__init__(pattern)
        self.tag = tag
        self.key = key
        self.value = value

    def handleMatch(self, match, match_line):
        outer_tag = xml.etree.ElementTree.Element(self.outer_tag)  # 创建外层标签
        inner_tag = xml.etree.ElementTree.SubElement(outer_tag, self.inner_tag)  # 创建内层标签
        outer_tag.text = match.group(1)  # 设置外层标签文本
        inner_tag.text = match.group(2)  # 设置内层标签文本

        return outer_tag, match.start(), match.end()


class Basic(Extension):
    """
    渲染字体样式
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
            r'\[(.*?)]-\((.*?)\)', outer_tag='ruby', inner_tag='rt'), 'hide', 0
        )  # [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)


class Syllabus(Preprocessor):
    def run(self, lines: List[str]) -> List[str]:
        return [
            (lambda match, origen:
             re.sub(f'^({match.groups()[0]})',  # 按照提纲等级添加#和锚点
                    fr'{"#" * len(match.groups()[0].split("."))} \1', origen)
             if match is not None else origen)  # 对于不是提纲的行,直接返回原始字符
            ((lambda x: re.match(r'^([\d.]+) ', x)  # 判断是否是提纲
            if not any((x.startswith('.'),  # 以.开头
                        re.search('\. ', x) is not None,  # 存在.+空格
                        re.search('\.{2,}', x),  # 存在连续的.
                        ))
            else None)(line), line)  # 排除.在提纲号开头或结尾的情况
            for line in lines  # 分割并遍历文本的每一行
        ]


class Value(Preprocessor):
    def run(self, lines: List[str]) -> List[str]:
        values = {
            key: value.strip()  # 去除值两侧的空白字符
            for line in lines
            for match in [re.match(r'\{([^{}#]+)} ?= ?(.+?)(?=\n|$)', line)]
            if match
            for key, value in [match.groups()]
        }  # 识别变量定义
        anchors = re.findall(r'\{#([^{}#]+)}', '\n'.join(lines))  # 识别锚点定义
        text = '\n'.join(lines)  # 先合并成一行
        for item in anchors:
            text = re.sub(r'\{#(' + item + ')}', r'<span id="\1"></span>', text)  # 添加锚点
            text = re.sub(r'\{' + item + '}', fr'<a href="#{item}">{item}</a>', text)  # 添加页内链接
        for k, v in values.items():
            text = re.sub(r'\{' + k + '} ?= ?(.+?)(?=\n|$)', '', text)  # 移除变量的定义
            text = re.sub(r'\{' + k + '}', fr'{v}', text)  # 给变量赋值
        return text.split('\n')  # 再分割为列表


class Tag(Treeprocessor):
    def run(self, root):
        """
        通过修改AST来给标题添加锚点
        """
        for header in root.iter():
            if header.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):  # 查找标题
                header.set('id', header.text.split(' ')[0])  # 给标题添加锚点
            elif header.tag == 'ul':  # 是无序列表
                for i in header:  # 遍历列表内容
                    try:
                        i[0].set('href', '#' + i[0].text.split(' ')[0])  # 是目录,更改链接为标准格式
                    except IndexError:
                        pass  # 是普通的无序列表


class Basic_(Extension):
    """
    基本扩展
    """

    def extendMarkdown(self, md):
        md.registerExtension(self)  # 注册扩展
        md.preprocessors.register(Syllabus(md), 'syllabus', 0)


class More(Extension):
    """
    高级扩展
    """

    def extendMarkdown(self, md):
        md.preprocessors.register(Value(md), 'values', 0)


class Decorate(Extension):
    """
    修饰扩展,最后处理
    """

    def extendMarkdown(self, md):
        md.treeprocessors.register(Tag(md), 'header', 0)


def main(text: str) -> Tuple[str, Dict[str, List[str]]]:
    md = Markdown(extensions=[Basic(), Basic_(), More()] + list(Extensions.values()) + [Decorate()], safe_mode=False)
    return md.convert(text), md.Meta
