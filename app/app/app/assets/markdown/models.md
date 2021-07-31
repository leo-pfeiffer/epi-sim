# Models

The epidemic models used in this application are so-called *compartmental models*.
Compartmental models divide the population in different *compartments* based
according to the current stage of the disease. For example, in one of the most
widely used compartmental models, the *SIR*, we have the *SUSCEPTIBLE*, 
*INFECTED*, and *REMOVED* compartments. Individuals start out as susceptible,
move into the *INFECTED* compartments when they contract the disease, and 
finally transition to *REMOVED* once they have recovered or died.

Originally, compartmental models were solved purely mathematically using
Ordinary Differential Equations (ODEs). More recently, they have also been
used in simulation-based modelling as is the case in this thesis. The 
implementation of the models in our case was done using the epidemic modelling
framework [epydemic](https://github.com/simoninireland/epydemic).

Compartmental models are very easily extendable by adding more compartments.
Incorporated in this app are two extensions.

### SEIR
*SEIR* extends the classical *SIR* model by the *EXPOSED* compartment, which
hold all those individuals that have contracted the disease but are not 
symptomatic yet. 

The following figure depicts the transitions and probabilities
between compartments. The Dashed arrows represent the transmission of the 
disease; solid arrows represent compartment transitions. The colour of 
the arrow corresponds to the colour of the compartment that is 
responsible for the transition. The mathematical symbols are explained in the
tables at the bottom of this page.

![SEIR flow diagram ><](/assets/img/SEIR-adapted.png)

### SEIVR
*SEIVR* adds yet another compartment, *VACCINATED* containing all those 
individuals that have received a vaccine against the disease. No vaccine is 
100% effective, so it is possible for vaccinated individuals to become infected,
albeit with a smaller probability. This probability is given by multiplying
the original probability of infection by 1 minus the relative risk reduction 
(RRR) of the vaccine.

For the *SEIVR* based models, you can change the following parameters in the
control bar on the main page:

- *p_vaccinated*
- *p_vaccinated_initial*
- *rrr*

A diagram of the compartments and transitions is given below. Again, the
mathematical symbols are explained in the tables at the bottom of this page.
![SEIVR flow diagram ><](/assets/img/SEIVR.png)

### Quarantine
Quarantine are used to isolate infectious or potentially infectious individuals 
by temporarily shielding them from interactions with other susceptible 
individuals to prevent the spread of the disease. This is implemented in our 
models by changing the structure of the network by removing edges to and from 
the quarantined nodes with some probability.

The models including the extension are called *SEIR_Q* and *SEIVR_Q* 
respectively. For these models, you can set the probability of 
quarantine *p_quarantine* via the control bar on the main page.

----
### Parameterisation

The following tables give an overview of all parameters used in the model.
Disease specific parameters are listed in extra tables.

#### General parameters
| Parameter             | Mathematical symbol | Value          | Description                        |
|-----------------------|---------------------|----------------|------------------------------------|
| P_EXPOSED             | n/a                 | 0.01           | Pr. of initially exposed           |
| P_INFECT_SYMPTOMATIC  | &beta;              | **&#42**       | Pr. of infection (I infects S)     |
| P_INFECT_ASYMPTOMATIC | &gamma;             | **&#42**       | Pr. of infection (E infects S)     |
| P_VACCINATED          | &nu;                | **&#42;&#42;** | Pr. of getting vaccinated          |
| P_VACCINATED_INITIAL  | n/a                 | **&#42;&#42;** | Pr. of initial vaccination         |
| VACCINE_RRR           | &rho;               | **&#42;&#42;** | Vaccine efficacy                   |
| P_QUARANTINE          | n/a                 | **&#42;&#42;** | Pr. of quarantine                  |

**&#42;** Infection rates are calculated based on *R0* of the disease as well as
network that is used. A straightforward explanation of how this is done is
provided in the [documentation of epydemic](https://pyepydemic.readthedocs.io/en/latest/cookbook/from-r-to-probabilities.html).
The asymptomatic infection rate is assumed to be half the symptomatic infection rate.

**&#42;&#42;** User can set these parameters manually 

#### COVID-19
| Parameter             | Mathematical symbol | Value          | Description                        |
|-----------------------|---------------------|----------------|------------------------------------|
| R0                    | n/a                 | 2.85           | Basic reproduction number          |
| P_SYMPTOMS            | &mu;                | 0.2            | Pr. of exposed developing symptoms |
| P_REMOVE              | &alpha;             | 0.1            | Pr. of removal                     |

#### INFLUENZA
| Parameter             | Mathematical symbol | Value          | Description                        |
|-----------------------|---------------------|----------------|------------------------------------|
| R0                    | n/a                 | 1.46           | Basic reproduction number          |
| P_SYMPTOMS            | &mu;                | 0.25           | Pr. of exposed developing symptoms |
| P_REMOVE              | &alpha;             | 0.14           | Pr. of removal                     |
