<!DOCTYPE html>  
<html lang="zh-CN">  
<head>  
    <meta charset="UTF-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  
    <title>UTF-8编码示例</title>  
    <script type="text/javascript" async
      src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
    <link href="https://cdn.jsdelivr.net/npm/prismjs/themes/prism.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/prismjs/prism.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs/components/prism-yaml.min.js"></script>
    <style>  
    .block {  
        background-color: grey; /* 灰色背景 */  
        color: white; /* 白色文字 */  
    }
    </style> 
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <!-- 可以在这里添加其他元数据和CSS链接 -->  
</head>  
<body>
    <script>  
        mermaid.initialize({startOnLoad:true});  
    </script>
        <h1>CrossDown示例</h1>
    <h1>1 基本语法<span id="1"></span></h1>
    <h2>1.1 标题<span id="1.1"></span></h2>
    <h1>一级标题</h1>
    <h2>二级标题</h2>
    <h3>三级标题</h3>
    <h4>四级标题</h4>
    <h5>五级标题</h5>
    <h6>六级标题</h6>
    <h2>1.2 样式<span id="1.2"></span></h2>
    <h3>1.2.1 <i>斜体</i><span id="1.2.1"></span></h3>
    <h3>1.2.2 <b>粗体</b><span id="1.2.2"></span></h3>
    <h3>1.2.3 <i><b>粗斜体</b></i><span id="1.2.3"></span></h3>
    <h3>1.2.4 <u>下划线</u><span id="1.2.4"></span></h3>
    <h3>1.2.5 <s>删除线</s><span id="1.2.5"></span></h3>
    <h3>1.2.6 <mark>高亮</mark><span id="1.2.6"></span></h3>
    <h3>1.2.7 <ruby>在文本的正上方添加一行小文本<rt>主要用于标拼音</rt></ruby><span id="1.2.7"></span></h3>
    <h3>1.2.8 <span title="只有鼠标放在上面才会显示隐藏文本">在指定的文本里面隐藏一段文本</span><span id="1.2.8"></span></h3>
    <h3>1.2.9 分割线<span id="1.2.9"></span></h3>
    <hr><hr><hr><h2>1.3 链接<span id="1.3"></span></h2>
    <h3>1.3.1 <a href="链接地址">链接文本</a><span id="1.3.1"></span></h3>
    <h3>1.3.2 <img src="链接地址" alt="链接图片"><span id="1.3.2"></span></h3>
    <h1>2 变量<span id="2"></span></h1>
    <h2>2.1 定义<span id="2.1"></span></h2>
    <h2>2.2 赋值<span id="2.2"></span></h2>
    <p>值 <a href="#锚点名">锚点名</a></p>
    <h2>2.3 添加锚点<span id="2.3"></span></h2>
    <span id="锚点名"></span>
    <h1>3 代码块<span id="3"></span></h1>
    <h2>3.1 <span class="block">单行</span><span id="3.1"></span></h2>
    <h3>3.1.1 LaTex<span id="3.1.1"></span></h3>
    <p>\(CO^2\)</p>
    <h2>3.2 多行<span id="3.2"></span></h2>
    <h3>3.2.1 YAML<span id="3.2.1"></span></h3>
    <pre><code class="language-yaml">
    A:
        1. a
        2. b
        3. c
    B:
        - a
        - b
        - c
    </code></pre>
    <h3>3.2.2 Python<span id="3.2.2"></span></h3>
    <pre><code class="language-python">
    print('CrossDown')
    </code></pre>
    <h3>3.2.3 Mermaid<span id="3.2.3"></span></h3>
    <div class="mermaid">
    graph LR
        A-->B
        A-->C
        B-->D
        C-->D
    </div>
    <h1>4 转义<span id="4"></span></h1>
    <p>\\</p>
    <h1>5 引用<span id="5"></span></h1>
    <blockquote>渲染引用<footer><cite>引用来源</cite></footer></blockquote><h1>6 提纲<span id="6"></span></h1>
    <h1>7 注释<span id="7"></span></h1>
    <h2>7.1 强注释<span id="7.1"></span></h2>
