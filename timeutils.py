
from datetime import datetime, date, timedelta
import pytz
from config import Config

def now_local():
    tz = pytz.timezone(Config.TIMEZONE)
    return datetime.now(tz)

def days_ahead(d):
    return (d - date.today()).days

def is_before_cutoff(target_date, hours_cutoff):
    # booking/cancellation must be >= cutoff hours before the target midnight
    # We treat the 'service day' as the target_date. Cutoff is 24h before 00:00 of target_date.
    from datetime import datetime
    tz = pytz.timezone(Config.TIMEZONE)
    cutoff_dt = tz.localize(datetime.combine(target_date, datetime.min.time())) - timedelta(hours=hours_cutoff)
    return now_local() <= cutoff_dt
