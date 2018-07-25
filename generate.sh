mkdir output 2> /dev/null
jinja2 index.html.j2 data.yml > output/index.html
