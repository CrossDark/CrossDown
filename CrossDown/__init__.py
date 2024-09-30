from typing import *
from .Core import main


__all__ = [
    'main',  # 主函数
    'indent',  # 添加空格
    'HEAD',  #
    'BODY',  #
]
__version__ = '0.11.2'
__author__ = 'CrossDark'
__email__ = 'liuhanbo333@icloud.com'
__source__ = 'https://crossdark.net/'
__license__ = """MIT"""


HEAD = (
    '<script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"></script>',
    '<link href="https://cdn.jsdelivr.net/npm/prismjs/themes/prism.css" rel="stylesheet" />',
    '<script src="https://cdn.jsdelivr.net/npm/prismjs/prism.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/prismjs/components/prism-yaml.min.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>',
    '<style>',
    '   .block {',
    '   background-color: grey; /* 灰色背景 */',
    '   color: white; /* 白色文字 */',
    '}',
    '</style>'
)

BODY = (
    '<script>',
    '   mermaid.initialize({{startOnLoad:true}});',
    '</script>',
    '<script>',
    '   document.addEventListener("DOMContentLoaded", function() {',
    '   emojify.run();',
    '});',
    '</script>',
)


def indent(input_: Union[str, List, Tuple], indent_spaces: int = 4) -> str:
    """
    给字符串中的每一行前面加上缩进。
    :param input_: 原始字符串，可以包含多行。
    :param indent_spaces: 每行前面要添加的空格数，默认为4。
    :return: 带缩进的新字符串。
    """
    # 使用字符串的splitlines()方法分割原始字符串为行列表,如果是可迭代对象则直接遍历
    # 遍历行列表，给每行前面加上相应的缩进，并重新组合成字符串
    return "\n".join(
        f"{' ' * indent_spaces}{line}" for line in (lambda x: x.splitlines() if isinstance(x, str) else x)(input_))
