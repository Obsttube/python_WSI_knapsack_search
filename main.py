#!/usr/bin/env python

__copyright__ = "Copyright 2020, Piotr Obst"

import knapsack
import os
from typing import Union


def __pad_string(text: Union[str, int], length: int) -> str:
	string = str(text)
	return string + ' ' * (length - len(string))


def __compare_ints_to_str(int1: int, int2: int) -> str:
	compare = 'equal'
	if int1 > int2:
		compare = ' more'
	elif int1 < int2:
		compare = ' less'
	return compare


def print_solutions(filename: str, dataset: knapsack.Dataset, solution: knapsack.Solution, solution2: knapsack.Solution):
	max_len = 10
	if len(filename) > max_len * 2 + 1:
		max_len = len(filename) // 2
	for item in solution.selected_items:
		if len(str(item)) > max_len:
			max_len = len(str(item))
	for item in solution2.selected_items:
		if len(str(item)) > max_len:
			max_len = len(str(item))
	print('╔' + '═' * 10 + '╦' + '═' * max_len * 2 + '═╗')
	print('║' + 'file      ' + '║' + __pad_string(filename, max_len * 2 + 1) + '║')
	print('╠' + '═' * 10 + '╬' + '═' * max_len * 2 + '═╣')
	print('║' + 'max weight' + '║' + __pad_string(dataset.max_backpack_weight, max_len * 2 + 1) + '║')
	print('╠' + '═' * 10 + '╬' + '═' * max_len + '╦' + '═' * max_len +'╣')
	print('║' + 'algorithm ' + '║' + __pad_string('bruteforce', max_len) + '║' + __pad_string('greedy', max_len) + '║')
	print('╠' + '═' * 10 + '╬' + '═' * max_len + '╬' + '═' * max_len +'╣')
	compare = __compare_ints_to_str(solution2.total_weight, solution.total_weight)
	print('║' + 'weight    ' + '║' + __pad_string(solution.total_weight, max_len) + '║' + __pad_string(solution2.total_weight, max_len - 5) + compare + '║')
	print('╠' + '═' * 10 + '╬' + '═' * max_len + '╬' + '═' * max_len +'╣')
	compare = __compare_ints_to_str(solution2.total_value, solution.total_value)
	print('║' + 'value     ' + '║' + __pad_string(solution.total_value, max_len) + '║' + __pad_string(solution2.total_value, max_len - 5) + compare + '║')
	print('╠' + '═' * 10 + '╬' + '═' * max_len + '╬' + '═' * max_len +'╣')
	compare = __compare_ints_to_str(solution2.iterations, solution.iterations)
	print('║' + 'iterations' + '║' + __pad_string(solution.iterations, max_len) + '║' + __pad_string(solution2.iterations, max_len - 5) + compare + '║')
	print('╠' + '═' * 10 + '╬' + '═' * max_len + '╬' + '═' * max_len +'╣')
	max_items = max(len(solution.selected_items), len(solution2.selected_items))
	first_line = True
	for i in range(max_items):
		first = ''
		second = ''
		if len(solution.selected_items) > i:
			first = str(solution.selected_items[i])
		if len(solution2.selected_items) > i:
			second = str(solution2.selected_items[i])
		if first_line:
			print('║' + 'items     ', end = '')
			first_line = False
		else:
			print('║' + '          ', end = '')
		print('║' + __pad_string(first, max_len) + '║' + __pad_string(second, max_len) + '║')
	print('╚' + '═' * 10 + '╩' + '═' * max_len + '╩' + '═' * max_len +'╝')


def compare_algorithms(filename: str):
	dataset = knapsack.Dataset.from_file(filename)
	bruteforce_solution = knapsack.BruteforceMultiple.find_solution(dataset)
	greedy_solution = knapsack.GreedyMultiple.find_solution(dataset)
	print_solutions(filename, dataset, bruteforce_solution, greedy_solution)


if __name__ == "__main__":
	print('Please wait, it can take some time...')
	for filename in os.listdir('input_files'):
		if filename.endswith(".txt"): 
			compare_algorithms('input_files/' + filename)
	print('Done.')
