using_multiprocessing = True

if using_multiprocessing:
	import multiprocessing
	Value = multiprocessing.Value
else:
	class Value(object):
		def __init__(self, type='i', val=None):
			self.value = val


class Neural_Network(object):
	def __init__(self, arch, sigmoid=True, convolutional=False):
		self.sigmoid = sigmoid
		self.convolutional = convolutional
		self.layers = []
		self.inputs = [Value('f', 0) for i in range(arch[0])]
		self.readies = [Value('b', 0) for i in range(arch[0])]
		for i in range(len(arch)):
			self.layers.append([])
			for j in range(arch[i]):
				if convolutional:
					print("Convolutional networks are not yet supported")
				elif i > 0:
					self.layers[-1].append(Neuron([n.output for n in self.layers[-2]], readies=[n.ready for n in self.layers[-2]], sigmoid=sigmoid))
				else:
					self.layers[-1].append(Neuron([self.inputs[j]], readies=[self.readies[j]], sigmoid=sigmoid))

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
			raise IndexError("Incorrect length of inputs")
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


class Neuron(object):
	def __init__(self, inputs, readies=[], weights=None, biases=None, sigmoid=True):
		import random
		self.inputs = inputs
		self.readies = readies
		self.weights = weights
		if not self.weights:
			self.weights = [random.gauss(0, 1) for x in inputs]
		self.biases = biases
		if not self.biases:
			self.biases = [random.gauss(0, 1) for x in inputs]
		if not sigmoid:
			self.sigmoid = self.step
		self.output = Value('f', 0.0)
		self.ready = Value('b', False)
		if using_multiprocessing:
			self.thread = multiprocessing.Process(target=Neuron_wrapper, args=(self,))
			self.thread.daemon = True
			self.thread.start()
		else:
			self.thread = False

	def process(self):
		while self.readies != [] and False in [x.value for x in self.readies]:
			import time
			time.sleep(0.1)
		values = [self.weights[i] * self.inputs[i].value + self.biases[i] for i in range(len(self.inputs))]
		self.output.value = self.sigmoid(sum(values))
		self.ready.value = True
		return self.sigmoid(sum(values))

	def sigmoid(self, value):
		"""The sigmoid function."""
		import math
		return 1.0 / (1.0 + math.exp(-value))

	def step(self, value):
		"""A step function posing as the sigmoid function."""
		if value <= 0:
			return 0
		else:
			return 1

	def sigmoid_prime(self, value):
		"""Derivative of the sigmoid function."""
		sigmoid = self.sigmoid(value)
		return (sigmoid * (1 - sigmoid))


def Neuron_wrapper(neuron):
	while True:
		neuron.process()