#!/usr/bin/env python
import os
from cyber_role import celery, init_app

app = init_app()
app.test_request_context().push()