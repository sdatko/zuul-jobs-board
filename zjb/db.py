#!/usr/bin/env python3

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


def set_notes(ID, text) -> None:
    with session() as s:
        s.query(Build).filter(Build.id == ID).update({'notes': text})
        s.commit()
