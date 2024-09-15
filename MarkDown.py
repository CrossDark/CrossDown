import markdown


with open('README.md', encoding='utf-8') as text:
    html = markdown.markdown(text.read(), extensions=['markdown.extensions.extra'])
    print(html)

