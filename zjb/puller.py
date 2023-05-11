#!/usr/bin/env python3

from datetime import datetime
import time

from zjb import config
from zjb import db
from zjb.utils import any_match
from zjb.utils import progress
from zjb.zuul import get_branches
from zjb.zuul import get_jobs
from zjb.zuul import get_last_build
from zjb.zuul import get_pipelines
from zjb.zuul import get_projects


def find_buils_to_query() -> list:
    builds_to_query = []

    for view in config.views:
        pipelines_filter = config.views[view].get('pipelines')
        projects_filter = config.views[view].get('projects')
        branches_filter = config.views[view].get('branches')
        all_jobs_filter = [
            job
            for branch in config.views[view].get('branches').values()
            for job in branch
        ]

        pipelines = get_pipelines(pipelines_filter)
        projects = get_projects(projects_filter)
        branches = get_branches(branches_filter)
        jobs = get_jobs(all_jobs_filter)

        for pipeline in pipelines:
            if pipelines_filter:
                if not any_match(pipeline, pipelines_filter):
                    continue

            for project in projects:
                if projects_filter:
                    if not any_match(project, projects_filter):
                        continue

                for branch in branches:
                    if branches_filter:
                        if not any_match(branch, branches_filter):
                            continue

                    jobs_filter = config.views[view]['branches'][branch]
                    for job in jobs:
                        if jobs_filter:
                            if not any_match(job, jobs_filter):
                                continue

                        builds_to_query.append(
                            (pipeline, project, branch, job),
                        )

    return list(set(builds_to_query))


def update(builds_to_query: list) -> None:
    i = 0
    end = len(builds_to_query)
    progress(i, end)

    session = db.session()

    for build_args in builds_to_query:
        pipeline, project, branch, job = build_args

        build = get_last_build(project, branch, pipeline, job)

        if build.get('uuid') and build.get('start_time'):
            build['start_time'] = datetime.fromisoformat(
                build.get('start_time')
            )

            days_passed = (datetime.now() - build['start_time']).days

            if days_passed > config.obsolete_days:
                build['result'] = '---'
                build['voting'] = True

        db.Build.create_or_update(
            session, project, branch, pipeline, job,
            build.get('uuid', ''),
            build.get('start_time'),
            build.get('result', '---'),
            build.get('log_url', ''),
            build.get('voting', True),
        )

        i += 1
        progress(i, end)

    session.close()


def main() -> None:
    while True:
        print('::', time.asctime(), '::')
        print('Updating results database...')
        time_start = time.time()
        builds_to_query = find_buils_to_query()
        update(builds_to_query)
        time_end = time.time()
        print('Done.')

        time_took = time_end - time_start
        time_left = config.pull_interval - time_took
        print(f'Took: {time_took:.2f} seconds.')

        if time_left > 0:
            print(f'Going to sleep for {time_left:.2f} seconds...')
            time.sleep(time_left)
