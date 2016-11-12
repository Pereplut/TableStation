# -*- coding: utf8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///tableStation.db'
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'tableStation.db')
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
