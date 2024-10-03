import emoji
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import Pattern
from markdown.preprocessors import Preprocessor
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


class Style(Preprocessor):
    """
    渲染字体样式
    """

    @staticmethod
    def underline(text):
        """
        ~下划线~
        :return: text
        """
        return re.sub(r'~([^~\n]+)~', r'<u>\1</u>', text)

    @staticmethod
    def strikethrough(text):
        """
        ~~删除线~~
        :return: text
        """
        return re.sub(r'~~([^~\n]+)~~', r'<s>\1</s>', text)

    @staticmethod
    def highlight(text):
        """
        ==高亮==
        :return: text
        """
        return re.sub(r'==([^=\n]+)==', r'<mark>\1</mark>', text)

    @staticmethod
    def up(text):
        """
        [在文本的正上方添加一行小文本]^(主要用于标拼音)
        :return: text
        """
        return re.sub(r'\[(.*?)]\^\((.*?)\)', r'<ruby>\1<rt>\2</rt></ruby>', text)

    @staticmethod
    def hide(text):
        """
        [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)
        :return: text
        """
        return re.sub(r'\[(.*?)]-\((.*?)\)', r'<span title="\2">\1</span>', text)

    def run(self, lines: List[str]) -> List[str]:
        new_line = []
        for line in lines:
            line = re.sub(r'~~([^~\n]+)~~', r'<s>\1</s>', line)  # ~~删除线~~
            line = re.sub(r'~([^~\n]+)~', r'<u>\1</u>', line)  # ~下划线~
            line = re.sub(r'==([^=\n]+)==', r'<mark>\1</mark>', line)  # ==高亮==
            line = re.sub(r'\[(.*?)]\^\((.*?)\)', r'<ruby>\1<rt>\2</rt></ruby>', line)  # [在文本的正上方添加一行小文本]^(主要用于标拼音)
            line = re.sub(r'\[(.*?)]-\((.*?)\)', r'<span title="\2">\1</span>', line)  # [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)
            line = emoji.emojize(line)  # 渲染Emoji
            new_line.append(line)
        return new_line


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
        print(anchors)
        for index, line in enumerate(lines):
            if any(value in line for value in values):  # 匹配到了变量
                for key, value in values.items():
                    if '=' in line:  # 是变量定义
                        lines.remove(line)  # 删除
                    else:  # 应该被赋值
                        lines[index] = re.sub('{' + key + '}', value, line)  # 对变量赋值
            if any(anchor in line for anchor in anchors):  # 匹配到了锚点
                if re.search('\{#', line):  # 是锚点定义
                    lines[index] = re.sub(r'\{#(.+)}', r'<span id="\1"></span>', line)  # 定义锚点
                else:  # 是页内链接
                    print(line)
        return lines


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


class Basic(Extension):
    """
    基本扩展
    """

    def extendMarkdown(self, md):
        md.registerExtension(self)  # 注册扩展
        md.preprocessors.register(Style(md), 'style', 0)
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
    md = Markdown(extensions=[Basic(), More()] + list(Extensions.values()) + [Decorate()], safe_mode=False)
    return md.convert(text), md.Meta
