from epydemic import SEIR, Monitor


class MonitoredSEIR(SEIR, Monitor):

    def __init__(self):
        super(MonitoredSEIR, self).__init__()

    def build(self, params):
        """
        Build observation process and define compartments to track.
        :param params: experimental parameters.
        """

        super(MonitoredSEIR, self).build(params)

        self.trackNodesInCompartment(SEIR.SUSCEPTIBLE)
        self.trackNodesInCompartment(SEIR.REMOVED)
