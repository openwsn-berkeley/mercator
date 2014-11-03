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

class Mercator(object):

  def __init__(self):
    self.motes  = {}
    self.iotlab = True
    self.dataLock   = threading.Lock()
    self.experiment_id = 0

  def create_experiment(self):
    # Create a new experiment
    command_line = 'experiment-cli load -f "../bin/experiment/experiment.json" -l "../../firmware/03oos_mercator_prog.ihex"'
    out, err = run_command(command_line)
    data = json.loads(out)
    self.experiment_id = data["id"]
    print "New Experiment ID:", self.experiment_id

  def get_experiment_state(self):
    command_line = 'experiment-cli get -i {0} -s'.format(self.experiment_id)
    out, err = run_command(command_line)
    data = json.loads(out)
    return data["state"]

  def wait_for_running(self):
    # Check if experiment is running
    while True:
      print "Checking experiment {0} state...".format(self.experiment_id)
      state = self.get_experiment_state()
      print "State: %s" % state
      if state == "Running":
        def check_state():
          if (self.get_experiment_state() != "Running"):
            print "The experiment has stoped"
            sys.exit()
        set_interval(check_state, 1)
        return
      else:
        time.sleep(1)

  def get_motes(self):
    command = "experiment-cli get -i {0} -r".format(self.experiment_id)
    out, err = run_command(command)
    data = json.loads(out)
    self.motes = {}
    for mote in data["items"]:
      motename = mote["network_address"].split('.')[0]
      mote["motename"] = motename
      self.motes[motename] = mote

  def connect_motes(self):
    self.get_motes()
    for motename, mote in self.motes.iteritems():
      with self.dataLock:
        print "Connecting {0}".format(motename)
        mote["connection"] = MoteHandler.MoteHandler(motename, iotlab=self.iotlab)

  # Puts the last mote to TX and the rest to RX
  def send_TX_and_RX(self, freq, txpower, transctr, txnumpk, txifdur, txlength, txfillbyte):
    c = 0
    # get last mote mac address
    self.srcmote = self.motes.items()[-1][0]
    self.motes[self.srcmote]["connection"].send_REQ_ST()
    while self.motes[self.srcmote]["connection"].mac == []:
          time.sleep(0.2)
    for motename, mote in self.motes.iteritems():
      if motename == self.srcmote:
        print "TX: {0}".format(motename)
        mote["connection"].send_REQ_TX(freq, txpower, transctr, txnumpk, txifdur, txlength, txfillbyte)
      else:
        print "RX: {0}".format(motename)
        mote["connection"].send_REQ_RX(freq, self.srcmac, transctr, txlength, txfillbyte)
      c += 1

  def stop_TX_and_RX(self):
    for motename, mote in self.motes.iteritems():
      mote["connection"].send_REQ_IDLE()

#=== Function that executes a function 'func' every 'sec' seconds

def set_interval(func, sec):
  def func_wrapper():
    set_interval(func, sec)
    func()
  t = threading.Timer(sec, func_wrapper)
  t.start()
  return t

#=== Function that executes a linux command and returns the result.

def run_command(command_line):
  args = shlex.split(command_line)
  p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  return p.communicate()

if __name__ == '__main__':
  mercator = Mercator()
  mercator.create_experiment()
  mercator.wait_for_running()
  mercator.connect_motes()
  mercator.send_TX_and_RX(26, 0, 0x0a, 30, 1000, 100, 0x0b)