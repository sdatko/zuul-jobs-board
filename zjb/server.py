#!/usr/bin/env python3

from flask import abort
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import url_for
from gunicorn.app.base import BaseApplication

from zjb import config
from zjb import db


app = Flask(__name__)


@app.route("/", methods=['GET'])
def index():
    last_update = db.get_last_update()

    return render_template(
        'index.html.j2',
        last_update=last_update,
        views=config.views,
    )


@app.route("/view/<string:name>", methods=['GET'])
def view(name):
    if name not in config.views:
        abort(404)

    query = request.args.get('q')

    results, headers = db.get_results_for_view(config.views[name])
    last_update = db.get_last_update()

    return render_template(
        'results.html.j2',
        name=name,
        headers=headers,
        last_update=last_update,
        query=query,
        results=results,
    )


@app.route("/details", methods=['GET', 'POST'])
def details():
    ID = request.args.get('id')

    if not ID:
        abort(400)

    result = db.get_result(ID)
    last_update = db.get_last_update()

    if not result:
        abort(404)

    if request.method == 'POST' and 'notes' in request.form:
        db.set_notes(ID, text=request.form.get('notes'))
        return redirect(url_for('details', id=ID))

    return render_template(
        'details.html.j2',
        last_update=last_update,
        result=result,
    )


@app.route("/notes", methods=['GET'])
def notes():
    query = request.args.get('q')

    if request.args.get('missing'):
        results = db.get_missing_notes()
    elif request.args.get('obsolete'):
        results = db.get_obsolete_notes()
    else:
        results = db.get_results_with_notes()

    last_update = db.get_last_update()

    return render_template(
        'notes.html.j2',
        last_update=last_update,
        query=query,
        results=results,
    )


@app.route("/zjb.sqlite3", methods=['GET'])
def dumpdb():
    return send_file(db.dbfile)


class StandaloneApplication(BaseApplication):
    # From: https://docs.gunicorn.org/en/stable/custom.html

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main() -> None:
    options = {
        'accesslog': '-',
        'bind': f'127.0.0.1:{config.app_port}',
        'reload': True,
        'workers': 4,
    }
    StandaloneApplication(app, options).run()
