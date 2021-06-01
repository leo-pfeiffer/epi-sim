from epydemic import CompartmentedModel, StochasticDynamics
import networkx


class SIR(CompartmentedModel):
    # the possible dynamics states of a node for SIR dynamics
    SUSCEPTIBLE = 'S'
    INFECTED = 'I'
    REMOVED = 'R'

    # the model parameters
    P_INFECTED = 'pInfected'
    P_INFECT = 'pInfect'
    P_REMOVE = 'pRemove'

    # the edges at which dynamics can occur
    SI = 'SI'

    def build(self, params):
        pInfected = params[self.P_INFECTED]
        pInfect = params[self.P_INFECT]
        pRemove = params[self.P_REMOVE]

        # Add compartments with initial probabilities
        self.addCompartment(self.INFECTED, pInfected)
        self.addCompartment(self.REMOVED, 0.0)
        self.addCompartment(self.SUSCEPTIBLE, 1 - pInfected)

        # Create Loci to track I nodes and SI edges
        self.trackNodesInCompartment(self.INFECTED)
        self.trackEdgesBetweenCompartments(self.SUSCEPTIBLE, self.INFECTED, name=self.SI)

        # Add events that occur with a given probability to each element in the locus
        self.addEventPerElement(self.SI, pInfect, self.infect)
        self.addEventPerElement(self.INFECTED, pRemove, self.remove)

    def infect(self, t, e) -> None:
        """
        Infect event.
        :param t: time index
        :param e: edge of infection
        :return: None
        """
        (n, m) = e
        self.changeCompartment(n, self.INFECTED)
        self.markOccupied(e, t)

    def remove(self, t, n) -> None:
        """
        Remove event.
        :param t: time index
        :param n: node to remove
        :return: None
        """
        self.changeCompartment(n, self.REMOVED)


if __name__ == '__main__':
    param = dict()
    param[SIR.P_INFECT] = 0.1
    param[SIR.P_REMOVE] = 0.5
    param[SIR.P_INFECTED] = 0.01

    N = 1000
    kmean = 5
    phi = (kmean + 0.0) / N

    g = networkx.erdos_renyi_graph(N, phi)

    m = SIR()
    e = StochasticDynamics(m, g)
    rc = e.set(param).run()

    from pprint import pprint
    pprint(rc)
