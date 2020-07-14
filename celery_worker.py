#!/usr/bin/env python
import os
from cyber_role import celery, init_app

# Fichero que nos sirve para la inicializacion del celery worker
app = init_app()
app.test_request_context().push()