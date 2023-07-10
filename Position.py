from kivy.properties import BooleanProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField


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
				screen = MDApp.get_running_app().manager.get_screen("list")
				screen.get_list().remove_position(self)
				screen.update()
				return

			self.text = instance.text
			self.edit = False
