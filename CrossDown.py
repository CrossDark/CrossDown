import re


class Header:
    @staticmethod
    def header(text: str) -> str:
        """
        渲染标题
        :param text: 原始文本
        :return: 处理后的文本
        """
        h6 = re.sub(r'###### (.*?)\n', r'<h6>\1</h6>\n', text)  # H6
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
        斜体
        :return:
        """
        self.text = re.sub(r'\*([^*\n]+)\*', r'<i>\1</i>\n', self.text)

    def bold(self):
        """
        粗体
        :return:
        """
        self.text = re.sub(r'\*\*([^*\n]+)\*\*', r'<b>\1</b>\n', self.text)

    def underline(self):
        """
        下划线
        :return:
        """
        self.text = re.sub(r'~([^~\n]+)~', r'<u>\1</u>\n', self.text)

    def strikethrough(self):
        """
        删除线
        :return:
        """
        self.text = re.sub(r'~~([^~\n]+)~~', r'<s>\1</s>\n', self.text)

    def highlight(self):
        """
        高亮
        :return:
        """
        self.text = re.sub(r'==([^=\n]+)==', r'<mark>\1</mark>\n', self.text)

    def __call__(self, *args, **kwargs):
        """
        一键运行
        :param args:
        :param kwargs:
        :return:
        """
        self.bold()
        self.italic()
        self.strikethrough()
        self.underline()
        self.highlight()
        return self.text


class Function:
    """
    添加特殊功能
    """

    def __init__(self, text: str):
        """
        初始化
        :param text: cd文本
        """
        self.text = text

    def link(self):
        self.text = re.sub(r'\[([^\[\]\n]+)]\(([^()\n]+)\)', r'<a href="\2">\1</a>\n', self.text)

    def __call__(self, *args, **kwargs):
        """
        一键运行
        :param args:
        :param kwargs:
        :return:
        """
        self.link()
        return self.text


class Basic:
    @ staticmethod
    def paragraph(text):
        return re.sub(r'(.*?)\n', r'<p>\1</p>\n', text)


def main(text: str) -> str:
    text = Header.header(text)  # 渲染标题
    text = Style(text)()
    text = Function(text)()

    # text = Basic.paragraph(text)  # 渲染段落
    return text


if __name__ == '__main__':
    with open('test.md', encoding='utf-8') as test:
        cd = f"""<!DOCTYPE html>
<html>
<head>
    <title>页面标题</title>
</head>
<body>
    {main(test.read())}
</body>
</html>"""
    with open('test.html', 'w', encoding='utf-8') as html:
        html.write(cd)
