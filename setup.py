import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="telegram-autoconv",
    version="0.0.10",
    author="Moris Doratiotto",
    author_email="moris.doratiotto@gmail.com",
    description="A python module to auto build conversation for a Telegram bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mortafix/AutoConv-Telegram-Python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.8',
    keywords=['conversation', 'generator', 'telegram', 'bot'],
)