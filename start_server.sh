#!/bin/bash
celery -A app.tasks.periodical_tasks -B --loglevel=INFO
