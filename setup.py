import pathlib
from setuptools import setup, find_namespace_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

extras = dict()
extras["javascript"] = ["pythonmonkey"]
extras["svg"] = ["cairosvg"]
extras["requests"] = ["brotli"]
extras["full"] = extras["javascript"] + extras["svg"] + extras["requests"]

setup(
    name="tkinterweb",
    version="4.6.1",
    python_requires=">=3.2",
    description="HTML/CSS viewer for Tkinter",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Andereoo/TkinterWeb",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: Freeware",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
      ],
    keywords="tkinter, Tkinter, tkhtml, Tkhtml, Tk, HTML, CSS, webbrowser",
    packages=find_namespace_packages(include=["tkinterweb", "tkinterweb.*"]),
    include_package_data=True,
    install_requires=["tkinterweb-tkhtml>=2.0.0", "pillow"],
    extras_require = extras,
)
