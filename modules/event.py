from configobj import ConfigObj
from sqlalchemy import * 
from types import *

import random
import re 
import sys 
import time

class event:
  def __init__(self,core):
    self.core    = core
    self.load()

  def load(self):
    try:
      config = ConfigObj('/etc/puby/commands.conf')
    except Exception,e:
      print 'configuration error: '+str(e)

    self.cmds = {}   
    for i in config['cmd']:
      if isinstance(config['cmd'][i],ListType):
        for x in config['cmd'][i]:
          self.cmds[x] = i
      else:
        self.cmds[i] = i

  def handler(self,source,line):
    cakeObj(self.core,source,line)

class cakeObj:
  def __init__(self,core,source,line):
    self.core = core
    self.source = source
    type = self.whatCake(line)
    
    if type is None:
      return self.core.log.debug("Caketype is None, None meaning nonexistant")
    
    line = self.extractIngredient(line,type)
    
    self.dsn = self.core.config['database']['type']+'://'+ \
               self.core.config['database']['user']+':'+ \
               self.core.config['database']['pass']+'@'+ \
               self.core.config['database']['host']+'/'+ \
               self.core.config['database']['name']
    self.db = create_engine(self.dsn,pool_size=100,pool_recycle=7200)
    self.metadata = BoundMetaData(self.db) 
 
    self.inject(line,type)

  def extractIngredient(self,line,type):
    if re.match('(image|url)',type):
      return re.search('(https?|ftp)://.+',line).group().rsplit(' ') [0] 
    else:
      return re.compile('^\!('+type+')\ ').sub('',line) 

  def whatCake(self,line):
    for i in self.core.event.cmds:
      if re.match('^\!'+i,line):
        return i
      elif re.search('(https?|ftp)://.+',line):
        if re.match('.+(jpe?g|png|gif|tiff|bmp)$',line, re.I):
          return 'image'
        else:
          return 'url'

  def inject(self,line,type):
    self.core.log.debug("cake-inject --source=%s --type=%s --line=%s" % (self.source,type,line))
    
    try:
      pie = Table('pie',self.metadata,autoload=True)
    except Exception,e:
      self.core.log.warning('CakeObj: '+str(Exception)+str(e))

    ins = pie.insert(values={
      'is_it_yummeh' : random.randint(0,42),
      'content'      : line,
      'type'         : type,
      'who_did_it'   : self.source,
      'timestamp'    : int(time.time())})
