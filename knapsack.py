#!/usr/bin/env python

__copyright__ = "Copyright 2020, Piotr Obst"

from abc import ABC, abstractmethod
from copy import copy
import math
from typing import List, Tuple


class Item:
	
	def __init__(self, weight: int, value: int, amount: int = 1):
		self.weight = weight
		self.value = value
		self.amount = amount  # amount equal to -1 means unlimited supply of that item

	def __str__(self):
		message = 'Item(weight: ' + str(self.weight) +', value: ' + str(self.value)
		if self.amount > 1:
			message += ', amount: ' + str(self.amount)
		return message + ')'


class Solution:

	def __init__(self, total_weight, total_value, selected_items, iterations):
		self.total_weight = total_weight
		self.total_value = total_value
		self.selected_items = selected_items
		self.iterations = iterations


class Dataset:

	def __init__(self):
		self.items = []
		self.max_backpack_weight = 0
		self.amount_gt_one = False  # amount of any item is grater than one

	@staticmethod
	def __represents_int(string: str) -> bool:
		try: 
			int(string)
			return True
		except ValueError:
			return False

	def load_from_file(self, path_to_file: str) -> List[Item]:
		items = []
		with open(path_to_file) as file:
			first_line = True
			for line in file:  # weight value (amount)
				if line.startswith('#'):  # lines starting with `#` are comments
					continue
				if first_line:
					arguments = line.split()
					if len(arguments) != 1 or not self.__represents_int(arguments[0]):
						print("File loader: First line should contain only one integer - max backpack weight.")
						return
					self.max_backpack_weight = int(line)
					first_line = False
					continue
				arguments = line.split()
				if len(arguments) < 2:
					print("File loader: Each item should have at least weight and value!")
					return
				if len(arguments) > 3:
					print("File loader: Only weigh, value and amount of each item is allowed!")
					return
				for i in range(len(arguments)):
					if not self.__represents_int(arguments[i]):
						print("File loader: Only integer values are allowed!")
						return
					arguments[i] = int(arguments[i])
				item = Item(*arguments)
				items.append(item)
				if item.amount > 1:
					self.amount_gt_one = True
		self.items = items

	def add_item(self, item: Item):
		self.items.append(item)
		if item.amount > 1:
			self.amount_gt_one = True

	@classmethod
	def from_file(cls, path_to_file: str):
		dataset = cls()
		dataset.load_from_file(path_to_file)
		return dataset


class KnapsackSolver(ABC):

	@classmethod
	@abstractmethod
	def find_solution(cls, dataset: Dataset) -> Solution:
		"""Return array containing total backpack weight, total backpack value, a list of packed items and a number of iterations."""
		pass


class Bruteforce(KnapsackSolver):

	@staticmethod
	def __pack_items(items: List[Item], combination: int, max_backpack_weight: int) -> Tuple[int, int, bool]:
		total_weight = 0
		total_value = 0
		too_heavy = False
		for j in range(len(items)):
			if combination & (2 ** j):  # binnary multiplication used to count only selected items in that combination
				total_weight += items[j].weight
				total_value += items[j].value
				if total_weight > max_backpack_weight:
					too_heavy = True
					break
		return (total_weight, total_value, too_heavy)

	@classmethod
	def __find_optimum(cls, items: List[Item], max_backpack_weight: int) -> Tuple[int, int, int, int]:
		max_total_value = 0
		optimal_items = 0
		optimal_items_weight = 0
		iterations = 0
		for combination in range(1, 2 ** len(items)):  # iterate over all combinations
			iterations += 1
			total_weight, total_value, too_heavy = cls.__pack_items(items, combination, max_backpack_weight)
			if too_heavy:
				continue
			if total_value > max_total_value:
				max_total_value = total_value
				optimal_items = combination
				optimal_items_weight = total_weight
			elif total_value == max_total_value and total_weight < optimal_items_weight:
				optimal_items = combination
				optimal_items_weight = total_weight
		return (optimal_items_weight, max_total_value, optimal_items, iterations)

	@staticmethod
	def __get_selected_items(items: List[Item], optimal_items: int) -> List[Item]:
		selected_items = []
		for i in range(len(items)):
				if optimal_items & (2 ** i):  # binnary multiplication used to count only selected items in optimal combination
					selected_items.append(items[i])
		return selected_items

	@classmethod
	def find_solution(cls, dataset: Dataset) -> Solution:
		optimal_items_weight, max_total_value, optimal_items, iterations = cls.__find_optimum(dataset.items, dataset.max_backpack_weight)
		selected_items = cls.__get_selected_items(dataset.items, optimal_items)
		return Solution(optimal_items_weight, max_total_value, selected_items, iterations)

class Greedy(KnapsackSolver):


	class __GreedyItem:

		def __init__(self, item: Item):
			self.weight = item.weight
			self.value = item.value
			self.ratio = self.value / self.weight

		def get_as_item(self) -> Item:
			'''Convert to a normal Item.'''
			return Item(self.weight, self.value)


	@staticmethod
	def __get_item_ratio(item: Item) -> int:
		'''Function required for sorting.'''
		return item.ratio

	@classmethod
	def __sort_items(cls, items: List[Item]) -> List[Item]:
		sorted_items = []
		for item in items:
			sorted_items.append(cls.__GreedyItem(item))  # Items converted to GreedyItems, because `ratio` is needed
		return sorted(sorted_items, reverse = True, key = cls.__get_item_ratio)

	@staticmethod
	def __pack_items(sorted_items: List[Item], max_backpack_weight: int) -> Tuple[int, int, List[int], int]:
		selected_items = []
		total_value = 0
		total_weight = 0
		iterations = 0
		for item in sorted_items:
			iterations += 1
			if total_weight + item.weight > max_backpack_weight:
				continue
			total_weight += item.weight
			total_value += item.value
			selected_items.append(item.get_as_item())
			if total_weight == max_backpack_weight:
				break
		return (total_weight, total_value, selected_items, iterations)

	@classmethod
	def find_solution(cls, dataset: Dataset) -> Solution:
		sorted_items = cls.__sort_items(dataset.items)
		return Solution(*cls.__pack_items(sorted_items, dataset.max_backpack_weight))

class BruteforceMultiple(KnapsackSolver):

	class BruteforceItem:

		def __init__(self, item: Item, id: int):
			self.weight = item.weight
			self.value = item.value
			self.id = id

	@classmethod
	def __unpack_items(cls, items: List[Item], max_backpack_weight: int) -> List[Item]:
		items_unpacked = []  # array of single items (if an item in items has amount > 1, then it is added here multiple times)
		for i in range(len(items)):
			bruteforce_item = cls.BruteforceItem(items[i], i)  # Items converted to BruteforceItems, because `id` is needed
			item_amount = items[i].amount
			if item_amount == -1:  # amount equal to -1 means unlimited supply of that item
				if items[i].weight <= 0:  # if weight is less or equal to 0, then ignore that item
					item_amount = 0
				else:
					item_amount = max_backpack_weight // items[i].weight  # calculate maximum number of items of this kind, that be packed
			for _ in range(item_amount):
				items_unpacked.append(bruteforce_item)
		return items_unpacked

	@staticmethod
	def __pack_items(items_unpacked: List[Item], combination: int, max_backpack_weight: int) -> Tuple[int, int, bool]:
		total_weight = 0
		total_value = 0
		too_heavy = False
		for j in range(len(items_unpacked)):
			if combination & (2 ** j):  # binnary multiplication used to count only selected items in that combination
				total_weight += items_unpacked[j].weight
				total_value += items_unpacked[j].value
				if total_weight > max_backpack_weight:
					too_heavy = True
					break
		return (total_weight, total_value, too_heavy)

	@classmethod
	def __find_optimum(cls, items_unpacked: List[Item], max_backpack_weight: int) -> Tuple[int, int, int, int]:
		max_total_value = 0
		optimal_items = 0
		optimal_items_weight = 0
		iterations = 0
		for combination in range(1, 2 ** len(items_unpacked)):  # iterate over all combinations
			iterations += 1
			total_weight, total_value, too_heavy = cls.__pack_items(items_unpacked, combination, max_backpack_weight)
			if too_heavy:
				continue
			if total_value > max_total_value:
				max_total_value = total_value
				optimal_items = combination
				optimal_items_weight = total_weight
			elif total_value == max_total_value and total_weight < optimal_items_weight:
				optimal_items = combination
				optimal_items_weight = total_weight
		return (optimal_items_weight, max_total_value, optimal_items, iterations)

	@staticmethod
	def __get_item_amount(items: List[Item], items_unpacked: List[Item], optimal_items: int) -> List[int]:
		item_amount = [0] * len(items)
		for i in range(len(items_unpacked)):
				if optimal_items & (2 ** i):  # binnary multiplication used to count only selected items in optimal combination
					item_amount[items_unpacked[i].id] += 1
		return item_amount  # items other than the optimal ones have amount of 0

	@staticmethod
	def __get_selected_items(items: List[Item], item_amount: List[int]) -> List[Item]:
		selected_items = []
		for i in range(len(items)):
			if item_amount[i] > 0:  # take only items that are packed (when amount > 0)
				new_item = copy(items[i])
				new_item.amount = item_amount[i]
				selected_items.append(new_item)
		return selected_items

	@classmethod
	def find_solution(cls, dataset: Dataset) -> Solution:
		items_unpacked = cls.__unpack_items(dataset.items, dataset.max_backpack_weight)
		optimal_items_weight, max_total_value, optimal_items, iterations = cls.__find_optimum(items_unpacked, dataset.max_backpack_weight)
		item_amount = cls.__get_item_amount(dataset.items, items_unpacked, optimal_items)
		selected_items = cls.__get_selected_items(dataset.items, item_amount)
		return Solution(optimal_items_weight, max_total_value, selected_items, iterations)

class GreedyMultiple(KnapsackSolver):

	class __GreedyItem:

		def __init__(self, item: Item):
			self.weight = item.weight
			self.value = item.value
			self.amount = item.amount  # amount equal to -1 means unlimited supply of that item
			self.ratio = self.value / self.weight

		def get_as_item(self) -> Item:
			'''Convert to a normal Item.'''
			return Item(self.weight, self.value, self.amount)


	@staticmethod
	def __get_item_ratio(item: Item) -> int:
		'''Function required for sorting.'''
		return item.ratio

	@classmethod
	def __sort_items(cls, items: List[Item]) -> List[Item]:
		sorted_items = []
		for item in items:
			sorted_items.append(cls.__GreedyItem(item))  # Items converted to GreedyItems, because `ratio` is needed
		return sorted(sorted_items, reverse = True, key = cls.__get_item_ratio)

	@staticmethod
	def __pack_items(sorted_items: List[Item], max_backpack_weight: int) -> Tuple[int, int, List[int], int]:
		amounts = [0] * len(sorted_items)
		total_value = 0
		total_weight = 0
		iterations = 0
		for i in range(len(sorted_items)):
			item = sorted_items[i]
			while item.amount > amounts[i] or (item.amount == -1 and item.weight > 0):  # amount equal to -1 means unlimited supply of that item
				iterations += 1
				if total_weight + item.weight > max_backpack_weight:
					break
				total_weight += item.weight
				total_value += item.value
				amounts[i] += 1
			if total_weight == max_backpack_weight:
				break
		return (total_weight, total_value, amounts, iterations)

	@staticmethod
	def __get_selected_items(sorted_items: List[Item], amounts: List[int]) -> List[Item]:
		selected_items = []
		for i in range(len(sorted_items)):
			if amounts[i] > 0:  # if at least one Item of that kind is packed
				as_item = sorted_items[i].get_as_item()
				as_item.amount = amounts[i]  # set Item.amount to an amount that was packed
				selected_items.append(as_item)
		return selected_items

	@classmethod
	def find_solution(cls, dataset: Dataset) -> Solution:
		sorted_items = cls.__sort_items(dataset.items)
		total_weight, total_value, amounts, iterations = cls.__pack_items(sorted_items, dataset.max_backpack_weight)
		selected_items = cls.__get_selected_items(sorted_items, amounts)
		return Solution(total_weight, total_value, selected_items, iterations)
