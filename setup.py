from setuptools import setup, find_packages


setup(
    name="abstract",
    version="0.1.0",
    packages=find_packages(),
    setup_requires=["pytest-runner"],
    install_requires=["jinja2", "markdown", "publish"],
    tests_require=["pytest"],
    entry_points={"console_scripts": ["abstract = abstract:cli"]},
)
