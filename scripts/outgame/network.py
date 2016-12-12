#!/usr/bin/python
# -*- coding: utf-8 -*-
from io import BytesIO
from message import Message
import socket
import datetime
import time
import pickle
from socket import error as socket_error


def add_zero(value):
	res = str(value)
	if len(res) == 1:
		res = '0' + res
	return res


class Network:

	PORT = 10000
	BUFFER = 1024
	END = pickle.dumps(None)

	def get_ip():

		# Require Internet

		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.connect(('8.8.8.8', 0))
			return s.getsockname()[0]
		except Exception:
			return None

	def send(sock, object_):
		sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		sock.sendall(pickle.dumps(object_))
		sock.sendall(Network.END)

	def is_no_data(buf):
		buf.seek(-len(Network.END), 2)
		if buf.read() == Network.END:
			return True
		return False

	def recv(sock):
		buf = BytesIO()
		while True:
			data = sock.recv(Network.BUFFER)
			buf.write(data)
			if Network.is_no_data(buf):
				break
		buf.seek(0)
		return pickle.loads(buf.read())


class Server:

	UPDATE_ROUTINE = 10000
	ARTY = 'ARTY_UPDATE'

	def __init__(self, team_config, ip):
		self.server_map = None
		self.update_msg = {}
		self.update_msg[team_config.host_name] = []
		self.up_to_date = {}
		self.up_to_date[team_config.host_name] = True
		self.team_config = team_config
		self.ip = ip
		self.server_address = (self.ip, Network.PORT)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.server_address)

	def start(self):
		print ('Start listening on', Network.PORT, 'at', self.ip)
		self.sock.listen(self.team_config.MAX_PLAYER_PER_TEAM * 2 + 1)
		self.stop = False
		while not self.stop:
			(connection, client_address) = self.sock.accept()
			# print ('Connection from', client_address)
			try:
				msg = Network.recv(connection)
				self.handle(connection, msg)
			finally:

			# except Exception as error:
			# ....print('Host ended')

				connection.close()

	def reset_up_to_date(self):
		for name in self.up_to_date:
			self.up_to_date[name] = False

	def handle(self, connection, msg):
		request = msg[0]
		if request == Message.JOIN:
			name = msg[1]
			if self.team_config.is_full():
				Network.send(connection, Message.refuse(Message.FULL))
			elif self.team_config.is_player_in(name):
				Network.send(connection,
							 Message.refuse(Message.SAME_NAME))
			elif self.team_config.is_start:
				Network.send(connection,
							 Message.refuse(Message.STARTED))
			else:
				self.team_config.add_player(name,
						self.team_config.NOT_READY)
				self.reset_up_to_date()
				Network.send(connection,
							 Message.accept(self.team_config))
				self.up_to_date[name] = True
				self.update_msg[name] = []
		elif request == Message.QUIT:
			name = msg[1]
			self.team_config.remove_player(name)
			self.up_to_date.pop(name)
			self.update_msg.pop(name)
			self.reset_up_to_date()
			Network.send(connection, Message.accept())
		elif request == Message.UPDATE:
			name = msg[1]
			if not self.team_config.is_start:
				if name not in self.up_to_date:
					return
				if not self.up_to_date[name]:
					Network.send(connection,
								 Message.accept(self.team_config,
								 *self.update_msg[name]))
					self.update_msg[name] = []
					self.up_to_date[name] = True
				else:
					Network.send(connection, Message.accept(None))
			else:
				Network.send(connection,
							 Message.update((self.server_map,
							 self.team_config)))
		elif request == Message.UPDATE_TEAM_CONFIG:
			player = msg[1]
			data = self.team_config.players[player['name']]
			isUpdate = False
			if player['color'] != data['color'] \
				and self.team_config.is_change_color_possible(player['name'
					], player['color']):
				isUpdate = True
				data['color'] = player['color']
			if player['tank'] != data['tank']:
				isUpdate = True
				data['tank'] = player['tank']
			if player['team'] != data['team'] \
				and self.team_config.is_change_team_possible(player['name'
					]):
				isUpdate = True
				self.team_config.change_team(player['name'])
			if player['status'] != data['status']:
				isUpdate = True
				data['status'] = player['status']
			if isUpdate:
				self.reset_up_to_date()
			Network.send(connection, Message.accept())
		elif request == Message.UPDATE_MAP:
			self.server_map = msg[1]
			Network.send(connection, Message.accept())
		elif request == Message.CHAT:
			name = msg[1]
			text = msg[2]
			now = datetime.datetime.now()
			message = \
				'{hour}:{min}:{sec} [{name}] {text}'.format(hour=add_zero(now.hour),
					min=add_zero(now.minute), sec=add_zero(now.second),
					name=name, text=text)
			for li in self.update_msg.values():
				li.append(message)
			self.reset_up_to_date()
			Network.send(connection, Message.accept())
		elif request == Message.START:
			self.team_config.place_players(self.server_map)
			self.team_config.is_start = True
			self.index_frame = {}
			for name in self.team_config.players:
				self.index_frame[name] = 0
			self.data_frame = {0: {}}
			self.edit = 1
			self.last_delete = time.time() * 1000
			self.last_index = 0
			Network.send(connection, Message.accept())
		elif request == Message.UPDATE_GAME_INPUT:
			name = msg[1]
			pressed = msg[2]
			data_frame = []
			for i in range(self.index_frame[name], self.edit):
				data_frame.append(self.data_frame[i])
			if self.index_frame[name] == self.edit:
				data_frame.append(self.data_frame[self.edit])
			Network.send(connection, Message.update(data_frame))
			self.index_frame[name] += len(data_frame)
			# print('NAME',name,'FRAME AT',self.index_frame[name])
			self.edit = max(self.edit, self.index_frame[name])
			if self.edit not in self.data_frame:
				self.data_frame[self.edit] = {}
			self.data_frame[self.edit][name] = pressed
			now = time.time() * 1000
			if now - self.last_delete > Server.UPDATE_ROUTINE:
				self.last_delete = now
				min_dex = min(self.index_frame.values())
				for index in range(self.last_index, min_dex):
					self.data_frame.pop(index)
				self.last_index = min_dex
		elif request == Message.UPDATE_ARTY:
			arty = msg[1]
			if Server.ARTY not in self.data_frame[self.edit]:
				self.data_frame[self.edit][Server.ARTY] = []
			self.data_frame[self.edit][Server.ARTY].append(arty)
			Network.send(connection, Message.accept())


class Client:

	def __init__(self, server_ip, master):
		self.server_ip = server_ip
		self.master = master
		self.server_address = (server_ip, Network.PORT)
		self.is_quit = False

	def add_master(self, master):
		self.master = master

	def send(self, object_):
		msg = None
		try:
			self.sock = socket.socket(socket.AF_INET,
					socket.SOCK_STREAM)
			self.sock.setsockopt(socket.IPPROTO_TCP,
								 socket.TCP_NODELAY, 1)
			self.sock.connect(self.server_address)
			Network.send(self.sock, object_)
			msg = Network.recv(self.sock)
		except socket_error:
			self.master.handle_bad_host()
			print ('Unable to connect the server')
		finally:
			self.sock.close()
			return msg

	def handle_join(self, msg):
		result = msg[0]
		if result == Message.ACCEPT:
			team_config = msg[1]
			self.master.init_team_config(team_config)
		elif result == Message.REFUSE:
			reason = msg[1]
			self.master.handle_reason(reason)

	def identify(self):
		msg = self.send(Message.join(self.master.owner))
		if msg == None:
			return False
		else:
			self.handle_join(msg)
			return True

	def request_update(self, package=None):
		if self.is_quit:
			return
		msg = None
		try:
			self.sock_update = socket.socket(socket.AF_INET,
					socket.SOCK_STREAM)
			self.sock_update.setsockopt(socket.IPPROTO_TCP,
					socket.TCP_NODELAY, 1)
			self.sock_update.connect(self.server_address)
			if package == None:
				Network.send(self.sock_update,
							 Message.update(self.master.owner))
			else:
				Network.send(self.sock_update,
							 Message.update_game_input(self.master.owner,
							 package))
			msg = Network.recv(self.sock_update)
		except socket_error:
			self.master.handle_bad_host()
			print ('Unable to connect the server')
		finally:
			self.sock_update.close()
			self.master.handle_update(msg)



			