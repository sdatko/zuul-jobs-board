#!/usr/bin/env python3

from collections import defaultdict
import os

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker

from zjb import config
from zjb.utils import any_match


dbfile = os.path.abspath(os.path.expanduser(config.db_file))
engine = create_engine('sqlite:///' + dbfile)
session = sessionmaker(bind=engine)

Base = declarative_base()


class Build(Base):
    __tablename__ = 'results'
    __table_args__ = (
        UniqueConstraint('project', 'branch', 'pipeline', 'job'),
    )

    id = Column(Integer, primary_key=True)
    project = Column(String)
    branch = Column(String)
    pipeline = Column(String)
    job = Column(String)
    uuid = Column(String)
    date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String)
    URL = Column(String)
    voting = Column(Boolean)
    notes = Column(String, nullable=True)
    updated = Column(DateTime(timezone=True),
                     default=func.now(),
                     onupdate=func.now())

    def __init__(self, project, branch, pipeline, job,
                 uuid, date, status, URL, voting, notes=None):
        self.project = project
        self.branch = branch
        self.pipeline = pipeline
        self.job = job
        self.uuid = uuid
        self.date = date
        self.status = status
        self.URL = URL
        self.voting = voting
        self.notes = notes

    @classmethod
    def create_or_update(cls, session, project, branch, pipeline, job,
                         uuid, date, status, URL, voting):
        instance = session.query(cls).filter_by(project=project,
                                                branch=branch,
                                                pipeline=pipeline,
                                                job=job).one_or_none()

        if instance:
            instance.uuid = uuid
            instance.date = date
            instance.status = status
            instance.URL = URL
            instance.voting = voting
        else:
            instance = cls(project, branch, pipeline, job,
                           uuid, date, status, URL, voting)
            session.add(instance)

        session.commit()
        return instance


Base.metadata.create_all(engine)


def get_last_update() -> str:
    with session() as s:
        last_update = (
            s.query(Build.updated)
             .order_by(Build.updated.desc())
             .first()
        )

    if last_update:
        last_update = last_update[0]

    return last_update


def get_result(ID: int) -> dict:
    with session() as s:
        result = s.query(Build).filter(Build.id == ID).one_or_none()

    return result


def get_results_for_view(filters: dict) -> dict:
    with session() as s:
        pipelines = [v for (v, ) in s.query(Build.pipeline).distinct()]
        projects = [v for (v, ) in s.query(Build.project).distinct()]
        branches = [v for (v, ) in s.query(Build.branch).distinct()]
        jobs = [v for (v, ) in s.query(Build.job).distinct()]

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

                        build = s.query(Build).filter(
                            Build.project == project,
                            Build.branch == branch,
                            Build.pipeline == pipeline,
                            Build.job == job,
                        ).one_or_none()

                        if build:
                            results[pipeline][project].append(build.__dict__)
                        else:
                            results[pipeline][project].append(None)

    return results, headers


def get_missing_notes() -> dict:
    results = []

    with session() as s:
        for result in (s.query(Build)
                        .filter(Build.notes.is_(None),
                                Build.status.not_in(['SUCCESS', '---']))
                        .order_by(Build.project, Build.branch,
                                  Build.job, Build.pipeline).all()):
            results.append(result.__dict__)

    return results


def get_obsolete_notes() -> dict:
    results = []

    with session() as s:
        for result in (s.query(Build)
                        .filter(Build.notes.is_not(None),
                                Build.status.in_(['SUCCESS', '---']))
                        .order_by(Build.project, Build.branch,
                                  Build.job, Build.pipeline).all()):
            results.append(result.__dict__)

    return results


def get_results_with_notes() -> dict:
    results = []

    with session() as s:
        for result in (s.query(Build)
                        .filter(Build.notes.is_not(None))
                        .order_by(Build.project, Build.branch,
                                  Build.job, Build.pipeline).all()):
            results.append(result.__dict__)

    return results


def set_notes(ID, text) -> None:
    text = text.strip()
    if not text:
        text = None

    with session() as s:
        s.query(Build).filter(Build.id == ID).update({'notes': text})
        s.commit()
