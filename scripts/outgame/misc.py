import csv
from scripts.ingame import utils

class Map:
	from_ = 'from'
	to_ = 'to'
	height_ = 'height'
	def __init__(self, map_csv):
		reader = csv.DictReader(map_csv)
		self.walls = []
		for line in reader:
			self.walls.append(line)
			line[Map.from_] = utils.Utils.int_tuple(line[Map.from_].split(';'))
			line[Map.to_] = utils.Utils.int_tuple(line[Map.to_].split(';'))
			if line[Map.height_] != '':
				line[Map.height_] = int(line[Map.height_])
		self.spawns = self.walls[-2:]
		self.walls = self.walls[:-2]

from tkinter import Frame, Text, Scrollbar, Pack, Grid, Place
from tkinter.constants import RIGHT, LEFT, Y, BOTH

class ScrolledText(Text):
	def __init__(self, master=None, **kw):
		self.frame = Frame(master)
		self.vbar = Scrollbar(self.frame)
		self.vbar.pack(side=RIGHT, fill=Y)

		kw.update({'yscrollcommand': self.vbar.set})
		Text.__init__(self, self.frame, **kw)
		self.pack(side=LEFT, fill=BOTH, expand=True)
		self.vbar['command'] = self.yview

		text_meths = vars(Text).keys()
		methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
		methods = methods.difference(text_meths)

		for m in methods:
			if m[0] != '_' and m != 'config' and m != 'configure':
				setattr(self, m, getattr(self.frame, m))

	def __str__(self):
		return str(self.frame)