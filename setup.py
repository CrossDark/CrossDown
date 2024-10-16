import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CrossDown",
    version="2.0.1",
    author="CrossDark",
    author_email="liuhanbo333@icloud.com",
    description="CrossDark's MarkDown",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CrossDark/CrossDown",
    packages=setuptools.find_packages(),
    install_requires=[
        'markdown',
        'matplotlib',
        'numpy',
    ],
    package_data={
        '': ['static/*'],  # 这将包含static文件夹下的所有子文件夹和文件
    },
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent"
    ],
)
