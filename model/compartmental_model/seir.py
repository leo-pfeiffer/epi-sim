from typing import Final, Dict, Any

from epydemic import SEIR, Monitor, Node
from model.compartmental_model.mixins import QuarantineMixin


class SEIRWithQuarantine(SEIR, QuarantineMixin):

    P_QUARANTINE: Final[str] = 'epydemic.SEIRWithQuarantine.p_quarantine'  #: Parameter for probability of quarantine

    def __init__(self):
        super(SEIRWithQuarantine, self).__init__()
        self._p_quarantine: float = 0.

    def build(self, params: Dict[str, Any]):
        super(SEIRWithQuarantine, self).build(params)

        self.trackNodesInCompartment(self.SUSCEPTIBLE)

        # define _p_quarantine for QuarantineMixin
        self._p_quarantine = params[self.P_QUARANTINE]

    def symptoms(self, t, n: Node):
        super(SEIRWithQuarantine, self).symptoms(t, n)
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


class MonitoredSEIRWithQuarantine(SEIRWithQuarantine, Monitor):

    def __init__(self):
        super(MonitoredSEIRWithQuarantine, self).__init__()

    def build(self, params):
        """
        Build observation process and define compartments to track.
        :param params: experimental parameters.
        """

        super(MonitoredSEIRWithQuarantine, self).build(params)

        self.trackNodesInCompartment(SEIRWithQuarantine.REMOVED)
