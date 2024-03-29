#!/usr/bin/env python3

import os
from typing import Optional

import requests

from zjb import config
from zjb.utils import match


api_base = os.path.join(config.api_url, 'tenant', config.api_tenant)

builds_endpoint = os.path.join(api_base, 'builds')
jobs_endpoint = os.path.join(api_base, 'jobs')
pipelines_endpoint = os.path.join(api_base, 'pipelines')
projects_endpoint = os.path.join(api_base, 'projects')


def get_branches(filter: list) -> list:
    # NOTE(sdatko): There is no easy way to get list of tracked branches
    #               from Zuul, or at least I was unable to find anything
    #               better than processing the builds list (which is not
    #               really reliable, as we cannot get all builds easily).
    #               For the time being, lets have this coming from filter.
    return filter


def get_jobs(filter: Optional[list] = None) -> list:
    resp = requests.get(jobs_endpoint)
    jobs = [job.get('name') for job in resp.json()]

    if filter:
        jobs = [job for job in jobs
                if any(match(job, job_specifier)
                       for job_specifier in filter)]

    return jobs


def get_pipelines(filter: Optional[list] = None) -> list:
    resp = requests.get(pipelines_endpoint)
    pipelines = [pipeline.get('name') for pipeline in resp.json()]

    if filter:
        pipelines = [pipeline for pipeline in pipelines
                     if any(match(pipeline, pipeline_specifier)
                            for pipeline_specifier in filter)]

    return pipelines


def get_projects(filter: Optional[list] = None) -> list:
    resp = requests.get(projects_endpoint)
    projects = [project.get('name') for project in resp.json()]

    if filter:
        projects = [project for project in projects
                    if any(match(project, project_specifier)
                           for project_specifier in filter)]

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
