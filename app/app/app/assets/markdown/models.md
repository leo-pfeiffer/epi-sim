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

![SEIR flow diagram ><](/assets/img/SEIR-adapted.png)

### SEIVR
![SEIVR flow diagram ><](/assets/img/SEIVR.png)