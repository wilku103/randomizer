from random import choice

import kivy
from kivy.app import App
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

kivy.require("2.1.0")


class PickedPopup(Popup):
	text = StringProperty("")


class Position(BoxLayout):
	picked = BooleanProperty(False)
	text = StringProperty("")


class Randomizer(GridLayout):
	labels_list: GridLayout = ObjectProperty(None)
	list_name: TextInput = ObjectProperty(None)
	list_path: TextInput = ObjectProperty(None)
	input: TextInput = ObjectProperty(None)
	saved_lists = JsonStore("saved_lists.json")

	def load_list(self, name: str):
		if name == "":
			return
		if name not in self.saved_lists:
			popup = PickedPopup(title="List doesn't exist", text="List doesn't exist",
								size_hint=(None, None),
								size=(400, 400))
			popup.open()
			return
		path = self.saved_lists.get(name)["path"]
		_list = JsonStore(path)
		positions = _list.get("list")["positions"]
		for position in positions:
			self.labels_list.add_widget(
					Position(text=position["text"], picked=position["picked"], size_hint_y=None, height=50))

	def save_list(self, name: str):
		if name == "":
			return
		if name in self.saved_lists:
			popup = PickedPopup(title="List already exists", text="List already exists, please choose another name",
								size_hint=(None, None),
								size=(400, 400))
			popup.open()
			return
		positions = [{"picked": child.picked, "text": child.text} for child in reversed(self.labels_list.children)]
		self.saved_lists.put(name, path=f"lists/{name}.txt")
		_list = JsonStore(f"lists/{name}.txt")
		_list.put("list", positions=positions)
		_list.store_sync()

	def add_position(self, text: str):
		if text == "":
			return
		self.labels_list.add_widget(Position(text=text, size_hint_y=None, height=50))
		self.input.text = ""  # clear the input

	def clear_list(self):
		if len(self.labels_list.children) == 0:
			return
		self.labels_list.clear_widgets()

	def print_random_child(self):
		if len(self.labels_list.children) == 0:
			return
		can_be_picked = [child for child in self.labels_list.children if not child.picked]

		if len(can_be_picked) == 0:
			popup = PickedPopup(title="No positions left", text="All positions have been picked",
								size_hint=(None, None),
								size=(400, 400))
			popup.open()
			return
		picked_child = choice(can_be_picked)
		picked_child.picked = True

		# create a popup with the picked child text
		popup = PickedPopup(title="Picked position", text=picked_child.text, size_hint=(None, None),
							size=(400, 400))
		popup.open()

	def import_from_txt(self, path: str):
		with open(path, "r") as f:
			for line in f:
				self.add_position(line)


class RandomizerApp(App):
	def build(self):
		return Randomizer()

	def on_stop(self):
		pass


if __name__ == '__main__':
	RandomizerApp().run()
