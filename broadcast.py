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
        return self.config[key]['contents']


def broadcast(input_path, output_path, published_path=None):
    input_path = pathlib.Path(input_path)
    output_path = pathlib.Path(output_path)
    if published_path is not None:
        published_path = pathlib.Path(published_path)

    # create the output path, if it doesn't already exist
    output_path.mkdir(exist_ok=True)

    # load the publications
    if published_path is not None:
        with (published_path / "published.json").open() as fileobj:
            published = publish.deserialize(fileobj.read())

        # update their paths relative to the output directory
        for collection in published.collections.values():
            for publication in collection.publications.values():
                for artifact_key, artifact in publication.artifacts.items():
                    relative_path = published_path.relative_to(output_path) / artifact.path
                    new_artifact = artifact._replace(path=relative_path)
                    publication.artifacts[artifact_key] = new_artifact
    else:
        published = None

    with (input_path / 'config.yaml').open() as fileobj:
        config = yaml.load(fileobj, Loader=yaml.Loader)
    elements = Elements(config)

    # convert markdown to html
    for page_path in (input_path / "pages").iterdir():
        with page_path.open() as fileobj:
            contents = fileobj.read()

        template = jinja2.Template(contents, variable_start_string='${', variable_end_string='}')

        if published:
            contents = template.render(published=published, elements=elements)
        else:
            contents = template.render(elements=elements)

        body_html = markdown.markdown(contents)

        environment = jinja2.Environment(loader=jinja2.FileSystemLoader(input_path / 'theme' / 'templates'))
        html = environment.get_template('base.html').render(body=body_html)

        new_path = output_path / page_path.relative_to(
            input_path / "pages"
        ).with_suffix(".html")
        with new_path.open("w") as fileobj:
            fileobj.write(html)

    # render theme pages
    for page_path in (input_path / 'theme' / 'pages').iterdir():
        with page_path.open() as fileobj:
            contents = fileobj.read()

        template = jinja2.Template(contents, variable_start_string='${', variable_end_string='}')

        if published:
            contents = template.render(published=published, elements=elements)
        else:
            contents = template.render(elements=elements)

        body_html = contents

        environment = jinja2.Environment(loader=jinja2.FileSystemLoader(input_path / 'theme' / 'templates'))
        html = environment.get_template('base.html').render(body=body_html)

        new_path = output_path / page_path.relative_to(
            input_path / 'theme' / "pages"
        ).with_suffix(".html")
        with new_path.open("w") as fileobj:
            fileobj.write(html)

