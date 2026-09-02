"""Shared extension instances.

Kept in their own module so they can be imported without creating a circular
dependency on the application factory.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
