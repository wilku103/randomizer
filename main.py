from random import randint, sample
from typing import Dict

import kivy
from kivy.properties import ObjectProperty, BooleanProperty
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


class Position(MDLabel):
	edit = BooleanProperty(False)
	picked = BooleanProperty(False)

	textinput = ObjectProperty(None, allownone=True)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.size_hint_y = None
		self.height = 50
		self.halign = "center"

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
				pos=self.pos, size=self.size, halign=self.halign, multiline=False)
		self.add_widget(self.textinput)
		self.text = ""
		self.textinput.bind(focus=self.on_text_focus)

	def on_text_focus(self, instance, focus):
		if focus is False:
			if instance.text == "":
				screen: ListScreen = MDApp.get_running_app().manager.get_screen("list")
				screen.get_list().remove_position(self)
				screen.update()
				return

			self.text = instance.text
			self.edit = False


class NewPosition(MDTextField):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.text = ""
		self.hint_text = "new position"
		self.multiline = False
		self.size_hint_y = None
		self.height = 50
		self.halign = "center"

	def on_focus(self, instance, focus):
		if focus is False and instance.text != "":
			screen: ListScreen = MDApp.get_running_app().manager.get_screen("list")
			screen.get_list(
					).add_position(Position(text=instance.text))
			screen.update()
			self.text = ""


class SavedList:
	def __init__(self, name: str, _positions: list[Dict] = None):
		self.name = name
		if _positions is None:
			self.positions = []
		else:
			self.positions = [Position(**position) for position in _positions]

	def add_position(self, position: Position):
		self.positions.append(position)

	def remove_position(self, position: Position):
		self.positions.remove(position)

	def clear_positions(self):
		self.positions.clear()

	def get_positions(self):
		return self.positions

	def get_random_position(self, count=1, unique=False):
		picked = []
		if unique:
			positions = [position for position in self.positions if not position.picked]
			if len(positions) == 0:
				return None
			elif len(positions) < count:
				count = len(positions)
			picked = sample(positions, count)
			for position in picked:
				position.picked = True
		else:
			picked = sample(self.positions, count)

		text = "\n".join([position.text for position in picked])
		popup = MDDialog(
				title="Random Position", text=text,
				buttons=[MDFlatButton(text="OK", on_release=lambda _: popup.dismiss())])
		popup.open()

	def get_name(self):
		return self.name

	def set_name(self, name: str):
		self.name = name


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
		self.menu = MDDropdownMenu()

		self.lists: ListManager = ListManager()

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
