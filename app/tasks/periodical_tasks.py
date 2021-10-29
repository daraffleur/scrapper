from celery.schedules import crontab

from celery_app import app

from app.tasks import make_contact, check_contact


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # """Send invites to the contacts if the email info is absent (executes every day at 11:05 a.m.)"""
    # sender.add_periodic_task(
    #     crontab(hour=11, minute=5),
    #     make_contact.s(),
    # )

    # """Check if the email info of a contact is available (executes every day at 19:05 a.m.)"""
    # sender.add_periodic_task(
    #     crontab(hour=19, minute=5),
    #     check_contact.s(),
    # )

    sender.add_periodic_task(10.0, check_contact.s(), name="executes every 200 seconds")
