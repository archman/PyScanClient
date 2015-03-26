import time
from scan import *

  
client = ScanClient('localhost')
print client

print client.serverInfo()
 
cmds = [ Comment('Hello'), Set('motor_x', 10) ]

# Optionally, request a simulation that shows
# how 'Include' and 'Loop' commands get expanded.
simulation = client.simulate(cmds)
print simulation

# Submit scan for execution
id = client.submit(cmds, 'My First Scan')
print id

# Could poll scanInfo until scan is done
info = client.scanInfo(id)
print info

# Shortcut for waiting until it'd done
info = client.waitUntilDone(id)
print info


# A submitted scan can be paused or even aborted
id = client.submit(cmds, 'Not sure about this one')

client.pause(id)
print client.scanInfo(id)

client.resume(id)
print client.scanInfo(id)

client.abort(id)
print client.scanInfo(id)


# get commands

# get data

# delete