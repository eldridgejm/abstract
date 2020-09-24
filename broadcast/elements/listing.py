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
                "on_missing_url": {"type": "string", "default": None, "nullable": True},
            },
        },
    },
}


def listing(environment, context, element_config, now):
    validator = cerberus.Validator(SCHEMA, require_all=True)
    element_config = validator.validated(element_config)

    if element_config is None:
        raise RuntimeError(f"Invalid config: {validator.errors}")

    # sort the publications by key
    collections = context["published"].collections
    collection = collections[element_config["collection"]]
    publications_and_keys = sorted(collection.publications.items())
    publications = [v for (j, v) in publications_and_keys]

    template = environment.get_template("listing.html")
    return template.render(element_config=element_config, publications=publications,)
