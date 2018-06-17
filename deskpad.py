#!/usr/bin/python2
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
import gtk
import glib
import gobject


class DeskpadWindow(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self)

		#self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_TOOLBAR)

		self.opacityActive = 0.9
		self.opacityHover = 0.5
		self.opacityHidden = 0.02

		monitor = 0
		corner = 1
		spacing = (20, 40)
		size = (325, 1000)
		self.focused = False
		self.stuck = False

		self.set_size_request(*size)
		self.resize(*size)

		# Get all the screen size variables
		offset = gtk.gdk.get_default_root_window().property_get(gtk.gdk.atom_intern('_NET_WORKAREA'))[2]
		dimensions = list(gtk.gdk.screen_get_default().get_monitor_geometry(monitor))

		# Calculate the position
		if corner == 0:
			(xPos, yPos) = (dimensions[0]+spacing[0], dimensions[1]+spacing[1])
		elif corner == 1:
			(xPos, yPos) = (dimensions[0]+dimensions[2]-spacing[0]-size[0], dimensions[1]+spacing[1])
		elif corner == 2:
			(xPos, yPos) = (dimensions[0]+spacing[0], dimensions[1]+dimensions[3]-size[1]-spacing[1])
		elif corner == 3:
			(xPos, yPos) = (dimensions[0]+dimensions[2]-spacing[0]-size[0], dimensions[1]+dimensions[3]-size[1]-spacing[1])

		if xPos < offset[0]+spacing[0]:
			xPos = offset[0]+spacing[0]
		if yPos < offset[1]+spacing[1]:
			yPos = offset[1]+spacing[1]

		self.move(xPos, yPos)

		self.text = gtk.TextView()
		self.text.set_wrap_mode(gtk.WRAP_WORD_CHAR)
		self.text.connect('button-press-event', self.event_button_press)
		self.text.show()

		# Load it
		dataPath = '%s/deskpad.txt' % glib.get_user_data_dir()

		if os.path.exists(dataPath):
			with open(dataPath, 'rb') as fileHandle:
				self.text.get_buffer().set_text(fileHandle.read())

		scrolled = gtk.ScrolledWindow()
		scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolled.add(self.text)
		scrolled.show()

		self.pinnedLabel = gtk.Button('Unpin')
		self.pinnedLabel.connect('clicked', self.event_button_pinned)

		box = gtk.VBox()
		box.pack_start(scrolled)
		box.pack_end(self.pinnedLabel, False, True)
		box.show()
		self.add(box)

		self.set_opacity(self.opacityHidden)

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

		gtk.Window.show(self)

	def event_button_pinned(self, button):
		self.pinnedLabel.hide()
		self.stuck = not self.stuck

	def event_button_press(self, widget, event):
		if event.type == gtk.gdk._2BUTTON_PRESS:
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
			# Save it
			with open('%s/deskpad.txt' % glib.get_user_data_dir(), 'wb') as fileHandle:
				fileHandle.write(self.text.get_buffer().get_text(*self.text.get_buffer().get_bounds()))
			self.set_opacity(self.opacityHidden)

	def set_opacity(self, opacity):
		if not self.stuck:
			gtk.Window.set_opacity(self, opacity)

	def destroy(self):
		gtk.Window.destroy(self)


if __name__ == "__main__":
	DeskpadWindow()

	gobject.threads_init()
	gobject.set_application_name('deskpad')
	gobject.set_prgname('deskpad')

	glib.MainLoop().run()
