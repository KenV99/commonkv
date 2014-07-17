#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 KenV99
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import time
import re
import xbmc
debug = True
remote = False
if debug:
    if remote:
        import sys
        sys.path.append(r'C:\\Users\\Ken User\\AppData\\Roaming\\XBMC\\addons\\script.ambibox\\resources\\lib\\'
                        r'pycharm-debug.py3k\\')
        import pydevd
        pydevd.settrace('192.168.1.103', port=51234, stdoutToServer=True, stderrToServer=True)
    else:
        sys.path.append('C:\Program Files (x86)\JetBrains\PyCharm 3.1.3\pycharm-debug-py3k.egg')
        import pydevd
        pydevd.settrace('localhost', port=51234, stdoutToServer=True, stderrToServer=True)

def round_down_to_half_hour(xtime):
    """
    Returns a string with the time rounded down to the nearest half-hour in format h:mm am
    Example:
        now_time = time.localtime()
        r_time = round_down_to_half_hour(now_time)
        > 7:30 am
    @param xtime: the time to be converted in either string YYYYmmddHHMMSS format or a time.struct_time typed obj
    @type xtime: str
    @type xtime: time.struct_time
    @rtype: str
    """
    if type(xtime) is str:
        try:
            xxtime = time.strptime(xtime, '%Y%m%d%H%M%S')
        except:
            return None
    elif type(xtime) is time.struct_time:
        xxtime = xtime
    else:
        return None
    if xxtime.tm_min <= 30:
        newmin = ':00'
    else:
        newmin = ':30'
    xformat = xbmc.getRegion('time').replace(':%S', '').replace('%H%H', '%H')
    tmp = time.strftime(xformat, xxtime).lower()
    ret = re.sub(':..', newmin, tmp)
    return ret

##########################################################################################

__killme__ = False
import urllib2
import types
def download_file(url, obj2rcv_status, int_percentofjob, int_block_size):
    """
    Downloads data/file from url and returns it as a string
    Sends status updates as a percent done to obj2rcv_status.setstatus() - obj must have this fxn
    Needs to be run at a separate thread/process if using the global flag __killme__ to abort
    @param url: the url to download from - no error checking done
    @type url: str
    @param obj2rcv_status: the object to receive status updates, set to None if not using
    @type obj2rcv_status: function
    @param int_percentofjob: the percent to show when 100% job done, set to 100 if this is complete job; useful if
                             the download is only one part of a larger job
    @type int_percentofjob: int
    @param int_block_size: the block size to use during download ie. 2048, 4096, 8192
    @type int_block_size: int
    @rtype: str
    """
    global __killme__
    try:
         data = ''
         u = urllib2.urlopen(url)
         meta = u.info()
         file_size = int(meta.getheaders("Content-Length")[0])
         file_size_dl = 0
         block_sz = int_block_size
         while True and not __killme__:
             mbuffer = u.read(block_sz)
             if not mbuffer:
                 break
             file_size_dl += len(mbuffer)
             data += mbuffer
             state = int(file_size_dl * float(int_percentofjob) / file_size)
             if obj2rcv_status is not None:
                obj2rcv_status.setstatus(state)
         else:
             if __killme__:
                 raise AbortDownload('downloading')
         del u
         return data
    except AbortDownload, e:
     __killme__ = False
     if e.value == 'downloading':
         try:
            if u is not None:
                del u
            return None
         except:
            return None

class AbortDownload(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

##########################################################################################

import threading

class GenericThread(threading.Thread):
    def __init__(self, xtarget, threadname):
        threading.Thread.__init__(self, name=threadname)
        self.xtarget = xtarget

    def start(self):
        threading.Thread.start(self)

    def run(self):
        self.xtarget()

    def stop(self):
        self.join(2000)

########################################################################################

import math


class Stream_stats():
    """
    Uses numerical methods to calculate ongoing mean and variance without holding large sums in memory
    Con is for small sample sizes, there may be some inaccuracy
    After creating an instance, call update() with the varaible you want stats on
    Reset variance (reset_var) can be called, keeping last mean as starting point
    In addition, init_mean can be used if a previous mean is known
    """

    def __init__(self):
        self.last_mean = None
        self.last_var = 0.0
        self.n = 0

    def update(self, x):
        self.n += 1
        if self.last_mean is None:
            self.last_mean = x
        alpha = 1.0/self.n
        m = self.last_mean + (x - self.last_mean)/self.n
        v = ((self.n - 1) * self.last_var + (x - self.last_mean) * (x - m)) * alpha
        self.last_mean = m
        self.last_var = v

    def mean(self):
        return self.last_mean

    def var(self):
        return self.last_var

    def sd(self):
        return math.sqrt(self.last_var)

    def count(self):
        return self.n

    def reset_var(self):
        self.last_var = 0.0
        self.n = 0

    def init_mean(self, m):
        self.last_mean = m
