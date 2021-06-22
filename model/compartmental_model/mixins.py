import numpy as np


class QuarantineMixin:

    def quarantine(self, n):
        g = self.network()

        rng = np.random.default_rng()

        ms = list(g.neighbors(n))

        for m in ms:

            if rng.random() > self.p_rewire:
                continue

            if self.getCompartment(m) == self.SUSCEPTIBLE:
                self.removeEdge(n, m)

                m_prime = self.locus(self.SUSCEPTIBLE).draw()
                self.addEdge(m, m_prime)
