from collections import Counter
import collections
import itertools
import numpy
import random
import subprocess as sub
from sympy.solvers import solve
from sympy import *
import sys

def input_points(s):
	points = {s.split(',').index(x): set(int(a) for a in x.split()) for x in s.split(',')}
	return points

def dual_solve(system):
	sol = solve(system, complex = True, manual = True)
	if not sol:
		sol2 = solve(system, complex = True)
		return sol2
	else:
		return sol

class Alpha_proj(object):
	def __init__(self, name):
		self.name = name

	def f_points_alpha(self, pointsP, name):
		points = []
		for p in pointsP:
			if name in p:
				points.append(p)
		return points

	def f_double_points_alpha(self, points, X, line):
		if points == []:
			double_points = X
		else:
			double_points = (X.difference(set.union(*points)))
		return double_points

	def f_alpha_proj(self, line, points, global_points, X):
		alpha_proj = {key: None for key in X.difference({line})}

		for p in points:
			if line in p:
				for i in p.difference({line, self.name}):
					alpha_proj[i] = 0
			if line not in p:
				for i in p - {self.name}:
					alpha_proj[i] = Symbol('a_{}'.format(global_points.index(p)))

		for i in set(self.f_double_points_alpha(points,X,line)).difference({line}):
			alpha_proj[i] = Symbol('b_{}{}'.format(self.name,i))

		counter = Counter({k:v for k, v in alpha_proj.items() if v != 0}.values())
		maxim = max(i for i in counter.values())
		for c in counter.keys():
			if counter[c] == maxim:
				max_c = c
				break

		for v in alpha_proj.values():
			for k, val in alpha_proj.iteritems():
				if val == max_c:
						alpha_proj[k] = 1
			break
		return  alpha_proj 


class Combinatorial_Configuration(object):
	def __init__(self, input_points, input_arr_cardinal):

		self.set_of_points = input_points
		self.cardinal_of_arrangement = input_arr_cardinal

	def validate_input_points_multiplicity(self):
		test = True
		for m in self.set_of_points.values():
			if len(m) < 3:
				test = False
				print 'incorrect input: some of the declared points have multiplicity smaller than 3! '
		return test

	def validate_input_points_overlap(self):
		test = True
		for pair in set(itertools.combinations(set(self.set_of_points.keys()), 2)):
			if len(self.set_of_points[pair[0]] & self.set_of_points[pair[1]]) > 1:
				test = False
				print 'incorrect input: there are multiple points with more than one line in common! '
		return test

	def validate_input_points(self):
		return self.validate_input_points_multiplicity() and self.validate_input_points_overlap()

	def validate_arrangement_cardinal(self):
		test = True
		if max(set().union(*self.set_of_points.values())) > self.cardinal_of_arrangement: 
			test = False
			print 'incorrect input: the arrangement does not contain all the '\
			' hyperplanes appearing in the multiple points declared!'
		return test

	def test_pencil_like(self, N):
		test = False
		M = max(set().union(*self.set_of_points.values()))
		if len(self.set_of_points) == 1 and M == N:
			test = True
			print 'the arrangement is a pencil of {} lines of equations:'.format(N)
			print ' \n L_1 : x \n \n L_2 : y \n'
			for i in range(3, N + 1):
				print ' L_{} : x+a_{}*y \n '.format(i, i)
			print '(the obvious restrictions on the values of a_i apply to make sure'\
			' that the equations are distinct)'
		return test

	def test_almost_pencil_like(self, N):
		test = False
		M = max(set().union(*self.set_of_points.values()))
		if len(self.set_of_points) == 1 and M < N:
			test = True
			print 'the arrangement is a pencil of {} lines '.format(M)
			print 'with {} general position line(s) added, '.format(N - M)
			print 'of equations: \n L_1 : x \n \n L_2 : y \n'
			for i in range(3, M + 1):
				print ' L_{} : x+a_{}*y  \n '.format(i, i)
			print ' L_{} : z  \n '.format(M + 1)
			for j in range (M + 2, N + 1):
				print '\n L_{} : a_{}*x+b_{}*y+z \n '.format(j, j, j)
			print '(the obvious restrictions on the values of a_i, b_i apply '\
				'to make sure that the equations are distinct and that the'\
				' general position claim holds)'
		return test

	def setIndeterminates(self, N):
		P = max(self.set_of_points.values(), key = len) # a maximum multiplicity point
		B = set(range(1, N + 1)) - P
		last_line = list(B)[-1]
		points_in_P = [p for p in self.set_of_points.values() if (p != P and len(P&p) == 1)] # multiple points on the lines through P
		alpha_projs = dict.fromkeys(list(P))

		for i in P:
			l = Alpha_proj(i).f_points_alpha(points_in_P, i)
			alpha_projs[i] = Alpha_proj(i).f_alpha_proj(last_line, l, self.set_of_points.values(), B)

		u = {key: Symbol('u_{}'.format(key)) for key in range(1, len(alpha_projs) - 1)}
		t = {key: Symbol('v_{}'.format(key)) for key in range(1, len(alpha_projs) - 1)}
		ls = alpha_projs.values()
		dict_indeterminates = {'P' : P, 'B' : B, 'last_line' : last_line, 'u' : u, 't' : t, 'ls' : ls}
		return dict_indeterminates

	def systemSol(self, N):
		d = self.setIndeterminates(N)
		P = d['P']
		B = d['B']
		last_line = d['last_line']
		u = d['u']
		t = d['t']
		ls = d['ls']
		points_in_B = [p for p in self.set_of_points.values() if (p != P and len(B&p) == len(p))] # multiple points on the subarrangement B
		subconfig_B = []

		for x in points_in_B:
			if last_line in x:
				first = list(x)[0]
				M = Matrix(([ls[0][first], ls[1][first], 1],[0, 0, 1]))
				subconfig_B.extend([M.row_insert(0, Matrix([[ls[0][i], ls[1][i], 1]])).det() for i in x - {last_line, first}])
			else:
				r = list(x)[:2]
				M = Matrix(([ls[0][r[0]], ls[1][r[0]], 1], [ls[0][r[1]], ls[1][r[1]], 1]))
				subconfig_B.extend([M.row_insert(0, Matrix([[ls[0][i], ls[1][i], 1]])).det() for i in x - set(r)])

		Q = [t[i]*ls[0][j] + u[i]*ls[1][j] - ls[i+1][j] for j in B - {last_line} for i in u.keys()] + subconfig_B
		S = dual_solve(Q)
		return S

	def describe_realization_space(self, N):
		d = self.setIndeterminates(N)
		P = d['P']
		B = d['B']
		ls = d['ls']
		last_line = d['last_line']
		u = d['u']
		t = d['t']
		S = self.systemSol(N)
		if S:
			ls_subs = [{} for i in range (len(ls))]

			for j in range(len(S)):
				for k in range(len(ls)):
					for i in B - {last_line}:
						if type(ls[k][i]) == int:
							ls_subs[k][i] = ls[k][i]
						else: 
							ls_subs[k][i] = ls[k][i].subs(S[j])

				print '\n the set S_{} of hyperplane equations is: '.format(j)

				for i in B.difference({last_line}):
					print '\n L_{} : '.format(i), sympify('({})*x + ({})*y + z'.format(ls_subs[0][i], ls_subs[1][i]))

				print '\n L_{} : z \n \n L_{} : y \n \n L_{} : x'.format(last_line,list(P)[0],list(P)[1])

				for i in u.keys():
					print  '\n L_{} : '.format(list(P)[i+1]), sympify('({})*x - ({})*y \n'.format(u[i].subs(S[j]), t[i].subs(S[j])))
			print '\n A finite set of values for the parameters is excluded.'



