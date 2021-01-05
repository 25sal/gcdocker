import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import pandas
import scipy.interpolate as inter


class EnergyOutput:
    cons_series = {'HC', 'EV', 'BG', 'SH'}
    prod_series = {'PV'}
    sample_time = None
    self_consumption = None
    tot_consumption = None
    tot_production = None
    productions = None
    consumptions = None
    interval = 600
    folder = None

    def __init__(self, folder, interval=600):
        self.interval = interval
        self.folder = folder + "/output"
        self.min_time = 0
        self.max_time = 0
        pass

    def load(self, rel=False):
        self.productions = self.load_series(self.prod_series, rel)
        self.consumptions = self.load_series(self.cons_series, rel)
        self.sample_time = np.arange(0, (self.max_time-self.min_time), self.interval)

    def compute_production(self):
        temp_series = None
        for group_key in self.productions.keys():
            for ts_key in self.productions[group_key]:
                temp_series = self.__sum_ts(temp_series, self.productions[group_key][ts_key])
        self.tot_production = temp_series
        pass

    def compute_consumption(self):
        temp_series = None
        for group_key in self.consumptions.keys():
            for ts_key in self.consumptions[group_key]:
                temp_series = self.__sum_ts(temp_series, self.consumptions[group_key][ts_key])
        self.tot_consumption = temp_series

    def compute_self(self):
        if self.tot_consumption is not None and self.tot_consumption is not None:
            self.self_consumption = np.zeros(len(self.sample_time))

            for i in range(1, len(self.sample_time)):
                cons = self.tot_consumption[i] - self.tot_consumption[i-1]
                prod = self.tot_production[i] - self.tot_production[i-1]
                self_incr = 0
                if cons >= 0:
                    self_incr = min(prod, cons)
                self.self_consumption[i] = self.self_consumption[i - 1] + self_incr


    def __sum_ts(self, ts_sum, ts_new):
        if ts_sum is None:
            ts_sum = np.zeros(len(self.sample_time))
        start_time = ts_new[0, 0]
        xx = ts_new[:, 0] - start_time
        try:
            ts_spline = inter.InterpolatedUnivariateSpline(xx, ts_new[:, 1])
        except:
            ts_spline = inter.interp1d(xx, ts_new[:, 1])
        for i in range(len(self.sample_time)):
            if ts_new[0, 0] <= self.sample_time[i] <= ts_new[-1, 0]:
                ts_sum[i] += ts_spline(self.sample_time[i]-ts_new[0, 0])
        return ts_sum

    def load_series(self, typ, rel=False):
        ts_groups = {}
        for ser_typ in typ:
            series = glob.glob(self.folder + "/" + ser_typ + "/*.csv")
            ts_groups[ser_typ] = {}
            for ts_file in series:
                ts = np.genfromtxt(ts_file, delimiter=' ')
                if rel:
                    start_time = ts[0, 0] - np.mod(ts[0, 0], 86400)
                    ts[:, 0] = ts[:, 0] - start_time
                if ts[0, 0] < self.min_time or self.min_time == 0:
                    self.min_time = ts[0, 0]
                if ts[-1, 0] > self.max_time:
                    self.max_time = ts[-1, 0]
                ts_groups[ser_typ][os.path.basename(ts_file)[:-4]] = ts
        return ts_groups


def e2p(xx, yy):
    yy1 = np.zeros(len(yy))
    for i in range(1, len(yy)):
        if yy[i] >= yy[i - 1]:
            yy1[i] = 3600 * (yy[i] - yy[i - 1]) / (xx[i] - xx[i - 1])
        else:
            yy1[i] = yy1[i - 1]
    return yy1

def plot_output(sim_output):

    plt.figure()
    plot_power(sim_output.productions, 'b')
    plot_power(sim_output.consumptions)
    plt.legend()
    plt.ylabel("power (kW)")
    plt.xlabel("hour")
    xlim = np.arange(sim_output.min_time, 60 * 60 * 24, 60 * 60 * 3)
    plt.xticks(xlim, [str(n).zfill(2) + ':00' for n in np.arange(int(sim_output.min_time / 3600), 24, 3)])
    plt.savefig("output_power.png")

    plt.figure()
    plt.plot(sim_output.sample_time, e2p(sim_output.sample_time, sim_output.tot_production), 'b', linestyle='-', marker='.', label="tot_production")
    plt.plot(sim_output.sample_time, e2p(sim_output.sample_time,sim_output.tot_consumption), 'r', linestyle='-', marker='.', label="tot_consumption")
    plt.fill(sim_output.sample_time, e2p(sim_output.sample_time,sim_output.self_consumption), 'g', label="self_consumption")

    plt.legend()
    plt.ylabel("power (kW)")
    plt.xlabel("hour")
    xlim = np.arange(sim_output.min_time, 60 * 60 * 24, 60 * 60 * 3)
    plt.xticks(xlim, [str(n).zfill(2) + ':00' for n in np.arange(int(sim_output.min_time / 3600), 24, 3)])
    plt.savefig("output_self.png")


def plot_power(groups, colr=None):
    for group_key in groups.keys():
        for ts_key in groups[group_key].keys():
            ts = groups[group_key][ts_key]
            xx = ts[:, 0]
            yy = ts[:, 1]
            yy1 = np.zeros(len(yy))
            for i in range(1, len(yy)):
                if yy[i] >= yy[i - 1]:
                    yy1[i] = 3600 * (yy[i] - yy[i - 1]) / (xx[i] - xx[i - 1])
                else:
                    yy1[i] = yy1[i-1]
            if colr is not None:
                plt.plot(xx, yy1, colr, linestyle='-', marker='.', label=group_key + "_" + ts_key)
            else:
                plt.plot(xx, yy1, linestyle='-', marker='.', label=group_key + "_" + ts_key)


if __name__ == "__main__":
    folder = "/home/salvatore/projects/gcsimulator/docker/users/demo/Simulations/trivial/Results/12_12_15_82"
    folder = "/home/salvatore/projects/gcsimulator/docker/users/demo/Simulations/demo1"
    sim_output = EnergyOutput(folder)

    sim_output.load(True)
    sim_output.compute_production()
    sim_output.compute_consumption()
    sim_output.compute_self()
    plot_output(sim_output)
