from mistune import Renderer, escape
from mistune import Markdown as mis_Markdown
from flask import Markup
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html


class HighlightRenderer(Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter()
        return highlight(code, lexer, formatter)


class Mistune:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.jinja_env.filters.setdefault('markdown', self.render)

    def render(self, text):
        return markdown(text)


def markdown(text):
    renderer = HighlightRenderer()
    markdown_mid = mis_Markdown(renderer=renderer)
    return Markup(markdown_mid(text))
