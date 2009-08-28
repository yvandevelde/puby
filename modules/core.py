from configobj import ConfigObj
import os
import sys

class core:
  def __init__(self):
    self.loaded = []
    try:
      self.config = ConfigObj('/etc/puby/system.conf')
    except Exception,e:
      print 'Configuration error: %s (%d)' % (e,Exception)
   
    os.setegid(int(self.config['sys']['gid'])) 
    os.seteuid(int(self.config['sys']['uid']))

    for i in self.config['modules']:
      if not i in self.loaded:
        self.load(i)
    
    if 'log' in self.loaded:
      self.log.debug("Loaded modules %s" % str(self.loaded))

  def load(self,i):
    exec "from %s import %s" % (i,i)
    exec "self.%s = %s(self)" % (i,i)
    self.loaded.append(i)


