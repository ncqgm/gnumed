import time
from handler_popup import *


class timed_button_behaviour:
	def __init__(self, instruction= "re do in ", interval = 4):
		self.clear_time = 0
		self.interval = interval
		self.instruction = instruction
		self.command = None

	def check_time( self):
		timing = time.time()
		print timing, self.clear_time, self.interval
		if timing - self.clear_time  > self.interval:
			self.clear_time = timing
			msg =  " ".join((\
" ARE YOU SURE?\n click outside to close this message, then ,\n click button again within",\
		str(self.interval) , " seconds to perform" , \
 		self.get_message()))

			handler_popup(self.owner.panel,msg)
			
			return None
		return self.action()

	def get_command(self):
		return self.command

	def action(self):
		return None

	def get_message(self):
		return self.instruction

	


class ClearCommand:
	def __init__(self, model_ui_handle):
		self.model = model_ui_handle.model
		self.old_model = {}
		self.ui_handle = model_ui_handle
	
	def Do(self):
		self.old_model.update( self.model)
		for x in self.model.keys():
			self.model[x] = ""
		self.ui_handle.update_ui(self.model)
	
	def UnDo(self):
		self.ui_handle.update_ui( self.old_model)


	def GetName(self):
		return "Clear Edit Area"

class timed_clear_map_behaviour(timed_button_behaviour):
		def __init__( self, owner, instruction = "", interval =4):
			timed_button_behaviour.__init__(self, instruction, interval)
			self.owner = owner

		def action(self):
			self.command = ClearCommand(self.owner)
			self.command.Do()
			return self.command	

		def get_message(self):
			if self.instruction == "":
				return "Clearing of fields."
			return self.instruction
