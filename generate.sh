mkdir public 2> /dev/null
jinja2 index.html.j2 data.yml > public/index.html
