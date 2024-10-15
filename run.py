import time

from CrossDown import *


if __name__ == '__main__':
    # 开始计时
    start_time = time.perf_counter_ns()
    # 主程序
    with open('README.md', encoding='utf-8') as test:
        cd, meta = main(test.read(), variable={
            'a': 'b',
            '强调变量': '强调值'
        })
        print(meta)
    with open('README.html', 'w', encoding='utf-8') as html:
        html.write(f"""<!DOCTYPE html>  
<html lang="zh-CN">  
<head>  
    <meta charset="UTF-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  
    <title>UTF-8编码示例</title>  
{indent(list(HEAD.values()))}
    <!-- 可以在这里添加其他元数据和CSS链接 -->  
</head>  
<body>
{indent(cd, 4)}
</body>  
</html>
""")
    # 停止计时
    end_time = time.perf_counter_ns()
    # 输出用时
    print("运行时间: {:.9f} 秒".format((end_time - start_time) / 1e9))
