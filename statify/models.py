"""
@file           models.py
@author         Max Legrand
@description    Model to store token authentication
@lastUpdated    11/18/2020
"""

from django.db import models


class Auth(models.Model):
    token = models.JSONField()
