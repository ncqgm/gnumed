#IdMgr_i.py implements  IdMgr interface
import PersonIdService__POA

import CORBA
import CosNaming
import ResolveIdComponent
from StartIdentificationComponent import StartIdentificationComponent
import PersonIdTraits
from PlainConnectionProvider import *
import HL7Version2_3

import threading, thread, traceback, time

from  PersonIdTestUtils import *
from SqlTraits import *

class IdMgr_i (PersonIdService__POA.IdMgr, StartIdentificationComponent):

	def __init__(self, dsn=None, ProviderClass = PlainConnectionProvider, limit = MAX_TRAITS_RETURNED ):
		self.connector = ProviderClass(dsn)
		self.limit = limit
		self._optimize_calltime_by_sql_prepare()

	def _optimize_calltime_by_sql_prepare(self):
		con = self.connector.getConnection()


	def find_or_register_ids( profiles):
		
