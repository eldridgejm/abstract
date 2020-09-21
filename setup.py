from setuptools import setup


setup(
    name="broadcast",
    version="0.1.0",
    py_modules=["broadcast"],
    install_requires=["jinja2", "markdown", "publish"],
    tests_require=["pytest"],
    entry_points={"console_scripts": ["broadcast = broadcast:cli"]},
)
