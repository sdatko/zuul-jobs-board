#!/usr/bin/env python3

from collections import defaultdict

from flask import Flask
from jinja2 import Environment
from jinja2 import PackageLoader

from zjb import config
from zjb import db


app = Flask(__name__)

j2env = Environment(loader=PackageLoader('zjb', 'templates'))
template = j2env.get_template('index.html.j2')


def get_results() -> dict:
    session = db.session()
    projects = [v for (v, ) in session.query(db.Build.project).distinct()]
    branches = [v for (v, ) in session.query(db.Build.branch).distinct()]
    pipelines = [v for (v, ) in session.query(db.Build.pipeline).distinct()]
    jobs = [v for (v, ) in session.query(db.Build.job).distinct()]

    results = defaultdict(lambda: defaultdict(list))

    for project in projects:
        for branch in branches:
            for pipeline in pipelines:
                for job in jobs:
                    build = session.query(db.Build).filter(
                        db.Build.project == project,
                        db.Build.branch == branch,
                        db.Build.pipeline == pipeline,
                        db.Build.job == job,
                    ).one_or_none()

                    if build:
                        results[f'{pipeline} / {branch}'][project].append({
                            'name': job,
                            'status': build.status,
                            'URL': build.URL,
                            'voting': build.voting,
                        })

    session.close()
    return results


@app.route("/", methods=['GET'])
def index():
    results = get_results()
    return template.render(results=results, groups=config.groups)


def main() -> None:
    app.run(port=config.app_port)
