"""
data objects for organization. Hoping to use the helper class to act as Facade
for aggregated data objects ? with validation rules. 
re-used working code form gmClinItem and followed Script Module layout of gmEMRStructItems.


license: GPL
"""
#============================================================
__version__="0.1"
from Gnumed.pycommon import gmExceptions, gmLog, gmPG
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.business import gmClinItem

_log = gmLog.gmDefLog
if __name__ == '__main__':
	        _log.SetAllLogLevels(gmLog.lData)
		_log.Log(gmLog.lInfo, __version__)

cmd_fetch_payload = "select * from %s where id=%%s"
class cOrgCategory(gmClinItem.cClinItem):

	_cmd_init_store_payload="""insert into org_category( description) values (%(description)s)"""
	_cmd_fetch_payload = cmd_fetch_payload % "org_category"
	_cmds_store_payload=[ """select 1 from org_category where id = %(id)s for update""", """update org_category set description=%(description)s where id=%(id)s"""]
	_updatable_fields= ["description"]
	_list_all="select * from org_category"

class  cOrganization(gmClinItem.cClinItem):
	_cmd_fetch_payload = cmd_fetch_payload % "org"
	_cmd_init_store_payload= "insert into org( id_category, description) values( %(id_category)s, %(description)s )"
	_cmds_store_payload= ["""select 1 from org where id = %(id)s for update""",
		   """update organization set id_category=(%id_category)s , description =(%description)s where id=%(id)s"""]

	_updatable_fields= ["id_category", "description"]


class cCommTypes(gmClinItem.cClinItem):
	_cmd_fetch_payload = cmd_fetch_payload % "enum_comm_types"

	_cmd_init_store_payload="insert into enum_comm_types(description) values( %(description)s)"
	
	_cmds_store_payload=["select 1 from enum_comm_types where id = %(id)s for update",
		"""update enum_comm_types set description= %(description)s where id=%(id)s"""]
	_updatable_fields=["description"]
	

class cCommChannel(gmClinItem.cClinItem):
	_cmd_fetch_payload = cmd_fetch_payload % "comm_channel"
	_cmd_init_store_payload= "insert into comm_channel(id_type, url) values ( %(id_type)s, %(url)s )"
	_cmds_store_payload=["select 1 from comm_channel where id = %(id)s for update",
			"update comm_channel set id_type= %(id_type)s, set url=%(url)s where id=%(id)s"]
	_updatable_fields=["id_type", "url"]
	
class cLnkPersonOrgAddress(gmClinItem.cClinItem):
	_cmd_fetch_payload = cmd_fetch_payload % "lnk_person_org_address"
	_cmd_init_store_payload="""
		insert into lnk_person_org_address(
		id_identity, id_address , id_type, id_org ,id_occupation, address_source)
		values
		( %(id_identity)s, %(id_address)s , %(id_type)s, %(id_org)s , 
		%(id_occupation)s, %(address_source)s )
		"""
	_cmds_store_payload=["select 1 lnk_person_org_address from where id = %(id)s for update",
	"""update lnk_person_org_address set 
	id_identity = %(id_identity)s,
	id_address = %(id_address)s,
	id_type = %(id_type)s,
	id_org =%(id_org)s ,
	id_occupation  =  %(id_occupation)s,
	address_source = %(address_source)s 
	where id=%(id)s"""]

	_updatable_fields=["id_identity", "id_address" , "id_type", 
		"id_org" ,"id_occupation", "address_source"]


		


	
class cOrgHelper:
	def __init__(self):
		pass

	def set(self, name, office, department, address, memo, category, phone, fax, email,mobile):			pass

	def get_name_office_department_address_memo_category_phone_fax_email_mobile(self): 
		return []

	def findAllOrganizations():
		return []

	def findAllOrganizationPKAndName():
		return [ (0,"") ]

	def load(self, pk):
		return

	def save(self):
		return


if __name__== "__main__":
        _log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
		
	for n in xrange(1,8):
		print "Test Fetch of CommType , id=",n
		commType = cCommTypes(aPK_obj=n)
		print commType
		fields = commType.get_fields()
		for f in fields:
			print f,":", commType[f]
		print "updateable : ", commType.get_updatable_fields()
		print "-"*50
		

	
	
