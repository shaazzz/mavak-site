import re

from markdown2 import markdown as markdown2


def markdown(content):
    content = re.sub(r"%[ \t\n]*aparat\.(.{5})[ \t\n]*%", r'<div id="\1">'
                                                          r'<script type="text/JavaScript" '
                                                          r'src="https://www.aparat.com/embed/\1?data[rnddiv]='
                                                          r'\1&data[responsive]=yes">'
                                                          r'</script></div><br>', content)
    return markdown2(content)
