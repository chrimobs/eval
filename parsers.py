# -*- coding: utf-8 -*-

import datetime as dt
import formatdefs


class DstatTimeParser:

   def __init__(self, year):
       if not year:
           self._year = dt.date.today().year
       else:
           self._year = year

   @property
   def year(self):
       return self._year

   def parse(self, dstring):
       return dt.datetime.strptime(dstring, formatdefs.dstat_timef).replace(self.year)

