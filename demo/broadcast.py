import pathlib
import json

import jinja2
import markdown
import publish

OUTPUT = pathlib.Path('_build/public')
PUBLISHED = pathlib.Path('_build/public/published')


def main():
    # load the publications
    with (PUBLISHED / 'published.json').open() as fileobj:
        published = publish.deserialize(fileobj.read())

    # update their paths relative to the output directory
    for collection in published.collections.values():
        for publication in collection.publications.values():
            for artifact_key, artifact in publication.artifacts.items():
                relative_path = PUBLISHED.relative_to(OUTPUT) / artifact.path
                new_artifact = artifact._replace(path=relative_path)
                publication.artifacts[artifact_key] = new_artifact

    print(published)


if __name__ == '__main__':
    main()
