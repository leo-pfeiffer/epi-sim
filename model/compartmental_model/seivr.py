from typing import Any, Dict, Final

from epydemic import CompartmentedModel, Monitor
from epydemic.types import Node, Edge


class SEIVR(CompartmentedModel):

    _PREFIX: Final[str] = 'epydemic.SEIVR'

    # dynamic states
    SUSCEPTIBLE: Final[str] = f'{_PREFIX}.S'  # Susceptible compartment
    EXPOSED: Final[str] = f'{_PREFIX}.E'  # Exposed compartment
    INFECTED: Final[str] = f'{_PREFIX}.I'  # Infected compartment
    VACCINATED: Final[str] = f'{_PREFIX}.V'  # Vaccinated compartment
    REMOVED: Final[str] = f'{_PREFIX}.R'  # Removed compartment

    # model parameters
    P_EXPOSED: Final[str] = f'{_PREFIX}.p_exposed'  # Being initially exposed
    P_INFECT_ASYMPTOMATIC: Final[str] = f'{_PREFIX}.p_infect_a'  # Infection from asymptomatic contact
    P_INFECT_SYMPTOMATIC: Final[str] = f'{_PREFIX}.p_infect_s'  # Infection from symptomatic contact
    P_REMOVE: Final[str] = f'{_PREFIX}.p_remove'  # Recovering from an infection
    P_SYMPTOMS: Final[str] = f'{_PREFIX}.p_symptoms'  # Becoming symptomatic after exposure
    P_VACCINATED_INITIAL: Final[str] = f'{_PREFIX}.p_vac_init'  # Being initially vaccinated
    P_VACCINATED: Final[str] = f'{_PREFIX}.p_vac'  # Being vaccinated
    VACCINE_RRR: Final[str] = f'{_PREFIX}.vac_rrr'  # Relative Risk Reduction of vaccine

    # loci of the dynamics
    SE: Final[str] = f'{_PREFIX}.SE'  # Transmission from exposed to susceptible
    SI: Final[str] = f'{_PREFIX}.SI'  # Transmission from infected to susceptible
    EV: Final[str] = f'{_PREFIX}.EV'  # Transmission from exposed to vaccinated
    IV: Final[str] = f'{_PREFIX}.IV'  # Transmission from infected to vaccinated

    def __init__(self):
        super(SEIVR, self).__init__()

    def build(self, params: Dict[str, Any]):
        """
        Build the SEIVR model.
        :param params: experiment parameters
        """
        super(SEIVR, self).build(params)

        p_exposed = params[self.P_EXPOSED]
        p_infect_a = params[self.P_INFECT_ASYMPTOMATIC]
        p_infect_s = params[self.P_INFECT_SYMPTOMATIC]
        p_remove = params[self.P_REMOVE]
        p_symptoms = params[self.P_SYMPTOMS]
        p_vac_init = params[self.P_VACCINATED_INITIAL]
        p_vac = params[self.P_VACCINATED]
        vac_rrr = params[self.VACCINE_RRR]

        # add compartments
        self.addCompartment(self.SUSCEPTIBLE, 1.0 - p_exposed - p_vac_init)
        self.addCompartment(self.EXPOSED, p_exposed)
        self.addCompartment(self.INFECTED, p_vac_init)
        self.addCompartment(self.VACCINATED, 0.0)
        self.addCompartment(self.REMOVED, 0.0)

        # track edges
        self.trackEdgesBetweenCompartments(self.SUSCEPTIBLE, self.EXPOSED, name=self.SE)
        self.trackEdgesBetweenCompartments(self.SUSCEPTIBLE, self.INFECTED, name=self.SI)
        self.trackEdgesBetweenCompartments(self.EXPOSED, self.VACCINATED, name=self.EV)
        self.trackEdgesBetweenCompartments(self.INFECTED, self.VACCINATED, name=self.IV)

        # track nodes
        self.trackNodesInCompartment(self.SUSCEPTIBLE)
        self.trackNodesInCompartment(self.EXPOSED)
        self.trackNodesInCompartment(self.INFECTED)
        self.trackNodesInCompartment(self.VACCINATED)

        # infection events
        self.addEventPerElement(self.SE, p_infect_a, self.infect_asymptomatic)
        self.addEventPerElement(self.SI, p_infect_s, self.infect_symptomatic)
        self.addEventPerElement(self.EV, vac_rrr * p_infect_a, self.infect_vac_asymptomatic)
        self.addEventPerElement(self.IV, vac_rrr * p_infect_s, self.infect_vac_symptomatic)

        # other events ...
        self.addEventPerElement(self.EXPOSED, p_symptoms, self.symptoms)
        self.addEventPerElement(self.INFECTED, p_remove, self.remove)
        self.addEventPerElement(self.SUSCEPTIBLE, p_vac, self.vaccinate)

    def infect_asymptomatic(self, t: float, e: Edge):
        self.infect(t, e)

    def infect_symptomatic(self, t: float, e: Edge):
        self.infect(t, e)

    def infect_vac_asymptomatic(self, t: float, e: Edge):
        self.infect(t, e)

    def infect_vac_symptomatic(self, t: float, e: Edge):
        self.infect(t, e)

    def infect(self, t: float, e: Edge):
        n, _ = e
        self.changeCompartment(n, self.EXPOSED)
        self.markOccupied(e, t)

    def symptoms(self, t, n: Node):
        self.changeCompartment(n, self.INFECTED)

    def remove(self, t, n: Node):
        self.changeCompartment(n, self.REMOVED)

    def vaccinate(self, t, n: Node):
        self.changeCompartment(n, self.VACCINATED)


class MonitoredSEIVR(SEIVR, Monitor):

    def __init__(self):
        super(MonitoredSEIVR, self).__init__()

    def build(self, params: Dict[str, Any]):
        super().build(params)

        self.trackNodesInCompartment(SEIVR.REMOVED)
