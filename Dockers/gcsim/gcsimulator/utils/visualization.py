import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import pandas
import scipy.interpolate as inter
from scipy.integrate import simps


class Intersection:
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
    def intersect(cls, x, y1,y2):
        f = y1 - y2
        z = cls.solve(f, x)
        ans = cls.interp(f, x, z)
        return ans


class EnergyOutput:
    cons_series = {'HC', 'SH'}
    prod_series = {'EV'}
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
        pow_cons = e2p(sim_output.sample_time, sim_output.tot_consumption)
        pow_prod = e2p(sim_output.sample_time, sim_output.tot_production)
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


def e2p(xx, yy):
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
        plt.plot(sim_output.sample_time, e2p(sim_output.sample_time, sim_output.tot_production), 'b', linestyle='-', marker='.', label="tot_production")
    if sim_output.tot_consumption[-1] > 0:
        plt.plot(sim_output.sample_time, e2p(sim_output.sample_time, sim_output.tot_consumption), 'r', linestyle='-', marker='.', label="tot_consumption")
    if sim_output.self_consumption[-1] > 0:
        plt.fill(sim_output.sample_time, e2p(sim_output.sample_time, sim_output.self_consumption), 'g', label="self_consumption")

    """
    Temporary code
    """
    threshold = np.zeros(len(sim_output.sample_time))
    threshold[:] = threshold[:] + 6000
    plt.plot(sim_output.sample_time, threshold, 'k', label='threshold')


    print("intersect", Intersection.intersect(sim_output.sample_time, threshold, sim_output.tot_consumption))

    interplated_cons = inter.interp1d(sim_output.sample_time, e2p(sim_output.sample_time, sim_output.tot_consumption))
    print(sim_output.tot_consumption[-1])
    def ffunc(x):
        return interplated_cons(x) - 6000

    idx = np.argwhere(np.diff(np.sign(ffunc(sim_output.sample_time)))).flatten()
    print(idx)
    print(sim_output.sample_time[idx])
    area1 = simps(ffunc(sim_output.sample_time[idx[0]:idx[-1]]),sim_output.sample_time[idx[0]:idx[-1]])/3600

    # plt.plot(sim_output.sample_time[idx],  threshold[idx], 'x')
    print(area1)
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
        pow_serie = e2p(consumption[:, 0], consumption[:, 1])
        return np.max(pow_serie)/avg_pow


def shift_load(shift_time, infile, outfile):
    series = np.genfromtxt(infile, delimiter=' ')
    start_time = series[0, 0]
    series[:, 0] = series[:, 0] - start_time + shift_time
    np.savetxt(outfile, series, delimiter=' ', fmt="%d %f")



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
    print('cons PEAK:', np.max(e2p(sim_output.sample_time, sim_output.tot_consumption)))
    res_energy = np.vstack((sim_output.sample_time, p2ce(sim_output.sample_time, sim_output.res_power()))).T
    print('res_energy PAR:', Performance.peak2average(res_energy))
    print('res_energy PEAK:',np.max(sim_output.res_power()))
    print('self consumption:', Performance.self_consumption(sim_output.self_consumption, sim_output.tot_production))
    #plot_output(sim_output)
    '''
    exit(0)
    ev_ce = np.genfromtxt(folder + "/output/EV/4_run_3_1_ecar.csv", delimiter=' ')
    ev_energy = ev_ce[-1, 1]
    ev_max_en = (ev_ce[-1, 1]/(ev_ce[-1, 0]-ev_ce[0, 0]))*600
    print("ev_demand", ev_energy)
    res_energy = ce2e(sim_output.tot_production) - ce2e(sim_output.tot_consumption)
    for i in range(len(res_energy)):
        if res_energy[i] < 0:
            res_energy[i] = 0

    charged_energy = [0]
    charged_times = []
    for i in range(len(sim_output.sample_time)):
        if sim_output.sample_time[i] >= 10*3600:
            if res_energy[i] < ev_max_en:
                usable_energy = res_energy[i]
            else:
                usable_energy = ev_max_en
            ev_energy -= usable_energy

            charged_energy.append(charged_energy[-1]+usable_energy)
            charged_times.append(sim_output.sample_time[i])
            if ev_energy <= 0:
                print('charged at:', sim_output.sample_time[i]/3600, ":", sim_output.sample_time[i]%60)
                break
    print("ev_residual", ev_energy)

    charged_ts = np.vstack((charged_times, charged_energy[:-1])).T
    # print(charged_ts)
    np.savetxt(folder + "/output/EV/4_run_3_1_ecar.csv", charged_ts, delimiter=' ', fmt="%d %f")
    '''
    total_power = e2p(sim_output.sample_time,sim_output.tot_consumption)
    total_available = np.zeros((len(total_power))) +6000
    total_available -= total_power
    total_evpower = e2p(sim_output.sample_time, sim_output.tot_production)

    ev3 = np.zeros((len(total_power)))
    ev1= np.zeros((len(total_power)))
    ev2 = np.zeros((len(total_power)))
    ev3_energy=9816
    ev2_energy=8970
    ev1_energy=8231
    for i in range(1, len(sim_output.sample_time)):
        av_pow = total_available[i] - sim_output.tot_production[i]
        if sim_output.sample_time[i] > 25200 and ev3_energy>0 and av_pow>0:
            ev3[i]=min(av_pow, 1621)
            av_pow-=ev3[i]
            ev3_energy-= 0.5*(ev3[i]+ev3[i-1])*(sim_output.sample_time[i]-sim_output.sample_time[i-1])/3600
        if sim_output.sample_time[i] > 34200 and ev2_energy>0 and av_pow>0:
            ev2[i]=min(av_pow, 1546)
            av_pow-=ev2[i]
            ev2_energy-=0.5 * (ev2[i] + ev2[i - 1]) * (sim_output.sample_time[i] - sim_output.sample_time[i - 1]) / 3600
        if sim_output.sample_time[i] > 36200 and ev1_energy>0 and av_pow>0:
            ev1[i]=min(av_pow, 3228)
            av_pow-=ev1[i]
            ev1_energy-=0.5 * (ev1[i] + ev1[i - 1]) * (sim_output.sample_time[i] - sim_output.sample_time[i - 1]) / 3600

    print(ev1)
    print(ev2)
    print(ev3)
    plt.figure()
    plt.plot(sim_output.sample_time,ev1,'r')
    plt.plot(sim_output.sample_time, ev2,'c')
    plt.plot(sim_output.sample_time, ev3,'b')
    plt.show()





