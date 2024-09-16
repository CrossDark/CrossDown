import unittest
import markdown


def convert_markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text, extensions=['markdown.extensions.extra'])


class TestMarkdownToHtmlConversion(unittest.TestCase):

    def test_simple_conversion(self):
        markdown_text = "# Hello, World!"
        expected_html = "<h1>Hello, World!</h1>\n"
        self.assert_conversion(markdown_text, expected_html)

    def test_paragraph_conversion(self):
        markdown_text = "This is a paragraph."
        expected_html = "<p>This is a paragraph.</p>\n"
        self.assert_conversion(markdown_text, expected_html)

    def test_bold_and_italic_conversion(self):
        markdown_text = "**Bold** and *Italic*"
        expected_html = "<p><strong>Bold</strong> and <em>Italic</em></p>\n"
        self.assert_conversion(markdown_text, expected_html)

    def test_list_conversion(self):
        markdown_text = """
        - Item 1
        - Item 2
        - Item 3
        """
        expected_html = """
        <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
        </ul>\n
        """
        self.assert_conversion(markdown_text, expected_html)

    def test_code_block_conversion(self):
        markdown_text = """

```python\nprint('Hello, World!')\n
```"
expected_html = '''
        <pre><code class="language-python">print('Hello, World!')
        </code></pre>\n
        """  # 注意：实际输出可能包含额外的空白或换行符，这取决于markdown库的处理方式
        self.assert_conversion(markdown_text, expected_html)


def test_link_conversion(self):
    markdown_text = "[Google](https://www.google.com)"
    expected_html = '<p><a href="https://www.google.com">Google</a></p>\n'
    self.assert_conversion(markdown_text, expected_html)


def test_image_conversion(self):
    markdown_text = "![Alt Text](https://www.example.com/image.jpg)"
    expected_html = '<p><img class=" long-press-able-img " alt="Alt Text" src="https://www.example.com/image.jpg" /></p>\n'
    self.assert_conversion(markdown_text, expected_html)


def test_blockquote_conversion(self):
    markdown_text = "> This is a quote."
    expected_html = '<blockquote>\n<p>This is a quote.</p>\n</blockquote>\n'
    self.assert_conversion(markdown_text, expected_html)


def assert_conversion(self, markdown_text, expected_html):
    converted_html = convert_markdown_to_html(markdown_text)
    # 使用replace方法去除不必要的空白字符，以便更灵活地比较输出
    self.assertEqual(converted_html.replace('\n', '').replace('\r', ''),
                     expected_html.replace('\n', '').replace('\r', ''))


if __name__ == '__main__':
    unittest.main()
