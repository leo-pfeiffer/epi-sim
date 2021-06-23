from typing import Final

from epydemic import SEIR, Monitor, Edge
from model.compartmental_model.mixins import QuarantineMixin


class SEIRWithQuarantine(SEIR, QuarantineMixin):

    P_QUARANTINE: Final[str] = 'epydemic.SEIRWithQuarantine.p_quarantine'  #: Parameter for probability of removal (recovery).

    def __init__(self):
        super(SEIRWithQuarantine, self).__init__()

    def infect(self, t : float, e : Edge):
        super(SEIRWithQuarantine).infect(t, e)
        n, _ = e
        self.quarantine(n)


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
