from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.textfield import MDTextField

from Position import Position


class NewPosition(MDTextField):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.text = ""
		self.hint_text = "new position"
		self.multiline = False
		self.size_hint_y = None
		self.height = 50
		self.halign = "center"
		Clock.schedule_once(self.focus_text_input, 0.1)
		
	def focus_text_input(self, _):
		self.focus = True

	def on_focus(self, instance, focus):
		if focus is False and instance.text != "":
			screen = MDApp.get_running_app().manager.get_screen("list")
			screen.get_list(
					).add_position(Position(text=instance.text))
			screen.update()
			self.text = ""
