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


def update_for_view(name: str) -> None:
    pipelines_filter = config.views[name].get('pipelines')
    projects_filter = config.views[name].get('projects')
    branches_filter = config.views[name].get('branches')
    jobs_filter = [job
                   for branch in config.views[name].get('branches').values()
                   for job in branch]

    pipelines = get_pipelines(pipelines_filter)
    projects = get_projects(projects_filter)
    branches = get_branches(branches_filter)
    jobs = get_jobs(jobs_filter)

    i = 0
    end = len(branches) * len(jobs) * len(pipelines) * len(projects)
    progress(i, end)

    session = db.session()

    for pipeline in pipelines:
        for project in projects:
            for branch in branches:
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


def update() -> None:
    for view in config.views:
        print(view)
        update_for_view(view)


def main() -> None:
    while True:
        print('::', time.asctime(), '::')
        print('Updating results database...')
        time_start = time.time()
        update()
        time_end = time.time()
        print('Done.')

        time_took = time_end - time_start
        time_left = config.pull_interval - time_took
        print(f'Took: {time_took:.2f} seconds.')

        if time_left > 0:
            print(f'Going to sleep for {time_left:.2f} seconds...')
            time.sleep(time_left)
