from random import choice

import kivy
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.textfield import MDTextField

kivy.require("2.1.0")


class Position(MDBoxLayout):
	picked = BooleanProperty(False)
	text = StringProperty("")


class Randomizer(MDScreen):
	positions_list: MDGridLayout = ObjectProperty(None)
	list_name: MDTextField = ObjectProperty(None)
	list_path: MDTextField = ObjectProperty(None)
	input: MDTextField = ObjectProperty(None)
	saved_lists = JsonStore("saved_lists.json")

	def load_list(self, name: str):
		if name == "":
			return
		if name not in self.saved_lists:
			popup = MDDialog(title="List doesn't exist")
			popup.open()
			return
		path = self.saved_lists.get(name)["path"]
		_list = JsonStore(path)
		positions = _list.get("list")["positions"]
		for position in positions:
			self.positions_list.add_widget(
					Position(text=position["text"], picked=position["picked"], size_hint_y=None, height=50))

	def save_list(self, name: str):
		if name == "":
			return
		if name in self.saved_lists:
			popup = MDDialog(title="List already exists", text="List already exists, please choose another name",
			                 size_hint=(None, None),
			                 size=(400, 400))
			popup.open()
			return
		positions = [{"picked": child.picked, "text": child.text} for child in reversed(self.positions_list.children)]
		self.saved_lists.put(name, path=f"lists/{name}.txt")
		_list = JsonStore(f"lists/{name}.txt")
		_list.put("list", positions=positions)
		_list.store_sync()

	def add_position(self, text: str):
		if text == "":
			return
		self.positions_list.add_widget(Position(text=text, size_hint_y=None, height=50))
		self.input.text = ""  # clear the input

	def clear_list(self):
		if len(self.positions_list.children) == 0:
			return
		self.positions_list.clear_widgets()

	def print_random_child(self):
		if len(self.positions_list.children) == 0:
			return
		can_be_picked = [child for child in self.positions_list.children if not child.picked]

		# if no positions left, show a popup
		if len(can_be_picked) == 0:
			popup = MDDialog(title="No positions left", text="All positions have been picked",
			                 size_hint=(None, None),
			                 size=(400, 400))
			popup.open()
			return

		picked_child = choice(can_be_picked)
		picked_child.picked = True

		# create a popup with the picked child text
		popup = MDDialog(title="Picked position", text=picked_child.text, size_hint=(None, None),
		                 size=(400, 400))
		popup.open()

	def import_from_txt(self, path: str):
		with open(path, "r") as f:
			for line in f:
				self.add_position(line)


class MainScreen(MDScreen):
	pass


class RandomizerApp(MDApp):
	def build(self):
		manager = MDScreenManager()
		manager.add_widget(MainScreen(name="main"))
		manager.add_widget(Randomizer(name="randomizer"))

		return manager


if __name__ == '__main__':
	RandomizerApp().run()
