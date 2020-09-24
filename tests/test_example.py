import pathlib
import shutil
import datetime
import lxml.html

import publish
from pytest import fixture, mark

import broadcast

# default theme tests
# --------------------------------------------------------------------------------------

# here we test the default theme on an example class. The example class has homeworks,
# labs, lectures, and discussions.
#
#   - the last lab was released October 15 and is due on October 22
#   - the last homework was released October 15 and is due on October 22
#   - the last lecture is on October 22
#   - the last discussion is on October 15
#
# the first week is set to start on Monday, September 28


EXAMPLE_CLASS = pathlib.Path(__file__).parent / "../example"


def example_class(tempdir, date):
    destination = tempdir / "example_class"
    shutil.copytree(EXAMPLE_CLASS, destination)

    builddir = destination / "website" / "_build"
    if builddir.exists():
        shutil.rmtree(builddir)

    builddir.mkdir()

    def now():
        return date

    publish.cli(
        [
            str(destination),
            str(destination / "website/_build/published"),
            "--skip-directories",
            "template",
        ],
        now=now,
    )

    return destination


def clean_build(builddir):
    for f in builddir.iterdir():
        if not f.name == "published":
            if f.is_dir():
                shutil.rmtree(f)
            else:
                f.unlink()


@fixture(scope="module")
def publish_on_oct_16(tmp_path_factory):
    tempdir = tmp_path_factory.mktemp("example_16th")
    path = example_class(tempdir, datetime.datetime(2020, 10, 16, 0, 0, 0))
    clean_build(path / "website" / "_build")
    return path


@fixture(scope="module")
def publish_on_oct_15(tmp_path_factory):
    tempdir = tmp_path_factory.mktemp("example_15th")
    path = example_class(tempdir, datetime.datetime(2020, 10, 15, 0, 0, 0))
    clean_build(path / "website" / "_build")
    return path


@fixture(scope="module")
def publish_before_quarter(tmp_path_factory):
    tempdir = tmp_path_factory.mktemp("example_before")
    path = example_class(tempdir, datetime.datetime(2020, 9, 15, 0, 0, 0))
    clean_build(path / "website" / "_build")
    return path


@mark.slow
def test_fixture(publish_on_oct_15):
    path = publish_on_oct_15
    assert (path / "website" / "theme").exists()
    assert (path / "website" / "_build" / "published" / "published.json").exists()


def test_last_homework_visible(publish_on_oct_15):
    # when
    path = publish_on_oct_15
    clean_build(path / "website" / "_build")
    broadcast.broadcast(
        path / "website/",
        path / "website/_build",
        path / "website/_build/published",
        now=lambda: datetime.datetime(2020, 10, 15, 12, 0, 0),
    )

    # then
    out = path / "website" / "_build" / "index.html"
    with out.open() as fileobj:
        contents = fileobj.read()

    etree = lxml.html.fromstring(contents)

    # select the div containing all homework links
    xpath = '//div[ h3[ contains(text(), "Homework 3") ] ]'
    [div] = etree.xpath(xpath)

    # get the link to the homework notebook
    [a] = div.xpath('.//a[ text() = "Homework Notebook" ]')
    assert a.values()[0] == "published/homeworks/03-charts_and_functions/homework.txt"

    # also assert that the due date is displayed
    [elem] = div.xpath('.//*[ contains(text(), "Due")]')
    assert "Oct 22" in elem.text


def test_last_homework_solutions_not_posted_on_15th(publish_on_oct_15):
    # when
    path = publish_on_oct_15
    clean_build(path / "website" / "_build")
    broadcast.broadcast(
        path / "website/",
        path / "website/_build",
        path / "website/_build/published",
        now=lambda: datetime.datetime(2020, 10, 15, 12, 0, 0),
    )

    # then
    out = path / "website" / "_build" / "index.html"
    with out.open() as fileobj:
        contents = fileobj.read()

    etree = lxml.html.fromstring(contents)

    # select the div containing all homework links
    xpath = '//div[ h3[ contains(text(), "Homework 3") ] ]'
    [div] = etree.xpath(xpath)

    # get the link to the homework notebook
    results = div.xpath('.//a[ text() = "Solution Notebook" ]')
    assert not results


def test_homework_2_solutions_posted_on_16th(publish_on_oct_16):
    # when
    path = publish_on_oct_16
    clean_build(path / "website" / "_build")
    broadcast.broadcast(
        path / "website/",
        path / "website/_build",
        path / "website/_build/published",
        now=lambda: datetime.datetime(2020, 10, 16, 12, 0, 0),
    )

    # then
    out = path / "website" / "_build" / "index.html"
    with out.open() as fileobj:
        contents = fileobj.read()

    etree = lxml.html.fromstring(contents)

    # select the div containing all homework links
    xpath = '//div[ h3[ contains(text(), "Homework 2") ] ]'
    [div] = etree.xpath(xpath)

    # get the link to the homework notebook
    results = div.xpath('.//a[ text() = "Solution Notebook" ]')
    assert results


def test_homework_2_solutions_not_posted_on_15th(publish_on_oct_16):
    # when
    path = publish_on_oct_16
    clean_build(path / "website" / "_build")
    broadcast.broadcast(
        path / "website/",
        path / "website/_build",
        path / "website/_build/published",
        now=lambda: datetime.datetime(2020, 10, 16, 12, 0, 0),
    )

    # then
    out = path / "website" / "_build" / "index.html"
    with out.open() as fileobj:
        contents = fileobj.read()

    assert "published/homeworks/02-tables/solution.txt" in contents