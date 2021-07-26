# Welcome to EpiSim...
... the web application that makes epidemic simulations accessible.

To get the most out of the app, have a look at the following to see how to use it.

---

## Control bar
![Help control >](/assets/img/help-control.png)
The control bar on the left side of the page is where you can select the type 
of model and network you want to simulate, and set the appropriate parameters.

Most importantly, you can select one of the provided models from the `Model` 
dropdown list. To find out more about the different models, have a look at the 
[models page](/models).

You can also select a different human contact network from the `Network` dropdown.
These models don't give you access to more parameters but they make different
assumptions about how individuals in the epidemic simulation interact with each other.
Again, you can find out more details on the [models page](/models).

Depending on which model you selected, you can further set up to four parameters.

1. `p_quarantine` (available for SEIR_Q, SEIVR_Q): This parameter is available 
   for models that implement a quarantine and describes the probability with which 
   the connection between a susceptible individual and an infected individual is 
   removed when the infected individual becomes symptomatic.

2. `p_vaccinated` (SEIVR, SEIVR_Q): For models that implement vaccination, this 
   parameter sets the probability with which a susceptible, unvaccinated individual
   receives their vaccination in any given time step. This translates in how long
   it takes (on average) for individuals to be vaccinated. For example if
   `p_vaccinated = 0.01`, then it takes on average `1/0.01=100` days from the
   start of the epidemic until individuals are vaccinated.
   
3. `p_vaccinated_initial` (SEIVR, SEIVR_Q): This parameter lets you set 
   the fraction of vaccinated individuals at the start of the epidemic. 
   
4. `rrr` (SEIVR, SEIVR_Q): This is the so-called relative risk reduction of 
   the vaccine, commonly referred to as the efficacy. It determines by how much
   the rate of infection is reduced for vaccinated individuals compared to 
   unvaccinated individuals. For example, if the infection probability for
   unvaccinated individuals is `P_INFECT=0.2` and `RRR=0.5`, then the infection
   probability for vaccinated individuals is reduced to 
   `P_INFECT * (1 - RRR) = 0.2 * (1 - 0.5) = 0.1`.
   
You can also download the simulation results as a CSV file by clicking the 
button at the bottom of the control bar.
   
## Epidemic curves
![Help curves >](/assets/img/help-curves.png)
The main graph next to the control bar is the main graph of the application.
It depicts the fraction of individuals per compartment over the course of the 
epidemic. 

For each time step, there are several data points shown, one for each
of the simulation runs. This gives you a sense of how reliable the results are.
The line through the middle of the points is the average of all runs.

Hovering over data points in the graph lets you explore the exact values.
In some cases it might be beneficial to zoom into the graph, which
is possible by clicking and dragging over parts of the graph. You can also exclude
compartments from the graph by clicking on the respective label in the legend.


## Data table
![Help table >](/assets/img/help-table.png)
Below the epidemic curves graph, you can find a data table containing some
numeric results of the simulation.

- `total infected` is the total fraction of the population that was 
  infected with the disease over the course of the epidemic.
  
- `susceptible remaining` is the fraction of individuals that are still in the
  susceptible compartment  (and the vaccinated compartment, if applicable) 
  at the end of the epidemic.
  
- `peak time` is the time step in which the fraction of infected individuals 
  hits its maximum
  
- `peak infected` is the fraction of infected individuals at the `peak time`

- `effective end` is the time step in which the number of infected individuals 
  falls below `1%` after an initial surge over that threshold
  
> ℹ️ `total infected` + `susceptible remaining` should some up to `1`. However, 
there might be a very small discrepancy that results from how the networks 
are created. Don't worry, the deviance should be very small and the values 
are still proportionate to the correct value.


## Scatter plot
![Help scatter >](/assets/img/help-scatter.png)
In the top right quadrant of the dashboard you can find a scatter plot that
depicts how the epidemic size changes when a parameter changes.
To compare another parameter, click on the respective tab above the figure.
Of course, the scatter plots are only available if the currently selected model 
includes the parameter of the scatter plot. The results displayed in this graph 
always fix all parameters except the one to compare to whatever values are 
currently set in the control bar. Only the parameter to be compared is varied to 
show the results for all possible settings.
As with the scatters in the epidemic curve graph, each dot per parameter setting
represents one of many simulation runs and the spread of the dots can serve
as a measure for uncertainty.


## Heatmap
![Help heatmap >](/assets/img/help-heatmap.png)
The heatmap in the bottom right quadrant of the dashboard is fairly similar to
the scatter plot in that it also allows you to compare the epidemic size of the 
models for different parameter settings. However, it allows you to compare the
results between all the models that encapsulate this parameter. For example, 
if you select the `p_vaccinated_initial` parameter for comparisong you can
compare it's effect on the epidemic size for all models that include 
vaccination. As with the scatter plot, all currently selected parameter settings
are fixed and only the parameter to compare is varied.
