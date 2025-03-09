# from datetime import datetime
#
# original_now = datetime.now()
#
#
# def reformatted_now_f(*args,**kwargs):
#     now = datetime.now(*args,**kwargs)
#     return now.replace(microsecond=0)
#
#
# datetime.now = reformatted_now_f()

import datetime as original_datetime

original_datetime_class = original_datetime.datetime


class ReformatDatetime(original_datetime.datetime):
    @classmethod
    def now(cls, *args, **kwargs):
        now = super().now(*args, **kwargs)
        return now.replace(microsecond=0)


class DatetimeWrapper:
    @classmethod
    def __getattr__(self, item):
        return getattr(original_datetime, item)

    def now(self, *args, **kwargs):
        return ReformatDatetime.now(*args,**kwargs)


datetime = DatetimeWrapper()