#!/usr/bin/env python3

import os
import time

import requests

from zjb import config
from zjb import db
from zjb.utils import match


api_base = os.path.join(config.api_url, 'tenant', config.api_tenant)

builds_endpoint = os.path.join(api_base, 'builds')
jobs_endpoint = os.path.join(api_base, 'jobs')
pipelines_endpoint = os.path.join(api_base, 'pipelines')
projects_endpoint = os.path.join(api_base, 'projects')


def get_branches() -> list:
    # NOTE(sdatko): There is no easy way to get list of tracked branches
    #               from Zuul, or at least I was unable to find anything
    #               better than processing the builds list (which is not
    #               really reliable, as we cannot get all builds easily).
    #               For the time being, lets have this coming from config.
    return config.branches


def get_jobs() -> list:
    resp = requests.get(jobs_endpoint)
    jobs = [job.get('name') for job in resp.json()]

    if config.jobs:
        jobs = [job for job in jobs
                if any(match(job, job_specifier)
                       for job_specifier in config.jobs)]

    return jobs


def get_pipelines() -> list:
    resp = requests.get(pipelines_endpoint)
    pipelines = [pipeline.get('name') for pipeline in resp.json()]

    if config.pipelines:
        pipelines = [pipeline for pipeline in pipelines
                     if any(match(pipeline, pipeline_specifier)
                            for pipeline_specifier in config.pipelines)]

    return pipelines


def get_projects() -> list:
    resp = requests.get(projects_endpoint)
    projects = [project.get('name') for project in resp.json()]

    if config.projects:
        projects = [project for project in projects
                    if any(match(project, project_specifier)
                           for project_specifier in config.projects)]

    return projects


def get_last_build(project=None, branch=None, pipeline=None, job=None) -> dict:
    params = {'limit': 1}

    if project:
        params['project'] = project
    if branch:
        params['branch'] = branch
    if job:
        params['job_name'] = job
    if pipeline:
        params['pipeline'] = pipeline

    resp = requests.get(builds_endpoint, params=params)
    try:
        return resp.json().pop()
    except IndexError:
        return {}


def update() -> None:
    branches = get_branches()
    jobs = get_jobs()
    pipelines = get_pipelines()
    projects = get_projects()

    session = db.session()

    for project in projects:
        for branch in branches:
            for pipeline in pipelines:
                for job in jobs:
                    build = get_last_build(project, branch, pipeline, job)

                    db.Build.create_or_update(
                        session, project, branch, pipeline, job,
                        build.get('uuid', ''),
                        build.get('result', '---'),
                        build.get('log_url', ''),
                        build.get('voting', False)
                    )

    session.close()


def main() -> None:
    while True:
        print('Updating results database...')
        update()
        print('Done.')
        time.sleep(60 * 60 * 6)
