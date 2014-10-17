#============================ adjust path =====================================
import subprocess
import sys
import json
import shlex
import time
import os

if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here,'..','Mercator'))

#============================ imports =========================================

import threading

import OpenCli
import MoteHandler

#============================ body ============================================

def run_command(command_line):
  args = shlex.split(command_line)
  p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  return p.communicate()

if __name__ == "__main__":
  # Create a experiment
  command_line = 'experiment-cli load -f "9714.json" -l "01bsp_radio_tx_prog.ihex" -l "01bsp_radio_rx_prog.ihex"'
  out, err = run_command(command_line)
  data = json.loads(out)
  experiment_id = data["id"]
  print "ID:", data["id"]

  # Check if experiment is running
  while True:
    print "Checking experiment %f state..." % experiment_id
    command_line = 'experiment-cli get -i %f -s' % experiment_id
    out, err = run_command(command_line)
    data = json.loads(out)
    state = data["state"]
    print "State: %s" % state
    if state == "Running":
      break
    else:
      time.sleep(0.2)

  # Connect with every motes in experiment
