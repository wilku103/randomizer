from kivy.properties import BooleanProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen

from NewPosition import NewPosition
from SavedList import SavedList


class ListScreen(MDScreen):
	positions: MDGridLayout = ObjectProperty(None)
	_list: SavedList = ObjectProperty(SavedList("default", None))
	skip_leave = BooleanProperty(False)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def set_list(self, _list: SavedList):
		self._list = _list
		MDApp.get_running_app().toolbar.title = _list.get_name()

	def get_list(self):
		return self._list

	def clear_list(self):
		MDApp.get_running_app().lists.clear_list(self._list)
		self.update()

	def delete_list(self):
		self.skip_leave = True
		MDApp.get_running_app().lists.remove_list(self._list)

	def update(self):
		self.positions.clear_widgets()
		for position in self._list.get_positions():
			self.positions.add_widget(position)
		self.positions.add_widget(NewPosition())

	def on_enter(self, *args):

		self.update()
		MDApp.get_running_app().menu = MDDropdownMenu(items=[
			{
				"text":       "Clear",
				"viewclass":  "OneLineListItem",
				"on_release": lambda _=None: MDApp.get_running_app().lists.clear_list(self._list)
				},
			{
				"text":       "Delete",
				"viewclass":  "OneLineListItem",
				"on_release": lambda _=None: MDApp.get_running_app().lists.remove_list(self._list)
				},
			{
				"text":       "Rename",
				"viewclass":  "OneLineListItem",
				"on_release": lambda _=None: MDApp.get_running_app().lists.rename_list(self._list)
				},
			], width_mult=4, caller=MDApp.get_running_app().toolbar)

	def on_leave(self, *args):
		MDApp.get_running_app().menu = MDDropdownMenu()
		MDApp.get_running_app().lists.save()
