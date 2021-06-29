from epydemic import SIR, Monitor


class MonitoredSIR(SIR, Monitor):

    def __init__(self):
        super(MonitoredSIR, self).__init__()

    def build(self, params):
        """
        Build observation process and define compartments to track.
        :param params: experimental parameters.
        """
        super(MonitoredSIR, self).build(params)

        self.trackNodesInCompartment(SIR.SUSCEPTIBLE)
        self.trackNodesInCompartment(SIR.REMOVED)
