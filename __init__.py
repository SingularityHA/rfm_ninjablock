# Singularity
# Copyright (C) 2014 Internet by Design Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import input_to_mqtt
import output_to_433mhz
from multiprocessing import Process
import time

def signal_handler(signal, frame):
        print "Got CTL+C"
        time.sleep(1)
        for job in jobs:
                job.terminate()
                job.join()
        sys.exit(0)

def main():
	try:
		jobs = []
                p = Process(target=input_to_mqtt.main)
                p2 = Process(target=output_to_433mhz.main)
                jobs.append(p)
                jobs.append(p2)
                p.start()
                p2.start()
                signal.signal(signal.SIGINT, signal_handler)
        except KeyboardInterrupt:
                signal_handler(None, None)
		pass
