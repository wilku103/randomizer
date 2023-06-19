from os import remove
from os.path import exists
from random import choice, randint, sample

import kivy
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty
from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

kivy.require("2.1.0")


# class Toolbared(MDWidget):
# 	def __init__(self, **kwargs):
# 		super().__init__(**kwargs)
# 		self.toolbar = MDTopAppBar(left_action_items=[["arrow-left", lambda x: MDApp.get_running_app().go_back()]],
# 		                           right_action_items=[["dots-vertical", lambda x: self.open_menu()]])
# 		self.toolbar_menu = None
# 		self.add_widget(self.toolbar)
#
# 	def open_menu(self):
# 		self.toolbar_menu.open()


class Position(MDLabel):
	edit = BooleanProperty(False)
	picked = BooleanProperty(False)

	textinput = ObjectProperty(None, allownone=True)

	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos) and not self.edit:
			self.edit = True
		return super(Position, self).on_touch_down(touch)

	def on_edit(self, _, value):
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
		self.edit = True
		self.textinput.hint_text = "new position"

	def on_text_focus(self, instance, focus):
		if focus is False and instance.text != "":
			self.parent.parent.parent.parent.get_list(
					).add_position(Position(text=instance.text))
			self.parent.parent.parent.parent.update()
			self.text = ""
			self.edit = False


class SavedList:
	def __init__(self, name: str):
		self.name = name
		self.path = f"lists/{name}.json"
		self.positions = []

		if exists(self.path):
			self.load()

	def add_position(self, position: Position):
		self.positions.append(position)

	def remove_position(self, position: Position):
		self.positions.remove(position)

	def clear_positions(self):
		self.positions.clear()

	def get_positions(self):
		return self.positions

	def get_random_position(self):
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

		saved_lists = JsonStore("saved_lists.json")
		if not saved_lists.exists(self.name):
			saved_lists.put(self.name, name=self.name, path=self.path)
			saved_lists.store_sync()


class ListScreen(MDScreen):
	positions: MDGridLayout = ObjectProperty(None)
	_list: SavedList = ObjectProperty(SavedList("default"))

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def set_list(self, _list: SavedList):
		self._list = _list
		MDApp.get_running_app().toolbar.title = _list.get_name()

	def get_list(self):
		return self._list

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
				"on_release": self._list.clear_positions
				},
			{
				"text":       "Delete",
				"on_release": lambda _: MDApp.get_running_app().manager.get_screen("randomizer").delete_list(self._list)
				}
			], width_mult=4, caller=MDApp.get_running_app().toolbar)

	def on_leave(self, *args):
		self._list.save()
		self.positions.clear_widgets()


class Randomizer(MDScreen):
	lists = ListProperty([])
	corrupted_lists = ListProperty([])
	saved_lists = JsonStore("saved_lists.json")
	lists_grid: MDGridLayout = ObjectProperty(None)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def update(self):
		self.identify_lists()
		self.lists_grid.clear_widgets()
		for name in self.lists:
			list_button = MDFlatButton(text=name, on_press=self.open_list_screen)
			self.lists_grid.add_widget(list_button)

	def on_enter(self, *args):
		MDApp.get_running_app().toolbar.title = "lists"

		self.update()

		if len(self.corrupted_lists) > 0:
			text = ""
			for name in self.corrupted_lists:
				text += f"{name}\n"
			popup = MDDialog(title="the following lists are corrupted:", text=text)
			popup.open()
		self.add_widget(MDFlatButton(text="new list", on_press=self.open_list_screen))

	def identify_lists(self):
		self.lists.clear()

		for name in self.saved_lists:
			if not exists(self.saved_lists.get(name)["path"]):
				self.corrupted_lists.append(name)
			else:
				self.lists.append(name)

	def open_list_screen(self, instance):
		_list = SavedList(name=instance.text)
		self.manager.get_screen("list").set_list(_list)
		MDApp.get_running_app().go_forward_to("list")

	def delete_list(self, _list: SavedList):
		MDApp.get_running_app().go_back()
		if exists(_list.get_path()):
			remove(_list.get_path())
		if self.saved_lists.exists(_list.get_name()):
			self.saved_lists.delete(_list.get_name())
		if _list.get_name() in self.lists:
			self.lists.remove(_list.get_name())
		self.lists_grid.clear_widgets()
		self.update()


class RandomNumber(MDScreen):
	numbers = ObjectProperty(None)

	def on_enter(self, *args):
		MDApp.get_running_app().toolbar.title = "random number"

	def get_numbers(self, min_val: int, max_val: int, amount: int, unique: bool):

		if min_val > max_val:
			self.numbers.text = "min value must be smaller than max value"
			return
		if unique and amount > max_val - min_val + 1:
			self.numbers.text = "amount must be smaller than range"
			return

		if unique:
			num_list = sample(range(min_val, max_val + 1), amount)
		else:
			num_list = [randint(min_val, max_val) for _ in range(amount)]

		num_list.sort()
		self.numbers.text = str(num_list)[1:-1]


class MainScreen(MDScreen):
	pass


class RandomizerApp(MDApp):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.theme_cls.primary_palette = "BlueGray"
		self.theme_cls.primary_hue = "500"
		self.theme_cls.theme_style = "Dark"

		self.manager = MDScreenManager()
		self.toolbar = MDTopAppBar(title="Randomizer", elevation=10, pos_hint={"top": 1},
		                           left_action_items=[["arrow-left", lambda x: self.go_back()]],
		                           right_action_items=[["dots-vertical", lambda x: self.open_menu()]])
		self.menu = MDDropdownMenu(width_mult=4, caller=self.toolbar)

	def build(self):
		self.manager.add_widget(MainScreen(name="main"))
		self.manager.add_widget(Randomizer(name="randomizer"))
		self.manager.add_widget(ListScreen(name="list"))
		self.manager.add_widget(RandomNumber(name="random_number"))

		self.root = MDBoxLayout(orientation="vertical")
		self.root.add_widget(self.toolbar)
		self.root.add_widget(self.manager)

		return self.root

	def go_back(self):
		self.manager.transition.direction = "right"
		self.manager.current = self.manager.previous()

	def go_forward_to(self, screen):
		self.manager.transition.direction = "left"
		self.manager.current = screen

	def open_menu(self):
		self.menu.open()


if __name__ == '__main__':
	RandomizerApp().run()
