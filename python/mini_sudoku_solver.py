#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: Michal Niklas

import os.path
import sys
import time

USAGE = """usage:
	python mini_sudoku_solver.py [sudoku_str] [sudoku_file]

	sudoku_str: string of 36 chars with digits from 6 rows and 6 columns with 1..6 digits or '.' char
	sudoku_file: file name of file with 6 rows and 6 columns of 1..6 digits or '.' char

	examples:

	python mini_sudoku_solver.py "aaaaaaBBBBBBccccccDDDDDDeeeeeeFFFFFF"

	python mini_sudoku_solver.py ".......4..2.3....6..12...2..3..3416."
	python mini_sudoku_solver.py "..3.5..2.4.61..........22.4.1..1.3.."
	python mini_sudoku_solver.py ".1...22.3.1......15......2.4.34...2."
	python mini_sudoku_solver.py ".......1234.12..3454..21.3516......."
	python mini_sudoku_solver.py "1.63...2....4.3..22..4.1....5...12.6"


"""

TEST_TABLE = """
1234..
......
..234.
.456..
......
..4231
"""

DIGITS = '123456'


class SudokuException(Exception):
	"""raised when someting is wrong with sudoku table"""
	pass


def show_available(available):
	for row in range(6):
		col_items = []
		for col in range(6):
			if available[row][col]:
				col_items.append('%6s' % (available[row][col]))
			else:
				col_items.append('......')
			#col_items.append(" ; ")
			if col == 2:
				col_items.append(' | ')
		print(' '.join(col_items))
		if row in [1, 3]:
			print('-' * 25)
	print('\n\n')


def check_columns(digit, available, column):
	r = 0
	if column < 3:
		columns = [0, 1, 2]
	else:
		columns = [3, 4, 5]
	for row in range(6):
		for col in columns:
			if digit in available[row][col]:
				r += 1
	return r == 1


class MiniSudokuSolver:
	def __init__(self):
		self.table = [list('111111'), list('222222'), list('333333'), list('444444'), list('555555'), list('666666')]

	def read_table_from_str(self, table_str):
		table_str = table_str.replace('\n', '')
		table_str = table_str.replace('\r', '')
		if len(table_str) != 36:
			raise SudokuException(f"bledna tablica, dlugosc powinna wynosic 36, a nie {len(table_str)}!")
		char_idx = 0
		for row in range(6):
			for col in range(6):
				self.table[row][col] = table_str[char_idx]
				char_idx += 1

	def read_table_from_file(self, filename):
		f = open(filename, 'r')
		content = f.read()
		f.close()
		self.read_table_from_str(content)

	def show_row(self, row_nr):
		row_str = []
		for j in range(6):
			row_str.append(self.table[row_nr][j])
			if len(row_str) == 3:
				row_str.append('|')
		print(' '.join(row_str))

	def show_table(self):
		for i in range(6):
			self.show_row(i)
			if i in [1, 3]:
				print('-' * 14)
		print('\n\n')

	def is_solved(self):
		for row in range(6):
			for col in range(6):
				if self.table[row][col] not in DIGITS:
					return False
		return True

	def check_valid(self):
		def is_valid_str(digits_str, comment):
			for c in DIGITS:
				if digits_str.count(c) > 1:
					raise SudokuException(f"bledna tablica [{digits_str}], za duzo [{c}]! {comment}")
		for row in range(6):
			digits = ''.join(self.table[row])
			is_valid_str(digits, f'row[{row}]')
		for column in range(6):
			digits = ''
			for row in range(6):
				digits += self.table[row][column]
			is_valid_str(digits, f'column[{column}]')

	def next_step(self):
		# wstepne wypelnienie
		available = []
		for row in range(6):
			available.append([])
			for col in range(6):
				if self.table[row][col] in DIGITS:
					available[row].append('')
				else:
					available[row].append(DIGITS)

		# sprawdzenie w poziomie
		for row in range(6):
			row_data = self.table[row]
			for c in row_data:
				if c in DIGITS:
					for column in range(6):
						available[row][column] = available[row][column].replace(c, '')

		# sprawdzenie w pionie
		for column in range(6):
			for row in range(6):
				c = self.table[row][column]
				if c in DIGITS:
					for j in range(6):
						available[j][column] = available[j][column].replace(c, '')

		# sprawdzanie w grupie
		for grp_row in range(3):
			for grp_col in range(2):
				chars_in_grp = ''
				for j in range(2):
					for i in range(3):
						column = grp_col * 3 + i
						row = grp_row * 2 + j
						if self.table[row][column] in DIGITS:
							chars_in_grp += self.table[row][column]
				#print(f'cyfry w grupie [{grp_row}][{grp_col}] = [{chars_in_grp}]')
				if chars_in_grp:
					for c in chars_in_grp:
						for j in range(2):
							for i in range(3):
								column = grp_col * 3 + i
								row = grp_row * 2 + j
								available[row][column] = available[row][column].replace(c, '')

		# wypelnianie tych, ktore maja tylko jedna cyfre
		changed = 0
		for row in range(6):
			for column in range(6):
				if len(available[row][column]) == 1:
					changed += 1
					self.table[row][column] = available[row][column]

		if changed == 0:
			for digit in DIGITS:
				# sprawdzanie w poziomie, czy dana liczba wystepuje tylko raz
				for row in range(6):
					solo_idx = -1
					digit_cnt = 0
					for column in range(6):
						if digit in available[row][column]:
							digit_cnt += 1
							solo_idx = column
					if digit_cnt == 1:
						print(f'\n\nrc digit {digit},   row={row}  column={solo_idx}')
						show_available(available)
						if check_columns(digit, available, solo_idx):
							changed += 1
							self.table[row][solo_idx] = digit
							self.check_valid()
							return 1
				# sprawdzanie w poziomie, czy dana liczba wystepuje tylko raz
				for column in range(6):
					solo_idx = -1
					digit_cnt = 0
					for row in range(6):
						if digit in available[row][column]:
							digit_cnt += 1
							solo_idx = row
					if digit_cnt == 1:
						print(f'\n\nvc digit {digit},   row={solo_idx}  column={column}')
						show_available(available)
						if check_columns(digit, available, column):
							changed += 1
							self.table[solo_idx][column] = digit
							self.check_valid()
							return 1
				# sprawdzanie w grupie, czy dana liczba występuje tylko raz
				for grp_row in range(3):
					solo_col = solo_row = -1
					for grp_col in range(2):
						for j in range(2):
							digit_cnt = 0
							for i in range(3):
								column = grp_col * 3 + i
								row = grp_row * 2 + j
								if digit in available[row][column]:
									digit_cnt += 1
									solo_col = column
									solo_row = row
							if digit_cnt == 1:
								print(f'\n\ngc digit {digit},   row={solo_row}  column={solo_col}')
								show_available(available)
								changed += 1
								self.table[solo_row][solo_col] = digit
								self.check_valid()
								return 1

		if not changed:
			print("don't know what to do next :( !!!")
			show_available(available)
			return 0
		return changed


def main():
	sudoku_str = sudoku_file = ''
	for s in sys.argv[1:]:
		if len(s) == 36:
			sudoku_str = s
		if os.path.isfile(s):
			sudoku_file = s
	solver = MiniSudokuSolver()
	if sudoku_str:
		solver.read_table_from_str(sudoku_str)
	elif sudoku_file:
		solver.read_table_from_file(sudoku_file)
	elif '--test' in sys.argv:
		solver.read_table_from_str(TEST_TABLE)
	else:
		print(USAGE)
		return
	solver.show_table()
	while not solver.is_solved():
		changed_cnt = solver.next_step()
		print(f'changed_cnt={changed_cnt}\n')
		solver.show_table()
		if changed_cnt == 0:
			print('the end')
			return
		time.sleep(1)


if __name__ == '__main__':
	main()
