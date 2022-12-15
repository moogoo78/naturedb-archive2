from flask import (
    Blueprint,
    render_template,
)
import markdown

from app.database import session
from app.models.site import (
    Organization,
    Article,
)

page = Blueprint('page', __name__)

@page.route('/researcher')
def researcher():
    return render_template('researcher.html')

@page.route('/visiting')
def visiting():
    return render_template('visiting.html')

@page.route('/making-specimen')
def making_specimen():
    return render_template('making-specimen.html')

@page.route('/about')
def about_page():
    return render_template('about.html')

@page.route('/related_links')
def related_links():
    org = session.get(Organization, 1)
    return render_template('related_links.html', organization=org)

@page.route('/articles/<article_id>')
def article_detail(article_id):
    article = Article.query.get(article_id)
    article.content_html = markdown.markdown(article.content)
    return render_template('article-detail.html', article=article)
