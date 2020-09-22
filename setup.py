from setuptools import setup, find_packages


setup(
    name="broadcast",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["jinja2", "markdown", "publish"],
    tests_require=["pytest"],
    entry_points={"console_scripts": ["broadcast = broadcast:cli"]},
)