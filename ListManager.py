from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField

from SavedList import SavedList


class ListManager:
	def __init__(self):
		self.lists = []
		self.load()

	def add_list(self, _list: SavedList):
		self.lists.append(_list)
		self.save()

	def remove_list(self, _list: SavedList):
		self.lists.remove(_list)
		self.save()

	@staticmethod
	def clear_list(_list: SavedList):
		_list.clear_positions()

	def get_lists(self):
		return self.lists

	def get_list(self, name: str):
		for _list in self.lists:
			if _list.get_name() == name:
				return _list
		return None

	def save(self):
		store = JsonStore("lists.json")
		for _list in self.lists:
			store.clear()
			store.put(_list.get_name(), positions=[{"text": position.text, "picked": position.picked} for position in
			                                       _list.get_positions() if position.text != ""])

	def load(self):
		self.lists.clear()
		store = JsonStore("lists.json")
		for key in store.keys():
			self.lists.append(SavedList(key, store.get(key)["positions"]))

	def rename_list(self, _list: SavedList):
		def change_callback(_popup: MDDialog):
			_list.set_name(_popup.content_cls.text)
			self.save()
			_popup.dismiss()
			MDApp.get_running_app().toolbar.title = _list.get_name()

		popup = MDDialog(
				title="Rename list",
				type="custom",
				content_cls=MDTextField(
						hint_text="new name",
						text=_list.get_name(),
						),
				buttons=[
					MDFlatButton(
							text="cancel",
							on_release=lambda x: popup.dismiss()
							),
					MDFlatButton(
							text="ok",
							on_release=lambda x: change_callback(popup)
							)
					]
				)
		popup.open()
