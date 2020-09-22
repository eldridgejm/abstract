import cerberus
import markdown


SCHEMA = {
    "contents": {"type": "string", "nullable": True},
    "urgent": {"type": "boolean", "default": False},
}


def announcement_box(templates, published, config):
    validator = cerberus.Validator(SCHEMA)
    config = validator.validated(config)

    if config is None:
        raise RuntimeError(f"Invalid config: {validator.errors}")

    if config["contents"] is None:
        return ""

    config["contents"] = markdown.markdown(config["contents"])
    template = templates.get_template("announcement-box.html")
    return template.render(config=config)
