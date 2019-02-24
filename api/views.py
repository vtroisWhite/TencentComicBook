from flask import Blueprint, jsonify, request, abort
import cachetools.func

from onepiece.comicbook import ComicBook
from onepiece.exceptions import ComicbookException, NotFoundError, SiteNotSupport


app = Blueprint("main", __name__)


@app.errorhandler(ComicbookException)
def handle_404(error):
    if isinstance(error, NotFoundError):
        return jsonify(
            {
                "message": str(error)
            }), 404
    elif isinstance(error, SiteNotSupport):
        return jsonify(
            {
                "message": str(error)
            }), 400
    else:
        return jsonify(
            {
                "message": str(error)
            }), 500


@app.route("/")
def index():
    return jsonify(
        {
            "api_status": "ok",
            "example": [
                "/comic/ishuhui/1",
                "/comic/ishuhui/1/933",
                "/comic/qq/505430",
                "/comic/qq/505430/933",
                "/comic/wangyi/5015165829890111936",
                "/comic/wangyi/5015165829890111936/933",
                "/search/qq?name=海贼王",
                "/search/wangyi?name=海贼王",
                "/search/ishuhui?name=海贼王"
            ]
        }
    )


@cachetools.func.ttl_cache(maxsize=1024, ttl=3600, typed=False)
def get_comicbook(site, comicid):
    return ComicBook.create_comicbook(site=site, comicid=comicid)


@app.route("/comic/<site>/<comicid>")
def get_comicbook_info(site, comicid):
    comicbook = get_comicbook(site=site, comicid=comicid)
    return jsonify(comicbook.to_dict())


@app.route("/comic/<site>/<comicid>/<int:chapter_number>")
def get_chapter_info(site, comicid, chapter_number):
    comicbook = get_comicbook(site, comicid)
    chapter = comicbook.Chapter(chapter_number)
    rv = comicbook.to_dict()
    rv["chapter"] = chapter.to_dict()
    return jsonify(rv)


@app.route("/search/<site>")
def search(site):
    name = request.args.get('name')
    if not name:
        abort(400)
    search_result_item_list = ComicBook.search(site=site, name=name)
    return jsonify(
        {
            "search_result": [item.to_dict() for item in search_result_item_list]
        }
    )
