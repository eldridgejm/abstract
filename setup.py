from setuptools import setup, find_packages


setup(
    name="abstract",
    version="0.1.3",
    packages=find_packages(),
    install_requires=["jinja2", "pyyaml", "markdown", "publish"],
    entry_points={"console_scripts": ["abstract = abstract:cli"]},
)
