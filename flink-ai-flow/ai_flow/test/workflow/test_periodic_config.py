# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import unittest
from datetime import datetime, timedelta
from pytz import timezone
from ai_flow.workflow.periodic_config import PeriodicConfig


class TestPeriodicConfig(unittest.TestCase):

    def test_periodic_config_start_date(self):
        pc = PeriodicConfig(trigger_config={'start_date': "2020,1,1,1,1,1,"})
        self.assertEqual(datetime(2020, 1, 1, 1, 1, 1), pc.get_start_date())
        pc = PeriodicConfig(trigger_config={'start_date': "2020,1,1,,,,Asia/Chongqing"})
        self.assertEqual(datetime(2020, 1, 1, tzinfo=timezone('Asia/Chongqing')), pc.get_start_date())

    def test_periodic_config_interval(self):
        pc = PeriodicConfig(trigger_config={'interval': "1,,,"})
        self.assertEqual(timedelta(days=1), pc.get_interval())
        pc = PeriodicConfig(trigger_config={'interval': "1,1,1,1"})
        self.assertEqual(timedelta(days=1, hours=1, minutes=1, seconds=1), pc.get_interval())

    def test_periodic_config_from_dict(self):
        pc = PeriodicConfig.from_dict({'start_date': "2020,1,1,1,1,1,", 'cron': '* * * * * * *'})
        self.assertEqual(datetime(2020, 1, 1, 1, 1, 1), pc.get_start_date())

        pc = PeriodicConfig.from_dict({'start_date': "2020,1,1,1,1,1,", 'interval': '1,1,1,1'})
        self.assertEqual(timedelta(days=1, hours=1, minutes=1, seconds=1), pc.get_interval())

    def test_periodic_config_to_dict(self):
        pc = PeriodicConfig.from_dict({'start_date': "2020,1,1,1,1,1,", 'cron': '* * * * * * *'})
        data = PeriodicConfig.to_dict(pc)
        self.assertEqual('2020,1,1,1,1,1,', data.get('start_date'))
        self.assertEqual('* * * * * * *', data.get('cron'))

        pc = PeriodicConfig.from_dict({'start_date': "2020,1,1,1,1,1,", 'interval': '1,1,1,1'})
        data = PeriodicConfig.to_dict(pc)
        self.assertEqual('1,1,1,1', data.get('interval'))


if __name__ == '__main__':
    unittest.main()
