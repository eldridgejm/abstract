import pathlib
import json

import jinja2
import markdown
import publish
import yaml


class Elements:
    def __init__(self, config):
        self.config = config

    def announcement_box(self, key):
        return self.config[key]["contents"]


def _load_published(published_path, output_path):
    """Load published artifacts from published.json and update their paths."""

    # read the universe
    with (published_path / "published.json").open() as fileobj:
        published = publish.deserialize(fileobj.read())

    # we need to update their paths to be relative to output directory; this function
    # will do it for one artifact
    def _update_path(artifact):
        relative_path = published_path.relative_to(output_path) / artifact.path
        return artifact._replace(path=relative_path)

    # apply the function to all artifacts, modifying `published`
    for collection in published.collections.values():
        for publication in collection.publications.values():
            for artifact_key, artifact in publication.artifacts.items():
                publication.artifacts[artifact_key] = _update_path(artifact)

    return published


def _interpolate(contents, elements, published=None):
    as_template = jinja2.Template(
        contents, variable_start_string="${", variable_end_string="}"
    )
    context = {"elements": elements}

    if published is not None:
        context["published"] = published

    return as_template.render(**context)


def _convert_markdown_to_html(contents):
    return markdown.markdown(contents)


def _render_page(environment, body):
    return environment.get_template("base.html").render(body=body)


def _all_pages(input_path, output_path):
    for page_path in (input_path / 'pages').iterdir():
        new_path = output_path / page_path.relative_to(
            input_path / "pages"
        ).with_suffix(".html")

        with page_path.open() as fileobj:
            contents = fileobj.read()

        yield contents, new_path

    for page_path in (input_path / 'theme' / 'pages').iterdir():
        new_path = output_path / page_path.relative_to(
            input_path / 'theme' / "pages"
        ).with_suffix(".html")

        with page_path.open() as fileobj:
            contents = fileobj.read()

        yield contents, new_path


def broadcast(input_path, output_path, published_path=None):
    input_path = pathlib.Path(input_path)
    output_path = pathlib.Path(output_path)
    if published_path is not None:
        published_path = pathlib.Path(published_path)

    # create the output path, if it doesn't already exist
    output_path.mkdir(exist_ok=True)

    # load the publications and update their paths
    if published_path is not None:
        published = _load_published(published_path, output_path)
    else:
        published = None

    # load the configuration file
    with (input_path / "config.yaml").open() as fileobj:
        config = yaml.load(fileobj, Loader=yaml.Loader)

    # get the elements ready
    elements = Elements(config)

    # load the theme environment
    jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(input_path / "theme" / "templates")
    )

    # convert user pages
    for contents, new_path in _all_pages(input_path, output_path):

        interpolated = _interpolate(contents, elements=elements, published=published)
        body_html = _convert_markdown_to_html(interpolated)
        html = _render_page(jinja_environment, body_html)

        with new_path.open("w") as fileobj:
            fileobj.write(html)
