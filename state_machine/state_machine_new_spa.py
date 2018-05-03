import nengo
import nengo_spa as spa
import numpy as np
import matplotlib.pyplot as plt

d = 32
"""
with spa.Network() as model:
    scene = spa.Transcode('BLUE * CIRCLE + RED * SQUARE', output_vocab=d)
    query = spa.Transcode(lambda t: 'CIRCLE' if t < 0.25 else 'SQUARE', output_vocab=d)
    result = spa.State(vocab=d)

    scene * ~query >> result

    p = nengo.Probe(result.output, synapse=0.01)

with nengo.Simulator(model) as sim:
	sim.run(0.5)

plt.plot(sim.trange(), spa.similarity(sim.data[p], result.vocab))
plt.xlabel("Time [s]")
plt.ylabel("Similarity")
plt.legend(result.vocab, loc="best")

plt.show()

"""

with spa.Network() as model:
	stimulus = spa.Transcode('Hello', output_vocab=d)
	state = spa.State(vocab=d)
	nengo.Connection(stimulus.output, state.input)
	p = nengo.Probe(state.output, synapse=0.01)

with nengo.Simulator(model) as sim:
	sim.run(0.5)

plt.plot(sim.trange(), spa.similarity(sim.data[p], state.vocab))
plt.xlabel("Time [s]")
plt.ylabel("Similarity")
plt.legend(state.vocab, loc="best")

plt.show()
""""""