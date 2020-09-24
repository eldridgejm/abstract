import pathlib
import shutil
import datetime
import lxml.html
from textwrap import dedent

import publish

from pytest import raises, fixture, mark

import broadcast


# basic tests
# --------------------------------------------------------------------------------------


class Demo:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.builddir = self.path / "_build"
        (path / "pages").mkdir()
        (path / "config.yaml").touch()

        shutil.copytree(pathlib.Path(__file__).parent / "basic_theme", path / "theme")

        self.add_to_config(
            """
            theme:
                page_title: "example theme"
            """
        )

    def use_example_published(self, s):
        src = pathlib.Path(__file__).parent / s
        dst = self.builddir / "published"
        shutil.copytree(src, dst)
        return dst

    def use_example_theme(self, s):
        src = pathlib.Path(__file__).parent / s
        dst = self.path / "theme"
        shutil.copytree(src, dst)
        return dst

    def make_page(self, name, content):
        path = self.path / "pages" / name
        with path.open("w") as fileobj:
            fileobj.write(content)

    def make_theme_page(self, name, content):
        path = self.path / "theme" / "pages" / name
        with path.open("w") as fileobj:
            fileobj.write(content)

    def get_output(self, name):
        with (self.builddir / name).open() as fileobj:
            return fileobj.read()

    def add_to_config(self, content):
        with (self.path / "config.yaml").open("a") as fileobj:
            fileobj.write(dedent(content))


@fixture
def demo(tmpdir):
    return Demo(pathlib.Path(tmpdir))


def test_converts_pages_from_markdown_to_html(demo):
    # given
    demo.make_page("one.md", "# This is a header\n**this is bold!**")

    # when
    broadcast.broadcast(demo.path, demo.builddir)

    # then
    assert "<h1>This is a header</h1>" in demo.get_output("one.html")


def test_pages_have_access_to_published_artifacts(demo):
    # given
    contents = dedent(
        """
        {{ published.collections.homeworks.publications["01-intro"].artifacts["homework.pdf"].path }}
        """
    )
    demo.make_page("one.md", contents)
    demo.use_example_published("basic_published")

    # when
    broadcast.broadcast(
        demo.path, demo.builddir, published_path=demo.builddir / "published"
    )

    # then
    assert "published/homeworks/01-intro/homework.pdf" in demo.get_output("one.html")


def test_pages_have_access_to_elements(demo):
    # given
    demo.make_page("one.md", "{{ elements.announcement_box(config['announcement']) }}")
    config = dedent(
        """
        announcement:
            contents: This is a test.
            urgent: true
        """
    )
    demo.add_to_config(config)

    # when
    broadcast.broadcast(demo.path, demo.builddir)

    # then
    assert "This is a test" in demo.get_output("one.html")


def test_pages_are_rendered_in_base_template(demo):
    # given
    demo.make_page("one.md", "this is the page")

    # when
    broadcast.broadcast(demo.path, demo.builddir)

    # then
    assert "<html>" in demo.get_output("one.html")


def test_raises_if_an_unknown_variable_is_accessed_during_page_render(demo):
    # given
    demo.make_page("one.md", "{{ foo }}")

    # when
    with raises(broadcast.PageError) as excinfo:
        broadcast.broadcast(demo.path, demo.builddir)

    assert "one.md" in str(excinfo.value)


def test_raises_if_an_unknown_attribute_is_accessed_during_page_render(demo):
    # given
    demo.make_page("one.md", "{{ config.this_dont_exist }}")

    # when
    with raises(broadcast.PageError) as excinfo:
        broadcast.broadcast(demo.path, demo.builddir)

    assert "one.md" in str(excinfo.value)


def test_raises_if_an_unknown_attribute_is_accessed_during_element_render(demo):
    # given

    # x is in the element evaluation context, but y is not
    demo.add_to_config(
        dedent(
            """
        announcement:
            contents: Here ${ y } is
        """
        )
    )
    demo.make_page("one.md", "{{ elements.announcement_box(config['announcement']) }}")

    # when
    with raises(Exception) as excinfo:
        broadcast.broadcast(demo.path, demo.builddir)

    assert "${ y }" in str(excinfo.value)


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
DEFAULT_THEME = pathlib.Path(__file__).parent / "../example/theme"

DATETIME = datetime.datetime(2020, 10, 10, 23, 0, 0)


def example_class(tempdir, date):
    destination = tempdir / "example_class"
    shutil.copytree(EXAMPLE_CLASS, destination)
    shutil.copytree(DEFAULT_THEME, destination / "website" / "theme")

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
