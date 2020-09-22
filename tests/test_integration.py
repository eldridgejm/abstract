import pathlib
import shutil
from textwrap import dedent

from pytest import fixture

import broadcast


class Demo:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.builddir = self.path / "_build"
        (path / "pages").mkdir()
        (path / "config.yaml").touch()

        shutil.copytree(pathlib.Path(__file__).parent / "theme", path / "theme")

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
        ${ published.collections.homeworks.publications["01-intro"].artifacts["homework.pdf"].path }
        """
    )
    demo.make_page("one.md", contents)
    demo.use_example_published("example_published_1")

    # when
    broadcast.broadcast(
        demo.path, demo.builddir, published_path=demo.builddir / "published"
    )

    # then
    assert "published/homeworks/01-intro/homework.pdf" in demo.get_output("one.html")


def test_pages_have_access_to_elements(demo):
    # given
    demo.make_page("one.md", "${ elements.announcement_box(config['announcement']) }")
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
    assert "<title>example theme</title>" in demo.get_output("one.html")
