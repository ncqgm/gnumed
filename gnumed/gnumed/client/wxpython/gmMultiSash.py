#----------------------------------------------------------------------
# ORIGINAL HEADER:
#
# Name:			multisash
# Purpose:		Multi Sash control
#
# Author:		Gerrit van Dyk
#
# Created:		2002/11/20
# Version:		0.1
# RCS-ID:		$Id: gmMultiSash.py,v 1.7 2005-09-28 21:27:30 ncq Exp $
# License:		wxWindows licensie
#----------------------------------------------------------------------
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMultiSash.py,v $
# $Id: gmMultiSash.py,v 1.7 2005-09-28 21:27:30 ncq Exp $
__version__ = "$Revision: 1.7 $"
__author__ = "Gerrit van Dyk, Carlos, Karsten"
#__license__ = "GPL"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx
	   
MV_HOR = 0
MV_VER = not MV_HOR

SH_SIZE = 5
CR_SIZE = SH_SIZE * 3

#----------------------------------------------------------------------
class cMultiSash(wx.Window):
	"""
	Main multisash widget. Dynamically displays a stack of child widgets.	
	"""	
	def __init__(self, *_args,**_kwargs):
		apply(wx.Window.__init__,(self,) + _args,_kwargs)
		#self._defChild = cEmptyChild
		self.child = cMultiSashSplitter(self,self,wxPoint(0,0),self.GetSize())
		
		# Gnumed: focused and bottom leaf
		self.focussed_leaf = self.child.leaf1
		self.bottom_leaf = self.child.leaf1
		self.displayed_leafs = []

		wx.EVT_SIZE(self,self._on_size)
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
	def get_displayed_leafs(self):
		"""
		Retrieves the currently displayed leafs.
		"""
		return self.displayed_leafs
	#---------------------------------------------
	def add_content(self, content):
		"""
		Adds he supplied content widget to the multisash, setting it as
		child of the bottom leaf.
		
		@param content The new content widget to add.
		@type content Any wx.Window derived object.
		"""
		successful, errno = self.bottom_leaf.AddLeaf(direction = MV_VER, pos = 100)
		if successful:
			self.bottom_leaf.set_content(content)
		return successful, errno
	#---------------------------------------------
	def Clear(self):
		"""
		Clear all mulsisash leafs and restores initial values
		"""
		# FIXME: keep an eye if strange behaviour
		old = self.child
		self.child = cMultiSashSplitter(self,self,wxPoint(0,0),self.GetSize())
		old.Destroy()
		self.child.OnSize(None)
		
		# Gnumed: focused and bottom leaf
		self.focussed_leaf = self.child.leaf1
		self.bottom_leaf = self.child.leaf1
		self.bottom_leaf.Select()
		self.displayed_leafs = []
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
		@type bottom_leaf wx.MultiViewLeaf
		"""
		if bottom_leaf is None:
			self.bottom_leaf = self.__find_bottom_leaf(self.child)
		else:
			self.bottom_leaf = bottom_leaf
		self.bottom_leaf.Select()
		
	#---------------------------------------------
	def refresh_displayed_leafs(self, splitter):
		"""
		Recursively find all displayed leafs.
		@param splitter The multisash splitter to traverse its leafs for.
		@type splitter cMultiSashSplitter
		"""
		if id(splitter) == id(self.child):
			self.displayed_leafs = []
#		print "__refresh_displayed_leafs()"
#		print "splitter: %s [%s]" % (splitter.__class__.__name__, id(splitter))
#		print "- leaf 1: %s [%s]" % (splitter.leaf1.__class__.__name__, id(splitter.leaf1))
#		print "- leaf 2: %s [%s]" % (splitter.leaf2.__class__.__name__, id(splitter.leaf2))
		if isinstance(splitter.leaf1, cMultiSashSplitter):
#			print "leaf 1 is splitter, recurse down"
			self.refresh_displayed_leafs(splitter.leaf1)
		if isinstance(splitter.leaf2, cMultiSashSplitter):
#			print "leaf 2 is splitter, recurse down"
			self.refresh_displayed_leafs(splitter.leaf2)
#		print "found bottom split: %s [%s]" % (splitter.__class__.__name__, id(splitter))
		if not splitter.leaf2 is None and not isinstance(splitter.leaf2, cMultiSashSplitter):
#			print "found leaf (leaf2): %s [%s]" % (splitter.leaf2.__class__.__name__, id(splitter.leaf2))
			self.displayed_leafs.append(splitter.leaf2)
		if not splitter.leaf1 is None and not isinstance(splitter.leaf1, cMultiSashSplitter):
#			print "found leaf (leaf1): %s [%s]" % (splitter.leaf1.__class__.__name__, id(splitter.leaf1))			
			self.displayed_leafs.append(splitter.leaf1)
	#---------------------------------------------
	# event handlers
	#---------------------------------------------
	def _on_size(self, evt):
		self.child.SetSize(self.GetSize())
	#---------------------------------------------
	# internal API
	#---------------------------------------------
	def __find_bottom_leaf(self, splitter):
		"""
		Recursively find and return the bottom leaf.
		"""
#		print "__find_bottom_leaf()"
#		print "splitter: %s [%s]" % (splitter.__class__.__name__, id(splitter))
#		print "- leaf 1: %s [%s]" % (splitter.leaf1.__class__.__name__, id(splitter.leaf1))
#		print "- leaf 2: %s [%s]" % (splitter.leaf2.__class__.__name__, id(splitter.leaf2))
		if isinstance(splitter.leaf1, cMultiSashSplitter):
#			print "leaf 1 is splitter, recurse down"
			return self.__find_bottom_leaf(splitter.leaf1)
		if isinstance(splitter.leaf2, cMultiSashSplitter):
#			print "leaf 2 is splitter, recurse down"
			return self.__find_bottom_leaf(splitter.leaf2)
#		print "found bottom split: %s [%s]" % (splitter.__class__.__name__, id(splitter))
		if not splitter.leaf2 is None:
#			print "bottom leaf (leaf2): %s [%s]" % (splitter.leaf2.__class__.__name__, id(splitter.leaf2))
			return splitter.leaf2
		else:
#			print "bottom leaf (leaf1): %s [%s]" % (splitter.leaf1.__class__.__name__, id(splitter.leaf1))
			return splitter.leaf1
	#---------------------------------------------
	def _unselect(self):
		self.child._unselect()						
#----------------------------------------------------------------------
class cMultiSashSplitter(wx.Window):
	"""
	Basic split windows container of the multisash widget.
	Has references to two leafs or splitted windows (typically, first leaf
	is another cMultiSashSplitter and the second leaf is the displayed content
	widget).
	"""
	def __init__(self, top_parent, parent, pos, size, leaf1 = None):
		wx.Window.__init__ (
			self,
			id = -1,
			parent = parent,
			pos = pos,
			size = size,
			style = wx.CLIP_CHILDREN
		)
		self.top_parent = top_parent
		self.leaf2 = None
		if leaf1:
			self.leaf1 = leaf1
			self.leaf1.Reparent(self)
			self.leaf1.MoveXY(0,0)
		else:
			self.leaf1 = cMultiSashLeaf (
				self.top_parent,
				self,
				wxPoint(0,0),
				self.GetSize()
			)
		self.direction = None

		wx.EVT_SIZE(self,self.OnSize)
	#---------------------------------------------
	def _unselect(self):
		if self.leaf1:
			self.leaf1._unselect()
		if self.leaf2:
			self.leaf2._unselect()

	#---------------------------------------------
	def AddLeaf(self,direction,caller,pos):		
#		print '%s[%s].AddLeaf()' % (self.__class__.__name__, id(self))
#		print "leaf 1: %s [%s]" % (self.leaf1.__class__.__name__, id(self.leaf1))
#		print "leaf 2: %s [%s]" % (self.leaf2.__class__.__name__, id(self.leaf2))
		if self.leaf2:
#			print "we have two leafs"
#			print "caller: %s [%s]" % (caller.__class__.__name__, id(caller))	 
			if caller == self.leaf1:
#				print "caller was leaf 1, hence splitting leaf 1"
				self.leaf1 = cMultiSashSplitter(self.top_parent,self,
										  caller.GetPosition(),
										  caller.GetSize(),
										  caller)
				self.leaf1.AddLeaf(direction,caller,pos)
			else:
#				print "caller was leaf 2, hence splitting leaf 2"
				self.leaf2 = cMultiSashSplitter(self.top_parent,self,
										  caller.GetPosition(),
										  caller.GetSize(),
										  caller)
				self.leaf2.AddLeaf(direction,caller,pos)
		else:
#			print "we have only one leaf"
#			print "caller: %s [%s]" % (caller.__class__.__name__, id(caller))
#			print "hence caller must have been leaf 1 hence adding leaf 2 ..."	  
			self.direction = direction
			w,h = self.GetSizeTuple()
			if direction == MV_HOR:
#				print "... next to leaf 1"
				x,y = (pos,0)
				w1,h1 = (w-pos,h)
				w2,h2 = (pos,h)
			else:
#				print "... below leaf 1"
				x,y = (0,pos)
				w1,h1 = (w,h-pos)
				w2,h2 = (w,pos)
			self.leaf2 = cMultiSashLeaf(self.top_parent,self,
										 wxPoint(x,y),wx.Size(w1,h1))									 
			self.leaf1.SetSize(wx.Size(w2,h2))
			self.leaf2.OnSize(None)
			# Gnumed: register added leaf content
			self.top_parent.displayed_leafs.append(self.leaf2)
			# Gnumed: sets the newly created leaf as the bottom and focus it
			self.top_parent.refresh_bottom_leaf(self.leaf2)
			self.leaf2.set_focus()

	def DestroyLeaf(self,caller):
#		print '%s[%s].DestroyLeaf()' % (self.__class__.__name__, id(self))
		top_parent = self.top_parent
		if not self.leaf2:
			self.leaf1.set_content(cEmptyChild(self))	# We will only have 2 windows if
			return						# we need to destroy any
		parent = self.GetParent()		# Another splitview
		if parent == self.top_parent:	# We'r at the root
#			print "parent is root view"
#			print "caller: %s [%s]" % (caller.__class__.__name__, id(caller))	 
			if caller == self.leaf1:
#				print "caller is leaf 1, hence destroying leaf 1 and copying leaf 2 to leaf 1"
				old = self.leaf1
				self.leaf1 = self.leaf2
				self.leaf2 = None
				# Gnumed: remove content from displayed leafs
				#print "Removing old: %s [%s]" % (old.__class__.__name__, id(old))
				#self.top_parent.displayed_leafs.remove(old)
				old.Destroy()
			else:
#				print "caller is leaf 2, hence destroying leaf 2"
				# Gnumed: remove content from displayed leafs
				#print "Removing leaf2: %s [%s]" % (self.leaf2.__class__.__name__, id(self.leaf2))
				#self.top_parent.displayed_leafs.remove(self.leaf2)
				self.leaf2.Destroy()
				self.leaf2 = None
			self.leaf1.SetSize(self.GetSize())
			self.leaf1.Move(self.GetPosition())
		else:
#			print "parent is NOT root view"
#			print "caller: %s [%s]" % (caller.__class__.__name__, id(caller))
#			print "Removing caller"
			# Gnumed: remove content from displayed leafs
			self.top_parent.displayed_leafs.remove(caller)
			w,h = self.GetSizeTuple()
			x,y = self.GetPositionTuple()
			if caller == self.leaf1:
				if self == parent.leaf1:
#					print "... leaf 1 ..."
					parent.leaf1 = self.leaf2
				else:
#					print "... leaf 2 ..."
					parent.leaf2 = self.leaf2
#					print "... so replacing ourselves in the parent with our leaf 2"					
				self.leaf2.Reparent(parent)
				self.leaf2.SetDimensions(x,y,w,h)
#				print "caller is leaf 2"
#				print "in the parent we are ..."
			else:
				if self == parent.leaf1:
#					print "... leaf 1 ..."
					parent.leaf1 = self.leaf1
				else:
#					print "... leaf 2 ..."
					parent.leaf2 = self.leaf1
#					print "... so replacing ourselves in the parent with our leaf 1"
				self.leaf1.Reparent(parent)
				self.leaf1.SetDimensions(x,y,w,h)

			self.leaf1 = None
			self.leaf2 = None
			top_parent = self.top_parent
			self.Destroy()
#			try:
#				print "leaf 1: %s [%s]" % (self.leaf1.__class__.__name__, id(self.leaf1))
#			except:
#				pass
#			try:
#				print "leaf 2: %s [%s]" % (self.leaf2.__class__.__name__, id(self.leaf2))
#			except:
#				pass
		# Gnumed: find and update the bottom leaf
		top_parent.refresh_bottom_leaf()
		top_parent.refresh_displayed_leafs(top_parent.child)
#		print "\nGuessed leafs:"
#		cont = 0
#		for a_leaf in top_parent.displayed_leafs:
#			cont +=1
#			print "leaf %d: %s [%s]" % (cont, a_leaf.__class__.__name__, id(a_leaf))
	#---------------------------------------------
	def CanSize(self,side,view):
		if self.SizeTarget(side,view):
			return True
		return False

	def SizeTarget(self,side,view):
		if self.direction == side and self.leaf2 and view == self.leaf1:
			return self
		parent = self.GetParent()
		if parent != self.top_parent:
			return parent.SizeTarget(side,self)
		return None

	def SizeLeaf(self,leaf,pos,side):
		if self.direction != side:
			return
		if not (self.leaf1 and self.leaf2):
			return
		if pos < 10: return
		w,h = self.GetSizeTuple()
		if side == MV_HOR:
			if pos > w - 10: return
		else:
			if pos > h - 10: return
		if side == MV_HOR:
			self.leaf1.SetDimensions(0,0,pos,h)
			self.leaf2.SetDimensions(pos,0,w-pos,h)
		else:
			self.leaf1.SetDimensions(0,0,w,pos)
			self.leaf2.SetDimensions(0,pos,w,h-pos)

	def OnSize(self,evt):
		if not self.leaf2:
			self.leaf1.SetSize(self.GetSize())
			self.leaf1.OnSize(None)
			return
		v1w,v1h = self.leaf1.GetSizeTuple()
		v2w,v2h = self.leaf2.GetSizeTuple()
		v1x,v1y = self.leaf1.GetPositionTuple()
		v2x,v2y = self.leaf2.GetPositionTuple()
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

		self.leaf1.SetDimensions(v1x,v1y,v1w,v1h)
		self.leaf2.SetDimensions(v2x,v2y,v2w,v2h)
		self.leaf1.OnSize(None)
		self.leaf2.OnSize(None)
		
#----------------------------------------------------------------------
class cMultiSashLeaf(wx.Window):
	"""
	A leaf represent a split window, one instance of the displayed content
	widget.
	"""	
	def __init__(self,top_parent,parent,pos,size):
		wx.Window.__init__(self,id = -1,parent = parent,pos = pos,size = size,
						  style = wx.CLIP_CHILDREN)
		self.top_parent = top_parent

		self.sizerHor = cMultiSizer(self,MV_HOR)
		self.sizerVer = cMultiSizer(self,MV_VER)
		# Gnumed: Disable creators until obvious solution
		#self.creatorHor = cMultiCreator(self,MV_HOR)
		#self.creatorVer = cMultiCreator(self,MV_VER)
		self.content = cMultiSashLeafContent(self)
		self.closer = cMultiCloser(self)

		wx.EVT_SIZE(self,self.OnSize)
	#-----------------------------------------------------								
	def set_focus(self):
		"""
		Set current leaf as focused leaf. Typically, the focused widget
		will be required to further actions and processing.
		"""
		self.top_parent.focussed_leaf = self
#		print "focussed soap editor leaf:", self.__class__.__name__, id(self)

	def _unselect(self):
		self.content._unselect()

	#-----------------------------------------------------		
	def set_content(self, content):
		"""
		Sets the as content child of this leaf.
		
		@param content The new content widget to set..
		@type content Any wx.Window derived object.
		"""				
		self.content.set_new_content(content)

	#-----------------------------------------------------		
	def get_content(self):
		"""
		Retrieves the content child of this leaf.
		"""				
		return self.content.child
		
	#-----------------------------------------------------				
	def Select(self):
		"""
		Select the leaf
		"""
		self.content.Select()
	#-----------------------------------------------------
	def AddLeaf(self,direction,pos):
		"""Add a leaf.
		
		returns (Status, error)
		errors:
			1: lacking space to add leaf
		"""
#		print '%s[%s].AddLeaf()' % (self.__class__.__name__, id(self))
		if pos < 10:
			pos = 10
		w,h = self.GetSizeTuple()
		if direction == MV_VER:
			if pos > h - 10:
#				print "pos", pos
#				print "w,h", w, h
				return (False, 1)
		else:
			if pos > w - 10: return (False, 1)
		# Gnumed: when initial leaf, replace its content widget and focus it
		#		 else, add a new leaf
		if not isinstance(self.content.child, cEmptyChild):
			self.GetParent().AddLeaf(direction,self,pos)
		else:
			self.set_focus()
			# Gnumed: register added leaf content
			self.GetParent().top_parent.displayed_leafs.append(self)
		return (True, None)
		
	#---------------------------------------------
	def DestroyLeaf(self):
#		print '%s[%s].DestroyLeaf()' % (self.__class__.__name__, id(self))		
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
		self.content.OnSize(evt)
		self.closer.OnSize(evt)

#----------------------------------------------------------------------
class cMultiSashLeafContent(wx.Window):
	"""
	Widget that encapsulate contents of a leaf or split window.
	"""	
	def __init__(self,parent):
		w,h = self.CalcSize(parent)
		wx.Window.__init__ (
			self,
			id = -1,
			parent = parent,
			pos = wxPoint(0,0),
			size = wx.Size(w,h),
			style = wx.CLIP_CHILDREN | wx.SUNKEN_BORDER
		)
		self.child = cEmptyChild(self)
		self.child.MoveXY(2,2)
		self.__normal_colour = self.GetBackgroundColour()
		self.selected = False

		wx.EVT_SET_FOCUS(self, self._on_set_focus)
		wx.EVT_CHILD_FOCUS(self, self._on_child_focus)
	#---------------------------------------------
	def set_new_content(self,content):
		"""
		Sets the as content child of this widget.
		
		@param content The new content widget to set..
		@type content Any wx.Window derived object.
		"""
		# Gnumed: avoid yellow blinking during widget replacement
		self.SetBackgroundColour(self.__normal_colour)
		if self.child:
			self.child.Destroy()
		content.Reparent(self)
		self.child = content
		self.child.MoveXY(2,2)
		# Gnumed: required to a proper layout of the child and parent widgets
		self.Select()
		self.OnSize(None)
	#---------------------------------------------
	# internal API
	#---------------------------------------------
	def _unselect(self):
		if self.selected:
			self.selected = False
			self.SetBackgroundColour(self.__normal_colour)
			self.Refresh()
	#---------------------------------------------
	def _on_set_focus(self,evt):
		self.Select()
	#---------------------------------------------
	def _on_child_focus(self,evt):
		self._on_set_focus(evt)
##		  from Funcs import FindFocusedChild
##		  child = FindFocusedChild(self)
##		  wx.EVT_KILL_FOCUS(child,self.OnChildKillFocus)

	#---------------------------------------------
	def Select(self):
		"""
		May be invoked by user clicking on the leaf, or programmatically after
		leaf creation. Highlight it and update focused leaf.
		"""
		# Gnumed: when the leaf is selected, highlight and update selected focus
		parent = self.GetParent()
		parent.top_parent._unselect()
		self.selected = True
		if parent.top_parent.focussed_leaf != parent:
			parent.set_focus()
		self.SetBackgroundColour(wx.Colour(255,255,0)) # Yellow
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
		self.child.SetSize(wx.Size(w-4,h-4))
#----------------------------------------------------------------------
class cMultiSizer(wx.Window):
	"""
	Leaf's sash bar
	"""	
	def __init__(self,parent,side):
		self.side = side
		x,y,w,h = self.CalcSizePos(parent)
		wx.Window.__init__(self,id = -1,parent = parent,
						  pos = wxPoint(x,y),
						  size = wx.Size(w,h),
						  style = wx.CLIP_CHILDREN)

		self.px = None					# Previous X
		self.py = None					# Previous Y
		self.isDrag = False				# In Dragging
		self.dragTarget = None			# View being sized

		wx.EVT_LEAVE_WINDOW(self,self.OnLeave)
		wx.EVT_ENTER_WINDOW(self,self.OnEnter)
		wx.EVT_MOTION(self,self.OnMouseMove)
		wx.EVT_LEFT_DOWN(self,self.OnPress)
		wx.EVT_LEFT_UP(self,self.OnRelease)

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
		self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

	def OnEnter(self,evt):
		if not self.GetParent().CanSize(not self.side):
			return
		if self.side == MV_HOR:
			self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))
		else:
			self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))

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
class cMultiCreator(wx.Window):
	"""
	Sash bar's creator element
	"""	
	def __init__(self,parent,side):
		self.side = side
		x,y,w,h = self.CalcSizePos(parent)
		wx.Window.__init__(self,id = -1,parent = parent,
						  pos = wxPoint(x,y),
						  size = wx.Size(w,h),
						  style = wx.CLIP_CHILDREN)

		self.px = None					# Previous X
		self.py = None					# Previous Y
		self.isDrag = False			  # In Dragging

		wx.EVT_LEAVE_WINDOW(self,self.OnLeave)
		wx.EVT_ENTER_WINDOW(self,self.OnEnter)
		wx.EVT_MOTION(self,self.OnMouseMove)
		wx.EVT_LEFT_DOWN(self,self.OnPress)
		wx.EVT_LEFT_UP(self,self.OnRelease)
		wx.EVT_PAINT(self,self.OnPaint)

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
		self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

	def OnEnter(self,evt):
		if self.side == MV_HOR:
			self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
		else:
			self.SetCursor(wx.StockCursor(wx.CURSOR_POINT_LEFT))

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
		dc.SetBackground(wx.Brush(self.GetBackgroundColour(),wx.SOLID))
		dc.Clear()

		highlight = wxPen(wx.SystemSettings_GetSystemColour(
			wx.SYS_COLOUR_BTNHIGHLIGHT),1,wx.SOLID)
		shadow = wxPen(wx.SystemSettings_GetSystemColour(
			wx.SYS_COLOUR_BTNSHADOW),1,wx.SOLID)
		black = wxPen(wx.BLACK,1,wx.SOLID)
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
class cMultiCloser(wx.Window):
	"""
	Sash bar's destroyer element
	"""	
	def __init__(self,parent):
		x,y,w,h = self.CalcSizePos(parent)
		wx.Window.__init__(self,id = -1,parent = parent,
						  pos = wxPoint(x,y),
						  size = wx.Size(w,h),
						  style = wx.CLIP_CHILDREN)

		self.down = False
		self.entered = False

		wx.EVT_LEFT_DOWN(self,self.OnPress)
		wx.EVT_LEFT_UP(self,self.OnRelease)
		wx.EVT_PAINT(self,self.OnPaint)
		wx.EVT_LEAVE_WINDOW(self,self.OnLeave)
		wx.EVT_ENTER_WINDOW(self,self.OnEnter)

	def OnLeave(self,evt):
		self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
		self.entered = False

	def OnEnter(self,evt):
		self.SetCursor(wx.StockCursor(wx.CURSOR_BULLSEYE))
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
		dc.SetBackground(wx.Brush(wx.RED,wx.SOLID))
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


class cEmptyChild(wx.Window):
	def __init__(self,parent):
		wx.Window.__init__(self,parent,-1, style = wx.CLIP_CHILDREN)


#----------------------------------------------------------------------


def DrawSash(win,x,y,direction):
	dc = wx.ScreenDC()
	dc.StartDrawingOnTopWin(win)
	bmp = wx.EmptyBitmap(8,8)
	bdc = wx.MemoryDC()
	bdc.SelectObject(bmp)
	bdc.DrawRectangle(-1,-1,10,10)
	for i in range(8):
		for j in range(8):
			if ((i + j) & 1):
				bdc.DrawPoint(i,j)

	brush = wx.Brush(wx.Colour(0,0,0))
	brush.SetStipple(bmp)

	dc.SetBrush(brush)
	dc.SetLogicalFunction(wx.XOR)

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
# $Log: gmMultiSash.py,v $
# Revision 1.7  2005-09-28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.6  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.5  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.4  2005/04/12 10:04:59  ncq
# - cleanup
#
# Revision 1.3  2005/03/18 16:48:41  cfmoro
# Fixes to integrate multisash notes input plugin in wxclient
#
# Revision 1.2  2005/03/17 19:54:20  cfmoro
# Ensure a the bottom leaf is selected after adding or removing leaf to avoid corrupted references
#
# Revision 1.1  2005/03/15 07:53:28  ncq
# - moved to main trunk from test_area
# - license check needed !
#
# Revision 1.12  2005/02/23 19:41:26  ncq
# - listen to episodes_modified() signal instead of manual refresh
# - cleanup, renaming, pretty close to being moved to main trunk
#
# Revision 1.11  2005/02/23 03:19:02  cfmoro
# Fixed bug while refreshing leafs, using recursivity. On save, clear the editor and reutilize on future notes. Clean ups
#
# Revision 1.10  2005/02/21 23:44:59  cfmoro
# Commented out New button. Focus editor when trying to add and existing one. Clean ups
#
# Revision 1.9  2005/02/21 11:52:37  cfmoro
# Ported action of buttons to recent changes. Begin made them functional
#
# Revision 1.8  2005/02/21 10:31:11  cfmoro
# Display empty child when removing first leaf. Some clean ups
#
# Revision 1.7  2005/02/21 10:20:46  cfmoro
# Class renaming
#
# Revision 1.6  2005/02/17 17:28:14  cfmoro
# Some clean ups. Replace when initial leaf. UI fixes.
#
# Revision 1.5  2005/02/17 16:46:20  cfmoro
# Adding and removing soap editors. Simplified multisash interface.
#
# Revision 1.4  2005/02/16 11:19:12  ncq
# - better error handling
# - tabified
# - get_bottom_leaf() verified
#
