from random import sample, randint

from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


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
