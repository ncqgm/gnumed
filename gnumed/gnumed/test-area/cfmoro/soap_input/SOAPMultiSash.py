#----------------------------------------------------------------------
# Name:		 multisash
# Purpose:	  Multi Sash control
#
# Author:	   Gerrit van Dyk
#
# Created:	  2002/11/20
# Version:	  0.1
# RCS-ID:	   $Id: SOAPMultiSash.py,v 1.27 2005-02-09 20:19:58 cfmoro Exp $
# License:	  wxWindows licensie
# GnuMed customization (Karsten, Carlos): 
#		Disabled vertical MultiSizer and MultiCreator (cMultiSashLeaf)
#		An instance of controller object is passed with DefaultChildClass,
#		to allow problem and emr connection with each SOAP editor control,
#		and also controlling duplicate entries per health issue.
#----------------------------------------------------------------------

from wxPython.wx import *

MV_HOR = 0
MV_VER = not MV_HOR

SH_SIZE = 5 
CR_SIZE = SH_SIZE * 3


from Gnumed.wxpython import gmSOAPWidgets

#============================================================
class cSOAPMultiSash(wxWindow):
	"""
	Main multisash widget. Dynamically displays a stack of child widgets,
	out SOAP input widgets.	
	"""
	def __init__(self, content_factory = None, *_args,**_kwargs):
		"""
		Creates a new instance of cSOAPMultiSash
		
		@param content_factory Factory funtion responsible of instantiating the
		leaf's content widget		
		"""
		print "----------------------------------------"
		print self.__class__.__name__, "-> __init__()", id(self)
		apply(wxWindow.__init__, (self,) + _args, _kwargs)		
		self.splitter = cMultiSashSplitter (
			root_multi_sash_win = self,
			parent = self,
			pos = wxPoint(0,0),
			size = self.GetSize(),
			content_factory = content_factory
		)
		self.content_factory = content_factory
		self.focussed_leaf = self.splitter.primary_leaf
		# FIXME temporary workaround to detect the first editor
		#       so just the current leaf content has to be replaced
		#       If not, we have 2 closers for 1 editor	
		self.is_first_leaf = True
		EVT_SIZE(self,self._on_size)
	#---------------------------------------------
	# event handling
	#---------------------------------------------
	def _on_size(self,evt):
		self.splitter.SetSize(self.GetSize())
	#---------------------------------------------
	# public API
	#---------------------------------------------
	def get_focussed_leaf(self):
		return self.focussed_leaf
	#---------------------------------------------
	def deselect_all_leafs(self):
		self.splitter.deselect_leafs()
	#---------------------------------------------
	def Clear(self):
#		self.SetController(None)
		old = self.splitter
		self.splitter = cMultiSashSplitter (
			root_multi_sash_win = self,
			parent = self,
			pos = wxPoint(0,0),
			size = self.GetSize()
		)
		old.Destroy()
		self.splitter.OnSize(None)
	#---------------------------------------------
#	def SetController(self, data_provider):
#		"""
#		Set SOAP multisash controller widget. Controller is responsible
#		for managing SOAP input widgets lifecycle, control cehcking and
#		action handling.
#		
#		@type data_provider: gmSOAPInput.cSOAPInputPanel instance
#		@param data_provider: SOAP input panel controller object
#		"""
#		self.data_provider = data_provider
#		self.splitter.DefaultChildChanged()
#
#	def GetController(self):
#		"""
#		Retrieve SOAP input panel controller object
#		"""
#		return self.data_provider
#============================================================
class cMultiSashSplitter(wxWindow):
	"""
	Basic split windows container of the multisash widget.
	Has references to two leafs or splitted windows (SOAP input widgets)
	"""
	def __init__(self, root_multi_sash_win, parent, pos, size, prev_leaf = None, content_factory = None):
		"""
		Creates a new instance of cMultiSashSplitter
		
		@param content_factory Factory funtion responsible of instantiating the
		leaf's content widget		
		"""		
		print "----------------------------------------"
		print self.__class__.__name__, "-> __init__()", id(self)
		wxWindow.__init__ (
			self,
			id = -1,
			parent = parent,
			pos = pos,
			size = size,
			style = wxCLIP_CHILDREN
		)
		self.root_multi_sash_win = root_multi_sash_win
		self.content_factory = content_factory
		if prev_leaf is None:
			print "prev_leaf is None"
			self.primary_leaf = cMultiSashLeaf (
				root_multi_sash_win = self.root_multi_sash_win,
				parent = self,
				pos = wxPoint(0,0),
				size = self.GetSize(),
				content_factory = content_factory
			)
		else:
			print "prev_leaf available"
			self.primary_leaf = prev_leaf
			self.primary_leaf.Reparent(self)
			self.primary_leaf.MoveXY(0,0)

		self.secondary_leaf = None
		self.direction = None

		EVT_SIZE(self,self.OnSize)

		print "primary leaf:", self.primary_leaf.__class__.__name__, id(self.primary_leaf)
		print "secondary leaf:", self.secondary_leaf.__class__.__name__, id(self.secondary_leaf)
	#--------------------------------------------------------
	def deselect_leafs(self):
#		if isinstance(self.GetParent(), cMultiSashSplitter):
#			print "Parent [%s], parent.secondary_leaf[%s]" % (self.GetParent(), self.secondary_leaf)
		if self.primary_leaf is not None:
			self.primary_leaf.deselect()
		if self.secondary_leaf is not None:
			self.secondary_leaf.deselect()
	#--------------------------------------------------------
	def DefaultChildChanged(self):
		if not self.secondary_leaf:
			self.primary_leaf.DefaultChildChanged()
	#--------------------------------------------------------
	def AddLeaf(self, direction, caller, pos):
		"""
		Construct a new leaf (split window, SOAP input widget)
		"""
		print '%s (%s) -> AddLeaf()' % (self.__class__.__name__, id(self))
		print "primary leaf: ", self.primary_leaf.__class__.__name__, id(self.primary_leaf)
		print "secondary leaf:", self.secondary_leaf.__class__.__name__, id(self.secondary_leaf)
		
		# FIXME temporary workaround to detect the first editor
		#       so just the current leaf content has to be replaced
		#       If not, we have 2 closers for 1 editor
		if self.root_multi_sash_win.is_first_leaf == True:
			print "creating first leaf, just replace" 
			self.root_multi_sash_win.is_first_leaf = False
			return		
			
		if self.secondary_leaf is None:
			print "adding secondary_leaf to *this* splitter instance"
			self.direction = direction
			w,h = self.GetSizeTuple()
			if direction == MV_HOR:
				print 'Direction MV_HOR'
				x,y = (pos,0)
				w1,h1 = (w-pos,h)
				w2,h2 = (pos,h)
			else:
				print 'Direction MV_VER'
				x,y = (0,pos)
				w1,h1 = (w,h-pos)
				w2,h2 = (w,pos)

			print "creating secondary_leaf (= new cMultiSashSplitter)"
			self.secondary_leaf = cMultiSashSplitter (
				root_multi_sash_win = self.root_multi_sash_win,
				parent = self,
				pos = wxPoint(x,y),
				size = wxSize(w1,h1),
				content_factory = self.content_factory
			)
			self.primary_leaf.SetSize(wxSize(w2,h2))
			self.secondary_leaf.resize()
			print "primary leaf: ", self.primary_leaf.__class__.__name__, id(self.primary_leaf)
			print "secondary leaf:", self.secondary_leaf.__class__.__name__, id(self.secondary_leaf)
			return True

#		caller = cMultiSashSplitter (
#			root_multi_sash_win = self.root_multi_sash_win,
#			parent = self,
#			pos = caller.GetPosition(),
#			size = caller.GetSize(),
#			prev_leaf = caller
#		)
#		caller.AddLeaf(direction, caller, pos)
		print "adding new splitter holding two leafs"
		print "caller:", caller
		new_splitter = cMultiSashSplitter (
			root_multi_sash_win = self.root_multi_sash_win,
			parent = self,
			pos = caller.GetPosition(),
			size = caller.GetSize(),
			prev_leaf = caller,
			content_factory = self.content_factory
		)
		if caller == self.primary_leaf:
#			self.primary_leaf = cMultiSashSplitter (
			self.primary_leaf = new_splitter
			self.primary_leaf.AddLeaf(direction, caller, pos)
		else:
#			self.secondary_leaf = cMultiSashSplitter (
			self.secondary_leaf = new_splitter
			self.secondary_leaf.AddLeaf(direction, caller, pos)
		print "primary leaf: ", self.primary_leaf.__class__.__name__, id(self.primary_leaf)
		print "secondary leaf:", self.secondary_leaf.__class__.__name__, id(self.secondary_leaf)
	#--------------------------------------------------------
	def DestroyLeaf(self, caller):
		"""
		Destroys selected leaf, both by controller's remove button or by
		leaf's destroyer element
		"""
		print "----------------------------------------"
		print self.__class__.__name__, "-> DestroyLeaf()"
		print "primary leaf: ", self.primary_leaf.__class__.__name__, id(self.primary_leaf)
		print "secondary leaf:", self.secondary_leaf.__class__.__name__, id(self.secondary_leaf)
#		# can't be sure is selected when user clicked destroyer element, so...
#		caller.Select()
		parent = self.GetParent()	   # Another splitview
		# root of the splitter hierarchy ?
		if parent == self.root_multi_sash_win:
			print "splitter is top level"
			if caller == self.primary_leaf:
				print "closing primary leaf"
				# destroy old leaf, eg primary
				self.primary_leaf.cleanup()
#				soap_widget = self.primary_leaf.content.soap_panel
#				soap_issue = soap_widget.GetProblem()
#				# FIXME: do this elsewhere
#				if len(self.primary_leaf.content.data_provider.get_managed_episodes()) > 0 and not soap_widget.IsSaved():
#				if not soap_widget.IsSaved():
#					self.primary_leaf.content.data_provider.get_managed_episodes().remove(soap_issue['pk_episode'])
				# FIXME: necessary ?
				self.primary_leaf.deselect()
#				if self.secondary_leaf is None:
#					#soap_widget.ResetAndHide()
#					self.primary_leaf.content.MakeEmptyWidget()
#					#self.primary_leaf.creatorHor.Hide()
#					#self.primary_leaf.closer.Hide()
#				else:
				if self.secondary_leaf is not None:
#					self.primary_leaf.Destroy()
					self.primary_leaf = self.secondary_leaf
					self.secondary_leaf = None
			else:
				print "closing secondary leaf"
				self.secondary_leaf.cleanup()
#				soap_issue = self.secondary_leaf.content.soap_panel.GetProblem()
#				if not self.secondary_leaf.content.soap_panel.IsSaved():
#					self.secondary_leaf.content.data_provider.get_managed_episodes().remove(soap_issue['pk_episode'])
				self.secondary_leaf.deselect()
#				self.secondary_leaf.Destroy()
				self.secondary_leaf = None
			self.primary_leaf.SetSize(self.GetSize())
			self.primary_leaf.Move(self.GetPosition())
		else:
			w,h = self.GetSizeTuple()
			x,y = self.GetPositionTuple()
			print "splitter is NOT top level"
			if caller == self.primary_leaf:
				print "closing primary leaf, moving secondary leaf onto parent"
				self.primary_leaf.cleanup()
				# move our secondary leaf onto our parent
				if parent.primary_leaf == self:
					parent.primary_leaf = self.secondary_leaf
				else:
					parent.secondary_leaf = self.secondary_leaf
				self.secondary_leaf.Reparent(parent)
				self.secondary_leaf.SetDimensions(x,y,w,h)
#				soap_issue = self.primary_leaf.content.soap_panel.GetProblem()
#				if not self.primary_leaf.content.soap_panel.IsSaved():
#					self.primary_leaf.content.data_provider.get_managed_episodes().remove(soap_issue['pk_episode'])
#				print "Removing: %s" % (soap_issue['pk_episode'])
			else:
				print "closing secondary leaf, moving primary leaf onto parent"
				self.secondary_leaf.cleanup()
				if parent.primary_leaf == self:
					parent.primary_leaf = self.primary_leaf
				else:
					parent.secondary_leaf = self.primary_leaf
				self.primary_leaf.Reparent(parent)
				self.primary_leaf.SetDimensions(x,y,w,h)
#				soap_issue = self.secondary_leaf.content.soap_panel.GetProblem()
#				if not self.secondary_leaf.content.soap_panel.IsSaved():
#					self.secondary_leaf.content.data_provider.get_managed_episodes().remove(soap_issue['pk_episode'])
#				print "Removing: %s"%(soap_issue['pk_episode'])
			self.primary_leaf = None
			self.secondary_leaf = None
			self.Destroy()
	#--------------------------------------------------------
	def CanSize(self,side,view):
		if self.SizeTarget(side,view):
			return True
		return False

	def SizeTarget(self,side,view):
		if self.direction == side and self.secondary_leaf and view == self.primary_leaf:
			return self
		parent = self.GetParent()
		if parent != self.root_multi_sash_win:
			return parent.SizeTarget(side,self)
		return None

	def SizeLeaf(self,leaf,pos,side):
		if self.direction != side:
			return
		if not (self.primary_leaf and self.secondary_leaf):
			return
		if pos < 10: return
		w,h = self.GetSizeTuple()
		if side == MV_HOR:
			if pos > w - 10: return
		else:
			if pos > h - 10: return
		if side == MV_HOR:
			self.primary_leaf.SetDimensions(0,0,pos,h)
			self.secondary_leaf.SetDimensions(pos,0,w-pos,h)
		else:
			self.primary_leaf.SetDimensions(0,0,w,pos)
			self.secondary_leaf.SetDimensions(0,pos,w,h-pos)

	def resize(self):
		self.OnSize(None)

	def OnSize(self,evt):
		if not self.secondary_leaf:
			self.primary_leaf.SetSize(self.GetSize())
			self.primary_leaf.resize()
			return
		v1w,v1h = self.primary_leaf.GetSizeTuple()
		v2w,v2h = self.secondary_leaf.GetSizeTuple()
		v1x,v1y = self.primary_leaf.GetPositionTuple()
		v2x,v2y = self.secondary_leaf.GetPositionTuple()
		w,h = self.GetSizeTuple()

		if v1x != v2x:
			ratio = float(w) / float((v1w + v2w))
			v1w *= ratio
			v2w = w - v1w
			v2x = v1w
		else:
			v1w = v2w = w

		if v1y != v2y:
			ratio = float(h) / float((v1h + v2h))
			v1h *= ratio
			v2h = h - v1h
			v2y = v1h
		else:
			v1h = v2h = h

		self.primary_leaf.SetDimensions(v1x,v1y,v1w,v1h)
		self.secondary_leaf.SetDimensions(v2x,v2y,v2w,v2h)
		self.primary_leaf.resize()
		self.secondary_leaf.resize()
#============================================================
class cMultiSashLeaf(wxWindow):
	"""A leaf represent a split window, one instance of our SOAP input widget.
	"""
	def __init__(self, root_multi_sash_win, parent, pos, size, content_factory=None):
		"""
		Creates a new instance of cSOAPMultiLeaf
		
		@param content_factory Factory funtion responsible of instantiating the
		leaf's content widget		
		"""		
		print "----------------------------------------"
		print self.__class__.__name__, "-> __init__()", id(self)
		wxWindow.__init__ (
			self,
			id = -1,
			parent = parent,
			pos = pos,
			size = size,
			style = wxCLIP_CHILDREN
		)
		self.root_multi_sash_win = root_multi_sash_win
		# only horizontal sizer is allowed, to display leafs in a stack-like way
		self.sizerHor = MultiSizer(self, MV_HOR)
#		self.content = cMultiSashLeafContent(self, self.root_multi_sash_win.data_provider)
#		self.content = cMultiSashLeafContent(self, episode = self.root_multi_sash_win.data_provider.get_selected_episode())
		self.content = None
		self.__content_factory = content_factory
		print "content:", self.content
		# only horizontal creator is allowed
		self.creatorHor = MultiCreator(self,MV_HOR)
		self.closer = MultiCloser(self)
#		# hide creator and closer when a unique leaf is shown
#		if self.root_multi_sash_win.data_provider is None or \
#			len(self.root_multi_sash_win.data_provider.get_managed_episodes()) == 0:
#			self.creatorHor.Hide()
#			self.closer.Hide()

		# event handling
		EVT_SET_FOCUS(self, self._on_set_focus)
		EVT_CHILD_FOCUS(self, self._on_set_focus)
		EVT_SIZE(self, self._on_size)

		# FIXME: needed ?
#		self.__set_focus()
	#-------------------------------------
	# event handlers
	#-------------------------------------
	def _on_set_focus(self, evt):
		self.__set_focus()
	#-------------------------------------
	def _on_size(self, evt):
		self.__resize(evt)
	#-------------------------------------
	# external API
	#-------------------------------------
	def cleanup(self):
		"""Called when about to close down."""
		if self.content is None:
			return
		self.content.cleanup()
	#-------------------------------------
	def deselect(self):
		if self.content is None:
			return
		self.content.deselect()
	#-------------------------------------
	def resize(self):
		self.__resize()
	#-------------------------------------
	def AddLeaf(self, direction, pos):
		"""Add a new widget to the stack.

		called from: splitter.AddLeaf()
		"""
		print '%s (%s) -> AddLeaf()' % (self.__class__.__name__, id(self))
		# first editor, replace EmptyWidget
#		if isinstance(self.content.soap_panel, EmptyWidget):
#			print "Creating first leaf..."
#			self.content.MakeSoapEditor()
#			return

		if self.content is None:
			self.content = self.__content_factory(parent=self)

		if pos < 10: return
		w, h = self.GetSizeTuple()
		if direction == MV_VER:
			if pos > h - 10: return
		else:
			if pos > w - 10: return
		# this is recursive
		self.GetParent().AddLeaf(direction, self, pos)
	#-------------------------------------
	# internal helpers
	#-------------------------------------
	def __resize(self, evt=None):
		self.closer.OnSize(evt)
		if self.content is not None:
			self.content.resize()
		self.creatorHor.OnSize(evt)
		self.sizerHor.OnSize(evt)
	#-------------------------------------
	def __set_focus(self):
		# update ui
		self.root_multi_sash_win.deselect_all_leafs()
		if self.content is not None:
			self.content.select()
		self.root_multi_sash_win.focussed_leaf = self
#		self.Refresh()
	#-------------------------------------
	#-------------------------------------
	def GetSOAPPanel(self):
		"""
		Retrieve split window's SOAP input widget
		"""
		return self.content.soap_panel

	def DefaultChildChanged(self):
		"""
		Set main controller
		"""
		self.content.SetNewController(self.root_multi_sash_win.data_provider)

	#-----------------------------------------------------
	def DestroyLeaf(self):
		self.GetParent().DestroyLeaf(self)

	def SizeTarget(self,side):
		return self.GetParent().SizeTarget(side,self)

	def CanSize(self,side):
		return self.GetParent().CanSize(side,self)

#============================================================
# FIXME: can we maybe get rid of this class by moving it into cMultiSashLeaf ?
class cMultiSashLeafContentMixin:
	def __init__(self):
		"""Create the contents for a leaf in the stack.

		@param parent - Widget's parent
		@type parent - MultiSashLeaf widget

		@param data_provider - Widget that register changes in the leaf,
		provide them with data for the ui and perform some basic funcional
		checks and behaviour control
		@type data_provider - gmSoapPlugins.cMultiSashedSoapPanel
		"""
		if not isinstance(self, wxWindow):
			 raise ValueError, 'parent of %s MUST be a xWindow instance' % self.__class__.__name__

		self.Move(wxPoint(0,0))
		w, h = self.__calc_size()
		self.SetSize(wxSize(w,h))
		self.SetWindowStyle(style = wxCLIP_CHILDREN | wxSUNKEN_BORDER)

		# basic variables
#		self.soap_panel = None
#		self.data_provider = data_provider
		self.__normalColour = self.GetBackgroundColour()

		# child widget creation
#		episode = data_provider.get_selected_episode()
#		if episode is None:
#			self.MakeEmptyWidget()
#		else:
#			self.MakeSoapEditor(episode)
#		# event handling
#		EVT_SET_FOCUS(self, self._on_set_focus)
#		EVT_CHILD_FOCUS(self, self._on_set_focus)

	#-------------------------------------
	# external API
	#-------------------------------------
	def resize(self):
		w, h = self.__calc_size()
		self.SetDimensions(0,0,w,h)
		w, h = self.GetClientSizeTuple()
		self.SetSize(wxSize(w-4,h-4))
	#-------------------------------------
	def deselect(self):
		self.SetBackgroundColour(self.__normalColour)
#		self.Refresh()
	#-------------------------------------
	def select(self):
		self.SetBackgroundColour(wxColour(255,255,0)) # Yellow
	#-------------------------------------
	def cleanup(self):
		print '[%s]: programmer forgot to override cleanup()' % self.__class__.__name__
	#-------------------------------------
	# internal helpers
	#-------------------------------------
	def __calc_size(self):
		parent = self.GetParent()
		w,h = parent.GetSizeTuple()
		w -= SH_SIZE
		h -= SH_SIZE
		return (w,h)


#	#-------------------------------------
#	# event handlers
#	#-------------------------------------
#	def _on_set_focus(self, evt):
#		self.__set_focus()
#	#-------------------------------------
#	# internal helpers
#	#-------------------------------------
#	def __set_focus(self):
#		# update ui
#		self.GetParent().root_multi_sash_win.UnSelect()
#		self.SetBackgroundColour(wxColour(255,255,0)) # Yellow
#		self.Refresh()
#		# update selected leaf in controller
#		self.data_provider.set_selected_leaf(self.GetParent(), self.soap_panel)

#	def UnSelect(self):
#		"""
#		Deselect currently selected leaf and reflect the change in controller.
#		"""
#		if not self.data_provider is None:
#			pass
#			#self.data_provider.set_selected_leaf(None)
#		self.SetBackgroundColour(self.normalColour)
#		self.Refresh()

#	def Select(self):
#		"""
#		Select leaf and reflect the change in controller.
#		"""
#		self.__set_focus()

#	def OnSize(self,evt):
#		w,h = self.__calc_size(self.GetParent())
#		self.SetDimensions(0,0,w,h)
#		w,h = self.GetClientSizeTuple()
#		self.soap_panel.SetSize(wxSize(w-4,h-4))

#	def SetNewController(self,data_provider):
#		"""
#		Configure main controller
#		
#		@param: multisash main controller
#		@type: gmSOAPInput.cSOAPInputPanel
#		"""
#		self.data_provider = data_provider
#		self.__set_focus()

	def MakeSoapEditor(self, episode = 'missing episode'):
		"""
		Destroys current widget (usually EmptyWidget, becouse no soap editors are
		displayed at startup - no episode selected)
		"""
#		self.SetBackgroundColour(self.normalColour)
		if self.soap_panel is not None:
			self.soap_panel.Destroy()
#			self.soap_panel = None
#		self.soap_panel = gmSOAPWidgets.cResizingSoapPanel(self, self.data_provider.get_selected_episode())
		self.soap_panel = gmSOAPWidgets.cResizingSoapPanel(self, episode)
		self.soap_panel.MoveXY(2,2)
#		self.__set_focus()
		self.OnSize(None)

	def MakeEmptyWidget(self):
		"""
		Destroys current widget (usually soap editor, becouse no soap editors
		displayed, eg. all removed)
		"""
#		self.SetBackgroundColour(self.normalColour)
		if self.soap_panel is not None:
			self.soap_panel.Destroy()
#			self.soap_panel = None
		self.soap_panel = EmptyWidget(self)
		self.soap_panel.MoveXY(2,2)
#		self.__set_focus()
		self.OnSize(None)
#============================================================
# FIXME: can we maybe get rid of this class by moving it into cMultiSashLeaf ?
class cMultiSashLeafContent(wxWindow):
	"""
	Widget that encapsulate contents of a leaf or split window.
	We have one SOAP input widget and a reference to the controller
	"""
#	def __init__(self, parent, data_provider):
	def __init__(self, parent, episode=None):
		"""
		Create the contents for a leaf in the stack
		
		@param parent - Widget's parent
		@type parent - MultiSashLeaf widget

		@param data_provider - Widget that register changes in the leaf,
		provide them with data for the ui and perform some basic funcional
		checks and behaviour control
		@type data_provider - gmSoapPlugins.cMultiSashedSoapPanel
		"""
		w, h = self.CalcSize(parent)
		wxWindow.__init__(
			self,
			id = -1,
			parent = parent,
			pos = wxPoint(0,0),
			size = wxSize(w,h),
			style = wxCLIP_CHILDREN | wxSUNKEN_BORDER
		)

		# basic variables
		self.soap_panel = None
#		self.data_provider = data_provider
#		self.normalColour = self.GetBackgroundColour()

		# child widget creation
#		episode = data_provider.get_selected_episode()
		if episode is None:
			self.MakeEmptyWidget()
		else:
			self.MakeSoapEditor(episode)

#		# event handling
#		EVT_SET_FOCUS(self, self._on_set_focus)
#		EVT_CHILD_FOCUS(self, self._on_set_focus)

#	#-------------------------------------
#	# event handlers
#	#-------------------------------------
#	def _on_set_focus(self, evt):
#		self.__set_focus()
#	#-------------------------------------
#	# internal helpers
#	#-------------------------------------
#	def __set_focus(self):
#		# update ui
#		self.GetParent().root_multi_sash_win.UnSelect()
#		self.SetBackgroundColour(wxColour(255,255,0)) # Yellow
#		self.Refresh()
#		# update selected leaf in controller
#		self.data_provider.set_selected_leaf(self.GetParent(), self.soap_panel)

#	def UnSelect(self):
#		"""
#		Deselect currently selected leaf and reflect the change in controller.
#		"""
#		if not self.data_provider is None:
#			pass
#			#self.data_provider.set_selected_leaf(None)
#		self.SetBackgroundColour(self.normalColour)
#		self.Refresh()

#	def Select(self):
#		"""
#		Select leaf and reflect the change in controller.
#		"""
#		self.__set_focus()

	def CalcSize(self, parent):
		w,h = parent.GetSizeTuple()
		w -= SH_SIZE
		h -= SH_SIZE
		return (w,h)

	def OnSize(self,evt):
		w,h = self.CalcSize(self.GetParent())
		self.SetDimensions(0,0,w,h)
		w,h = self.GetClientSizeTuple()
		self.soap_panel.SetSize(wxSize(w-4,h-4))

#	def SetNewController(self,data_provider):
#		"""
#		Configure main controller
#		
#		@param: multisash main controller
#		@type: gmSOAPInput.cSOAPInputPanel
#		"""
#		self.data_provider = data_provider
#		self.__set_focus()

#	def MakeSoapEditor(self, episode = 'missing episode'):
#		"""
#		Destroys current widget (usually EmptyWidget, becouse no soap editors are
#		displayed at startup - no episode selected)
#		"""
#		self.SetBackgroundColour(self.normalColour)
#		if self.soap_panel is not None:
#			self.soap_panel.Destroy()
#			self.soap_panel = None
#		self.soap_panel = gmSOAPWidgets.cResizingSoapPanel(self, self.data_provider.get_selected_episode())
#		self.soap_panel = gmSOAPWidgets.cResizingSoapPanel(self, episode)
#		self.soap_panel.MoveXY(2,2)
#		self.__set_focus()
#		self.OnSize(None)

	def MakeEmptyWidget(self):
		"""
		Destroys current widget (usually soap editor, becouse no soap editors
		displayed, eg. all removed)
		"""
#		self.SetBackgroundColour(self.normalColour)
		if self.soap_panel is not None:
			self.soap_panel.Destroy()
#			self.soap_panel = None
		self.soap_panel = EmptyWidget(self)
		self.soap_panel.MoveXY(2,2)
#		self.__set_focus()
		self.OnSize(None)
#============================================================
class MultiSizer(wxWindow):
	"""
	Leaf's sash bar
	"""
	def __init__(self,parent,side):
		self.side = side
		x,y,w,h = self.CalcSizePos(parent)
		wxWindow.__init__(self,id = -1,parent = parent,
						  pos = wxPoint(x,y),
						  size = wxSize(w,h),
						  style = wxCLIP_CHILDREN)

		self.px = None				  # Previous X
		self.py = None				  # Previous Y
		self.isDrag = False			 # In Dragging
		self.dragTarget = None		  # View being sized

		EVT_LEAVE_WINDOW(self,self.OnLeave)
		EVT_ENTER_WINDOW(self,self.OnEnter)
		EVT_MOTION(self,self.OnMouseMove)
		EVT_LEFT_DOWN(self,self.OnPress)
		EVT_LEFT_UP(self,self.OnRelease)

	def CalcSizePos(self,parent):
		pw,ph = parent.GetSizeTuple()
		if self.side == MV_HOR:
			x = CR_SIZE + 2
			y = ph - SH_SIZE
			w = pw - CR_SIZE - SH_SIZE - 2
			h = SH_SIZE
		else:
			x = pw - SH_SIZE
			y = CR_SIZE + 2 + SH_SIZE
			w = SH_SIZE
			h = ph - CR_SIZE - SH_SIZE - 4 - SH_SIZE # For Closer
		return (x,y,w,h)

	def OnSize(self,evt):
		x,y,w,h = self.CalcSizePos(self.GetParent())
		self.SetDimensions(x,y,w,h)

	def OnLeave(self,evt):
		self.SetCursor(wxStockCursor(wxCURSOR_ARROW))

	def OnEnter(self,evt):
		if not self.GetParent().CanSize(not self.side):
			return
		if self.side == MV_HOR:
			self.SetCursor(wxStockCursor(wxCURSOR_SIZENS))
		else:
			self.SetCursor(wxStockCursor(wxCURSOR_SIZEWE))

	def OnMouseMove(self,evt):
		if self.isDrag:
			DrawSash(self.dragTarget,self.px,self.py,self.side)
			self.px,self.py = self.ClientToScreenXY(evt.m_x,evt.m_y)
			self.px,self.py = self.dragTarget.ScreenToClientXY(self.px,self.py)
			DrawSash(self.dragTarget,self.px,self.py,self.side)
		else:
			evt.Skip()

	def OnPress(self,evt):
		self.dragTarget = self.GetParent().SizeTarget(not self.side)
		if self.dragTarget:
			self.isDrag = True
			self.px,self.py = self.ClientToScreenXY(evt.m_x,evt.m_y)
			self.px,self.py = self.dragTarget.ScreenToClientXY(self.px,self.py)
			DrawSash(self.dragTarget,self.px,self.py,self.side)
			self.CaptureMouse()
		else:
			evt.Skip()

	def OnRelease(self,evt):
		if self.isDrag:
			DrawSash(self.dragTarget,self.px,self.py,self.side)
			self.ReleaseMouse()
			self.isDrag = False
			if self.side == MV_HOR:
				self.dragTarget.SizeLeaf(self.GetParent(),
										 self.py,not self.side)
			else:
				self.dragTarget.SizeLeaf(self.GetParent(),
										 self.px,not self.side)
			self.dragTarget = None
		else:
			evt.Skip()

#============================================================
class MultiCreator(wxWindow):
	"""
	Sash bar's creator element
	"""
	def __init__(self,parent,side):
		self.side = side
		x,y,w,h = self.CalcSizePos(parent)
		wxWindow.__init__(self,id = -1,parent = parent,
						  pos = wxPoint(x,y),
						  size = wxSize(w,h),
						  style = wxCLIP_CHILDREN)

		self.px = None				  # Previous X
		self.py = None				  # Previous Y
		self.isDrag = False		   # In Dragging

		EVT_LEAVE_WINDOW(self,self.OnLeave)
		EVT_ENTER_WINDOW(self,self.OnEnter)
		EVT_MOTION(self,self.OnMouseMove)
		EVT_LEFT_DOWN(self,self.OnPress)
		EVT_LEFT_UP(self,self.OnRelease)
		EVT_PAINT(self,self.OnPaint)

	def CalcSizePos(self,parent):
		pw,ph = parent.GetSizeTuple()
		if self.side == MV_HOR:
			x = 2
			y = ph - SH_SIZE
			w = CR_SIZE
			h = SH_SIZE
		else:
			x = pw - SH_SIZE
			y = 4 + SH_SIZE			 # Make provision for closer
			w = SH_SIZE
			h = CR_SIZE
		return (x,y,w,h)

	def OnSize(self,evt):
		x,y,w,h = self.CalcSizePos(self.GetParent())
		self.SetDimensions(x,y,w,h)

	def OnLeave(self,evt):
		self.SetCursor(wxStockCursor(wxCURSOR_ARROW))

	def OnEnter(self,evt):
		if self.side == MV_HOR:
			self.SetCursor(wxStockCursor(wxCURSOR_HAND))
		else:
			self.SetCursor(wxStockCursor(wxCURSOR_POINT_LEFT))

	def OnMouseMove(self,evt):
		if self.isDrag:
			parent = self.GetParent()
			DrawSash(parent,self.px,self.py,self.side)
			self.px,self.py = self.ClientToScreenXY(evt.m_x,evt.m_y)
			self.px,self.py = parent.ScreenToClientXY(self.px,self.py)
			DrawSash(parent,self.px,self.py,self.side)
		else:
			evt.Skip()

	def OnPress(self,evt):
		self.isDrag = True
		parent = self.GetParent()
		self.px,self.py = self.ClientToScreenXY(evt.m_x,evt.m_y)
		self.px,self.py = parent.ScreenToClientXY(self.px,self.py)
		DrawSash(parent,self.px,self.py,self.side)
		self.CaptureMouse()

	def OnRelease(self,evt):
		print "Released creator... activating currently selected problem"
		if self.isDrag:
			parent = self.GetParent()
			DrawSash(parent,self.px,self.py,self.side)
			self.ReleaseMouse()
			self.isDrag = False
			# activate currently selected problem
			parent.content.data_provider.activate_selected_problem()
		else:
			evt.Skip()

	def OnPaint(self,evt):
		dc = wxPaintDC(self)
		dc.SetBackground(wxBrush(self.GetBackgroundColour(),wxSOLID))
		dc.Clear()

		highlight = wxPen(wxSystemSettings_GetSystemColour(
			wxSYS_COLOUR_BTNHIGHLIGHT),1,wxSOLID)
		shadow = wxPen(wxSystemSettings_GetSystemColour(
			wxSYS_COLOUR_BTNSHADOW),1,wxSOLID)
		black = wxPen(wxBLACK,1,wxSOLID)
		w,h = self.GetSizeTuple()
		w -= 1
		h -= 1

		# Draw outline
		dc.SetPen(highlight)
		dc.DrawLine(0,0,0,h)
		dc.DrawLine(0,0,w,0)
		dc.SetPen(black)
		dc.DrawLine(0,h,w+1,h)
		dc.DrawLine(w,0,w,h)
		dc.SetPen(shadow)
		dc.DrawLine(w-1,2,w-1,h)

#============================================================
class MultiCloser(wxWindow):
	"""
	Sash bar's destroyer element
	"""
	def __init__(self,parent):
		x,y,w,h = self.CalcSizePos(parent)
		wxWindow.__init__(self,id = -1,parent = parent,
						  pos = wxPoint(x,y),
						  size = wxSize(w,h),
						  style = wxCLIP_CHILDREN)

		self.down = False
		self.entered = False

		EVT_LEFT_DOWN(self,self.OnPress)
		EVT_LEFT_UP(self,self.OnRelease)
		EVT_PAINT(self,self.OnPaint)
		EVT_LEAVE_WINDOW(self,self.OnLeave)
		EVT_ENTER_WINDOW(self,self.OnEnter)

	def OnLeave(self,evt):
		self.SetCursor(wxStockCursor(wxCURSOR_ARROW))
		self.entered = False

	def OnEnter(self,evt):
		self.SetCursor(wxStockCursor(wxCURSOR_BULLSEYE))
		self.entered = True

	def OnPress(self,evt):
		self.down = True
		evt.Skip()

	def OnRelease(self,evt):
		if self.down and self.entered:
			self.GetParent().DestroyLeaf()
		else:
			evt.Skip()
		self.down = False

	def OnPaint(self,evt):
		dc = wxPaintDC(self)
		dc.SetBackground(wxBrush(wxRED,wxSOLID))
		dc.Clear()

	def CalcSizePos(self,parent):
		pw,ph = parent.GetSizeTuple()
		x = pw - SH_SIZE
		w = SH_SIZE
		h = SH_SIZE + 2
		y = 1
		return (x,y,w,h)

	def OnSize(self,evt):
		x,y,w,h = self.CalcSizePos(self.GetParent())
		self.SetDimensions(x,y,w,h)


#============================================================
class EmptyWidget(wxWindow):
	"""
	Empty default widget
	"""
	def __init__(self,parent):
		wxWindow.__init__(self,parent,-1, style = wxCLIP_CHILDREN)
		
		
#============================================================
def DrawSash(win,x,y,direction):
	"""
	Sash drawing method
	"""
	
	dc = wxScreenDC()
	dc.StartDrawingOnTopWin(win)
	bmp = wxEmptyBitmap(8,8)
	bdc = wxMemoryDC()
	bdc.SelectObject(bmp)
	bdc.DrawRectangle(-1,-1,10,10)
	for i in range(8):
		for j in range(8):
			if ((i + j) & 1):
				bdc.DrawPoint(i,j)

	brush = wxBrush(wxColour(0,0,0))
	brush.SetStipple(bmp)

	dc.SetBrush(brush)
	dc.SetLogicalFunction(wxXOR)

	body_w,body_h = win.GetClientSizeTuple()

	if y < 0:
		y = 0
	if y > body_h:
		y = body_h
	if x < 0:
		x = 0
	if x > body_w:
		x = body_w

	if direction == MV_HOR:
		x = 0
	else:
		y = 0

	x,y = win.ClientToScreenXY(x,y)

	w = body_w
	h = body_h

	if direction == MV_HOR:
		dc.DrawRectangle(x,y-2,w,4)
	else:
		dc.DrawRectangle(x-2,y,4,h)

	dc.EndDrawingOnTop()
#============================================================
if __name__ == '__main__':
	print "no test code, seemed to compile successfully"
#============================================================
# $Log: SOAPMultiSash.py,v $
# Revision 1.27  2005-02-09 20:19:58  cfmoro
# Making soap editor made factory function outside SOAPMultiSash
#
# Revision 1.26  2005/02/08 11:36:11  ncq
# - lessen reliance on implicit callbacks
# - make things more explicit, eg Pythonic
#
# Revision 1.25  2005/02/02 21:43:12  cfmoro
# Adapted to recent gmEMRStructWidgets changes. Multiple editors can be created
#
# Revision 1.24  2005/01/29 13:26:48  ncq
# - some cleanup
#
#
#----------------------------
# revision 1.23
# date: 2005/01/28 18:37:17;  author: cfmoro;  state: Exp;  lines: +2 -2
# Removed idx problem number. Begin to link issues w/o episodes with episode selector
#----------------------------
# revision 1.22
# date: 2005/01/18 19:51:13;  author: cfmoro;  state: Exp;  lines: +9 -4
# UI improvements: resizing of the widget in LeafContent, yellow background while replacing the child widget
#----------------------------
# revision 1.21
# date: 2005/01/18 19:23:16;  author: cfmoro;  state: Exp;  lines: +55 -44
# More cleanup. Soap editor created on double click. Clear and remove funtions working
#----------------------------
# revision 1.20
# date: 2005/01/17 19:56:10;  author: cfmoro;  state: Exp;  lines: +18 -2
# Initial soap editor creation for a selected episode. No editors are until a problem is selected and new button is pressed
#----------------------------
# revision 1.19
# date: 2005/01/16 20:30:54;  author: ncq;  state: Exp;  lines: +17 -11
# - some reformatting
#----------------------------
# revision 1.18
# date: 2005/01/15 20:37:17;  author: cfmoro;  state: Exp;  lines: +19 -10
# Initial adaptation to cProblem. Some comments for development
#----------------------------
# revision 1.17
# date: 2005/01/13 14:30:35;  author: ncq;  state: Exp;  lines: +226 -188
#- lot's of renaming/cleanup
#----------------------------
# revision 1.16
# date: 2004/12/31 16:44:21;  author: cfmoro;  state: Exp;  lines: +4 -4
# Separation of classes in appropiate modules. Note categories are dynamic
#----------------------------
# revision 1.15
# date: 2004/12/16 17:59:38;  author: cfmoro;  state: Exp;  lines: +719 -719
# Encapsulation syntax fixed (_ replaced by __). Using tab indentation, in consistency with the rest of gnumed files
#----------------------------
# revision 1.14
# date: 2004/12/03 16:34:44;  author: cfmoro;  state: Exp;  lines: +3 -1
# Controlled destroying last split using closer element and code clean up
#----------------------------
# revision 1.13
# date: 2004/12/03 16:22:25;  author: cfmoro;  state: Exp;  lines: +80 -76
# Implemented save action. Tons of code cleans more...
#----------------------------
# revision 1.12
# date: 2004/12/03 00:03:32;  author: cfmoro;  state: Exp;  lines: +188 -135
# Code clean up and comments. Ready for begin  to join to cClinicalRecord
#----------------------------
# revision 1.11
# date: 2004/11/27 21:16:25;  author: cfmoro;  state: Exp;  lines: +3 -3
# Begin code clean and bu fixing stage
#----------------------------
# revision 1.10
# date: 2004/11/27 20:42:48;  author: cfmoro;  state: Exp;  lines: +26 -4
# Action buttons are logically enabled/disabled. Creator and closer are logically hidden/shown
#----------------------------
# revision 1.9
# date: 2004/11/27 18:25:12;  author: cfmoro;  state: Exp;  lines: +27 -32
# Alert dialogs when no problem/soap is selected and some action is fired. Some code clean. Minor ui improvements
#----------------------------
# revision 1.8
# date: 2004/11/26 06:19:38;  author: cfmoro;  state: Exp;  lines: +12 -2
# The user cannot entre more than one SOAP note per health issue. A warning is displayed
#----------------------------
# revision 1.7
# date: 2004/11/24 22:46:52;  author: cfmoro;  state: Exp;  lines: +12 -4
# UI improvements: auto-selection of new split window; fixed heading size of refresh
#----------------------------
# revision 1.6
# date: 2004/11/23 00:26:25;  author: cfmoro;  state: Exp;  lines: +12 -4
# Properly handled unique/none soap note
#----------------------------
# revision 1.5
# date: 2004/11/21 20:10:14;  author: cfmoro;  state: Exp;  lines: +5 -14
# Clearer way for obtaining selected leaf
#----------------------------
# revision 1.4
# date: 2004/11/21 19:21:00;  author: cfmoro;  state: Exp;  lines: +26 -130
# Code clean. Unique note management. Remove button functional
#----------------------------
# revision 1.3
# date: 2004/11/21 16:53:04;  author: cfmoro;  state: Exp;  lines: +2 -1
# Fixed selection enabled border layout after setting default child widget
#----------------------------
# revision 1.2
# date: 2004/11/21 13:02:21;  author: cfmoro;  state: Exp;  lines: +12 -12
# Using test-area imports. Action buttons configuration. Save and clear buttons being functional
#----------------------------
# revision 1.1
# date: 2004/11/17 01:49:34;  author: cfmoro;  state: Exp;
# Initial SOAP input control implementation. It is just a first try, lot of feedback,review and advice is really needed. Just hope can serve as starting point to a not far away satisfactory design and implementation. It is open to changes and contributions from everybody so... :)
