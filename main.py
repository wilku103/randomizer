from os.path import exists
from random import choice

import kivy
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty
from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

kivy.require("2.1.0")


class Position(MDLabel):
	edit = BooleanProperty(False)
	picked = BooleanProperty(False)

	textinput = ObjectProperty(None, allownone=True)

	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos) and not self.edit:
			self.edit = True
		return super(Position, self).on_touch_down(touch)

	def on_edit(self, instance, value):
		if not value:
			if self.textinput:
				self.remove_widget(self.textinput)
			return
		self.textinput = MDTextField(
				text=self.text, size_hint=(1, 1),
				font_size=self.font_size, font_name=self.font_name,
				pos=self.pos, size=self.size, multiline=False)
		self.add_widget(self.textinput)
		self.text = ""
		self.textinput.bind(focus=self.on_text_focus)

	def on_text_focus(self, instance, focus):
		if focus is False:
			if instance.text == "":
				self.parent.parent.parent.parent.get_list().remove_position(self)
				self.parent.parent.parent.parent.update()
				return

			self.text = instance.text
			self.edit = False


class NewPosition(Position):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		# self.text = "new position"
		self.edit = True
		self.textinput.hint_text = "new position"

	def on_text_focus(self, instance, focus):
		if focus is False and instance.text != "":
			self.parent.parent.parent.parent.get_list().add_position(Position(text=instance.text))
			self.parent.parent.parent.parent.update()
			self.text = ""
			self.edit = False


class SavedList:
	def __init__(self, name: str, path: str):
		self.name = name
		self.path = path
		self.positions = []

	def add_position(self, position: Position):
		self.positions.append(position)

	def remove_position(self, position: Position):
		self.positions.remove(position)

	def clear_positions(self):
		self.positions.clear()

	def get_positions(self):
		return self.positions

	def get_random_position(self):
		# choose a random position that has not been picked yet
		positions = [position for position in self.positions if not position.picked]
		if len(positions) == 0:
			return None
		position = choice(positions)
		position.picked = True
		return position

	def get_name(self):
		return self.name

	def get_path(self):
		return self.path

	def set_name(self, name: str):
		self.name = name

	def load(self):
		_list = JsonStore(self.path)
		saved_positions = _list.get("list")["positions"]
		for position in saved_positions:
			self.positions.append(
					Position(text=position["text"], picked=position["picked"]))

	def save(self):
		positions_to_save = [{"picked": child.picked, "text": child.text} for child in
		                     self.positions if child.text != ""]
		_list = JsonStore(self.path)
		_list.put("list", positions=positions_to_save)
		_list.store_sync()


class ListScreen(MDScreen):
	positions: MDGridLayout = ObjectProperty(None)
	toolbar: MDTopAppBar = ObjectProperty(None)
	_list: SavedList = ObjectProperty(None, rebind=True)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def set_list(self, _list: SavedList):
		self._list = _list

	def get_list(self):
		return self._list

	def update(self):
		self.positions.clear_widgets()
		for position in self._list.get_positions():
			self.positions.add_widget(position)
		self.positions.add_widget(NewPosition())

	def on_enter(self, *args):
		self.update()

	def on_leave(self, *args):
		self._list.save()
		self.positions.clear_widgets()


class Toolbar(MDTopAppBar):
	left_action_items = ListProperty([["arrow-left", lambda x: MDApp.get_running_app().go_back()]])


class Randomizer(MDScreen):
	lists = ListProperty([])
	corrupted_lists = ListProperty([])
	saved_lists = JsonStore("saved_lists.json")
	lists_grid: MDGridLayout = ObjectProperty(None)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.identify_lists()
		self.load_saved_lists()

	def on_enter(self, *args):
		if len(self.corrupted_lists) > 0:
			text = ""
			for name in self.corrupted_lists:
				text += f"{name}\n"
			popup = MDDialog(title="the following lists are corrupted:", text=text)

	# popup.open()

	def identify_lists(self):
		for name in self.saved_lists:
			if not exists(self.saved_lists.get(name)["path"]):
				self.corrupted_lists.append(name)
			else:
				self.lists.append(name)

	def open_list_screen(self, instance):
		_list = SavedList(name=instance.text, path=self.saved_lists.get(instance.text)["path"])
		_list.load()
		self.manager.get_screen("list").set_list(_list)
		self.manager.get_screen("list").toolbar.title = instance.text
		self.manager.transition.direction = "left"
		self.manager.current = "list"

	def load_saved_lists(self):
		for name in self.lists:
			# _list = SavedList(name=name, path=self.saved_lists.get(name)["path"])
			# _list.load()
			list_button = MDFlatButton(text=name, on_press=self.open_list_screen)
			self.lists_grid.add_widget(list_button)


class MainScreen(MDScreen):
	pass


class RandomizerApp(MDApp):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.theme_cls.primary_palette = "BlueGray"
		self.theme_cls.primary_hue = "500"
		self.theme_cls.theme_style = "Dark"

		self.manager = MDScreenManager()

	def build(self):
		self.manager.add_widget(MainScreen(name="main"))
		self.manager.add_widget(Randomizer(name="randomizer"))
		self.manager.add_widget(ListScreen(name="list"))

		return self.manager

	def go_back(self):
		self.manager.transition.direction = "right"
		self.manager.current = self.manager.previous()
		self.manager.transition.direction = "left"


if __name__ == '__main__':
	RandomizerApp().run()
