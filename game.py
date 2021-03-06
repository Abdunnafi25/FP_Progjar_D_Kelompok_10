from typing import Counter
import pygame_textinput
import pygame
from network import Network
import pickle
import os

class Player:

	def __init__(self, color):
		self.color = color
		self.biji = [7, 7, 7, 7, 7, 7, 7]
		self.poin = 0
		self.lubang = []
		self.tanda = [False, False, False, False, False, False, False]

	def draw(self, g, color, x, y, gap, radius, border):
		for i in range(7):
			xx = x + (i * gap)
			yy = y
			self.lubang.append(pygame.draw.circle(g, color, (xx, yy), radius, border))

	def check_collision(self):
		if self.lubang[0].collidepoint(pygame.mouse.get_pos()) or self.lubang[1].collidepoint(pygame.mouse.get_pos()) or \
			self.lubang[2].collidepoint(pygame.mouse.get_pos()) or self.lubang[3].collidepoint(pygame.mouse.get_pos()) or \
			self.lubang[4].collidepoint(pygame.mouse.get_pos()) or self.lubang[5].collidepoint(pygame.mouse.get_pos()) or \
			self.lubang[6].collidepoint(pygame.mouse.get_pos()):
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
		else:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

class Game:

	def __init__(self, w, h):
		self.net = Network()
		self.width = w
		self.height = h
		self.animate = False
		self.brown_color = (198, 139, 89)
		self.bg_color = (134, 84, 57)
		self.bg_contrast = (255, 255, 255)
		self.on_color = (0, 255, 0)
		self.canvas = Canvas(self.width, self.height, "Congklak")
		self.inputUsername = pygame.image.load(r'assets/Username.png')
		self.dashboard = pygame.image.load(r'assets/Dashboard.png')
		self.leaderboard = pygame.image.load(r'assets/Leaderboard.png')
		self.winCondition = pygame.image.load(r'assets/Win.png')
		self.loseCondition = pygame.image.load(r'assets/Lose.png')
		self.tieCondition = pygame.image.load(r'assets/Tie.png')
		self.playing = pygame.image.load(r'assets/Playing.png')
		self.waitingRoom = pygame.image.load(r'assets/WaitingRoom.png')
		self.me = Player((255, 0, 0))
		self.rival = Player((0, 0, 255))
		self.rival_move = -1
		self.turn = 'me'
		self.me.draw(self.canvas.get_canvas(), self.me.color, 125, 280, 52, 25, 2)
		self.rival.draw(self.canvas.get_canvas(), self.rival.color, 125, 220, 52, 25, 2)
		self.poin_not_sent = True
		self.leaderboard_not_asked = True
		self.chat_ongoing = False
		self.chat = []
		self.chat_color = (255, 0, 0)
		self.penanda_chat = 0

		# textbox input username
		pygame.font.init()
		self.user_text = ''
		self.rival_text = ''
		self.textinput = pygame_textinput.TextInput()
		self.chatinput = pygame_textinput.TextInput()

	def run(self):
		clock = pygame.time.Clock()
		run = True
		flag = 4
		warna = ''
		cek = 0
		while run:
			clock.tick(30)

			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONUP:
					None

				if event.type == pygame.QUIT:
					run = False

				if event.type == pygame.K_ESCAPE:
					run = False

			# Update Canvas
			self.canvas.draw_background()
			self.canvas.draw_image(pygame.transform.scale(self.playing, (700, 700)), (0, 0))
			# menggambar lingkaran
			# menggambar jumlah biji
			if(self.animate == False):
				self.me.draw(self.canvas.get_canvas(), self.bg_color, 200, 340, 52, 25, 2)
				self.rival.draw(self.canvas.get_canvas(), self.bg_color, 200, 278, 52, 25, 2)
				for i in range(7):
					self.canvas.draw_text(str(self.me.biji[i]), 22, 190 + (i * 52), 327, self.me.color,"copse.ttf")
				for i in range(7):
					self.canvas.draw_text(str(self.rival.biji[i]), 22, 190 + (i * 52), 265, self.rival.color, "copse.ttf")
				self.canvas.draw_text(str(self.me.poin), 22, 554, 296, self.me.color,"copse.ttf")
				self.canvas.draw_text(str(self.rival.poin), 22, 134, 296, self.rival.color,"copse.ttf")
				pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (145, 308), 30, 2)
				pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (565, 308), 30, 2)

			if(flag == 1):
				self.canvas.draw_background()
				pesan = self.send_data('status')
				self.canvas.draw_image(pygame.transform.scale(self.waitingRoom, (700, 700)), (0, 0))
				print(pesan)
				if(pesan == 'start'):
					print('done')
					flag = 0
					pesan = self.net.client.recv(2048).decode()
					turn = pesan.split(':')[0]
					player1 = pesan.split(':')[1]
					player2 = pesan.split(':')[2]
					if(player1 == self.user_text):
						self.rival_text = player2
					else:
						self.rival_text = player1
					if(turn == '0'):
						warna = self.user_text + ', you are the First Player - Red vs ' + self.rival_text
						self.turn = 'me'
						self.me.color = ((255, 0, 0))
						self.rival.color = ((0, 0, 255))
					else:
						warna = self.user_text + ', you are the Second Player - Blue vs ' + self.rival_text
						self.turn = 'rival'
						self.rival.color = ((255, 0, 0))
						self.me.color = ((0, 0, 255))
					self.canvas.draw_text(turn, 23, 3, 3, (54, 38, 28),"copse.ttf")
			elif(flag == 0):
				self.me.check_collision()
				self.canvas.draw_text(warna, 23, 3, 3, (54, 38, 28),"copse.ttf")
				print('running')
				if(self.turn == 'rival'):
					print('waiting rival')
					if (cek == 22):
						self.canvas.draw_text("Your hole is empty, it's rival's turn..", 23, 3, 28, (54, 38, 28),"copse.ttf")
					else:
						self.canvas.draw_text("Waiting rival's turn..", 23, 3, 28, (54, 38, 28),"copse.ttf")
					self.rival_move = self.parse_data(self.send_data('ask'))
					print('from server', self.rival_move)
					if(self.rival_move != -1):
						self.animate = True
						ganti = self.ambil_biji_rival(self.rival_move, 'rival')
						print('rival ganti:', ganti)
						# check giliran
						if(ganti == 1):
							self.turn = 'me'
							cek = 0
						elif (ganti == 3):
							flag = 3
						elif (ganti == 2):
							self.turn = 'me'
							cek = 2
						elif (ganti == 22):
							cek = 22
				else:
					print('do ur move')
					if (cek == 1):
						self.canvas.draw_text("You reached home, it's your turn again, do your move..", 23, 3, 28, (54, 38, 28),"copse.ttf")
					elif (cek == 2):
						self.canvas.draw_text("Rival's hole is empty, do your move..", 23, 3, 28, (54, 38, 28),"copse.ttf")
					else:
						self.canvas.draw_text("It's your turn, do your move..", 23, 3, 28, (54, 38, 28),"copse.ttf")
					if(event.type == pygame.MOUSEBUTTONDOWN):
						if(self.me.lubang[0].collidepoint(event.pos) and self.me.biji[0] > 0 and self.animate == False):
							self.animate = True
							balasan = self.send_data('move:0')
							while(balasan != 'ack'):
								balasan = self.send_data('move:0')
							ganti = self.ambil_biji(0, 'me')
							print('me ganti:', ganti)
							#check giliran
							cek = 1
							if(ganti == 1):
								self.turn = 'rival'
								cek = 0
							elif(ganti == 2):
								cek = 2
							elif(ganti == 22):
								self.turn = 'rival'
								cek = 22
							elif(ganti == 3):
								flag = 3
							pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
						elif(self.me.lubang[1].collidepoint(event.pos) and self.me.biji[1] > 0 and self.animate == False):
							self.animate = True
							balasan = self.send_data('move:1')
							while(balasan != 'ack'):
								balasan = self.send_data('move:1')
							ganti = self.ambil_biji(1, 'me')
							print('me ganti:', ganti)
							#check giliran
							cek = 1
							if(ganti == 1):
								self.turn = 'rival'
								cek = 0
							elif(ganti == 2):
								cek = 2
							elif(ganti == 22):
								self.turn = 'rival'
								cek = 22
							elif(ganti == 3):
								flag = 3
							pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
						elif(self.me.lubang[2].collidepoint(event.pos) and self.me.biji[2] > 0 and self.animate == False):
							self.animate = True
							balasan = self.send_data('move:2')
							while(balasan != 'ack'):
								balasan = self.send_data('move:2')
							ganti = self.ambil_biji(2, 'me')
							print('me ganti:', ganti)
							#check giliran
							cek = 1
							if(ganti == 1):
								self.turn = 'rival'
								cek = 0
							elif(ganti == 2):
								cek = 2
							elif(ganti == 22):
								self.turn = 'rival'
								cek = 22
							elif(ganti == 3):
								flag = 3
							pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
						elif(self.me.lubang[3].collidepoint(event.pos) and self.me.biji[3] > 0 and self.animate == False):
							self.animate = True
							balasan = self.send_data('move:3')
							while(balasan != 'ack'):
								balasan = self.send_data('move:3')
							ganti = self.ambil_biji(3, 'me')
							print('me ganti:', ganti)
							#check giliran
							cek = 1
							if(ganti == 1):
								self.turn = 'rival'
								cek = 0
							elif(ganti == 2):
								cek = 2
							elif(ganti == 22):
								self.turn = 'rival'
								cek = 22
							elif(ganti == 3):
								flag = 3
							pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
						elif(self.me.lubang[4].collidepoint(event.pos) and self.me.biji[4] > 0 and self.animate == False):
							self.animate = True
							balasan = self.send_data('move:4')
							while(balasan != 'ack'):
								balasan = self.send_data('move:4')
							ganti = self.ambil_biji(4, 'me')
							print('me ganti:', ganti)
							#check giliran
							cek = 1
							if(ganti == 1):
								self.turn = 'rival'
								cek = 0
							elif(ganti == 2):
								cek = 2
							elif(ganti == 22):
								self.turn = 'rival'
								cek = 22
							elif(ganti == 3):
								flag = 3
							pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
						elif(self.me.lubang[5].collidepoint(event.pos) and self.me.biji[5] > 0 and self.animate == False):
							self.animate = True
							balasan = self.send_data('move:5')
							while(balasan != 'ack'):
								balasan = self.send_data('move:5')
							ganti = self.ambil_biji(5, 'me')
							print('me ganti:', ganti)
							#check giliran
							cek = 1
							if(ganti == 1):
								self.turn = 'rival'
								cek = 0
							elif(ganti == 2):
								cek = 2
							elif(ganti == 22):
								self.turn = 'rival'
								cek = 22
							elif(ganti == 3):
								flag = 3
							pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
						elif(self.me.lubang[6].collidepoint(event.pos) and self.me.biji[6] > 0 and self.animate == False):
							self.animate = True
							balasan = self.send_data('move:6')
							while(balasan != 'ack'):
								balasan = self.send_data('move:6')
							ganti = self.ambil_biji(6, 'me')
							print('me ganti:', ganti)
							#check giliran
							cek = 1
							if(ganti == 1):
								self.turn = 'rival'
								cek = 0
							elif(ganti == 2):
								cek = 2
							elif(ganti == 22):
								self.turn = 'rival'
								cek = 22
							elif(ganti == 3):
								flag = 3
							pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

				self.chat_btn_on = pygame.draw.rect(self.canvas.get_canvas(), (198, 139, 89), pygame.Rect(186, 458, 56, 31), 1)
				self.chat_btn_off = pygame.draw.rect(self.canvas.get_canvas(), (198, 139, 89), pygame.Rect(251, 458, 56, 31), 1)
				pygame.draw.circle(self.canvas.get_canvas(), self.chat_color, (165, 475), 5, 0)

				if(event.type == pygame.MOUSEBUTTONDOWN and self.chat_btn_on.collidepoint(event.pos)):
					self.chat_ongoing = False
					self.chat_color = (255, 0, 0)

				if(event.type == pygame.MOUSEBUTTONDOWN and self.chat_btn_off.collidepoint(event.pos)):
					self.chat_ongoing = True
					self.chat_color = (0, 255, 0)

				print(self.chat_ongoing, self.penanda_chat)
				# # online chat features
				if(self.chat_ongoing == True):
					events = pygame.event.get()
					self.chatinput.update(events)
					self.canvas.get_canvas().blit(self.chatinput.get_surface(), (57, 495))
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_RIGHT:
							chat_msg = self.chatinput.get_text()[1:]
							if(chat_msg == ''):
								continue
							chat_msg_send = self.user_text + ' > ' + chat_msg
							print(chat_msg_send)
							self.send_data('chat:' + chat_msg_send)
							self.chatinput.clear_text()
				chat_pickle = self.send_data('askchat:')
				self.chat = pickle.loads(chat_pickle)
				row = 535
				for i in range(len(self.chat)):
					self.canvas.draw_text(str(self.chat[i]), 20, 57, row, self.brown_color,"copse.ttf")
					row += 20
			elif(flag == 3): #winning condition
				if(self.poin_not_sent):
					self.poin_not_sent = False
					self.send_data('score:' + str(self.me.poin))
				self.canvas.draw_background()
				if(self.me.poin > self.rival.poin):
					self.canvas.draw_image(pygame.transform.scale(self.winCondition, (700, 700)), (0, 0))
					self.canvas.draw_text(self.user_text + ": " + str(self.me.poin), 30, 100, 200, (0, 255, 0),"copse.ttf")
					self.canvas.draw_text(self.rival_text + ": " + str(self.rival.poin), 30, 100, 250, (255, 0, 0),"copse.ttf")
					self.canvas.draw_text("Congrats " + self.user_text + ", you are the winner", 30, 80, 125, (54, 38, 28),"copse.ttf")
				elif(self.me.poin == self.rival.poin):
					self.canvas.draw_image(pygame.transform.scale(self.tieCondition, (700, 700)), (0, 0))
					self.canvas.draw_text(self.user_text + ": " + str(self.me.poin), 30, 100, 200, (0, 0, 255),"copse.ttf")
					self.canvas.draw_text(self.rival_text + ": " + str(self.rival.poin), 30, 100, 250, (0, 0, 255),"copse.ttf")
					self.canvas.draw_text("The game is tie", 30, 240, 125, (54, 38, 28),"copse.ttf")
				else:
					self.canvas.draw_image(pygame.transform.scale(self.loseCondition, (700, 700)), (0, 0))
					self.canvas.draw_text(self.user_text + ": " + str(self.me.poin), 30, 100, 200, (255, 0, 0),"copse.ttf")
					self.canvas.draw_text(self.rival_text + ": " + str(self.rival.poin), 30, 100, 250, (0, 255, 0),"copse.ttf")
					self.canvas.draw_text("Better luck next time!", 30, 200, 125, (54, 38, 28),"copse.ttf")
				self.menu_btn = pygame.draw.rect(self.canvas.get_canvas(), (198, 139, 89), pygame.Rect(190, 630, 285, 35), 1)
				if self.menu_btn.collidepoint(pygame.mouse.get_pos()):
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
				else:
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

				if(event.type == pygame.MOUSEBUTTONDOWN):
					if(self.menu_btn.collidepoint(event.pos)):
						flag = 5
			elif(flag == 4): #input username
				self.canvas.draw_background()
				self.canvas.draw_image(pygame.transform.scale(self.inputUsername, (700, 700)), (0, 0))
				self.canvas.draw_text("Press right arrow to enter the game", 26, 163, 400, (54, 38, 28), "dekko.ttf")
				events = pygame.event.get()
				self.textinput.update(events)
				self.canvas.get_canvas().blit(self.textinput.get_surface(), (155, 357))
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RIGHT:
						self.user_text = self.textinput.get_text()[1:]
						print(self.user_text)
						pesan = self.send_data('register:' + self.user_text)
						flag = 5
			elif(flag == 5): #main menu
				# reset all game data
				self.chatinput.clear_text()
				self.leaderboard_not_asked = True
				self.poin_not_sent = True
				self.chat_ongoing = False
				self.me.biji = [7, 7, 7, 7, 7, 7, 7]
				self.me.poin = 0
				self.me.lubang = []
				self.me.tanda = [False, False, False, False, False, False, False]
				self.rival.biji = [7, 7, 7, 7, 7, 7, 7]
				self.rival.poin = 0
				self.rival.lubang = []
				self.rival.tanda = [False, False, False, False, False, False, False]
				cek = 0

				self.canvas.draw_background()
				self.canvas.draw_image(pygame.transform.scale(self.dashboard, (700, 700)), (0, 0))
				self.play_btn = pygame.draw.rect(self.canvas.get_canvas(), (64, 34, 24), pygame.Rect(150, 260, 400, 80), 1)
				self.leaderboard_btn = pygame.draw.rect(self.canvas.get_canvas(), (64, 34, 24), pygame.Rect(150, 363, 400, 80), 1)

				if self.play_btn.collidepoint(pygame.mouse.get_pos()) or self.leaderboard_btn.collidepoint(pygame.mouse.get_pos()):
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
				else:
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

				if(event.type == pygame.MOUSEBUTTONDOWN):
					if(self.play_btn.collidepoint(event.pos)):
						flag = 1
					elif(self.leaderboard_btn.collidepoint(event.pos)):
						flag = 6
			elif(flag == 6): #leaderboard interface
				self.canvas.draw_background()
				self.canvas.draw_image(pygame.transform.scale(self.leaderboard, (700, 700)), (0, 0))
				self.menu_btn = pygame.draw.rect(self.canvas.get_canvas(), (198, 139, 89), pygame.Rect(190, 630, 285, 35), 1)
				if(self.leaderboard_not_asked):
					self.leaderboard_not_asked = False
					leaderboard_pickle = self.send_data('leaderboard')
					leaderboard = pickle.loads(leaderboard_pickle)
				row = 180
				count = 1
				for key, value in leaderboard.items():
					if(key == self.user_text):
						row_color = (0, 255, 0)
					else:
						row_color = self.bg_contrast
					self.canvas.draw_text(str(count) + '.', 22, 190, row, row_color,"copse.ttf")
					self.canvas.draw_text(key, 22, 290, row, row_color,"copse.ttf")
					self.canvas.draw_text(str(value), 22, 470, row, row_color,"copse.ttf")
					row += 25
					count += 1

				if self.menu_btn.collidepoint(pygame.mouse.get_pos()):
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
				else:
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

				if(event.type == pygame.MOUSEBUTTONDOWN):
					if(self.menu_btn.collidepoint(event.pos)):
						flag = 5

			self.canvas.update()

		pygame.quit()

	def send_data(self, pesan):
		data = str(self.net.id) + ":" + pesan
		reply = self.net.send(data)
		return reply

	def ambil_biji(self, start_pos, giliran):

		# clear biji before
		self.me.draw(self.canvas.get_canvas(), self.bg_color, 200, 340, 52, 22, 0)
		self.rival.draw(self.canvas.get_canvas(), self.bg_color, 200, 278, 52, 22, 0)
		pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (145, 308), 27, 0)
		pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (565, 308), 27, 0)

		# gambar kondisi awal
		self.me.draw(self.canvas.get_canvas(), self.bg_color, 200, 340, 52, 25, 2)
		self.rival.draw(self.canvas.get_canvas(), self.bg_color, 200, 278, 52, 25, 2)
		for i in range(7):
			self.canvas.draw_text(str(self.me.biji[i]), 22, 190 + (i * 52), 327, self.me.color,"copse.ttf")
		for i in range(7):
			self.canvas.draw_text(str(self.rival.biji[i]), 22, 190 + (i * 52), 265, self.rival.color,"copse.ttf")
		self.canvas.draw_text(str(self.me.poin), 22, 554, 296, self.me.color,"copse.ttf")
		self.canvas.draw_text(str(self.rival.poin), 22, 134, 296, self.rival.color,"copse.ttf")
		pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (145, 308), 30, 2)
		pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (565, 308), 30, 2)
		self.canvas.update()

		banyak_biji = self.me.biji[start_pos]
		self.me.biji[start_pos] = 0
		self.add_delay('me biji', start_pos, str(self.me.biji[start_pos]), 'Ambil')

		print('ambil me', banyak_biji, start_pos + 1)
		sisa_biji, cur_pos, player = self.animasi_biji_me(banyak_biji, start_pos + 1, giliran)
		print('back to home', player, cur_pos)
		if(giliran == 'me'):
			if(cur_pos == 7): #reach home
				print('finish animasi me back to home')
				self.animate = False
				check_finish = self.check_finish()
				if (check_finish):
					return 3
				if self.me.biji.count(0) == 7:
					return 22
				if self.rival.biji.count(0) == 7:
					return 2
				return 0 #giliran tetap ketika biji terakhir sampai di home/rumah sendiri
			elif(player == 'me'):
				if(self.me.biji[cur_pos] == 1): #tembak
					self.me.poin += self.rival.biji[cur_pos] + self.me.biji[cur_pos]
					self.add_delay('me poin', cur_pos, str(self.me.poin), str(sisa_biji))
					self.rival.biji[cur_pos] = 0
					self.me.biji[cur_pos] = 0
					print('finish animasi me', cur_pos)
					self.animate = False
				else:
					ganti = self.ambil_biji(cur_pos, giliran)
					return ganti
			else:
				if(self.rival.biji[cur_pos] == 1): #mati
					print('finish animasi rival', cur_pos)
					self.animate = False
				else:
					ganti = self.ambil_biji_rival(cur_pos, giliran)
					return ganti
		else:
			if(cur_pos == -1): #reach home
				print('finish animasi me back to home rival')
				self.animate = False
				check_finish = self.check_finish()
				if (check_finish):
					return 3
				if self.rival.biji.count(0) == 7:
					return 2
				if self.me.biji.count(0) == 7:
					return 22
				return 0 #giliran tetap ke rival ketika biji terakhir sampai di home rival
			elif(player == 'rival'):
				if(self.rival.biji[cur_pos] == 1): #tembak
					self.rival.poin += self.rival.biji[cur_pos] + self.me.biji[cur_pos]
					self.add_delay('rival poin', cur_pos, str(self.rival.poin), str(sisa_biji))
					self.rival.biji[cur_pos] = 0
					self.me.biji[cur_pos] = 0
					print('finish animasi me - rival', cur_pos)
					self.animate = False
				else:
					ganti = self.ambil_biji_rival(cur_pos, giliran)
					return ganti
			else:
				if(self.me.biji[cur_pos] == 1): #mati
					print('finish animasi rival - rival', cur_pos)
					self.animate = False
				else:
					ganti = self.ambil_biji(cur_pos, giliran)
					return ganti
		check_finish = self.check_finish()
		if (check_finish):
			return 3
		if self.rival.biji.count(0) == 7:
			return 2
		if self.me.biji.count(0) == 7:
			return 22
		return 1 #ganti giliran ke lawan

	def ambil_biji_rival(self, start_pos, giliran):

		# clear biji before
		self.me.draw(self.canvas.get_canvas(), self.bg_color, 200, 340, 52, 22, 0)
		self.rival.draw(self.canvas.get_canvas(), self.bg_color, 200, 278, 52, 22, 0)
		pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (145, 308), 27, 0)
		pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (565, 308), 27, 0)

		# gambar kondisi awal
		self.me.draw(self.canvas.get_canvas(), self.bg_color, 200, 340, 52, 25, 2)
		self.rival.draw(self.canvas.get_canvas(), self.bg_color, 200, 278, 52, 25, 2)
		for i in range(7):
			self.canvas.draw_text(str(self.me.biji[i]), 22, 190 + (i * 52), 327, self.me.color,"copse.ttf")
		for i in range(7):
			self.canvas.draw_text(str(self.rival.biji[i]), 22, 190 + (i * 52), 265, self.rival.color,"copse.ttf")
		self.canvas.draw_text(str(self.me.poin), 22, 554, 296, self.me.color,"copse.ttf")
		self.canvas.draw_text(str(self.rival.poin), 22, 134, 296, self.rival.color,"copse.ttf")
		pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (145, 308), 30, 2)
		pygame.draw.circle(self.canvas.get_canvas(), self.bg_color, (565, 308), 30, 2)
		self.canvas.update()

		banyak_biji = self.rival.biji[start_pos]
		self.rival.biji[start_pos] = 0
		self.add_delay('rival biji', start_pos, str(self.rival.biji[start_pos]), 'Ambil')
		print('ambil rival', banyak_biji, start_pos - 1)
		sisa_biji, cur_pos, player = self.animasi_biji_rival(banyak_biji, start_pos - 1, giliran)
		print('back to rival', player, cur_pos)
		if(giliran == 'me'):
			if(cur_pos == 7): #reach home
				print('finish animasi me back to home')
				self.animate = False
				check_finish = self.check_finish()
				if (check_finish):
					return 3
				if self.me.biji.count(0) == 7:
					return 22
				if self.rival.biji.count(0) == 7:
					return 2
				return 0 #giliran tetap ketika biji terakhir sampai ke home/rumah sendiri
			elif(player == 'me'):
				if(self.me.biji[cur_pos] == 1): #tembak
					self.me.poin += self.rival.biji[cur_pos] + self.me.biji[cur_pos]
					self.add_delay('me poin', cur_pos, str(self.me.poin), str(sisa_biji))
					self.rival.biji[cur_pos] = 0
					self.me.biji[cur_pos] = 0
					print('finish animasi me', cur_pos)
					self.animate = False
				else:
					ganti = self.ambil_biji(cur_pos, giliran)
					return ganti
			else:
				if(self.rival.biji[cur_pos] == 1): #mati
					print('finish animasi rival', cur_pos)
					self.animate = False
				else:
					ganti = self.ambil_biji_rival(cur_pos, giliran)
					return ganti
		else:
			if(cur_pos == -1): #reach home
				print('finish animasi me back to home rival')
				self.animate = False
				check_finish = self.check_finish()
				if (check_finish):
					return 3
				if self.rival.biji.count(0) == 7:
					return 2
				if self.me.biji.count(0) == 7:
					return 22
				return 0 #giliran tetap ke rival ketika biji terakhir sampai ke home rival
			elif(player == 'rival'):
				if(self.rival.biji[cur_pos] == 1): #tembak
					self.rival.poin += self.rival.biji[cur_pos] + self.me.biji[cur_pos]
					self.add_delay('rival poin', cur_pos, str(self.rival.poin), str(sisa_biji))
					self.rival.biji[cur_pos] = 0
					self.me.biji[cur_pos] = 0
					print('finish animasi me - rival', cur_pos)
					self.animate = False
				else:
					ganti = self.ambil_biji_rival(cur_pos, giliran)
					return ganti
			else:
				if(self.me.biji[cur_pos] == 1): #mati
					print('finish animasi rival - rival', cur_pos)
					self.animate = False
				else:
					ganti = self.ambil_biji(cur_pos, giliran)
					return ganti
		check_finish = self.check_finish()
		if (check_finish):
			return 3
		if self.rival.biji.count(0) == 7:
			return 2
		if self.me.biji.count(0) == 7:
			return 22
		return 1 #giliran ganti ke lawan


	def animasi_biji_me(self, banyak_biji, start_pos, giliran):
		cur_pos = start_pos
		sisa_biji = banyak_biji
		player = 'me'
		if(cur_pos == 7 and sisa_biji > 0):
			if(giliran == 'me'):
				self.me.poin += 1
				sisa_biji -= 1
				self.add_delay('me poin', cur_pos, str(self.me.poin), str(sisa_biji))
				if(sisa_biji == 0):
					return 0, cur_pos, 'me'
			sisa_biji, cur_pos, player = self.animasi_biji_rival(sisa_biji, 6, giliran)
		else:
			while(sisa_biji):
				print('animasi me', cur_pos, sisa_biji)
				self.me.biji[cur_pos] += 1
				sisa_biji -= 1
				self.add_delay('me biji', cur_pos, str(self.me.biji[cur_pos]), str(sisa_biji))
				if(sisa_biji == 0):
					return 0, cur_pos, 'me'
				cur_pos += 1
				if(cur_pos == 7 and sisa_biji > 0):
					if(giliran == 'me'):
						self.me.poin += 1
						sisa_biji -= 1
						self.add_delay('me poin', cur_pos, str(self.me.poin), str(sisa_biji))
						if(sisa_biji == 0):
							return 0, cur_pos, 'me'
						print('mau pindah ke rival', sisa_biji, cur_pos)
					sisa_biji, cur_pos, player = self.animasi_biji_rival(sisa_biji, 6, giliran)
		return sisa_biji, cur_pos, player

	def animasi_biji_rival(self, banyak_biji, start_pos, giliran):
		cur_pos = start_pos
		sisa_biji = banyak_biji
		player = 'rival'
		if(cur_pos == -1 and sisa_biji > 0):
			if(giliran == 'rival'):
				self.rival.poin += 1
				sisa_biji -= 1
				self.add_delay('rival poin', cur_pos, str(self.rival.poin), str(sisa_biji))
				if(sisa_biji == 0):
					return 0, cur_pos, 'rival'
			sisa_biji, cur_pos, player = self.animasi_biji_me(sisa_biji, 0, giliran)
		else:
			while(sisa_biji):
				print('animasi rival', cur_pos, sisa_biji)
				self.rival.biji[cur_pos] += 1
				sisa_biji -= 1
				self.add_delay('rival biji', cur_pos, str(self.rival.biji[cur_pos]), str(sisa_biji))
				if(sisa_biji == 0):
					return 0, cur_pos, 'rival'
				cur_pos -= 1
				if(cur_pos == -1 and sisa_biji > 0):
					if(giliran == 'rival'):
						self.rival.poin += 1
						sisa_biji -= 1
						self.add_delay('rival poin', cur_pos, str(self.rival.poin), str(sisa_biji))
						if(sisa_biji == 0):
							return 0, cur_pos, 'rival'
						print('oper to me', 0, sisa_biji);
					sisa_biji, cur_pos, player = self.animasi_biji_me(sisa_biji, 0, giliran)
		return sisa_biji, cur_pos, player

	def add_delay(self, player, pos, text, sisa_biji):
		# time.sleep(1)
		# using pygame.time.delay will make Pygame not responding, better use ticks
		# pygame.time.delay(250)
		ticks = pygame.time.get_ticks()
		delay_ticks = ticks + 10000
		while(ticks > delay_ticks):
			ticks = pygame.time.get_ticks()
		# self.canvas.screen.fill(self.bg_color, (0, 0, 500, 100))
		# self.canvas.update_text(sisa_biji, 32, 0, 0, (self.bg_contrast))
		if(player == 'me biji'):
			pygame.draw.circle(self.canvas.get_canvas(), self.on_color, ((200 + pos * 52), 340), 22)
			self.canvas.update_text(text, 22, 190 + (pos * 52), 327, self.me.color,"copse.ttf")
		elif(player == 'me poin'):
			pygame.draw.circle(self.canvas.get_canvas(), self.on_color, (565, 308), 27)
			self.canvas.update_text(text, 22, 554, 296, self.me.color,"copse.ttf")
		elif(player == 'rival biji'):
			pygame.draw.circle(self.canvas.get_canvas(), self.on_color, ((200 + pos * 52), 278), 22)
			self.canvas.update_text(text, 22, 190 + (pos * 52), 265, self.rival.color,"copse.ttf")
		else:
			pygame.draw.circle(self.canvas.get_canvas(), self.on_color, (145, 308), 27)
			self.canvas.update_text(text, 22, 134, 296, self.rival.color,"copse.ttf")

		self.canvas.update()

	@staticmethod
	def parse_data(data):
		try:
			d = data.split(":")[0]
			return int(d)
		except:
			return -1

	def check_finish(self):
		if (self.me.biji.count(0) == 7 and self.rival.biji.count(0) == 7):
			return 1
		return 0

class Canvas:

	def __init__(self, w, h, name="None"):
		self.width = w
		self.height = h
		self.screen = pygame.display.set_mode((w,h))
		pygame.display.set_caption(name)

	@staticmethod
	def update():
		pygame.display.update()

	def draw_text(self, text, size, x, y, color, type):
		pygame.font.init()
		if(len(text) == 1):
			x += 5
		font = pygame.font.Font(os.path.join("assets", type), size)
		render = font.render(text, 1, color)

		self.screen.blit(render, (x,y))

	def update_text(self, text, size, x, y, color, type):
		pygame.font.init()
		if(len(text) == 1):
			x += 5
		font = pygame.font.Font(os.path.join("assets", type), size)
		# self.screen.fill(pygame.Color("white"), ((x-5), (y-1), 29, 26))
		render = font.render(text, 1, color)

		self.screen.blit(render, (x,y))

	def get_canvas(self):
		return self.screen

	def draw_background(self):
		self.screen.fill((0,0,0))

	def draw_image(self, image, position):
		self.screen.blit(image, position)