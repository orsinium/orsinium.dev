mkdir public 2> /dev/null
jinja2 -e loopcontrols -e jinja2_markdown.MarkdownExtension index.html.j2 data.yml > public/index.html

