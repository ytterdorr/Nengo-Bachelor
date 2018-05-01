import nengo

model = nengo.Network()
with model:

	def printer(inp):
		printer._nengo_html_ = inp

	inp1 = nengo.Node(0)
	en = nengo.Ensemble(n_neurons=100, dimensions=1)
	display = nengo.Node(printer, size_in=1)

	nengo.Connection(inp1, en)
	nengo.Connection(en, display)