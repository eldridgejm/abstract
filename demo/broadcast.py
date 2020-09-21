import jinja2


loader = jinja2.FileSystemLoader('./theme/templates')
environment = jinja2.Environment(loader=loader) 
template = environment.get_template('default.html')
