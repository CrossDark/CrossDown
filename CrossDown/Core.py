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


class Style(Preprocessor):
    """
    渲染字体样式
    """

    @staticmethod
    def underline(text):
        """
        ~下划线~
        :return:
        """
        return re.sub(r'~([^~\n]+)~', r'<u>\1</u>', text)

    @staticmethod
    def strikethrough(text):
        """
        ~~删除线~~
        :return:
        """
        return re.sub(r'~~([^~\n]+)~~', r'<s>\1</s>', text)

    @staticmethod
    def highlight(text):
        """
        ==高亮==
        :return:
        """
        return re.sub(r'==([^=\n]+)==', r'<mark>\1</mark>', text)

    @staticmethod
    def up(text):
        """
        [在文本的正上方添加一行小文本]^(主要用于标拼音)
        :return:
        """
        return re.sub(r'\[(.*?)]\^\((.*?)\)', r'<ruby>\1<rt>\2</rt></ruby>', text)

    @staticmethod
    def hide(text):
        """
        [在指定的文本里面隐藏一段文本]-(只有鼠标放在上面才会显示隐藏文本)
        :return:
        """
        return re.sub(r'\[(.*?)]-\((.*?)\)', r'<span title="\2">\1</span>', text)

    def run(self, lines):
        new_line = []
        for line in lines:
            line = self.strikethrough(line)  # 渲染删除线
            line = self.underline(line)  # 渲染下划线
            line = self.highlight(line)  # 渲染高亮
            line = self.up(line)  # 渲染上部文本
            line = self.hide(line)  # 渲染隐藏文本
            new_line.append(line)
        return new_line


class Core(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)  # 注册扩展
        md.preprocessors.register(Style(md), 'custom_preprocessor', 0)


def main(text):
    md = Markdown(extensions=[Core()] + list(Extensions.values()))
    return md.convert(text), md.Meta
