# coding=utf-8

import typing
from dataclasses import dataclass
from flask.testing import FlaskClient
from flask_jwt import current_identity
from banking import api

# define tests
