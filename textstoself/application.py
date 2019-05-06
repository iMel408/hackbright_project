from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, g
)
from textstoself.auth import login_required
from textstoself.model import *

bp = Blueprint('application', __name__)


@bp.route('/user/<int:id>')
def user_page(id):
    """show user page/info"""

    user = User.query.get(id)
    active_job = Job.query.filter_by(user=user, active=True).first()

    if active_job:
        events = Event.query.filter_by(job_id=active_job.id, msg_type='inbound').all()

        return render_template('app/user.html', user=user, job=active_job, events=events)

    return render_template('app/user.html', user=user)


@bp.route('/<int:id>/jobs')
def user_jobs(id):
    """show user page/info"""

    user = User.query.get(id)
    jobs = Job.query.filter_by(user=user).all()

    return render_template('app/jobs.html', user=user, jobs=jobs)







