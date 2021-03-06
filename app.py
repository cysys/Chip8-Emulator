import sys
import os
import pygame
from tkinter import *
from tkinter.filedialog import askopenfilename

from emulation import cpu

def header():
	print("Chip8 Emulator")
	print("Author: aadithvmenon")
	print("github.com/cysys")

def handle_keypress(chip, key, down):
	if   key == pygame.K_1: chip.key_handler(0x1, down)
	elif key == pygame.K_2: chip.key_handler(0x2, down)
	elif key == pygame.K_3: chip.key_handler(0x3, down)
	elif key == pygame.K_4: chip.key_handler(0xC, down)

	elif key == pygame.K_q: chip.key_handler(0x4, down)
	elif key == pygame.K_w: chip.key_handler(0x5, down)
	elif key == pygame.K_e: chip.key_handler(0x6, down)
	elif key == pygame.K_r: chip.key_handler(0xD, down)

	elif key == pygame.K_a: chip.key_handler(0x7, down)
	elif key == pygame.K_s: chip.key_handler(0x8, down)
	elif key == pygame.K_d: chip.key_handler(0x9, down)
	elif key == pygame.K_f: chip.key_handler(0xE, down)

	elif key == pygame.K_z: chip.key_handler(0xA, down)
	elif key == pygame.K_x: chip.key_handler(0x0, down)
	elif key == pygame.K_c: chip.key_handler(0xB, down)
	elif key == pygame.K_v: chip.key_handler(0xF, down)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_screen(DISPLAYSURF, chip):
	px_w = DISPLAYSURF.get_width() / 64
	px_h = DISPLAYSURF.get_height() /32
	for x in range(64):
		for  y in range(32):
			if(chip.display)[x + 64 * y] != 0:
				pygame.draw.rect(DISPLAYSURF, WHITE,(x * px_w, y * px_h, px_w, px_h))
			else:
				pygame.draw.rect(DISPLAYSURF, BLACK,(x * px_w, y * px_h, px_w, px_h))

def main():
	header()
	root = Tk()
	pygame.init()

	chip = cpu()
	
	filename = askopenfilename(initialdir=os.getcwd(),filetypes =[("Chip8 ROM","*.c8")],title = "Choose a file.")

	root.destroy()
	DISPLAYSURF = pygame.display.set_mode((640, 320))
	pygame.display.set_caption('Chip8 Emulator |  |^anda')
	chip.load_rom(filename)
	#DISPLAYSURF.fill(BLACK)
	on = True

	while on:
		chip.update_time()

		if not chip.opcode_decode():
			break

		events = pygame.event.get()

		for event in events:

			if event.type == pygame.QUIT:
				on = False
				break

			if event.type == pygame.KEYDOWN:
				handle_keypress(chip, event.key, True)

			if event.type == pygame.KEYUP:
				handle_keypress(chip, event.key, False)

		draw_screen(DISPLAYSURF, chip)
		pygame.display.update()
		pygame.time.delay(1)


if __name__ == '__main__':
	main()




