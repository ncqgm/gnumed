#----------------------------------------------------------------------
# Name:			multisash
# Purpose:		Multi Sash control
#
# Author:		Gerrit van Dyk
#
# Created:		2002/11/20
# Version:		0.1
# RCS-ID:		$Id: multisash.py,v 1.5 2005-02-17 16:46:20 cfmoro Exp $
# License:		wxWindows licensie
#----------------------------------------------------------------------
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/cfmoro/soap_input/Attic/multisash.py,v $
# $Id: multisash.py,v 1.5 2005-02-17 16:46:20 cfmoro Exp $
__version__ = "$Revision: 1.5 $"
__author__ = "cfmoro"
__license__ = "GPL"
	   
from wxPython.wx import *

MV_HOR = 0
MV_VER = not MV_HOR

SH_SIZE = 5
CR_SIZE = SH_SIZE * 3

#----------------------------------------------------------------------

class wxMultiSash(wxWindow):
	def __init__(self, *_args,**_kwargs):
		apply(wxWindow.__init__,(self,) + _args,_kwargs)
		self._defChild = EmptyChild
		self.child = wxMultiSplit(self,self,wxPoint(0,0),self.GetSize())
		
		# Gnumed: focused and bottom leaf
		self.focussed_leaf = self.child.view1
		self.bottom_leaf = self.child.view1
		
		EVT_SIZE(self,self.OnMultiSize)

	def SetDefaultChildClass(self,childCls):
		self._defChild = childCls
		self.child.DefaultChildChanged()

	def OnMultiSize(self,evt):
		self.child.SetSize(self.GetSize())

	def UnSelect(self):
		self.child.UnSelect()

	def Clear(self):
		old = self.child
		self.child = wxMultiSplit(self,self,wxPoint(0,0),self.GetSize())
		old.Destroy()
		self.child.OnSize(None)
	#---------------------------------------------
	# public API
	#---------------------------------------------
	# Gnumed: 
	def get_focussed_leaf(self):
		"""
		Retrieves the currently focused leaf. Typically, used to
		process some action over the focused widget.
		"""
		return self.focussed_leaf
		
	#---------------------------------------------		  
	#def get_bottom_leaf(self):
	#	"""
	#	Retrieves the bottom leaf. Typically, used to call AddLeaf
	#	on it to ensure new widgets are created under the bottom leaf.		  
	#	"""
	#	return self.bottom_leaf

	#---------------------------------------------		  
	def add_content(self, content):
		"""
		Adds he supplied content widget to the multisash, setting it as
		child of the bottom leaf.
		
		@param content The new content widget to add.
		@type content Any wxWindow derived object.
		"""		
		successful, errno = self.bottom_leaf.AddLeaf(direction = MV_VER, pos = 100)
		if successful:
			self.bottom_leaf.set_content(content)
		return successful, errno
				
	#---------------------------------------------		  
	def refresh_bottom_leaf(self, bottom_leaf = None):
		"""
		Updates the field that keeps track of the bottom leaf. It is required
		to ensure new leafs are created under the bottom one.
		If the bottom leaf is supplied as parameter, it is set. Typically,
		after a new leaf has been added/created.
		If the bottom leaf ins not supplied ad parameter, it will be dinamically
		obtained. Typically, after leaf destruction.
		
		@param bottom_leaf The leaf to be set as bottom one
		@type bottom_leaf wxMultiViewLeaf
		"""
		if bottom_leaf is None:
			self.bottom_leaf = self.__find_bottom_leaf(self.child)
		else:
			self.bottom_leaf = bottom_leaf
		
	#---------------------------------------------
	# internal API
	#---------------------------------------------
	def __find_bottom_leaf(self, splitter):
		"""
		Recursively find and return the bottom leaf.
		"""
		print "__find_bottom_leaf()"
		print "splitter: %s [%s]" % (splitter.__class__.__name__, id(splitter))
		print "- leaf 1: %s [%s]" % (splitter.view1.__class__.__name__, id(splitter.view1))
		print "- leaf 2: %s [%s]" % (splitter.view2.__class__.__name__, id(splitter.view2))
		if isinstance(splitter.view1, wxMultiSplit):
			print "leaf 1 is splitter, recurse down"
			return self.__find_bottom_leaf(splitter.view1)
		if isinstance(splitter.view2, wxMultiSplit):
			print "leaf 2 is splitter, recurse down"
			return self.__find_bottom_leaf(splitter.view2)
		print "found bottom split: %s [%s]" % (splitter.__class__.__name__, id(splitter))
		if not splitter.view2 is None:
			print "bottom leaf (view2): %s [%s]" % (splitter.view2.__class__.__name__, id(splitter.view2))
			return splitter.view2
		else:
			print "bottom leaf (view1): %s [%s]" % (splitter.view1.__class__.__name__, id(splitter.view1))
			return splitter.view1

	#---------------------------------------------
#	def GetSaveData(self):
#		saveData = {}
#		saveData['_defChild'] = str(self._defChild)
#		saveData['child'] = self.child.GetSaveData()
#		return saveData

#	def SetSaveData(self,data):
#		dChild = data['_defChild']
#		mod = dChild.split('.')[0]
#		exec 'import %s' % mod
#		self._defChild = eval(dChild)
#		old = self.child
#		self.child = wxMultiSplit(self,self,wxPoint(0,0),self.GetSize())
#		self.child.SetSaveData(data['child'])
#		old.Destroy()
#		self.OnMultiSize(None)
#		self.child.OnSize(None)

#----------------------------------------------------------------------
class wxMultiSplit(wxWindow):
	def __init__(self,multiView,parent,pos,size,view1 = None):
		wxWindow.__init__(self,id = -1,parent = parent,pos = pos,size = size,
						  style = wxCLIP_CHILDREN)
		self.multiView = multiView
		self.view2 = None
		if view1:
			self.view1 = view1
			self.view1.Reparent(self)
			self.view1.MoveXY(0,0)
		else:
			self.view1 = wxMultiViewLeaf(self.multiView,self,
										 wxPoint(0,0),self.GetSize())
		self.direction = None

		EVT_SIZE(self,self.OnSize)

	def UnSelect(self):
		if self.view1:
			self.view1.UnSelect()
		if self.view2:
			self.view2.UnSelect()

	def DefaultChildChanged(self):
		if not self.view2:
			self.view1.DefaultChildChanged()
	#---------------------------------------------
	def AddLeaf(self,direction,caller,pos):
		print '%s[%s].AddLeaf()' % (self.__class__.__name__, id(self))
		print "leaf 1: %s [%s]" % (self.view1.__class__.__name__, id(self.view1))
		print "leaf 2: %s [%s]" % (self.view2.__class__.__name__, id(self.view2))
		if self.view2:
			print "we have two leafs"
			print "caller: %s [%s]" % (caller.__class__.__name__, id(caller))	 
			if caller == self.view1:
				print "caller was leaf 1, hence splitting leaf 1"
				self.view1 = wxMultiSplit(self.multiView,self,
										  caller.GetPosition(),
										  caller.GetSize(),
										  caller)
				self.view1.AddLeaf(direction,caller,pos)
			else:
				print "caller was leaf 2, hence splitting leaf 2"
				self.view2 = wxMultiSplit(self.multiView,self,
										  caller.GetPosition(),
										  caller.GetSize(),
										  caller)
				self.view2.AddLeaf(direction,caller,pos)
		else:
			print "we have only one leaf"
			print "caller: %s [%s]" % (caller.__class__.__name__, id(caller))
			print "hence caller must have been leaf 1 hence adding leaf 2 ..."	  
			self.direction = direction
			w,h = self.GetSizeTuple()
			if direction == MV_HOR:
				print "... next to leaf 1"
				x,y = (pos,0)
				w1,h1 = (w-pos,h)
				w2,h2 = (pos,h)
			else:
				print "... below leaf 1"
				x,y = (0,pos)
				w1,h1 = (w,h-pos)
				w2,h2 = (w,pos)
			self.view2 = wxMultiViewLeaf(self.multiView,self,
										 wxPoint(x,y),wxSize(w1,h1))									 
			self.view1.SetSize(wxSize(w2,h2))
			self.view2.OnSize(None)
			# Gnumed: sets the newly created leaf as the bottom and focus it
			self.multiView.refresh_bottom_leaf(self.view2)
			self.view2.set_focus()

	def DestroyLeaf(self,caller):
		print '%s[%s].DestroyLeaf()' % (self.__class__.__name__, id(self))
		if not self.view2:				# We will only have 2 windows if
			return						# we need to destroy any
		parent = self.GetParent()		# Another splitview
		if parent == self.multiView:	# We'r at the root
			print "parent is root view"
			print "caller: %s [%s]" % (caller.__class__.__name__, id(caller))	 
			if caller == self.view1:
				print "caller is leaf 1, hence destroying leaf 1 and copying leaf 2 to leaf 1"
				old = self.view1
				self.view1 = self.view2
				self.view2 = None
				old.Destroy()
			else:
				print "caller is leaf 2, hence destroying leaf 2"
				self.view2.Destroy()
				self.view2 = None
			self.view1.SetSize(self.GetSize())
			self.view1.Move(self.GetPosition())
		else:
			print "parent is NOT root view"
			print "caller: %s [%s]" % (caller.__class__.__name__, id(caller))	 
			w,h = self.GetSizeTuple()
			x,y = self.GetPositionTuple()
			if caller == self.view1:
				if self == parent.view1:
					print "... leaf 1 ..."
					parent.view1 = self.view2
				else:
					print "... leaf 2 ..."
					parent.view2 = self.view2
					print "... so replacing ourselves in the parent with our leaf 2"					
				self.view2.Reparent(parent)
				self.view2.SetDimensions(x,y,w,h)
				print "caller is leaf 2"
				print "in the parent we are ..."
			else:
				if self == parent.view1:
					print "... leaf 1 ..."
					parent.view1 = self.view1
				else:
					print "... leaf 2 ..."
					parent.view2 = self.view1
					print "... so replacing ourselves in the parent with our leaf 1"
				self.view1.Reparent(parent)
				self.view1.SetDimensions(x,y,w,h)
			# Gnumed: I am pretty sure this is wrong
			#if caller == self.multiView.get_bottom_leaf():
				#print "DESTROYING BOTTOM!! caller:self.view2:self.multiView.bottom_leaf %s:%s:%s" %(id(caller),id(self.view2),id(self.multiView.get_bottom_leaf()))
				# when destroying current bottom,
				# set the upper content leaf (view2) as bottom
				#self.GetParent().view2.set_bottom()													
			self.view1 = None
			self.view2 = None
			multiView = self.multiView
			self.Destroy()
			try:
				print "leaf 1: %s [%s]" % (self.view1.__class__.__name__, id(self.view1))
			except:
				pass
			try:
				print "leaf 2: %s [%s]" % (self.view2.__class__.__name__, id(self.view2))
			except:
				pass
			# Gnumed: find and update the bottom leaf
			multiView.refresh_bottom_leaf()
		
	#---------------------------------------------
	def CanSize(self,side,view):
		if self.SizeTarget(side,view):
			return True
		return False

	def SizeTarget(self,side,view):
		if self.direction == side and self.view2 and view == self.view1:
			return self
		parent = self.GetParent()
		if parent != self.multiView:
			return parent.SizeTarget(side,self)
		return None

	def SizeLeaf(self,leaf,pos,side):
		if self.direction != side:
			return
		if not (self.view1 and self.view2):
			return
		if pos < 10: return
		w,h = self.GetSizeTuple()
		if side == MV_HOR:
			if pos > w - 10: return
		else:
			if pos > h - 10: return
		if side == MV_HOR:
			self.view1.SetDimensions(0,0,pos,h)
			self.view2.SetDimensions(pos,0,w-pos,h)
		else:
			self.view1.SetDimensions(0,0,w,pos)
			self.view2.SetDimensions(0,pos,w,h-pos)

	def OnSize(self,evt):
		if not self.view2:
			self.view1.SetSize(self.GetSize())
			self.view1.OnSize(None)
			return
		v1w,v1h = self.view1.GetSizeTuple()
		v2w,v2h = self.view2.GetSizeTuple()
		v1x,v1y = self.view1.GetPositionTuple()
		v2x,v2y = self.view2.GetPositionTuple()
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

		self.view1.SetDimensions(v1x,v1y,v1w,v1h)
		self.view2.SetDimensions(v2x,v2y,v2w,v2h)
		self.view1.OnSize(None)
		self.view2.OnSize(None)
	#-----------------------------------------------------
#	def GetSaveData(self):
#		saveData = {}
#		if self.view1:
#			saveData['view1'] = self.view1.GetSaveData()
#			if isinstance(self.view1,wxMultiSplit):
#				saveData['view1IsSplit'] = 1
#		if self.view2:
#			saveData['view2'] = self.view2.GetSaveData()
#			if isinstance(self.view2,wxMultiSplit):
#				saveData['view2IsSplit'] = 1
#		saveData['direction'] = self.direction
#		v1,v2 = self.GetPositionTuple()
#		saveData['x'] = v1
#		saveData['y'] = v2
#		v1,v2 = self.GetSizeTuple()
#		saveData['w'] = v1
#		saveData['h'] = v2
#		return saveData

#	def SetSaveData(self,data):
#		self.direction = data['direction']
#		self.SetDimensions(data['x'],data['y'],data['w'],data['h'])
#		v1Data = data.get('view1',None)
#		if v1Data:
#			isSplit = data.get('view1IsSplit',None)
#			old = self.view1
#			if isSplit:
#				self.view1 = wxMultiSplit(self.multiView,self,
#										  wxPoint(0,0),self.GetSize())
#			else:
#				self.view1 = wxMultiViewLeaf(self.multiView,self,
#											 wxPoint(0,0),self.GetSize())
#			self.view1.SetSaveData(v1Data)
#			if old:
#				old.Destroy()
#		v2Data = data.get('view2',None)
#		if v2Data:
#			isSplit = data.get('view2IsSplit',None)
#			old = self.view2
#			if isSplit:
#				self.view2 = wxMultiSplit(self.multiView,self,
#										  wxPoint(0,0),self.GetSize())
#			else:
#				self.view2 = wxMultiViewLeaf(self.multiView,self,
#											 wxPoint(0,0),self.GetSize())
#			self.view2.SetSaveData(v2Data)
#			if old:
#				old.Destroy()
#		if self.view1:
#			self.view1.OnSize(None)
#		if self.view2:
#			self.view2.OnSize(None)

#----------------------------------------------------------------------
class wxMultiViewLeaf(wxWindow):
	def __init__(self,multiView,parent,pos,size):
		wxWindow.__init__(self,id = -1,parent = parent,pos = pos,size = size,
						  style = wxCLIP_CHILDREN)
		self.multiView = multiView

		self.sizerHor = MultiSizer(self,MV_HOR)
		self.sizerVer = MultiSizer(self,MV_VER)
		# Gnumed: Disable creators until obvious solution
		#self.creatorHor = MultiCreator(self,MV_HOR)
		#self.creatorVer = MultiCreator(self,MV_VER)
		self.detail = MultiClient(self,multiView._defChild)
		self.closer = MultiCloser(self)

		EVT_SIZE(self,self.OnSize)
	#-----------------------------------------------------								
	def set_focus(self):
		"""
		Set current leaf as focused leaf. Typically, the focused widget
		will be required to further actions and processing. If the leaf
		is not selected (eg. just after creation), select it. Otherwise,
		skip selecting it (prevents endless recursive call).
		"""
		self.multiView.focussed_leaf = self
		if self.detail is not None and not self.detail.selected :
			self.detail.Select()		
		print "focussed soap editor leaf:", self.__class__.__name__, id(self)
		#self.multiView.get_bottom_leaf()

	def UnSelect(self):
		self.detail.UnSelect()

	def DefaultChildChanged(self):
		self.detail.SetNewChildCls(self.multiView._defChild)
		
	def set_content(self, content):
		self.detail.set_new_content(content)		
	#-----------------------------------------------------
	def AddLeaf(self,direction,pos):
		"""Add a leaf.
		
		returns (Status, error)
		errors:
			1: lacking space to add leaf
		"""
		print '%s[%s].AddLeaf()' % (self.__class__.__name__, id(self))
		if pos < 10:
			pos = 10
		w,h = self.GetSizeTuple()
		if direction == MV_VER:
			if pos > h - 10:
				print "pos", pos
				print "w,h", w, h
				return (False, 1)
		else:
			if pos > w - 10: return (False, 1)
		self.GetParent().AddLeaf(direction,self,pos)
		return (True, None)
	#---------------------------------------------
	def DestroyLeaf(self):
		print '%s[%s].DestroyLeaf()' % (self.__class__.__name__, id(self))
		self.GetParent().DestroyLeaf(self)
	#-----------------------------------------------------
	def SizeTarget(self,side):
		return self.GetParent().SizeTarget(side,self)

	def CanSize(self,side):
		return self.GetParent().CanSize(side,self)

	def OnSize(self,evt):
		self.sizerHor.OnSize(evt)
		self.sizerVer.OnSize(evt)
		# Gnumed: creators disables until obvious solution
		#self.creatorHor.OnSize(evt)
		#self.creatorVer.OnSize(evt)
		self.detail.OnSize(evt)
		self.closer.OnSize(evt)
	#-----------------------------------------------------
#	def GetSaveData(self):
#		saveData = {}
#		saveData['detailClass'] = str(self.detail.child.__class__)
#		if hasattr(self.detail.child,'GetSaveData'):
#			attr = getattr(self.detail.child,'GetSaveData')
#			if callable(attr):
#				dData = attr()
#				if dData:
#					saveData['detail'] = dData
#		v1,v2 = self.GetPositionTuple()
#		saveData['x'] = v1
#		saveData['y'] = v2
#		v1,v2 = self.GetSizeTuple()
#		saveData['w'] = v1
#		saveData['h'] = v2
#		return saveData

#	def SetSaveData(self,data):
#		dChild = data['detailClass']
#		mod = dChild.split('.')[0]
#		exec 'import %s' % mod
#		detClass = eval(dChild)
#		self.SetDimensions(data['x'],data['y'],data['w'],data['h'])
#		old = self.detail
#		self.detail = MultiClient(self,detClass)
#		dData = data.get('detail',None)
#		if dData:
#			if hasattr(self.detail.child,'SetSaveData'):
#				attr = getattr(self.detail.child,'SetSaveData')
#				if callable(attr):
#					attr(dData)
#		old.Destroy()
#		self.detail.OnSize(None)

#----------------------------------------------------------------------
class MultiClient(wxWindow):
	def __init__(self,parent,childCls):
		w,h = self.CalcSize(parent)
		wxWindow.__init__(self,id = -1,parent = parent,
						  pos = wxPoint(0,0),
						  size = wxSize(w,h),
						  style = wxCLIP_CHILDREN | wxSUNKEN_BORDER)
		self.child = childCls(self)
		self.child.MoveXY(2,2)
		self.normalColour = self.GetBackgroundColour()
		self.selected = False

		EVT_SET_FOCUS(self,self.OnSetFocus)
		EVT_CHILD_FOCUS(self,self.OnChildFocus)

	def UnSelect(self):
		if self.selected:
			self.selected = False
			self.SetBackgroundColour(self.normalColour)
			self.Refresh()

	def Select(self):
		"""
		May be invoked by user clicking on the leaf, or programmatically after
		leaf creation. Highlight it and update focused leaf.
		"""
		# Gnumed: when the leaf is selected, highlight and update selected focus
		parent = self.GetParent()
		parent.multiView.UnSelect()
		self.selected = True
		if parent.multiView.focussed_leaf != parent:
			parent.set_focus()
		self.SetBackgroundColour(wxColour(255,255,0)) # Yellow
		self.Refresh()

	def CalcSize(self,parent):
		w,h = parent.GetSizeTuple()
		w -= SH_SIZE
		h -= SH_SIZE
		return (w,h)

	def OnSize(self,evt):
		w,h = self.CalcSize(self.GetParent())
		self.SetDimensions(0,0,w,h)
		w,h = self.GetClientSizeTuple()
		self.child.SetSize(wxSize(w-4,h-4))

	def SetNewChildCls(self,childCls):
		if self.child:
			self.child.Destroy()
			self.child = None
		self.child = childCls(self)
		self.child.MoveXY(2,2)
		
	def set_new_content(self,content):
		if self.child:
			self.child.Destroy()
			self.child = None
		content.Reparent(self)
		self.child = content
		self.child.MoveXY(2,2)		

	def OnSetFocus(self,evt):
		self.Select()

	def OnChildFocus(self,evt):
		self.OnSetFocus(evt)
##		  from Funcs import FindFocusedChild
##		  child = FindFocusedChild(self)
##		  EVT_KILL_FOCUS(child,self.OnChildKillFocus)


#----------------------------------------------------------------------


class MultiSizer(wxWindow):
	def __init__(self,parent,side):
		self.side = side
		x,y,w,h = self.CalcSizePos(parent)
		wxWindow.__init__(self,id = -1,parent = parent,
						  pos = wxPoint(x,y),
						  size = wxSize(w,h),
						  style = wxCLIP_CHILDREN)

		self.px = None					# Previous X
		self.py = None					# Previous Y
		self.isDrag = False				# In Dragging
		self.dragTarget = None			# View being sized

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

#----------------------------------------------------------------------


class MultiCreator(wxWindow):
	def __init__(self,parent,side):
		self.side = side
		x,y,w,h = self.CalcSizePos(parent)
		wxWindow.__init__(self,id = -1,parent = parent,
						  pos = wxPoint(x,y),
						  size = wxSize(w,h),
						  style = wxCLIP_CHILDREN)

		self.px = None					# Previous X
		self.py = None					# Previous Y
		self.isDrag = False			  # In Dragging

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
			y = 4 + SH_SIZE				# Make provision for closer
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
		if self.isDrag:
			parent = self.GetParent()
			DrawSash(parent,self.px,self.py,self.side)
			self.ReleaseMouse()
			self.isDrag = False

			if self.side == MV_HOR:
				parent.AddLeaf(MV_VER,self.py)
			else:
				parent.AddLeaf(MV_HOR,self.px)
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

#----------------------------------------------------------------------


class MultiCloser(wxWindow):
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


#----------------------------------------------------------------------


class EmptyChild(wxWindow):
	def __init__(self,parent):
		wxWindow.__init__(self,parent,-1, style = wxCLIP_CHILDREN)


#----------------------------------------------------------------------


def DrawSash(win,x,y,direction):
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
#----------------------------------------------------------------------
# $Log: multisash.py,v $
# Revision 1.5  2005-02-17 16:46:20  cfmoro
# Adding and removing soap editors. Simplified multisash interface.
#
# Revision 1.4  2005/02/16 11:19:12  ncq
# - better error handling
# - tabified
# - get_bottom_leaf() verified
#
