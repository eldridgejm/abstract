"""Generate a static site with broadcast.broadcast"""
import argparse
import pathlib
import functools
import shutil

import cerberus
import jinja2
import markdown
import publish
import yaml

from . import elements


def load_published(published_path, output_path):
    """Load artifacts from ``published.json`` and update their paths.

    The artifacts in ``published.json`` have a ``path`` attribute that gives
    their path relative to ``published.json``. But we need the path to the
    artifact from the website root: the ``output_path``. This function loads the
    artifacts and performs the update.

    Parameters
    ----------
    published_path : pathlib.Path
        Path to the directory containing ``published.json``.
    output_path : pathlib.Path
        Path to the output directory. This should be a directory under the
        output path.

    Returns
    -------
    published.Universe
        The universe of published artifacts, with each artifact's path updated
        to be relative to ``output_path``.

    """

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


def load_config(path):
    """Read the configuration from a yaml file.

    Parameters
    ----------
    path : pathlib.Path
        The path to the configuration file.

    Returns
    -------
    dict
        The configuration dictionary.

    Note
    ----

    This loader supports the ``!include`` tag, allowing the configuration file
    to be split into several files. For instance:

    .. code-block:: yaml
        
        # config.yaml
        theme:
            page_title: My Website

        schedule: !include schedule.yaml
        announcements: !include announcements.yaml

    """

    # we'll subclass yaml.Loader and add a constructor
    class IncludingLoader(yaml.Loader):
        def include(self, node):
            included_path = path.parent / self.construct_scalar(node)
            with included_path.open() as fileobj:
                return yaml.load(fileobj, IncludingLoader)

    IncludingLoader.add_constructor("!include", IncludingLoader.include)

    with path.open() as fileobj:
        return yaml.load(fileobj, Loader=IncludingLoader)


class _Elements:
    """A class to create closures for page elements.

    Used in broadcast(). We instantiate _Elements with a universe and a
    template loader. When an attribute of the instance is accessed, the element
    with that name will be pulled in from the elements module and its
    "templates" and "published" arguments will be closed over. The result is a
    function of one argument: the configuration.

    """

    def __init__(self, environment):
        self.environment = environment

    def __getattr__(self, attr):
        try:
            func = getattr(elements, attr)
        except AttributeError:
            raise RuntimeError(f'There is no element named "{attr}".')
        return jinja2.contextfunction(functools.partial(func, self.environment))


def _render_page(contents, context):
    """Given page contents and a context, perform Jinja2 interpolation.

    Parameters
    ----------
    contents : str
        The page contents.
    context : dict
        A dictionary mapping variable names to values available during
        interpolation.

    Returns
    -------
    str
        The input string after interpolation.

    Notes
    -----
    Variables are delimited by ${ }, and blocks are delimited by ${%  %}.

    """
    template = jinja2.Template(
        contents,
    )

    return template.render(**context)


def _convert_markdown_to_html(contents):
    """Convert markdown to HTML.

    Parameters
    ----------
    contents : str
        The markdown string.

    Returns
    -------
    str
        The HTML.

    """
    return markdown.markdown(contents)


def _all_pages(input_path, output_path):
    """Generate all page contents and their output paths.

    Parameters
    ----------
    input_path : pathlib.Path
        The path to the input. ``input_path / 'pages'`` should contain the pages.
    output_path : pathlib.Path
        The path to the directory where the rendered pages will be placed.

    Yields
    ------
    (str, pathlib.Path)
        The contents of the input page, along with the path to where the rendered
        page should be placed.

    """
    for page_path in (input_path / "pages").iterdir():
        root = input_path / "pages"
        new_path = output_path / page_path.relative_to(root).with_suffix(".html")

        with page_path.open() as fileobj:
            contents = fileobj.read()

        yield contents, new_path


def _render_base(base_environment, body_html, config):
    return base_environment.get_template('page.html').render(body=body_html, config=config)



def _validate_theme_schema(input_path, config):
    """Validate a config against the theme's schema."""
    with (input_path / "theme" / "schema.yaml").open() as fileobj:
        theme_schema = yaml.load(fileobj, Loader=yaml.Loader)

    validator = cerberus.Validator(theme_schema, allow_unknown=True, require_all=True)
    result = validator.validate(config)
    if not result:
        raise RuntimeError(f"Invalid theme config: {validator.errors}")


def _create_element_environment(input_path):
    """Create the element environment and its custom filters."""
    element_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(input_path / 'theme' / 'elements'),
    )

    def evaluate(s, **kwargs):
        _DELIMITER_KWARGS = dict(
                variable_start_string="${",
                variable_end_string="}",
                block_start_string="${%",
                block_end_string="%}",
                )

        try:
            return jinja2.Template(s, **_DELIMITER_KWARGS).render(**kwargs)
        except TypeError:
            return None
        except jinja2.UndefinedError:
            return None

    element_environment.filters['evaluate'] = evaluate
    element_environment.filters['markdown_to_html'] = _convert_markdown_to_html

    return element_environment


def _create_base_template_environment(input_path):
    """Create the base template environment."""
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(input_path / "theme" / "base_templates"),
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
        published = load_published(published_path, output_path)
    else:
        published = None

    # load the configuration file
    config = load_config(input_path / "config.yaml")

    # validate the config against the theme's schema
    _validate_theme_schema(input_path, config)

    # create environments for evaluation of base templates and element templates
    element_environment = _create_element_environment(input_path)
    base_environment = _create_base_template_environment(input_path)

    # construct the context used during page rendering
    context = {
        "elements": _Elements(environment=element_environment),
        "config": config,
        "published": published
    }

    # convert user pages
    for contents, new_path in _all_pages(input_path, output_path):
        interpolated = _render_page(contents, context)
        body_html = _convert_markdown_to_html(interpolated)
        html = _render_base(base_environment, body_html, config)

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
