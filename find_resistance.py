#!/usr/bin/env python3

# Round number <number> to <decimals> decimals
def round_number(number, decimals=3):
	rounded_number = round(number, decimals)
	rounded_number_as_int = int(rounded_number)
	return (rounded_number_as_int if (rounded_number == rounded_number_as_int) else rounded_number)

# Split the elements in iterable <iterable> using function <filter_function>
# Returns ([<Elements for which <filter_function> returned True>], [<Elements for which <filter_function> returned False>])
def split(iterable, filter_function):
	filtered = []
	passed = []
	for element in iterable:
		(filtered if filter_function(element) else passed).append(element)
	return (filtered, passed)

# Returns the string obtained by repeating <string> <repetitions> times
def repeated_string(string, repetitions):
	return (string*repetitions)

# Abstract Class representing a resistance
class Resistance:
	def __init__(self, value):
		self.value = round_number(value)
	def __eq__(self, other):
		return (self.value == other.value)
	def __lt__(self, other):
		return (self.value < other.value)
	def __hash__(self):
		return hash(self.value)
	def __str__(self):
		return self.value_expression_with_unit_string
	def __repr__(self):
		return '<{name} ({value}){details}>'.format(
			name=self.__class__.__name__,
			value=self.value_with_unit_string,
			details=self.get_repr_details_string(),
		)
	@property
	def value_string(self):
		return '{value}'.format(
			value=self.value,
		)
	@property
	def value_with_unit_string(self):
		return '{value}Ω'.format(
			value=self.value_string,
		)
	@property
	def value_expression_with_unit_string(self):
		return '{value_expression}Ω'.format(
			value_expression=self.value_expression_string,
		)
	@property
	def schematic_string(self):
		return '\n'.join(self.get_schematic_line(line_index) for line_index in range(self.get_schematic_height()))
	def deviation_from_value(self, value):
		return (self.value - value)
	def absolute_deviation_from_value(self, value):
		return abs(self.deviation_from_value(value))

# Class representing a resistance made up from a single resistor
class Resistor_Resistance(Resistance):
	def __init__(self, value):
		super().__init__(value)
		self.number_of_resistors = 1
	@property
	def value_expression_string(self):
		return self.value_string
	def get_repr_details_string(self):
		return ''
	def get_schematic_width(self):
		return (len(self.value_with_unit_string) + 4)
	def get_schematic_height(self):
		return 1
	def get_schematic_line(self, line_index):
		return '─[{value}]─'.format(
			value=self.value_with_unit_string,
		)

# Abstract Class representing a resistance made up from multiple (serial or parallel) resistances
class Combined_Resistance(Resistance):
	def __init__(self, resistances):
		own_class_resistances, other_resistances = split(resistances, (lambda resistance: isinstance(resistance, self.__class__)))
		for own_class_resistance in own_class_resistances:
			other_resistances += own_class_resistance.resistances
		other_resistances.sort(reverse=True)
		self.resistances = other_resistances
		super().__init__(self.__class__.CALCULATE_RESISTANCE_VALUE_FUNCTION([resistance.value for resistance in self.resistances]))
		self.number_of_resistors = sum(resistance.number_of_resistors for resistance in self.resistances)
	@property
	def value_expression_string(self):
		return '({expression})'.format(
			expression=self.RESISTANCES_SEPARATOR.join(resistance.value_expression_string for resistance in self.resistances),
		)
	def get_repr_details_string(self):
		return ': {resistances}'.format(
			resistances=self.RESISTANCES_SEPARATOR.join(repr(resistance) for resistance in self.resistances),
		)

# Computes the serial resistance of the resistance values in array <resistance_values>
def calculate_serial_resistance_value(resistance_values):
	return sum(resistance_values)

# Class representing a resistance made up a multiple serial resistances
class Serial_Resistance(Combined_Resistance):
	RESISTANCES_SEPARATOR = '+'
	CALCULATE_RESISTANCE_VALUE_FUNCTION = calculate_serial_resistance_value
	def get_schematic_width(self):
		return sum(resistance.get_schematic_width() for resistance in self.resistances)
	def get_schematic_height(self):
		return max(resistance.get_schematic_height() for resistance in self.resistances)
	def get_schematic_line(self, line_index):
		return ''.join((resistance.get_schematic_line(line_index) if (line_index < resistance.get_schematic_height()) else repeated_string(' ', resistance.get_schematic_width())) for resistance in self.resistances)

# Computes the parallel resistance of the resistance values in array <resistance_values>
def calculate_parallel_resistance_value(resistance_values):
	common_multiple = 1
	for resistance_value in resistance_values:
		common_multiple *= resistance_value
	return (common_multiple / sum((common_multiple / resistance_value) for resistance_value in resistance_values))

# Returns the prefix/suffix of a Parallel_Resistance schematic line.
def parallel_schematic_prefix_suffix(line_index, first_line_index, is_last_resistance, end_character, middle_character, is_prefix):
	is_very_first_line = (line_index == 0)
	outer_character = ('─' if is_very_first_line else ' ')
	line = (outer_character if is_prefix else '')
	line += (('┬' if is_very_first_line else (end_character if is_last_resistance else middle_character)) if (line_index == first_line_index) else (' ' if is_last_resistance else '│'))
	if (not is_prefix):
		line += outer_character
	return line

# Class representing a resistance made up a multiple parallel resistances
class Parallel_Resistance(Combined_Resistance):
	RESISTANCES_SEPARATOR = '||'
	CALCULATE_RESISTANCE_VALUE_FUNCTION = calculate_parallel_resistance_value
	def get_schematic_width(self):
		return (max(resistance.get_schematic_width() for resistance in self.resistances) + 4)
	def get_schematic_height(self):
		return sum(resistance.get_schematic_height() for resistance in self.resistances)
	def get_schematic_line(self, line_index):
		next_first_line_index = 0
		for resistance_index, resistance in enumerate(self.resistances):
			first_line_index = next_first_line_index
			next_first_line_index = (first_line_index + resistance.get_schematic_height())
			if (first_line_index <= line_index < next_first_line_index):
				break
		is_last_resistance = (resistance_index == (len(self.resistances) - 1))
		line = parallel_schematic_prefix_suffix(line_index, first_line_index, is_last_resistance, '└', '├', True)
		line += resistance.get_schematic_line(line_index - first_line_index)
		line += repeated_string('─', (self.get_schematic_width() - (len(line) + 1)))
		line += parallel_schematic_prefix_suffix(line_index, first_line_index, is_last_resistance, '┘', '┤', False)
		return line

# Creates all possible resistances that can be created from <maximum_number_of_resistors> resistors.
# Returns a set of Resistance instances
def create_resistances(resistor_values, maximum_number_of_resistors):
	resistances = set()
	for resistor_value in resistor_values:
		resistances.add(Resistor_Resistance(resistor_value))
	for number_of_resistors in range(2, (maximum_number_of_resistors + 1)):
		resistances_copy = resistances.copy()
		for first_resistance in resistances_copy:
			for second_resistance in resistances_copy:
				if ((first_resistance.value >= second_resistance.value) and ((first_resistance.number_of_resistors + second_resistance.number_of_resistors) == number_of_resistors)):
					resistances.add(Parallel_Resistance([first_resistance, second_resistance]))
					resistances.add(Serial_Resistance([first_resistance, second_resistance]))
	return resistances

# Creates all possible resistances that can be created from <maximum_number_of_resistors> resistors.
# Returns a list of Resistance instances, ordered by deviation from target value <target_value>
def create_resistances_ordered_by_target_value(resistor_values, maximum_number_of_resistors, target_value):
	return sorted(list(create_resistances(resistor_values, maximum_number_of_resistors)), key=(lambda resistance: (resistance.absolute_deviation_from_value(target_value), resistance.number_of_resistors)))

# Parse resistance value <resistance_value>, which may either be a number or a string (for example "4.7k", "4k7" "4700R")
def parse_resistance_value(resistance_value):
	import re
	if isinstance(resistance_value, str):
		try:
			groups = re.fullmatch(r'(\d+(?:[\.,]\d+)?)(?:([mRΩkM])(\d+)?)?', resistance_value).groups()
			decimals = int(groups[2] or '0')
			return ((float(groups[0].replace(',', '.')) + (decimals / (10**len(str(decimals))))) * {'m':0.001, 'R':1, 'Ω':1, 'k':1000, 'M':1000000}[(groups[1] or 'R')])
		except AttributeError:
			raise ValueError('"{resistance_value}" is not a valid resistance value string'.format(
				resistance_value=resistance_value,
			))
	else:
		return resistance_value

# The resistor values of the E6 series
E6_SERIES_RESISTOR_VALUES = [round_number(multiplier * (10**e)) for e in range(8) for multiplier in [1.0, 1.5, 2.2, 3.3, 4.7, 6.8]]

# ----
# Main
# ----
if __name__ == '__main__':
	import argparse
	argument_parser = argparse.ArgumentParser(
		description = 'Find possibilities for creating a resistance close to a certain target value, by combining resistors',
	)
	argument_parser.add_argument(
		'target_value',
		type = str,
		help = 'The target resistance value',
	)
	argument_parser.add_argument(
		'--resistors', '-r',
		type = str,
		default = ','.join(str(value) for value in E6_SERIES_RESISTOR_VALUES),
		help = 'The available resistor values, as a comma-separated list, for example "100R,330,4k7,10k,1.0M" (Default: All E6 series values)',
	)
	argument_parser.add_argument(
		'--maximum', '--max', '-m',
		type = int,
		default = 2,
		help = 'The maximum number of resistors to use. Increasing this value exponentially increases computation time! (Default: 2)',
	)
	argument_parser.add_argument(
		'--results', '-n',
		type = int,
		default = 1,
		help = 'The maximum number of results to output, or 0 for all results. Results will be ordered by their deviation from the target value (Default: 1)',
	)
	arguments = argument_parser.parse_args()
	target_value = parse_resistance_value(arguments.target_value)
	resistor_values = [parse_resistance_value(resistor_value) for resistor_value in arguments.resistors.split(',')]
	resistances = create_resistances_ordered_by_target_value(resistor_values, arguments.maximum, target_value)
	if (arguments.results > 0):
		resistances = resistances[:arguments.results]
	for index, resistance in enumerate(resistances):
		if (index > 0):
			print(repeated_string('=', 40))
		deviation = resistance.deviation_from_value(target_value)
		print('{value} ({deviation_sign}{deviation_absolute}Ω/{deviation_sign}{deviation_relative}%): {expression}'.format(
			value=resistance.value_with_unit_string,
			deviation_sign=('+' if (deviation >= 0) else '-'),
			deviation_absolute=round_number(abs(deviation)),
			deviation_relative=round_number((abs(deviation) / target_value) * 100),
			expression=resistance.value_expression_with_unit_string,
		))
		print()
		print(resistance.schematic_string)
