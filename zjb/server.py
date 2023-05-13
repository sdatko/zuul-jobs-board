#!/usr/bin/env python3

from collections import defaultdict

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
from zjb.utils import any_match


app = Flask(__name__)


def get_results(filters: dict) -> dict:
    session = db.session()
    pipelines = [v for (v, ) in session.query(db.Build.pipeline).distinct()]
    projects = [v for (v, ) in session.query(db.Build.project).distinct()]
    branches = [v for (v, ) in session.query(db.Build.branch).distinct()]
    jobs = [v for (v, ) in session.query(db.Build.job).distinct()]

    # The scheme for results is: pipelines{} -> projects{} -> jobs[]
    results = defaultdict(lambda: defaultdict(list))
    headers = defaultdict(list)

    for pipeline in pipelines:
        if filters.get('pipelines'):
            if not any_match(pipeline, filters['pipelines']):
                continue

        for project in projects:
            if filters.get('projects'):
                if not any_match(project, filters['projects']):
                    continue

            for branch in branches:
                if filters.get('branches'):
                    if not any_match(branch, filters['branches']):
                        continue

                for job in jobs:
                    if filters['branches'].get(branch):
                        if not any_match(job, filters['branches'][branch]):
                            continue

                    if job not in headers[branch]:
                        headers[branch].append(job)

                    build = session.query(db.Build).filter(
                        db.Build.project == project,
                        db.Build.branch == branch,
                        db.Build.pipeline == pipeline,
                        db.Build.job == job,
                    ).one_or_none()

                    if build:
                        results[pipeline][project].append(build.__dict__)
                    else:
                        results[pipeline][project].append(None)

    session.close()
    return results, headers


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

    results, headers = get_results(config.views[name])
    last_update = db.get_last_update()

    return render_template(
        'results.html.j2',
        name=name,
        groups=config.groups,
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


@app.route("/db.sqlite3", methods=['GET'])
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
