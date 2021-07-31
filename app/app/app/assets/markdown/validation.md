# Validation

To evaluate the simulation results produced by the models we can compare
them to empirical data of the COVID-19 pandemic. 
All validation is performed on the mobility networks for a few specific 
parameter settings. You can select your desired validation on the left.

## SEIR & SEIR_Q
Validation for these models is performed by comparing the simulation results
to the first 120 days of the COVID-19 pandemic in the 50 states of the US. The
start of the pandemic is defined as the day at which the total cases first
exceeded 0.1% of the population of the state.

The graphs available for these models include the cumulative case count over 
time as well as the new daily case counts.

## SEIVR & SEIVR_Q
Validation for the models that incorporate vaccination is more difficult as it
requires a lot of state specific parameterisation. Since vaccinations were not
available until the end of 2020, validation is only possible after this date.

Hence, the validation for SEIVR and SEIVR_Q is only performed on data from
the state of Connecticut, for the first 120 days of 2021. At that point,
a large fraction of the population had already been infected (and recovered). 
We therefore start the simulation with the occupancy of these model 
compartments set to reflect the approximate value found in the empirical data.
The vaccination parameters are set to approximate the situation in Connecticut.

Only the cumulative total case counts are available for the validation of these
models.
