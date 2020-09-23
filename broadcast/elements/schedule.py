import typing
import datetime
import cerberus
import publish

SCHEMA = {
    "week_topics": {"type": "list", "schema": {"type": "string"}},
    "first_week_number": {"type": "integer", "default": 1},
    "first_week_start_date": {"type": "date"},
    "lecture": {
        "type": "dict",
        "schema": {
            "collection": {"type": "string"},
            "date_key": {"type": "string"},
            "title": {"type": "string"},
            "resources": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "text": {"type": "string"},
                        "icon": {"type": "string"},
                    },
                },
            },
            "parts": {
                "type": "dict",
                "schema": {"key": {"type": "string"}, "text": {"type": "string"}},
            },
        },
    },
    "assignments": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "collection": {"type": "string"},
                "date_key": {"type": "string"},
                "due_key": {"type": "string"},
                "title": {"type": "string"},
                "resources": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": {
                            "text": {"type": "string"},
                            "icon": {"type": "string"},
                            "on_missing": {"type": "string", "default": None, "nullable": True},
                        },
                    },
                },
            },
        },
    },
}


ONE_WEEK = datetime.timedelta(weeks=1)


def _publication_within_week(start_date, date_key):
    def filter(key, node):
        if not isinstance(node, publish.Publication):
            return True
        else:
            date = node.metadata[date_key]
            if isinstance(date, datetime.datetime):
                date = date.date()

            return start_date <= date < start_date + ONE_WEEK

    return filter


class Week:
    def __init__(self, number, start_date, topic):
        self.number = number
        self.start_date = start_date
        self.topic = topic

    def filter(self, collection, date_key):
        return publish.filter_nodes(
            collection, _publication_within_week(self.start_date, date_key)
        )


def generate_weeks(element_config, published):
    weeks = []
    for i, topic in enumerate(element_config["week_topics"]):
        number = element_config["first_week_number"] + i
        week = Week(
            number=element_config["first_week_number"] + i,
            topic=topic,
            start_date=element_config["first_week_start_date"] + i * ONE_WEEK,
        )
        weeks.append(week)

    return weeks


def order_weeks(weeks, today):
    past_weeks = [w for w in weeks if w.start_date <= today]
    future_weeks = [w for w in weeks if w.start_date > today]

    past = sorted(past_weeks, key=lambda x: x.start_date, reverse=True)
    future = sorted(future_weeks, key=lambda x: x.start_date, reverse=False)

    return past + future


def schedule(environment, context, element_config):
    validator = cerberus.Validator(SCHEMA)
    element_config = validator.validated(element_config)

    if element_config is None:
        raise RuntimeError(f"Invalid config: {validator.errors}")

    weeks = generate_weeks(element_config, context["published"])
    weeks = order_weeks(weeks, datetime.date.today() + 3*ONE_WEEK)

    template = environment.get_template("schedule.html")
    return template.render(
        element_config=element_config, published=context["published"], weeks=weeks,
        now=datetime.datetime.now() + 3*ONE_WEEK
    )
