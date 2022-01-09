#!/usr/bin/python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# by: Jason Richards ~2011

import os

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

class DeskpadWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self)

		#self.startTypeHint = self.get_type_hint()
		#self.set_type_hint(Gdk.WINDOW_TYPE_HINT_TOOLBAR)

		self.opacityActive = 0.9
		self.opacityHover = 0.4
		self.opacityHidden = 0.00

		monitorNum = 0
		corner = 1
		spacing = (20, 40)
		size = (325, 1000)
		self.focused = False
		self.stuck = False

		self.set_size_request(*size)
		self.resize(*size)

		# Get all the screen size variables
		display = Gdk.Display.get_default()
		monitor = display.get_monitor(monitorNum)
		dimensions = monitor.get_workarea()
		#offset = Gdk.get_default_root_window().property_get(Gdk.atom_intern('_NET_WORKAREA'))[2]

		# Calculate the position
		if corner == 0:
			(xPos, yPos) = (dimensions.x+spacing[0], dimensions.y+spacing[1])
		elif corner == 1:
			(xPos, yPos) = (dimensions.x+dimensions.width-spacing[0]-size[0], dimensions.y+spacing[1])
		elif corner == 2:
			(xPos, yPos) = (dimensions.x+spacing[0], dimensions.y+dimensions.height-size[1]-spacing[1])
		elif corner == 3:
			(xPos, yPos) = (dimensions.x+dimensions.width-spacing[0]-size[0], dimensions.y+dimensions.height-size[1]-spacing[1])

		# if xPos < offset[0]+spacing[0]:
			# xPos = offset[0]+spacing[0]
		# if yPos < offset[1]+spacing[1]:
			# yPos = offset[1]+spacing[1]

		self.move(xPos, yPos)

		self.text = Gtk.TextView()
		self.text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
		self.text.connect('button-press-event', self.event_button_press)
		self.text.show()

		# Load it
		dataPath = '%s/deskpad.txt' % GLib.get_user_data_dir()

		if os.path.exists(dataPath):
			with open(dataPath, 'r') as fileHandle:
				self.text.get_buffer().set_text(fileHandle.read())

		scrolled = Gtk.ScrolledWindow()
		scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolled.add(self.text)
		scrolled.show()

		self.pinnedLabel = Gtk.Button(label='Unpin')
		self.pinnedLabel.connect('clicked', self.event_button_pinned)

		box = Gtk.VBox()
		box.pack_start(scrolled, True, True, 0)
		box.pack_end(self.pinnedLabel, False, True, 0)
		box.show()
		self.add(box)

		self.connect('enter-notify-event', self.event_enter_notify, True)
		self.connect('leave-notify-event', self.event_enter_notify, False)
		self.connect('focus-in-event', self.event_focus, True)
		self.connect('focus-out-event', self.event_focus, False)

		self.set_app_paintable(True)
		self.set_decorated(False)
		self.set_keep_below(True)
		self.set_resizable(False)
		self.set_role("deskpad")
		self.set_skip_pager_hint(True)
		self.set_skip_taskbar_hint(True)
		self.set_title("Desktop Notepad")
		self.set_can_focus(True)
		self.stick()

		Gtk.Window.show(self)
		self.set_opacity(self.opacityHidden)

	def event_button_pinned(self, button):
		self.pinnedLabel.hide()
		self.stuck = not self.stuck

	def event_button_press(self, widget, event):
		if event.type == Gdk.EventType._2BUTTON_PRESS:
			if not self.stuck:
				self.pinnedLabel.show()
				self.set_opacity(1)
			else:
				self.pinnedLabel.hide()

			self.stuck = not self.stuck

	def event_enter_notify(self, widget, event, entered):
		if not self.focused:
			if entered:
				self.set_opacity(self.opacityHover)
			else:
				self.set_opacity(self.opacityHidden)

	def event_focus(self, widget, direction, focused):
		self.focused = focused

		if focused:
			self.set_opacity(self.opacityActive)
		else:
			# # Save it
			# with open('%s/deskpad.txt' % GLib.get_user_data_dir(), 'w') as fileHandle:
				# fileHandle.write(self.text.get_buffer().get_text(*self.text.get_buffer().get_bounds()), True)
			self.set_opacity(self.opacityHidden)

	# We override this function to worry about self.stuck
	def set_opacity(self, opacity):
		if not self.stuck:
			Gtk.Widget.set_opacity(self, opacity)

	def destroy(self):
		Gtk.Window.destroy(self)


if __name__ == "__main__":
	DeskpadWindow()

	GLib.set_application_name('deskpad')
	GLib.set_prgname('deskpad')

	GLib.MainLoop().run()
