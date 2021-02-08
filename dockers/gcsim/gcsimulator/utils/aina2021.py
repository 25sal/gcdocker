#
# Copyright (c) 2019-2020 by University of Campania "Luigi Vanvitelli".
# Developers and maintainers: Salvatore Venticinque, Dario Branco.
# This file is part of GreenCharge
# (see https://www.greencharge2020.eu/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import utils.visualization as vis
from utils.visualization import EnergyOutput, Performance
import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import time
import scipy.interpolate as inter


def discriminate(values, sign=1):
    """
    Args:
        values:
        sign:
    """
    discriminated = np.zeros(len(values))
    for i  in range(len(values)):
        if values[i] * sign > 0:
            discriminated[i] = values[i]
    return discriminated




if __name__ == "__main__":
    folder = "/home/salvatore/Documents/ricerca/papers/drafts/2021_aina_simulator/data"

    sim_output = EnergyOutput(folder, 150)
    sim_output.cons_series = {'SH'}
    sim_output.prod_series = {}

    sim_output.load(True)
    sim_output.compute_production()
    sim_output.compute_consumption()
    sim_output.compute_self()
    # vis.plot_output(sim_output)
    tot_consumption = np.vstack((sim_output.sample_time, sim_output.tot_consumption)).T
    # tot_production = np.vstack((sim_output.sample_time, sim_output.tot_production)).T
    # self_cons = np.vstack((sim_output.sample_time, sim_output.self_consumption)).T

    np.savetxt("consumption.csv", tot_consumption, delimiter=" ", fmt="%i %f")
    # np.savetxt("production.csv", tot_production, delimiter=" ", fmt="%i %f")
    # np.savetxt("self_consumption.csv", self_cons, delimiter=" ", fmt="%i %f")



    # plot area EVS
    series = glob.glob(folder + "/output/3EVV2g/*.csv")
    ypos = None
    yneg = None
    for serie in series:
        ts = np.genfromtxt(serie, delimiter=" ")
        power = vis.ce2p(ts[:, 0], ts[:, 1], False)
        if ypos is None:
            ypos = discriminate(power, 1)
            yneg = discriminate(power, -1)
            x = ts[:, 0]

        else:
            ypos = np.row_stack((ypos, discriminate(power, 1)))
            yneg = np.row_stack((yneg, discriminate(power, -1)))
        plt.plot(x, power)
    plt.ylabel("power (W)")
    plt.xlabel("hour")

    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mtick.FixedLocator(x))
    loc = mtick.MaxNLocator(12)  # this locator puts ticks at regular intervals
    plt.gca().xaxis.set_major_locator(loc)
    plt.gca().xaxis.set_major_formatter(
        mtick.FuncFormatter(lambda pos, _: time.strftime("%H:%M", time.localtime(pos)))
    )

    plt.tight_layout()

    plt.show()

    sh_consumption = np.genfromtxt(folder + "/output/consumption.csv", delimiter=" ")

    '''
    func1 = inter.interp1d(sh_consumption[:, 0], sh_consumption[:, 1])
    start_time = x[0]
    temp_x = temp_x
    cons_values = func1(x)
    cons_power = vis.ce2p(x, cons_values)
    '''



    tempx = x % 86400
    for i in range(len(tempx)-1, 0, -1):
        if tempx[i] < tempx[i-1]:
            tempx[i-1] = tempx[i-1] -86400

    sh_consumption = np.vstack(([tempx[0], 0], sh_consumption))
    func1 = inter.interp1d(sh_consumption[:, 0], sh_consumption[:, 1])

    cons_power = vis.ce2p(tempx,  func1(tempx))
    cons_power *= 1000
    ypos = np.row_stack((ypos, cons_power))

    production = np.genfromtxt(folder + "/output/production.csv", delimiter=" ")
    prodpower = vis.ce2p(production[:, 0], production[:, 1])
    production[:, 0] += x[0] - tempx[0]

    fig = plt.figure()
    plt.stackplot(x,  ypos, colors=['g', 'y', 'c', 'r'], labels=["EV1", "EV2", "EV3", "shiftable loads"])
    plt.stackplot(x, yneg, colors=['g', 'y', 'c'])
    plt.plot(production[:, 0], prodpower*3000, 'b', label="PV")
    plt.ylabel("power (W)")
    plt.xlabel("hour")
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mtick.FixedLocator(x))
    loc = mtick.MaxNLocator(12)  # this locator puts ticks at regular intervals
    plt.gca().xaxis.set_major_locator(loc)
    plt.gca().xaxis.set_major_formatter(
        mtick.FuncFormatter(lambda pos, _: time.strftime("%H:%M", time.localtime(pos)))
    )

    plt.tight_layout()
    plt.show()
