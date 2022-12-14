#!/usr/bin/env python3

from datetime import datetime
import time

from zjb import config
from zjb import db
from zjb.utils import progress
from zjb.zuul import get_branches
from zjb.zuul import get_jobs
from zjb.zuul import get_last_build
from zjb.zuul import get_pipelines
from zjb.zuul import get_projects


def update() -> None:
    branches = get_branches()
    jobs = get_jobs()
    pipelines = get_pipelines()
    projects = get_projects()

    i = 0
    end = len(branches) * len(jobs) * len(pipelines) * len(projects)
    progress(i, end)

    session = db.session()

    for project in projects:
        for branch in branches:
            for pipeline in pipelines:
                for job in jobs:
                    build = get_last_build(project, branch, pipeline, job)
                    date = build.get('start_time', '')

                    if date and (datetime.now()
                                 - datetime.fromisoformat(date)).days > 14:
                        build['result'] = '---'
                        build['log_url'] = ''

                    db.Build.create_or_update(
                        session, project, branch, pipeline, job,
                        build.get('uuid', ''),
                        build.get('result', '---'),
                        build.get('log_url', ''),
                        build.get('voting', True)
                    )

                    i += 1
                    progress(i, end)

    session.close()


def main() -> None:
    while True:
        print('Updating results database...')
        update()
        print('Done.')
        time.sleep(60 * 60 * 6)
