import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import pandas
import scipy.interpolate as inter
from scipy.integrate import simps


class Intersection:
    """
    This class compute the intersection between two curve using different methods.
    """
    @classmethod
    def solve(cls, f, x):
        s = np.sign(f)
        z = np.where(s == 0)[0]
        if len(z) > 0:
            return z
        else:
            s = s[0:-1] + s[1:]
            z = np.where(s == 0)[0]
            return z

    @classmethod
    def interp(cls, f, x, z):
        m = (f[z + 1] - f[z]) / (x[z + 1] - x[z])
        return x[z] - f[z] / m

    @classmethod
    def intersect1(cls, x, y1,y2):
        f = y1 - y2
        z = cls.solve(f, x)
        ans = cls.interp(f, x, z)
        return ans

    @staticmethod
    def intersect2(f1, f2, xx):
        def diff_func(x):
            return f1(x) - f2(x)

        roots = np.argwhere(np.diff(np.sign(diff_func(xx)))).flatten()
        return roots


class EnergyOutput:
    cons_series = {'HC', 'SH', 'EV'}
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
        if len(self.productions.keys()) > 0:
            for group_key in self.productions.keys():
                for ts_key in self.productions[group_key]:
                    temp_series = self.__sum_cts(temp_series, self.productions[group_key][ts_key])
            self.tot_production = temp_series
        else:
            self.tot_production = np.zeros(len(self.sample_time))

    def compute_consumption(self):
        temp_series = None
        if len(self.consumptions.keys()) > 0:
            for group_key in self.consumptions.keys():
                for ts_key in self.consumptions[group_key]:
                    temp_series = self.__sum_cts(temp_series, self.consumptions[group_key][ts_key])
            self.tot_consumption = temp_series
        else:
            self.tot_consumption = np.zeros(len(self.sample_time))

    def compute_self(self):
        self.self_consumption = np.zeros(len(self.sample_time))
        if self.tot_production is not None and self.tot_production[-1] > 0:
            for i in range(1, len(self.sample_time)):
                cons = self.tot_consumption[i] - self.tot_consumption[i-1]
                prod = self.tot_production[i] - self.tot_production[i-1]
                self_incr = 0
                if cons >= 0 and prod > 0:
                    self_incr = min(prod, cons)
                self.self_consumption[i] = self.self_consumption[i - 1] + self_incr


    def res_power(self):
        pow_cons = ce2p(sim_output.sample_time, sim_output.tot_consumption)
        pow_prod = ce2p(sim_output.sample_time, sim_output.tot_production)
        res_pow = pow_cons - pow_prod
        for i in range(len(res_pow)):
            if res_pow[i] < 0:
                res_pow[i] = 0
        return res_pow

    def __sum_cts(self, ts_sum, ts_new):
        return self.__sum_sub_cts(ts_sum, ts_new)

    def __sub_cts(self, ts_sum, ts_new):
        return self.__sum_sub_cts(ts_sum, ts_new, -1)

    def __sum_sub_cts(self, ts_sum, ts_new, mult=1):
        if ts_sum is None:
            ts_sum = np.zeros(len(self.sample_time))
        start_time = ts_new[0, 0]
        xx = ts_new[:, 0] - start_time
        try:
            # ts_spline = inter.InterpolatedUnivariateSpline(xx, ts_new[:, 1])
            ts_spline = inter.interp1d(xx, ts_new[:, 1])
        except:
            ts_spline = inter.interp1d(xx, ts_new[:, 1])
        last_incr = 0
        for i in range(len(self.sample_time)):
            if ts_new[0, 0] <= self.sample_time[i] <= ts_new[-1, 0]:
                incr = ts_spline(self.sample_time[i]-ts_new[0, 0]) * mult
                if incr > 0:
                    last_incr = incr
                    ts_sum[i] += ts_spline(self.sample_time[i]-ts_new[0, 0])
            elif self.sample_time[i] > ts_new[-1, 0]:
                ts_sum[i] += last_incr
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


def ce2p(xx, yy):
    yy1 = np.zeros(len(yy))
    for i in range(1, len(yy)):
        if yy[i] >= yy[i - 1]:
            yy1[i] = 3600 * (yy[i] - yy[i - 1]) / (xx[i] - xx[i - 1])
        else:
            yy1[i] = yy1[i - 1]
    return yy1

def ce2e(yy):
    yy1 = np.zeros(len(yy))
    for i in range(0, len(yy)-1):
        yy1[i] = yy[i+1] - yy[i]
    return yy1

def p2ce(xx, yy):
    yy1 = np.zeros(len(yy))
    for i in range(1, len(yy)):
            yy1[i] = yy1[i-1] + yy[i] * (xx[i] - xx[i - 1])/3600
    return yy1


def plot_output(sim_output):

    plt.figure()
    plot_power(sim_output.productions, 'b')
    plot_power(sim_output.consumptions)
    plt.legend()
    plt.ylabel("power (W)")
    plt.xlabel("hour")
    xlim = np.arange(sim_output.min_time, 60 * 60 * 24, 60 * 60 * 3)
    plt.xticks(xlim, [str(n).zfill(2) + ':00' for n in np.arange(int(sim_output.min_time / 3600), 24, 3)])
    plt.savefig("output_power.png")

    plt.figure()
    if sim_output.tot_production[-1] > 0:
        plt.plot(sim_output.sample_time, ce2p(sim_output.sample_time, sim_output.tot_production), 'b', linestyle='-', marker='.', label="tot_production")
    if sim_output.tot_consumption[-1] > 0:
        plt.plot(sim_output.sample_time, ce2p(sim_output.sample_time, sim_output.tot_consumption), 'r', linestyle='-', marker='.', label="tot_consumption")
    if sim_output.self_consumption[-1] > 0:
        plt.fill(sim_output.sample_time, ce2p(sim_output.sample_time, sim_output.self_consumption), 'g', label="self_consumption")



    plt.legend()
    plt.ylabel("power (W)")
    plt.xlabel("hour")
    xlim = np.arange(sim_output.min_time, 60 * 60 * 24, 60 * 60 * 3)
    plt.xticks(xlim, [str(n).zfill(2) + ':00' for n in np.arange(int(sim_output.min_time / 3600), 24, 3)])
    plt.savefig("output_self.png")

    plt.figure()
    plt.plot(sim_output.sample_time, sim_output.res_power(), 'r', label="res_power")
    plt.legend()
    plt.ylabel("power (W)")
    plt.xlabel("hour")
    xlim = np.arange(sim_output.min_time, 60 * 60 * 24, 60 * 60 * 3)
    plt.xticks(xlim, [str(n).zfill(2) + ':00' for n in np.arange(int(sim_output.min_time / 3600), 24, 3)])
    plt.savefig("res_pow.png")



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
            print(group_key + "_" + ts_key, np.max(yy1))
            if colr is not None:
                plt.plot(xx, yy1, colr, linestyle='-', marker='.', label=group_key + "_" + ts_key)
            else:
                plt.plot(xx, yy1, linestyle='-', marker='.', label=group_key + "_" + ts_key)

class Performance:


    @staticmethod
    def self_consumption(self_consumption, production):
        if production[-1] > 0:
            return self_consumption[-1]/production[-1]
        else:
            return 0

    @staticmethod
    def average(groups):
        energy = 0
        min_time = None
        max_time = None
        for group_key in groups.keys():
            for ts_key in groups[group_key].keys():
                serie = groups[group_key][ts_key]
                energy += serie[-1, 1]
                if min_time is None or min_time > serie[0, 0]:
                    min_time = serie[0, 0]
                if max_time is None or max_time < serie[-1, 0]:
                    max_time = serie[-1, 0]

        average = 3600 * energy/(max_time-min_time)
        return average

    @staticmethod
    def peak2average(consumption):
        avg_pow = 3600 * consumption[-1, 1]/(consumption[-1, 0] - consumption[0, 0])
        pow_serie = ce2p(consumption[:, 0], consumption[:, 1])
        return np.max(pow_serie)/avg_pow


def shift_load(shift_time, infile, outfile):
    """
    This code shift a timeseries
    :param shift_time:
    :param infile:
    :param outfile:
    :return:
    """
    series = np.genfromtxt(infile, delimiter=' ')
    start_time = series[0, 0]
    series[:, 0] = series[:, 0] - start_time + shift_time
    np.savetxt(outfile, series, delimiter=' ', fmt="%d %f")


def compute_area(ffunc, xx, a, b):
    """"
    This code compute the area below the curve ffunc, between a and b
    """
    return simps(ffunc(xx[a:b]), xx[a:b])/3600


def ev2maxself(ev_ce, xx, res_energy, filename):
    """
    This function change the energy profile of an ev to optimize the usage of residual green energy
    :param ev_ce:
    :param xx:
    :param res_energy:
    :param filename:
    :return:
    """
    ev_energy = ev_ce[-1, 1]
    ev_max_en = (ev_ce[-1, 1] / (ev_ce[-1, 0] - ev_ce[0, 0])) * 600
    print("ev_demand", ev_energy)
    for i in range(len(res_energy)):
        if res_energy[i] < 0:
            res_energy[i] = 0

    charged_energy = [0]
    charged_times = []
    for i in range(len(xx)):
        if xx[i] >= 10 * 3600:
            if res_energy[i] < ev_max_en:
                usable_energy = res_energy[i]
            else:
                usable_energy = ev_max_en
            ev_energy -= usable_energy

            charged_energy.append(charged_energy[-1] + usable_energy)
            charged_times.append(xx[i])
            if ev_energy <= 0:
                print('charged at:', xx[i] / 3600, ":", xx[i] % 3600)
                break
    print("ev_residual", ev_energy)

    charged_ts = np.vstack((charged_times, charged_energy[:-1])).T
    # print(charged_ts)
    np.savetxt(filename, charged_ts, delimiter=' ', fmt="%d %f")




if __name__ == "__main__":
    folder = "/home/salvatore/projects/gcsimulator/docker/users/demo/Simulations/trivial/Results/12_12_15_82"
    folder = "/home/salvatore/projects/gcsimulator/docker/users/demo/Simulations/demo2"
    # folder = "/home/salvatore/projects/gcsimulator/docker/users/demo/Simulations/demo3"

    # shift_load(10 * 3600, folder + "/input/EV/4_run_3_1_ecar.csv",  folder + "/output/EV/4_run_3_1_ecar.csv")
    # shift_load(15 * 3600, folder + "/input/SH/10_run_1_1_dw.csv", folder + "/output/SH/10_run_1_1_dw.csv")
    # shift_load(10 * 3600, folder + "/input/SH/10_run_2_1_wm.csv", folder + "/output/SH/10_run_2_1_wm.csv")
    # shift_load(9.5 * 3600, folder + "/input/EV/10_54_.csv", folder + "/output/EV/10_54_.csv")

    sim_output = EnergyOutput(folder,150)

    sim_output.load(True)
    sim_output.compute_production()
    sim_output.compute_consumption()
    sim_output.compute_self()
    tot_consumption = np.vstack((sim_output.sample_time, sim_output.tot_consumption)).T
    print('tot_cons PAR:', Performance.peak2average(tot_consumption))
    print('cons PEAK:', np.max(ce2p(sim_output.sample_time, sim_output.tot_consumption)))
    res_energy = np.vstack((sim_output.sample_time, p2ce(sim_output.sample_time, sim_output.res_power()))).T
    print('res_energy PAR:', Performance.peak2average(res_energy))
    print('res_energy PEAK:',np.max(sim_output.res_power()))
    print('self consumption:', Performance.self_consumption(sim_output.self_consumption, sim_output.tot_production))
    plot_output(sim_output)

    '''
    Find the when the total consumed power intersect the maximum power (6000W)
    '''
    threshold = np.zeros(len(sim_output.sample_time)) + 6000
    tot_power = ce2p(sim_output.sample_time, sim_output.tot_consumption)
    print("Intersect", Intersection.intersect1(sim_output.sample_time, threshold, tot_power))

    func1 = inter.interp1d(sim_output.sample_time,tot_power)

    def func2(x):
        return threshold
    result = Intersection.intersect2(func1, func2, sim_output.sample_time)
    print("Intersect", result)
    print(sim_output.sample_time[result])
    exit(0)

    """
    This code is used to exploit charge flexibility in order to keep the total power below a threshold
    But it is not general and must be changed. 
    """
    folder = "/home/salvatore/projects/gcsimulator/docker/users/demo/Simulations/demo2"
    sim_output = EnergyOutput(folder, 150)
    sim_output.cons_series = {'HC', 'SH'}
    sim_output.prod_series = {'EV'}


    sim_output.load(True)
    sim_output.compute_production()
    sim_output.compute_consumption()
    sim_output.compute_self()

    total_power = ce2p(sim_output.sample_time, sim_output.tot_consumption)
    total_available = np.zeros((len(total_power))) +6000
    total_available -= total_power
    total_evpower = ce2p(sim_output.sample_time, sim_output.tot_production)

    ev3 = np.zeros((len(total_power)))
    ev1= np.zeros((len(total_power)))
    ev2 = np.zeros((len(total_power)))
    ev3_energy=9816
    ev2_energy=8970
    ev1_energy=8231

    for i in range(1, len(sim_output.sample_time)):
        av_pow = total_available[i] - total_power[i]
        if sim_output.sample_time[i] > 25200 and ev3_energy>0 and av_pow>0:
            ev3[i]=min(av_pow, 1621)
            av_pow-=ev3[i]
            ev3_energy-= 0.5*(ev3[i]+ev3[i-1])*(sim_output.sample_time[i]-sim_output.sample_time[i-1])/3600
            if ev3_energy<0:
                print('ev3 finish at', sim_output.sample_time[i] )
        if sim_output.sample_time[i] > 34200 and ev2_energy>0 and av_pow>0:
            ev2[i]=min(av_pow, 1546)
            av_pow-=ev2[i]
            ev2_energy-=0.5 * (ev2[i] + ev2[i - 1]) * (sim_output.sample_time[i] - sim_output.sample_time[i - 1]) / 3600
            if ev2_energy < 0:
                print('ev2 finish at', sim_output.sample_time[i])

        if sim_output.sample_time[i] > 36200 and ev1_energy>0 and av_pow>0:
            ev1[i]=min(av_pow, 3228)
            av_pow-=ev1[i]
            ev1_energy-=0.5 * (ev1[i] + ev1[i - 1]) * (sim_output.sample_time[i] - sim_output.sample_time[i - 1]) / 3600
            if ev1_energy < 0:
                print('ev1 finish at', sim_output.sample_time[i])


    plt.figure()
    plt.plot(sim_output.sample_time,total_power,'k', label='other loads')
    plt.plot(sim_output.sample_time,ev1,'r', label='EV_1')

    plt.plot(sim_output.sample_time, ev2,'c', label='EV_2')
    plt.plot(sim_output.sample_time, ev3,'b', label='EV_3')
    xlim = np.arange(sim_output.min_time, 60 * 60 * 24, 60 * 60 * 3)
    plt.ylabel("power (W)")
    plt.xlabel("hour")
    plt.xticks(xlim, [str(n).zfill(2) + ':00' for n in np.arange(int(sim_output.min_time / 3600), 24, 3)])

    plt.legend()
    plt.show()
    np.savetxt("1.csv", np.vstack((sim_output.sample_time, p2ce(sim_output.sample_time,ev1))).T, delimiter=' ', fmt="%d %f")
    np.savetxt("2.csv", np.vstack((sim_output.sample_time, p2ce(sim_output.sample_time,ev2))).T, delimiter=' ', fmt="%d %f")
    np.savetxt("3.csv", np.vstack((sim_output.sample_time, p2ce(sim_output.sample_time,ev3))).T, delimiter=' ', fmt="%d %f")






