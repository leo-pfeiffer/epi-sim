import numpy as np
from epydemic import Node


class QuarantineMixin:
    """
    Mixin class for compartmental models to implement a quarantine.
    To use the mixin:
    - add it as a Parent using multiple inheritance
    - define aat least a `SUSCEPTIBLE`  compartment
    - define the class model parameter p_quarantine` (the probability of an
        infected-adjacent node to be put in quarantine)
    - Call the `quarantine` method of the mixin when required (e.g. from the
        `infect` event)
    """

    def quarantine(self, n: Node):
        """
        Perform a quarantine event on node `n` by removing a fraction
        `p_quarantine` from its susceptible adjacent neighbors.
        This method is taken directly from
            Dobson (2020) - Epidemic Modelling. p. 139
        :param n: Node
        """
        g = self.network()

        rng = np.random.default_rng()

        neighbors = list(g.neighbors(n))

        for neighbor in neighbors:

            # Keep going with probability `p_quarantine`
            if rng.random() > self.p_quarantine:
                continue

            # Only remove susceptible neighbors
            if self.getCompartment(neighbor) == self.SUSCEPTIBLE:
                self.removeEdge(n, neighbor)

                neighbor_prime = self.locus(self.SUSCEPTIBLE).draw()
                self.addEdge(neighbor, neighbor_prime)
