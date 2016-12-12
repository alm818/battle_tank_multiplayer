import tkinter as tk
from tkinter import messagebox
from message import Message
from frame import Team_Room
from network import Server, Client
from team_config import Team_Config
from scripts.ingame import pgame, setting
from misc import Map
import threading, time, copy, sys

class Master(tk.Tk):
	SPF = setting.Setting.Window.MSPF / 1000
	def __init__(self):
		super().__init__()
		self.resizable(False, False)
		self.protocol("WM_DELETE_WINDOW", self.handle_quit)
		self.is_start = False
		self.owner = None
	def start_request(self):
		previous = time.time()
		self.thread.stop = False
		while not self.thread.stop:
			now = time.time()
			if now - previous > Master.SPF:
				previous = now
				if not self.is_start:
					self.client.request_update()
					pong = time.time()
					# print('Before start Ping',(pong - now) * 1000,'ms')
				else:
					if self.p_game.pressed != None:
						self.client.request_update(self.p_game.pressed)
					if self.p_game.globe.arty != None:
						self.client.send(Message.update_arty(self.p_game.globe.arty))
					# pong = time.time()
					# print('Ping',(pong - now) * 1000,'ms')
					self.p_game.frameize(self.list_dic_pressed)
					# print('Process',(time.time() - pong) * 1000,'ms')
	def host(self, owner, ip):
		try:
			self.owner = owner
			self.team_config = Team_Config(owner)
			self.server = Server(copy.deepcopy(self.team_config), ip)
			self.client = Client(self.server.ip, self)
			self.team_room = Team_Room(self, self.team_config, self.server.ip, owner)
			self.server_thread = threading.Thread(target=self.server.start)
			self.thread = threading.Thread(target=self.start_request)
			self.server_thread.start()
			self.thread.start()
			return True
		except Exception:
			return False
	def join(self, owner, host):
		self.owner = owner
		self.server_ip = host
		self.client = Client(self.server_ip, self)
		res = self.client.identify()
		if res == False:
			messagebox.showerror("Unable to join", "Bad IP or host does not exist")
	def handle_bad_host(self):
		messagebox.showerror("Unable to connect host", "Connection error")
		self.client.is_quit = True
		self.thread.stop = True
		self.destroy()
	def handle_reason(self, reason):
		if reason == Message.FULL:
			messagebox.showerror("Unable to join", "Waiting room is full")
		elif reason == Message.SAME_NAME:
			messagebox.showerror("Unable to join", "Someone already has that name")
		elif reason == Message.STARTED:
			messagebox.showerror("Unable to join", "Game has been started")
	def handle_chat(self, text):
		self.client.send(Message.chat(self.owner, text))
	def handle_update(self, msg):
		if msg == None:
			return
		request = msg[0]	
		if request == Message.ACCEPT:
			package = msg[1]
			if package == None:
				return
			elif type(package) == Team_Config:
				self.team_config = package
				self.team_room.update(package, msg[2:])
		elif request == Message.UPDATE:
			package = msg[1]
			if type(package) == tuple:
				self.team_config = package[1]
				self.p_game = pgame.Pgame(self.client, self.team_config, self.owner, package[0])
				self.is_start = True
				self.list_dic_pressed = None
			else:
				self.list_dic_pressed = package
	def handle_quit(self):
		result = messagebox.askquestion("Quitting", "Are You Sure?", icon='warning')
		if result == 'yes':
			if self.owner != None:
				msg = self.client.send(Message.quit(self.owner))
				self.client.is_quit = True
				if self.owner == self.team_config.host_name:
					self.server.stop = True
				self.thread.stop = True
			self.destroy()
	def handle_player_change(self, player):
		self.client.send(Message.update_team_config(player))
	def init_team_config(self, team_config):
		self.team_config = team_config
		self.child.destroy()
		self.team_room = Team_Room(self, self.team_config, self.server_ip, self.team_config.host_name)
		self.thread = threading.Thread(target=self.start_request)
		self.thread.start()
	def start_game(self):
		self.client.send(Message.start())
	def handle_map(self, file_name):
		map_csv = open(file_name)
		server_map = Map(map_csv)
		self.client.send(Message.update_map(server_map))
