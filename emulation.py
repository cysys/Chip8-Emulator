from random import random 

class cpu:

	# Fonts sprite data
	fonts = [
		0xF0, 0x90, 0x90, 0x90, 0xF0,	# 0
		0x20, 0x60, 0x20, 0x20, 0x70,	# 1
		0xF0, 0x10, 0xF0, 0x80, 0xF0,	# 2
		0xF0, 0x10, 0xF0, 0x10, 0xF0,	# 3
		0x90, 0x90, 0xF0, 0x10, 0x10,	# 4
		0xF0, 0x80, 0xF0, 0x10, 0xF0,	# 5
		0xF0, 0x80, 0xF0, 0x90, 0xF0,	# 6
		0xF0, 0x10, 0x20, 0x40, 0x40,	# 7
		0xF0, 0x90, 0xF0, 0x90, 0xF0,	# 8
		0xF0, 0x90, 0xF0, 0x10, 0xF0,	# 9
		0xF0, 0x90, 0xF0, 0x90, 0x90,	# A
		0xE0, 0x90, 0xE0, 0x90, 0xE0,	# B
		0xF0, 0x80, 0x80, 0x80, 0xF0,	# C
		0xE0, 0x90, 0x90, 0x90, 0xE0,	# D
		0xF0, 0x80, 0xF0, 0x80, 0xF0,	# E
		0xF0, 0x80, 0xF0, 0x80, 0x80,	# F
	]

	def __init__(self):
		self.memory = [0] * 4096 # 4096 bytes of memory
		self.V = [0] * 16 # 16 General purpose regsiters

		self.I = 0 # Additional register
		self.pc = 0x200 # Program counter starts from 0x200
		self.stack = [0] * 16 # Stack
		self.sp = 0 # Stack pointer

		self.display = [0] * 64 * 32 # Monochrome 64x32 display
		self.keys = [0] * 16 # 16 Inpute keys
		self.current_key = 0 # Last key pressed
		self.timer_delay = 0 # Delay for executing next cycle
		self.timer_sound = -1 # To be implemented
		self.memory[:len(cpu.fonts)] = cpu.fonts # Load fonts into beginning of memory

	def load_rom(self, filename):

		addr = 0x200 	# program space starts at address 0x0200

		# read bytes from file into RAM
		with open(filename, "rb") as f:
			byte = f.read(1)
			i = 0
			while byte:
				self.memory[0x200 + i] = byte[0]
				i += 1
				byte = f.read(1)

		

	def update_time(self):
		if self.timer_delay > 0:
			self.timer_delay -= 1

	def key_handler(self, key, down):
		if down:
			self.current_key = key
		self.keys[key] = down

	def opcode_decode(self):
		X = lambda op: (op >> 8) & 0xF # Operand 1 extraction 
		Y = lambda op: (op >> 4) & 0xF # Operand 2 extraction
		N = lambda op: op & 0xF
		KK = lambda op: op & 0xFF
		NNN = lambda op: op & 0xFFF

		opcode = (self.memory[self.pc] << 8) | (self.memory[self.pc + 1]) # Read the two bytes
		if opcode == 0x00E0:
			self.screen = [0] * 64 * 32
			self.pc += 2

		elif opcode == 0x00EE:
			self.sp -= 1
			self.pc = self.stack[self.sp] + 2

		elif opcode & 0xF000 == 0x1000:
			self.pc = NNN(opcode)

		elif opcode & 0xF000 == 0x2000:
			self.stack[self.sp] = self.pc
			self.sp += 1
			self.pc = NNN(opcode)

		elif opcode & 0xF000 == 0x3000:
			if self.V[X(opcode)] == KK(opcode):
				self.pc += 2
			self.pc += 2

		elif opcode & 0xF000 == 0x4000:
			if self.V[X(opcode)] != KK(opcode):
				self.pc += 2
			self.pc += 2

		elif opcode & 0xF000 == 0x5000:
			if self.V[X(opcode)] == self.V[Y(opcode)]:
				self.pc += 2
			self.pc += 2

		elif opcode & 0xF000 == 0x6000:
			self.V[X(opcode)] = KK(opcode)
			self.pc += 2

		elif opcode & 0xF000 == 0x7000:
			self.V[X(opcode)] += KK(opcode)
			self.V[X(opcode)] %= 256 # Restricting to 8 bit
			self.pc += 2

		elif opcode & 0xF000 == 0x8000:
			self.V[X(opcode)] = self.V[Y(opcode)]
			self.pc += 2

		elif opcode & 0xF00F == 0x8001:
			self.V[X(opcode)] |= self.V[Y(opcode)]
			self.pc += 2

		elif opcode & 0xF00F == 0x8002:
			self.V[X(opcode)] &= self.V[Y(opcode)]
			self.pc += 2

		elif opcode & 0xF00F == 0x8003:
			self.V[X(opcode)] ^= self.V[Y(opcode)]
			self.pc += 2
		elif opcode & 0xF00F == 0x8004:
			self.V[X(opcode)] += self.V[Y(opcode)]
			self.V[-1] = int(self.V[X(opcode)] > 255) # Carry flag
			self.V[X(opcode)] %= 256 # Restricting to 8 bit
			self.pc += 2

		elif opcode & 0xF00F == 0x8005:
			self.V[-1] = int(self.V[X(opcode)] > self.V[Y(opcode)])
			self.V[X(opcode)] -= self.V[Y(opcode)]
			self.V[X(opcode)] %= 256 # Restricting to 8 bit
			self.pc += 2

		elif opcode & 0xF000F == 0x8006:
			self.V[-1] = self.V[X(opcode)] & 1
			self.V[X(opcode)] = self.V[X(opcode)] >> 1
			self.pc += 2

		elif opcode & 0xF00F == 0x8007:
			self.V[-1] = int(self.V[Y(opcode)] > self.V[X(opcode)])
			self.V[X(opcode)] = self.V[Y(opcode)]- self.V[X(opcode)]
			self.V[X(opcode)] %= 256 # Restricting to 8 bit
			self.pc += 2

		elif opcode & 0xF00F == 0x800E:
			self.V[-1] = (self.V[X(opcode)] >> 7) & 1
			self.V[X(opcode)] = self.V[X(opcode)] << 1
			self.V[X(opcode)] %= 256 # Restricting to 8 bit
			self.pc += 2

		elif opcode & 0xF000 == 0x9000:
			if self.V[X(opcode)] != self.V[Y(opcode)]:
				self.pc += 2
			self.pc += 2

		elif opcode & 0xF000 == 0xA000:
			self.I = NNN(opcode)
			self.pc += 2

		elif opcode & 0xF000 == 0xB000:
			self.pc = NNN(opcode) + self.V[0] # Check this 

		elif opcode & 0xF000 == 0xC000:
			self.V[X(opcode)] = int(random() * 256) & KK(opcode)
			self.pc += 2

		elif opcode & 0xF000 == 0xD000:
			xOffset = self.V[X(opcode)]
			yOffset = self.V[Y(opcode)]
			n = N(opcode)

			self.V[-1] = 0

			for y in range(yOffset, yOffset + n):
				byte = self.memory[int(self.I + int((y - yOffset)))]
				for x in range(xOffset, xOffset + 8):

					
					byte_pos = x - xOffset

					# wrap the screen edge to edge 
					x %= 64
					y %= 32

					# set bits on screen
					set_before = self.display[x + 64*y]
					set_after = set_before ^ ((byte >> (7 - byte_pos)) & 1)

					self.display[x + 64*y] = set_after

					if set_before and not set_after:
						self.V[-1] = 1

			self.pc += 2

		elif opcode & 0xF0FF == 0xE09E:
			if self.keys[self.V[X(opcode)]]:
				self.pc += 2
			self.pc += 2

		elif opcode & 0xF0FF == 0xE0A1:
			if not self.keys[self.V[X(opcode)]]:
				self.pc += 2
			self.pc += 2

		elif opcode & 0xF0FF == 0xF007:
			self.V[X(opcode)] = self.timer_delay
			self.pc += 2

		elif opcode & 0xF0FF == 0XF00A:
			if self.current_key != -1:
				self.V[X(opcode)] = self.current_key
				self.current_key = -1 
			self.pc += 2

		elif opcode & 0xF0FF == 0xF015:
			self.timer_delay = self.V[X(opcode)]
			self.pc += 2

		elif opcode & 0xF0FF == 0xF018: # To be implemented
			self.timer_sound = self.V[X(opcode)]
			self.pc += 2

		elif opcode & 0xF0FF == 0xF01E:
			self.I += self.V[X(opcode)]
			self.pc += 2

		elif opcode & 0xF0FF == 0xF029:
			self.I = 5 * self.V[X(opcode)] # 5 bytes per font
			self.pc += 2

		elif opcode & 0xF0FF == 0xF033:
			self.memory[self.I] = self.V[X(opcode)] / 100
			self.memory[self.I + 1] = (self.V[X(opcode)] / 10) % 10
			self.memory[self.I + 2] = self.V[X(opcode)] % 10
			self.pc += 2

		elif opcode & 0xF0FF == 0xF055:
			offset = X(opcode) + 1
			self.memory[self.I : self.I + offset] = self.V[:offset]
			self.pc += 2

		elif opcode & 0xF0FF == 0xF065:
			offset = X(opcode) + 1
			self.V[:offset] = self.memory[self.I : self.I + offset]
			self.pc += 2


		else:
			print(opcode)
			return False

		return True	













