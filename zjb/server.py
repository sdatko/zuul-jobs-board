#!/usr/bin/env python3

from collections import defaultdict

from flask import abort
from flask import Flask
from jinja2 import Environment
from jinja2 import PackageLoader

from zjb import config
from zjb import db
from zjb.utils import any_match


app = Flask(__name__)

j2env = Environment(loader=PackageLoader('zjb', 'templates'))
template_index = j2env.get_template('index.html.j2')
template_results = j2env.get_template('results.html.j2')


def get_last_update() -> str:
    session = db.session()

    last_update = (
        session
        .query(db.Build.updated)
        .order_by(db.Build.updated.desc())
        .first()
    )

    if last_update:
        last_update = last_update[0]

    session.close()
    return last_update


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
                        results[pipeline][project].append({
                            'name': job,
                            'status': build.status,
                            'URL': build.URL,
                            'voting': build.voting,
                        })
                    else:
                        results[pipeline][project].append({
                            'name': '---',
                            'status': '---',
                            'URL': '',
                            'voting': True,
                        })

    session.close()
    return results, headers


@app.route("/", methods=['GET'])
def index():
    last_update = get_last_update()

    return template_index.render(
        last_update=last_update,
        url_prefix=config.url_prefix,
        views=config.views,
    )


@app.route("/<string:name>", methods=['GET'])
def view(name):
    if name not in config.views:
        abort(404)

    results, headers = get_results(config.views[name])
    last_update = get_last_update()

    return template_results.render(
        name=name,
        groups=config.groups,
        headers=headers,
        last_update=last_update,
        results=results,
        url_prefix=config.url_prefix,
    )


def main() -> None:
    app.run(port=config.app_port)
