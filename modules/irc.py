import irclib
import os
import time

class irc:
  def __init__(self,core):
    self.core      = core
    self.channels  = [] 
    self.irc       = irclib.IRC()
    self.server    = self.irc.server()

    self.server.connect(self.core.config['irc']['server'], 
                        int(self.core.config['irc']['port']), 
                        self.core.config['irc']['name'])
    self.irc.add_global_handler("all_events", self._dispatcher, -10)
      
    for channel in [self.core.config['irc']['channels']]:
      self.join('#%s' % channel)
      self.channels.append(channel)

  def _dispatcher(self,connection,event):
    method = "on_" + event.eventtype()
    if hasattr(self,method):
      getattr(self,method)(connection,event)

  def join(self,channel=None):
    self.core.log.debug("Joined channel %s" % channel)
    self.server.join(channel)    

  def on_kick(self,connection,event):
    source = event.source().split("!")[0]
    [kicked,kicker] = event.arguments()
    self.core.log.debug("%s got kicked by %s" % (kicked,kicker))
    self.join(event.target())

  def on_ping(self,connection,event):
    self.core.log.debug("PING? PONG!")
    connection.pong(event.target()) 

  def on_pubmsg(self,connection,event):
    source = event.source().split("!")[0]
    line = event.arguments()[0] 
    self.core.log.debug("received pubmsg from %s : %s" % (source,line))
    self.core.event.handler(source,line)

  def on_privmsg(self,connection,event):
    source = event.source().split("!")[0]
    line = event.arguments()[0]
    self.core.log.debug("received privmsg from %s : %s" % (source,line))
    self.core.event.handler(source,line)  
    connection.privmsg(source,'no functions bound to event: %s' % line)   

  def start(self):
    try:
      self.irc.process_forever()
    except KeyboardInterrupt,e:
      self.core.log.warning(str(e)+str(KeyboardInterrupt))
