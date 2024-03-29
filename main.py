import kivy
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar

from ListManager import ListManager
from screens.ListScreen import ListScreen
from screens.RandomNumber import RandomNumber
from screens.Randomizer import Randomizer
from screens.Wheel import Wheel

kivy.require("2.1.0")


class MainScreen(MDScreen):
	pass


class RandomizerApp(MDApp):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.theme_cls.primary_palette = "BlueGray"
		self.theme_cls.primary_hue = "500"
		self.theme_cls.theme_style = "Dark"

		self.manager: MDScreenManager = MDScreenManager()
		self.screen_stack = ["main"]

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
		self.manager.add_widget(Wheel(name="wheel"))

		self.root = MDBoxLayout(orientation="vertical")
		self.root.add_widget(self.toolbar)
		self.root.add_widget(self.manager)

		return self.root

	def go_back(self):
		if len(self.screen_stack) == 1:
			return
		self.manager.transition.direction = "right"
		self.manager.current = self.screen_stack.pop()

	def go_forward_to(self, screen_name):
		self.screen_stack.append(self.manager.current)
		self.manager.transition.direction = "left"
		self.manager.current = screen_name

	def open_menu(self):
		self.menu.open()


if __name__ == '__main__':
	RandomizerApp().run()
