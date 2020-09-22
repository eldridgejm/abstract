import jinja2
import cerberus


SCHEMA = {
    "collection": {"type": "string"},
    "numbered": {"type": "boolean", "default": False},
    "columns": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "content": {"type": "string"},
                "name": {"type": "string"},
                "url": {"type": "string", "default": None, "nullable": True},
                "on_missing": {"type": "string", "default": None, "nullable": True},
            },
        },
    },
}


def interpolate(publication, s):
    if s is None:
        return None

    as_template = jinja2.Template(
        s, variable_start_string="${", variable_end_string="}"
    )

    try:
        return as_template.render(
            artifacts=publication.artifacts, metadata=publication.metadata
        )
    except jinja2.UndefinedError:
        return None


def listing(templates, published, config):
    validator = cerberus.Validator(SCHEMA, require_all=True)
    config = validator.validated(config)

    if config is None:
        raise RuntimeError(f"Invalid config: {validator.errors}")

    # sort the publications by key
    publications = published.collections[config["collection"]].publications
    publications = sorted(publications.items())
    publications = [v for (j, v) in publications]

    template = templates.get_template("listing.html")
    return template.render(
        config=config, publications=publications, interpolate=interpolate
    )
