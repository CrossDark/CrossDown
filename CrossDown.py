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
        self.text = re.sub(r'\*([^*\n]+)\*', r'<i>\1</i>', self.text)

    def bold(self):
        """
        粗体
        :return:
        """
        self.text = re.sub(r'\*\*([^*\n]+)\*\*', r'<b>\1</b>', self.text)

    def underline(self):
        """
        下划线
        :return:
        """
        self.text = re.sub(r'~([^~\n]+)~', r'<u>\1</u>', self.text)

    def strikethrough(self):
        """
        删除线
        :return:
        """
        self.text = re.sub(r'~~([^~\n]+)~~', r'<s>\1</s>', self.text)

    def highlight(self):
        """
        高亮
        :return:
        """
        self.text = re.sub(r'==([^=\n]+)==', r'<mark>\1</mark>', self.text)

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
        self.text = re.sub(r'\[([^\[\]\n]+)]\(([^()\n]+)\)', r'<a href="\2">\1</a>', self.text)

    def __call__(self, *args, **kwargs):
        """
        一键运行
        :param args:
        :param kwargs:
        :return:
        """
        self.link()
        return self.text


class Value:
    def __init__(self, text: str):
        self.text = text
        self.values = {
            key: value for key, value in re.findall(r'\[([^]]+)]: (.+?)(?=\n|$)', text)
        }  # 从text中提取所有变量并转换成字典

    def __call__(self, *args, **kwargs):
        """
        将所有变量赋值并移除变量定义
        :param args:
        :param kwargs:
        :return: 赋值后的正文
        """
        text = self.text
        for k, v in self.values.items():
            text = re.sub(fr'\[([^]]+)]\({k}\)', fr'[\1]({v})', text)
            text = re.sub(fr'\[{k}]: (.+?)(?=\n|$)', '', text)
        return text


class CodeBlock:
    def __init__(self, text: str):
        self.text = text
        self.codes = [i for i in re.findall('`([^`]*)`', self.text) if i != '']
        print(self.codes)

    def __call__(self, *args, **kwargs):
        return re.sub(r'`[^`]*`', '', self.text)

    def restore(self):
        pass


class Basic:
    @staticmethod
    def paragraph(text: str):
        return re.sub(r'(.*?)\n', r'<p>\1</p>\n', text)


def add_indent_to_string(input_string: str, indent_spaces: int = 4):
    """
    给字符串中的每一行前面加上缩进。
    :param input_string: 原始字符串，可以包含多行。
    :param indent_spaces: 每行前面要添加的空格数，默认为4。

    :return: 带缩进的新字符串。
    """
    # 使用字符串的splitlines()方法分割原始字符串为行列表
    lines = input_string.splitlines()

    # 遍历行列表，给每行前面加上相应的缩进，并重新组合成字符串
    indented_string = "\n".join(f"{' ' * indent_spaces}{line}" for line in lines)

    return indented_string


def body(text: str) -> str:
    """
    渲染正文部分
    :param text: 输入正文
    :return: 输出渲染后的正文
    """
    text = Value(text)()  # 提取变量并赋值到文本中
    text = Header.header(text)  # 渲染标题
    text = Style(text)()  # 渲染字体样式
    text = Function(text)()  # 渲染特殊功能

    # text = Basic.paragraph(text)  # 渲染段落
    return text


def main(origen: str):
    # 预处理
    text = CodeBlock(origen)()
    return body(text)  # 处理正文
    #


if __name__ == '__main__':
    with open('test.md', encoding='utf-8') as test:
        cd = main(test.read())
    with open('test.html', 'w', encoding='utf-8') as html:
        html.write(f"""<!DOCTYPE html>  
<html lang="zh-CN">  
<head>  
    <meta charset="UTF-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  
    <title>UTF-8编码示例</title>  
    <!-- 可以在这里添加其他元数据和CSS链接 -->  
</head>  
<body>  
    {add_indent_to_string(cd, 4)}
</body>  
</html>
""")
