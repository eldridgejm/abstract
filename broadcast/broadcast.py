import argparse
import itertools
import pathlib
import functools
import shutil
import json

import cerberus
import jinja2
import markdown
import publish
import yaml

from . import elements


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


def _interpolate(contents, context):
    as_template = jinja2.Template(
        contents,
        variable_start_string="${",
        variable_end_string="}",
        block_start_string="${%",
        block_end_string="%}",
    )

    return as_template.render(**context)


def _convert_markdown_to_html(contents):
    return markdown.markdown(contents)


def _render_page(environment, body, config):
    return environment.get_template("base.html").render(body=body, config=config)


def _all_pages(input_path, output_path):

    for location in ["pages", "theme/pages"]:
        for page_path in (input_path / location).iterdir():
            root = input_path / location
            new_path = output_path / page_path.relative_to(root).with_suffix(".html")

            with page_path.open() as fileobj:
                contents = fileobj.read()

            yield contents, new_path


class Elements:
    def __init__(self, templates, published):
        self.templates = templates
        self.published = published

    def __getattr__(self, attr):
        try:
            func = getattr(elements, attr)
        except AttributeError:
            raise RuntimeError(f'There is no element named "{attr}".')
        return functools.partial(
            func, self.templates, self.published
        )


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

    # load the theme environment
    theme_templates = jinja2.Environment(
        loader=jinja2.FileSystemLoader(input_path / "theme" / "templates")
    )

    # validate the config against the theme's schema
    with (input_path / "theme" / "schema.yaml").open() as fileobj:
        theme_schema = yaml.load(fileobj, Loader=yaml.Loader)

    validator = cerberus.Validator(theme_schema, allow_unknown=True, require_all=True)
    result = validator.validate(config)
    if not result:
        raise RuntimeError(f"Invalid theme config: {validator.errors}")

    # the context used during interpolation
    context = {
        "elements": Elements(templates=theme_templates, published=published),
        "config": config,
    }

    if published is not None:
        context["published"] = published

    # convert user pages
    for contents, new_path in _all_pages(input_path, output_path):

        interpolated = _interpolate(contents, context)
        body_html = _convert_markdown_to_html(interpolated)
        html = _render_page(theme_templates, body_html, config)

        with new_path.open("w") as fileobj:
            fileobj.write(html)

    # copy static files
    shutil.copytree(input_path / "theme" / "style", output_path / "style")


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_path")
    parser.add_argument("--published_path")
    args = parser.parse_args()

    broadcast(pathlib.Path.cwd(), args.output_path, args.published_path)
