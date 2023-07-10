from random import sample
from typing import Dict

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from Position import Position


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

	def reset_picked(self, _, value):
		if not value:
			for position in self.positions:
				position.picked = False
