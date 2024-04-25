from models.database import db, UserSessions
from datetime import datetime, timedelta
from sqlalchemy import select, func

seconds_threshold = 10

def get_count(q):
    count_q = q.statement.with_only_columns(func.count()).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count

def count_recent_visits(streaming_name):
    time_limit = datetime.utcnow() - timedelta(seconds=seconds_threshold)
    stat = db.session.query(UserSessions.id).filter(UserSessions.last_visit >= time_limit, UserSessions.streaming_name ==streaming_name)
    return get_count(stat)

def get_or_create_session(footprint, streaming_name):
    session = UserSessions.query.filter_by(footprint=footprint).first()
    if session:
        now = datetime.utcnow()
        five_seconds_ago = now - timedelta(seconds=5)
        if check:=session.last_visit <= five_seconds_ago:
            session.last_visit = now
            db.session.commit()
    elif not session:
        new_session = UserSessions(footprint=footprint, streaming_name=streaming_name, last_visit=datetime.utcnow())
        db.session.add(new_session)
        db.session.commit()
        return new_session
    return session