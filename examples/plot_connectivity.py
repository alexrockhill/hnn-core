"""
=====================
07. Plot Connectivity
=====================

This example demonstrates how to modify the network connectivity.
"""

# Author: Nick Tolley <nicholas_tolley@brown.edu>

import os.path as op

###############################################################################
# Let us import ``hnn_core``.

import hnn_core
from hnn_core import read_params, Network, simulate_dipole

hnn_core_root = op.dirname(hnn_core.__file__)

###############################################################################
# Then we read the parameters file
params_fname = op.join(hnn_core_root, 'param', 'default.json')
params = read_params(params_fname)

###############################################################################
# To explore how to modify network connectivity, we will start with simulating
# the evoked response from the
# :ref:`evoked example <sphx_glr_auto_examples_plot_simulate_evoked.py>`, and
# explore how it changes with new connections. We first instantiate the
# network. (Note: Setting ``add_drives_from_params=True`` loads a set of
# predefined drives without the drives API shown previously).
net = Network(params, add_drives_from_params=True)

###############################################################################
# Instantiating the network comes with a predefined set of connections that
# reflect the canonical neocortical microcircuit. ``net.connectivity``
# is a list of dictionaries which detail every cell-cell, and drive-cell
# connection.
print(len(net.connectivity))
print(net.connectivity[0])
print(net.connectivity[-1])

###############################################################################
# Data recorded during simulations are stored under
# :class:`~hnn_core.Cell_Response`. To test multiple network structures, we can
# create a copy of the original network. The copied network is then simulated.
net_erp = net.copy()
dpl_erp = simulate_dipole(net_erp, n_trials=1)
net_erp.cell_response.plot_spikes_raster()

###############################################################################
# We can modify the connectivity list to test the effect of different
# connectivity patterns. For example, we can remove all layer 2 inhibitory
# connections.
new_connectivity = [conn for conn in net.connectivity
                    if conn['src_type'] != 'L2_basket']
net.connectivity = new_connectivity

net_remove = net.copy()
dpl_remove = simulate_dipole(net_remove, n_trials=1)
net_remove.cell_response.plot_spikes_raster()

###############################################################################
# That's a lot of spiking! Since basket cells are inhibitory, removing these
# connections increases network wide excitability. We can additionally add
# new connections using ``net.add_connection()``. Let's try connecting a
# single layer 2 basket cell, to every layer 2 pyramidal cell. We can utilize
# ``net.gid_ranges`` to help
# find the gids of interest.
print(net.gid_ranges)
src_gid = net.gid_ranges['L2_basket'][0]
target_gids = net.gid_ranges['L2_pyramidal']
location, receptor = 'soma', 'gabaa'
weight, delay, lamtha = 1.0, 1.0, 70
net.add_connection(src_gid, target_gids, location, receptor,
                   delay, weight, lamtha)

net_add = net.copy()
dpl_add = simulate_dipole(net_add, n_trials=1)
net_add.cell_response.plot_spikes_raster()

###############################################################################
# Adding more inhibitory connections did not completely restore the normal
# spiking. L2 basket and pyramidal cells rhythymically fire in the gamma
# range (30-80 Hz). As a final step, we can see how this change in spiking
# activity impacts the aggregate current dipole.
import matplotlib.pyplot as plt
from hnn_core.viz import plot_dipole
fig, axes = plt.subplots(2, 1, sharex=True, figsize=(6, 6),
                         constrained_layout=True)
dpls = [dpl_erp[0], dpl_remove[0], dpl_add[0]]
plot_dipole(dpls, ax=axes[0], layer='agg', show=False)
axes[0].legend(['Normal', 'No L2 Basket', 'Single L2 Basket'])
net_erp.cell_response.plot_spikes_hist(
    ax=axes[1], spike_types=['evprox', 'evdist'])
