from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

from SavedList import SavedList


class Randomizer(MDScreen):
	saved_lists = JsonStore("saved_lists.json")
	lists_grid: MDGridLayout = ObjectProperty(None)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def update(self):
		self.lists_grid.clear_widgets()
		for _list in MDApp.get_running_app().lists.get_lists():
			list_button = MDFlatButton(text=_list.get_name(), on_press=self.open_list_screen)
			self.lists_grid.add_widget(list_button)

	def on_enter(self, *args):
		MDApp.get_running_app().toolbar.title = "lists"

		self.update()
		self.lists_grid.add_widget(MDFlatButton(text="new list", on_press=self.new_list))

	def on_leave(self, *args):
		MDApp.get_running_app().lists.save()

	@staticmethod
	def new_list(_):
		def create_callback(_popup: MDDialog):
			if MDApp.get_running_app().lists.get_list(_popup.content_cls.text) is not None:
				_popup.dismiss()
				_popup = MDDialog(title="list already exists")
				_popup.open()
				return
			_list = SavedList(_popup.content_cls.text)
			MDApp.get_running_app().lists.add_list(_list)
			MDApp.get_running_app().manager.get_screen("list").set_list(_list)
			MDApp.get_running_app().go_forward_to("list")
			_popup.dismiss()

		popup = MDDialog(
				title="New list",
				type="custom",
				content_cls=MDTextField(
						hint_text="name",
						),
				buttons=[
					MDFlatButton(
							text="CANCEL",
							on_release=lambda x: popup.dismiss()
							),
					MDFlatButton(
							text="OK",
							on_release=lambda x: create_callback(popup)
							)
					]
				)
		popup.open()

	@staticmethod
	def open_list_screen(instance):
		_list = MDApp.get_running_app().lists.get_list(instance.text)
		if _list is None:
			_list = SavedList(instance.text)
			MDApp.get_running_app().lists.add_list(_list)
		MDApp.get_running_app().manager.get_screen("list").set_list(_list)
		MDApp.get_running_app().go_forward_to("list")

	def delete_list(self, _list: SavedList):
		MDApp.get_running_app().go_back()
		MDApp.get_running_app().lists.delete(_list)
		self.update()
