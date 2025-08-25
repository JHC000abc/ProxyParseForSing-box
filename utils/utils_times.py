# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: JHC000abc@gmail.com
@file: utils_times.py
@time: 2025/8/25 16:35 
@desc: 

"""
import pytz
from datetime import datetime


class UtilsTimes:
    """

    """
    @staticmethod
    def get_format_utc_8(format="%Y-%m-%d %H:%M:%S"):
        """

        :param format:
        :return:
        """
        beijing_tz = pytz.timezone('Asia/Shanghai')
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        beijing_now = utc_now.astimezone(beijing_tz)
        return beijing_now.strftime(format)



