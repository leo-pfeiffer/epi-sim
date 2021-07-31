# Networks
Epidemics depend on the population in which they break out. Generally, a
disease spreads faster in a population where individuals are close together 
and interact very closely, than in populations with
few interactions.

Epidemic simulations using *network* models try to incorporate this by defining
a network (or graph), where the nodes represent individuals of the populations
and edges represent the connections between these individuals

Constructing networks for larger populations usually follows some algorithm to
capture the details of human contacts in the target population. In this app, 
we provide three different types of networks. For each of these networks, there
exists a *baseline* (or *Pre*) network, and a *restricted* (or *Post*) network.
The former represents a population under normal circumstances whereas the 
latter aims to capture the reduced mobility when stay-at-home orders etc. are 
in place.

### Mobility networks
Mobility networks are the most sophisticated networks used in the app and are
built to incorporate real-world mobility patterns. This is done by leveraging
mobility data (collected from mobile data) provided by 
[SafeGraph](https://www.safegraph.com/covid-19-data-consortium) as well
as demographic 
[data from the 2019 US Census](https://www.safegraph.com/open-census-data). 
This data set provides information of how frequently individuals visit points 
of interest, such as parks, restaurants, schools etc. Our specific network is 
based on data from New Haven County, CT, USA, from February 2020 (Pre network) 
and April 2020 (Post network), respectively.

The algorithm roughly works like this:

1. Create many small complete graphs representing households. The size of the 
   households is drawn from a normal distribution centered around the average
   household size of the CBG the household is in. Then combine the household
   graphs into one large graph.
   
2. Assign a degree to each node drawn from a power-law with cutoff distribution. 
   Create as many copies of each node as its degree without any edges yet.
   These new unconnected nodes are called stubs.
   
3. Connect the stubs with each other. Since each stub belongs to a CBG, we bias 
   the connections to have the same distributions between CBGs as observed in 
   the frequency of connections in the mobility data.
   
In the Post network, the number of connections between CBGs is reduced based on
the empirical reduction in mobility between these CBGs from Feb 2020 to Apr 
2020.

For more details on the algorithm, have a read through my [thesis]().

### PLC networks
Power-law with cutoff (PLC) networks try to account for the fact that in most
populations, few individuals is highly connected why the 
vast majority of individuals have only few connections. This corresponds to a
power-law distribution of node degrees. However, power-law distribution based
graphs tend to produce some nodes with unrealistically many connections on one 
end. To cope with this, the PLC distribution introduces a cutoff value, beyond
which node degrees are exceedingly unlikely, making the node degree distribution
more realistic. This concept was introduced by 
[Newman et al. (2002)](https://doi.org/10.1073/pnas.012582999).

We build the Pre network such that the expected average node degree corresponds
to that of the Pre mobility network. For the Post network the exponent of the
power-law with cutoff distribution is reduced such that the expected node degree 
corresponds to that of the Post mobility network.

Compared to the mobility network, this approach might be less based on empirical
data. However, since such data is not always available, PLC networks provide
a powerful alternative for creating real-world networks.

### Distanced networks

The distanced networks attempt to capture a population in which each node
is part of a small bubble (or household) and only some members of the household
have connections outside of the household. This would, for example, describe
a population when social distancing measures are in place and observed.
The algorithm was given in
[Dobson (2020, pp.156)](http://simondobson.org/introduction-to-epidemics/distancing.html).

Once again, we set the parameters of the distanced network (Pre) to achieve
an expected node degree similar to that of the mobility network (Post), and 
likewise for the Post network.

