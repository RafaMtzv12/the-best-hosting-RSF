"""Objetos compartidos por toda la aplicación.

db es el ORM (SQLAlchemy): con él las tablas se manejan como clases de Python.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
