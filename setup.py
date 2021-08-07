import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="telegram-autoconv",
    version="0.0.69",
    author="Moris Doratiotto",
    author_email="moris.doratiotto@gmail.com",
    description="A python module to auto build conversation for a Telegram bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mortafix/AutoConv-Telegram-Python",
    packages=setuptools.find_packages(),
    install_requires=[
        "python-telegram-bot==13.7",
        "pydantic==1.8.2",
        "pyyaml==5.4.1",
        "toml==0.10.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.9",
    keywords=["conversation", "generator", "telegram", "bot"],
)
