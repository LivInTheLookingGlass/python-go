using_multiprocessing = False

if using_multiprocessing:
	import multiprocessing
	Value = multiprocessing.Value
else:
	class Value(object):
		def __init__(self, type='i', val=None):
			self.value = val

# Activation function section

def identity(value):
	return value


def step(value):
	"""A step function"""
	if value <= 0:
		return 0
	else:
		return 1

def sigmoid(value):
	"""The sigmoid function."""
	import math
	return 1.0 / (1.0 + math.exp(-value))


def tanh(value):
	import math
	return math.tanh(value)


def arctan(value):
	import math
	return math.atan(value)


def softsign(value):
	return value / (1 + abs(value))


def leaky_ReLU(value, weight):
	return max(value * weight, value)


def get_partial_ReLU(weight):
	from functools import partial
	return partial(leaky_ReLU, weight=weight)


def ReLU(value):
	return leaky_ReLU(value, 0)


def param_ReLU(value, weight):
	if value >= 0:
		return value
	else:
		return value * weight


def get_partial_PReLU(weight):
	from functools import partial
	return partial(param_ReLU, weight=weight)


def exp_ReLU(value, weight):
	if value >= 0:
		return value
	else:
		import math
		return weight * (math.e**value - 1)


def get_partial_ELU(weight):
	from functools import partial
	return partial(exp_ReLU, weight=weight)


def softplus(value):
	"""The softplus function"""
	import math
	return math.log(1 + math.e**x)


def bent_identity(value):
	import math
	return (math.sqrt(value**2 + 1) - 1) / float(2 + value)


def soft_exponential(value, weight):
	import math
	if weight > 0:
		return -(math.log(1 - weight * (value + weight)) / float(weight))
	elif weight == 0:
		return value
	else:
		return (math.e**(weight * value) - 1) / float(weight) + weight


def get_partial_soft_exponential(weight):
	from functools import partial
	return partial(soft_exponential, weight=weight)	


def sinusoid(value):
	import math
	return math.sin(value)


def sinc(value):
	if value == 0:
		return 1
	else:
		import math
		return math.sin(value) / float(value)


def gaussian(value):
	import math
	return math.e**(-value**2)

# End activation section


class Neural_Network(object):
	def __init__(self, arch, activation=tanh, convolutional=0):
		self.activation = activation
		self.convolutional = convolutional
		self.layers = []
		self.inputs = []
		self.readies = []
		for i in range(len(arch)):
			self.layers.append([])
			if convolutional:
				if not isinstance(arch[i], tuple) or len(arch[i]) != 2:
					raise TypeError("Architecture for convolutional networks must be fed as 2-item tuples. Arbitrary dimensions will be supported later\
									(Example: [(9,9), (5, 5), (3, 3), (1, 1)]")

				def distance(p0, p1):
					import math
					if len(p0) != len(p1):
						raise IndexError("Points do not have matching dimensionality")
					return math.sqrt(sum([(i - j)**2 for i, j in zip(p0, p1)]))

				if i > 0:
					print(i)
					ratiox = arch[i - 1][0] / float(arch[i][0])
					ratioy = arch[i - 1][1] / float(arch[i][1])
					for x in range(arch[i][0]):
						for y in range(arch[i][1]):
							# print(i, y + x * arch[i][1])
							indexes = [j for j in range(len(self.layers[-2])) if distance((x * ratiox, y * ratioy), (j / arch[i - 1][1], j % arch[i - 1][1])) <= convolutional]
							outputs = [self.layers[-2][j].output for j in indexes]
							readies = [self.layers[-2][j].ready for j in indexes]
							self.layers[-1].append(Neuron(outputs, readies=readies, activation=activation))
				else:
					from operator import mul
					for j in range(reduce(mul, arch[i])):	# n-dimension support achieved
						self.inputs.append(Value('f', 0))
						self.readies.append(Value('b', 0))
						self.layers[-1].append(Neuron([self.inputs[j]], readies=[self.readies[j]], activation=activation))
			else:
				for j in range(arch[i]):
					if i > 0:
						self.layers[-1].append(Neuron([n.output for n in self.layers[-2]], readies=[n.ready for n in self.layers[-2]], activation=activation))
					else:
						self.inputs.append(Value('f', 0))
						self.readies.append(Value('b', 0))
						self.layers[-1].append(Neuron([self.inputs[j]], readies=[self.readies[j]], activation=activation))

	def feed(self, inputs, multiple=False):
		if multiple:
			ret = []
			for i in inputs:
				ret.append(self.__feed__(i))
			return ret
		else:
			ret = self.__feed__(inputs)
			return ret

	def __feed__(self, inputs):
		if len(inputs) != len(self.inputs):
			raise IndexError("Incorrect length of inputs\
							  Expected " + str(len(self.inputs)) + ". Got " + str(len(inputs)))
		for i in range(len(inputs)):
			self.inputs[i].value = inputs[i]
			self.readies[i].value = True
		if not using_multiprocessing:
			for l in self.layers[:-1]:
				for n in l:
					n.process()
		ret = [n.process() for n in self.layers[-1]]
		if len(ret) == 1:
			ret = ret[0]
		self.unready_all()
		return ret

	def unready_all(self):
		for ready in self.readies:
			ready.value = False
		for l in self.layers:
			for n in l:
				n.ready.value = False

	def __del__(self):
		if using_multiprocessing:
			for layer in self.layers:
				for n in layer:
					n.thread.terminate()

	def get_serialized(self):
		serialized = [[self.sigmoid, self.convolutional]]
		for i in range(len(self.layers)):
			serialized.append([])
			for x in self.layers[i]:
				weights = [v for v in x.weights]
				biases = [v for v in x.biases]
				serialized[i + 1].append([weights, biases])
		return serialized

	def dump(self, protocol=2):
		import pickle
		return pickle.dumps(self.get_serialized(), protocol)

	@classmethod
	def load_serialized(cls, lst):
		meta = lst[0]
		lst = lst[1:]
		arch = [len(x) for x in lst]
		net = cls(arch, sigmoid=meta[0], convolutional=meta[1])
		for i in range(len(net.layers)):
			for j in range(len(net.layers[i])):
				for k in range(len(net.layers[i][j].weights)):
					net.layers[i][j].weights[k] = lst[i][j][0][k]
					net.layers[i][j].biases[k] = lst[i][j][1][k]
		return net

	@classmethod
	def load(cls, string):
		import pickle
		return cls.load_serialized(pickle.loads(string))


class Neuron(object):
	def __init__(self, inputs, readies=[], weights=None, biases=None, activation=tanh):
		import random
		self.inputs = inputs
		self.readies = readies
		self.weights = weights
		if not self.weights:
			self.weights = [random.gauss(0, 1) for x in inputs]
		self.biases = biases
		if not self.biases:
			self.biases = [random.gauss(0, 1) for x in inputs]
		try:
			activation(0)
			self.activation = activation
		except:
			raise Exception("Activation must be a function, and it must take one argument. If you're using a supplied activation function with two arguments, define the weight with the get_partial version")
		self.output = Value('f', 0.0)
		self.ready = Value('b', False)
		if using_multiprocessing:
			self.thread = multiprocessing.Process(target=Neuron_wrapper, args=(self,))
			self.thread.daemon = True
			self.thread.start()
		else:
			self.thread = False

	def process(self):
		while self.readies != [] and False in (x.value for x in self.readies):
			import time
			self.ready.value = False
			time.sleep(0.01)
		values = [self.weights[i] * self.inputs[i].value + self.biases[i] for i in range(len(self.inputs))]
		self.output.value = self.activation(sum(values))
		self.ready.value = True
		return self.activation(sum(values))

	def activation_prime(self, value):
		"""Derivative of the activation function (currently only works for sigmoid-like functions)."""
		val = self.activation(value)
		return (val * (1 - val))


def Neuron_wrapper(neuron):
	while True:
		neuron.process()