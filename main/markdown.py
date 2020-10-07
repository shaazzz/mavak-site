import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from markdown2 import markdown as markdown2


def markdown(content):
    content = re.sub(r"%[ \t\n]*aparat\.(.{5})[ \t\n]*%", r'<div id="\1">'
                                                          r'<script type="text/JavaScript" '
                                                          r'src="https://www.aparat.com/embed/\1?data[rnddiv]='
                                                          r'\1&data[responsive]=yes">'
                                                          r'</script></div><br>', content)

    val = URLValidator()
    try:
        val(content)
        content = '<a href="' + content \
                  + '" class="btn btn-light btn-lg active" role="button" aria-pressed="true">لینک این مطلب</a>'
    except ValidationError:
        pass
    return markdown2(content)
