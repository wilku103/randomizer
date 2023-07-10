import kivy
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar

from ListManager import ListManager
from ListScreen import ListScreen
from RandomNumber import RandomNumber
from Randomizer import Randomizer

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
		self.manager.switch_to(self.manager.previous(), direction="right")

	def go_forward_to(self, screen_name):
		self.manager.switch_to(self.manager.get_screen(screen_name), direction="left")

	def open_menu(self):
		self.menu.open()


if __name__ == '__main__':
	RandomizerApp().run()
