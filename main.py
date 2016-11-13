
from MODULES.proj_points import *

points = input_points()
arr_cardinal = input_arr_cardinal()

config = Combinatorial_Configuration(points, arr_cardinal)

config.validate_input_points()

config.validate_arrangement_cardinal()

if config.validate_input_points() and config.validate_arrangement_cardinal():
	config.test_pencil_like(arr_cardinal)
	if not config.test_pencil_like(arr_cardinal):
			config.describe_realization_space(arr_cardinal)

# Hesse: 1 4 7 10, 2 4 8 11, 3 4 9 12, 1 5 8 12, 2 5 9 10,3 5 7 11, 1 6 9 11, 2 6 7 12, 3 6 8 10