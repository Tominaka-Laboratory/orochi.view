"""Matplotlib-based viewer for PDF data reduction and analysis."""


import re
from collections import OrderedDict

import matplotlib

# import numpy as np
from numpy import (
    abs,
    amax,
    amin,
    append,
    arange,
    argmin,
    array,
    float,
    meshgrid,
    nan,
    ones,
    ones_like,
    pi,
    savetxt,
    sqrt,
    square,
    sum,
    vstack,
    where,
    zeros,
)

matplotlib.interactive(True)
# from matplotlib import path as mpltPath
from matplotlib import pyplot as plt
from matplotlib import widgets as mw

# matplotlib.use('WXAgg')
# matplotlib.use('QT5Agg')
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backend_bases import key_press_handler

# from matplotlib.ticker import FormatStrFormatter, MultipleLocator
from matplotlib.widgets import Slider
from mpl_toolkits.axes_grid1 import axes_size, make_axes_locatable


# mpd
class PDFs(object):
    def __init__(self, calculator, slider_keys, figure_keys):
        plt.rcParams["font.size"] = 10
        plt.rcParams["axes.linewidth"] = 1.0
        plt.rcParams["font.family"] = "Arial"

        self.calculator = calculator
        self.slider_keys = slider_keys
        self.figure_keys = figure_keys
        self.labelfont = 10

        self.figures()
        self.slider()

    def show(self):
        plt.show(block=True)

    def figures(self):
        self.fig1 = plt.figure(num=1, figsize=(9, 7), dpi=100)

        figure_number = len(self.figure_keys)
        row = -1 * (-figure_number // 2)
        grid = (row, 2)
        span = int(row * 2 - figure_number)

        n = 0
        m = 0
        for x, key in enumerate(self.figure_keys):
            if key == "raw":
                self.plot_raw(grid, (n, m), 1 + span)
            elif key == "bg":
                self.plot_ib(grid, (n, m), 1 + span)
            elif key == "iq":
                self.plot_iq(grid, (n, m), 1 + span)
            elif key == "ip":
                self.plot_ip(grid, (n, m), 1 + span)
            elif key == "ic":
                self.plot_ic(grid, (n, m), 1 + span)
            elif key == "i":
                self.plot_i(grid, (n, m), 1 + span)
            elif key == "sq":
                self.plot_sq(grid, (n, m), 1 + span)
            elif key == "fq":
                self.plot_fq(grid, (n, m), 1 + span)
            elif key == "Gr":
                self.plot_gr(grid, (n, m), 1 + span)
            elif key == "tr":
                self.plot_tr(grid, (n, m), 1 + span)

            if (x == 0) & (span == 1):
                m = 0
                n += 1
                span = 0
            else:
                m = abs(m - 1)
                if m == 0:
                    n += 1

        self.fig1.tight_layout()

    def plot_raw(self, grid, position, span):
        self.ax_raw = plt.subplot2grid(grid, position, colspan=span)
        self.ax_raw.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_raw.autoscale(enable=True, axis="both")
        self.ax_raw.set_xlim(left=0, right=self.calculator.ttraw[-1] * 1.01)
        plt.xlabel("$two theta$ / $\mathrm{\degree}$", fontsize=self.labelfont)
        plt.ylabel("$I$ / a.u.", fontsize=self.labelfont)

        self.p_raw = []
        for n in range(self.calculator.sdata.detectors):
            x = self.calculator.sdata.tc[n]
            y = self.calculator.sdata.ic[n]
            self.p_raw += plt.plot(x, y, ls="-", label=str(n), lw=0.8)

        self.ax_raw.relim()
        self.ax_raw.autoscale_view()
        plt.legend(loc=1, prop={"size": 8}, ncol=1, frameon=False, numpoints=3)

    def plot_iq(self, grid, position, span):
        self.ax_iq = plt.subplot2grid(grid, position, colspan=span)
        self.ax_iq.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_iq.autoscale(enable=True, axis="y")
        self.ax_iq.set_xlim(left=0, right=self.calculator.qraw[-1] * 1.01)
        plt.xlabel("$Q$ / $\mathrm{\AA}$$^{-1}$", fontsize=self.labelfont)
        plt.ylabel("$I$($Q$) / a.u.", fontsize=self.labelfont)

        x = self.calculator.qraw
        y = self.calculator.iraw
        (self.p_iq1,) = plt.plot(
            x, y, color="red", ls="-", label="raw", lw=0.8
        )

        x = self.calculator.q_iq
        y = self.calculator.iq
        (self.p_iq2,) = plt.plot(
            x, y, color="blue", ls="-", label="$I$($Q$)", lw=0.8
        )

        self.ax_iq.relim()
        self.ax_iq.autoscale_view()
        plt.legend(loc=1, prop={"size": 8}, ncol=1, frameon=False, numpoints=3)

    def plot_id(self, grid, position, span):
        self.ax_id = plt.subplot2grid(grid, position, colspan=span)
        self.ax_id.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_id.autoscale(enable=True, axis="y")
        self.ax_id.set_xlim(
            left=0, right=(2.0 * pi / self.calculator.qraw[::-1])[-1] * 1.01
        )
        plt.xlabel("$d$ / $\mathrm{\AA}$", fontsize=self.labelfont)
        plt.ylabel("$I$($d$) / a.u.", fontsize=self.labelfont)

        x = 2.0 * pi / self.calculator.qraw[::-1]
        y = self.calculator.iraw[::-1]
        (self.p_id,) = plt.plot(
            x, y, color="blue", ls="-", label="raw", lw=0.8
        )

        self.ax_id.relim()
        self.ax_id.autoscale_view()
        # plt.legend(loc=1,prop={'size':8},ncol=1,frameon=False,numpoints=3)

    def plot_ib(self, grid, position, span):
        self.ax_ib = plt.subplot2grid(grid, position, colspan=span)
        self.ax_ib.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_ib.autoscale(enable=True, axis="y")
        self.ax_ib.set_xlim(left=0, right=self.calculator.q_iq[-1] * 1.01)
        plt.xlabel("$Q$ / $\mathrm{\AA}$$^{-1}$", fontsize=self.labelfont)
        plt.ylabel("$I$($Q$) / a.u.", fontsize=self.labelfont)

        x = self.calculator.q_iq
        y = self.calculator.iq
        (self.p_iq,) = plt.plot(
            x, y, color="red", ls="-", label="$I$($Q$)", lw=0.8
        )

        num = len(self.calculator.bg_i)
        self.bg_each = []
        for n in range(num):
            y = self.calculator.bg_i[n]
            self.bg_each += plt.plot(x, y, ls=":", label=str(n), lw=0.8)

            if n == num - 1:
                y = self.calculator.bg
                (self.p_bg,) = plt.plot(
                    x, y, color="green", ls="-", label="bg", lw=0.8
                )

        y = self.calculator.ib
        (self.p_ib,) = plt.plot(
            x, y, color="blue", ls="-", label="subtracted", lw=0.8
        )

        self.ax_ib.relim()
        self.ax_ib.autoscale_view()
        plt.legend(loc=1, prop={"size": 8}, ncol=1, frameon=False, numpoints=3)

    def plot_ip(self, grid, position, span):
        self.ax_ip = plt.subplot2grid(grid, position, colspan=span)
        self.ax_ip.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_ip.autoscale(enable=True, axis="y")
        self.ax_ip.set_xlim(left=0, right=self.calculator.q_iq[-1] * 1.01)
        plt.xlabel("$Q$ / $\mathrm{\AA}$$^{-1}$", fontsize=self.labelfont)
        plt.ylabel("$I$($Q$) / a.u.", fontsize=self.labelfont)

        x = self.calculator.q_iq
        y = self.calculator.ib
        (self.p_ib,) = plt.plot(x, y, color="red", ls="-", label="bg", lw=0.8)

        y = self.calculator.ip
        (self.p_ip,) = plt.plot(
            x, y, color="blue", ls="-", label="abs & polar", lw=0.8
        )

        self.ax_ip.relim()
        self.ax_ip.autoscale_view()
        plt.legend(loc=1, prop={"size": 8}, ncol=1, frameon=False, numpoints=3)

    def plot_ic(self, grid, position, span):
        self.ax_ic = plt.subplot2grid(grid, position, colspan=span)
        self.ax_ic.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_ic.autoscale(enable=True, axis="y")
        self.ax_ic.set_xlim(left=0, right=self.calculator.q_iq[-1] * 1.01)
        plt.xlabel("$Q$ / $\mathrm{\AA}$$^{-1}$", fontsize=self.labelfont)
        plt.ylabel("$I$($Q$) / electron$^{2}$", fontsize=self.labelfont)

        x = self.calculator.q_iq
        y = self.calculator.ic
        (self.p_i,) = plt.plot(
            x, y, color="blue", ls="-", label="correct", lw=0.8
        )

        y = self.calculator.baseline
        (self.p_base,) = plt.plot(
            x, y, color="green", ls="-", label="baseline", lw=0.8
        )

        self.ax_ic.relim()
        self.ax_ic.autoscale_view()
        plt.legend(loc=1, prop={"size": 8}, ncol=1, frameon=False, numpoints=3)

    def plot_i(self, grid, position, span):
        self.ax_i = plt.subplot2grid(grid, position, colspan=span)
        self.ax_i.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_i.autoscale(enable=True, axis="y")
        self.ax_i.set_xlim(left=0, right=self.calculator.q_iq[-1] * 1.01)
        plt.xlabel("$Q$ / $\mathrm{\AA}$$^{-1}$", fontsize=self.labelfont)
        plt.ylabel("$I$($Q$) / electron$^{2}$", fontsize=self.labelfont)

        x = self.calculator.q_iq
        y = self.calculator.i
        (self.p_i,) = plt.plot(
            x, y, color="blue", ls="-", label="correct", lw=0.8
        )

        y = self.calculator.compton
        (self.p_comp,) = plt.plot(
            x, y, color="grey", ls=":", label="compton", lw=0.8
        )

        y = self.calculator.f_ave_sq
        (self.p_fas,) = plt.plot(
            x, y, color="black", ls=":", label="<f>$^{2}$", lw=0.8
        )

        y = self.calculator.f_sq_ave
        (self.p_fsa,) = plt.plot(
            x, y, color="red", ls="-", label="<f$^{2}$>", lw=0.8
        )

        self.ax_i.relim()
        self.ax_i.autoscale_view()
        plt.legend(loc=1, prop={"size": 8}, ncol=1, frameon=False, numpoints=3)

    def plot_sq(self, grid, position, span):
        self.ax_sq = plt.subplot2grid(grid, position, colspan=span)
        self.ax_sq.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_sq.autoscale(enable=True, axis="y")
        self.ax_sq.set_xlim(left=0, right=self.calculator.q_iq[-1] * 1.01)
        plt.xlabel("$Q$ / $\mathrm{\AA}$$^{-1}$", fontsize=self.labelfont)
        plt.ylabel("$S$($Q$)", fontsize=self.labelfont)

        self.p_one = plt.plot(
            [0, self.calculator.q_iq[-1] * 1.01],
            [1, 1],
            color="red",
            ls="-",
            label="1",
            lw=0.8,
        )

        x = self.calculator.q_iq
        y = self.calculator.sq
        (self.p_sq,) = plt.plot(
            x, y, color="blue", ls="-", label="$S$($Q$)", lw=0.8
        )

        self.ax_sq.relim()
        self.ax_sq.autoscale_view()

    def plot_fq(self, grid, position, span):
        self.ax_fq = plt.subplot2grid(grid, position, colspan=span)
        self.ax_fq.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_fq.autoscale(enable=True, axis="y")
        self.ax_fq.set_xlim(left=0, right=self.calculator.q_fq[-1] * 1.01)
        plt.xlabel("$Q$ / $\mathrm{\AA}$$^{-1}$", fontsize=self.labelfont)
        plt.ylabel("$F$($Q$) / $\mathrm{\AA}$$^{-1}$", fontsize=self.labelfont)

        x = self.calculator.q_fq
        y = self.calculator.fq
        (self.p_fq,) = plt.plot(
            x, y, color="blue", ls="-", label="$F$($Q$)", lw=0.8
        )

        self.ax_fq.relim()
        self.ax_fq.autoscale_view()

    def plot_gr(self, grid, position, span):
        self.ax_gr = plt.subplot2grid(grid, position, colspan=span)
        self.ax_gr.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_gr.autoscale(enable=True, axis="y")
        self.ax_gr.set_xlim(left=0, right=20)
        plt.xlabel("$r$ / $\mathrm{\AA}$", fontsize=self.labelfont)
        plt.ylabel("$G$($r$) / $\mathrm{\AA}$$^{-2}$", fontsize=self.labelfont)

        x = self.calculator.r
        y = self.calculator.gradient
        (self.plot_density,) = plt.plot(
            x[x < 5.0],
            y[x < 5.0],
            color="red",
            ls=":",
            label="number density",
            lw=0.8,
        )

        y = self.calculator.Gr
        (self.p_gr,) = plt.plot(
            x[x < 20.0],
            y[x < 20.0],
            color="blue",
            ls="-",
            label="$G$($r$)",
            lw=0.8,
        )

        self.ax_gr.relim()
        self.ax_gr.autoscale_view()

    def plot_tr(self, grid, position, span):
        self.ax_tr = plt.subplot2grid(grid, position, colspan=span)
        self.ax_tr.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)
        self.ax_tr.autoscale(enable=True, axis="y")
        self.ax_tr.set_xlim(left=0, right=20.0)
        plt.xlabel("$r$ / $\mathrm{\AA}$", fontsize=self.labelfont)
        plt.ylabel("$T$($r$) / $\mathrm{\AA}$$^{-2}$", fontsize=self.labelfont)

        x = self.calculator.r
        y = self.calculator.tr
        (self.p_tr,) = plt.plot(
            x[x < 20.0],
            y[x < 20.0],
            color="blue",
            ls="-",
            label="$T$($r$)",
            lw=0.8,
        )

        self.ax_tr.relim()
        self.ax_tr.autoscale_view()

    def update_raw(self):
        for n in range(self.calculator.sdata.detectors):
            x = self.calculator.sdata.tc[n]
            y = self.calculator.sdata.ic[n]
            self.p_raw[n].set_data(x, y)
        self.ax_raw.relim()
        self.ax_raw.autoscale_view()

    def update_iq(self):
        x = self.calculator.qraw
        y = self.calculator.iraw
        self.p_iq1.set_data(x, y)

        x = self.calculator.q_iq
        y = self.calculator.iq
        self.p_iq2.set_data(x, y)

        self.ax_iq.relim()
        self.ax_iq.autoscale_view()

    def update_id(self):
        x = 2.0 * pi / self.calculator.qraw
        y = self.calculator.iraw
        self.p_id.set_data(x, y)

        self.ax_id.relim()
        self.ax_id.autoscale_view()

    def update_ib(self):
        x = self.calculator.q_iq
        y = self.calculator.ib
        self.p_ib.set_data(x, y)

        y = self.calculator.iq
        self.p_iq.set_data(x, y)

        num = len(self.calculator.bg_i)
        for n in range(num):
            y = self.calculator.bg_i[n]
            self.bg_each[n].set_data(x, y)
            if n == num - 1:
                y = self.calculator.bg
                self.p_bg.set_data(x, y)

        self.ax_ib.relim()
        self.ax_ib.autoscale_view()

    def update_ip(self):
        x = self.calculator.q_iq
        y = self.calculator.ib
        self.p_ib.set_data(x, y)

        y = self.calculator.ip
        self.p_ip.set_data(x, y)

        self.ax_ip.relim()
        self.ax_ip.autoscale_view()

    def update_ic(self):
        x = self.calculator.q_iq
        y = self.calculator.ic
        self.p_i.set_data(x, y)

        y = self.calculator.baseline
        self.p_base.set_data(x, y)

        self.ax_ic.relim()
        self.ax_ic.autoscale_view()

    def update_i(self):
        x = self.calculator.q_iq
        y = self.calculator.i
        self.p_i.set_data(x, y)

        y = self.calculator.f_ave_sq
        self.p_fas.set_data(x, y)

        y = self.calculator.f_sq_ave
        self.p_fsa.set_data(x, y)

        y = self.calculator.compton
        self.p_comp.set_data(x, y)

        self.ax_i.relim()
        self.ax_i.autoscale_view()

    def update_sq(self):
        x = self.calculator.q_iq
        y = self.calculator.sq
        self.p_sq.set_data(x, y)
        self.ax_sq.relim()
        self.ax_sq.autoscale_view()

    def update_fq(self):
        x = self.calculator.q_fq
        y = self.calculator.fq
        self.p_fq.set_data(x, y)
        self.ax_fq.relim()
        self.ax_fq.autoscale_view()

    def update_gr(self):
        x = self.calculator.r
        y = self.calculator.Gr
        self.p_gr.set_data(x[x < 20], y[x < 20])

        y = self.calculator.gradient
        self.plot_density.set_data(x[x < 5], y[x < 5])

        self.ax_gr.relim()
        self.ax_gr.autoscale_view()

    def update_tr(self):
        x = self.calculator.r
        y = self.calculator.tr
        self.p_tr.set_data(x[x < 20], y[x < 20])
        self.ax_tr.relim()
        self.ax_tr.autoscale_view()

    def slider(self):
        def close_button(event):
            plt.close("all")

        def reset_button(event):
            for n in range(len(self.dic)):
                self.vals[n][0].reset()

        self.slider_input()
        self.fig2 = plt.figure(
            num=2, figsize=(8, self.num_sliders / 4), dpi=100
        )
        self.fig2.subplots_adjust(left=0.15, right=0.85, top=0.9, bottom=0.1)

        n = 0
        for item in list(self.dic.items()):
            ax = plt.subplot2grid(
                (self.num_sliders, 2),
                (n, 0),
                colspan=2,
                facecolor="lightgoldenrodyellow",
            )
            self.vals[n] = (
                Slider(
                    ax,
                    item[0],
                    float(item[1][0]),
                    float(item[1][1]),
                    valfmt=item[1][2],
                    valinit=float(item[1][3]),
                    valstep=item[1][4],
                ),
                item[1][-1],
            )
            self.vals[n][0].on_changed(self.update)
            n += 1

        resetax = plt.subplot2grid(
            (self.num_sliders, 2),
            (self.num_sliders - 1, 0),
            colspan=1,
            facecolor="lightgoldenrodyellow",
        )
        self.resetbutton = mw.Button(
            resetax, "reset", color="white", hovercolor="yellow"
        )
        self.resetbutton.on_clicked(reset_button)

        closeax = plt.subplot2grid(
            (self.num_sliders, 2),
            (self.num_sliders - 1, 1),
            colspan=1,
            facecolor="lightgoldenrodyellow",
        )
        self.closebutton = mw.Button(
            closeax, "close", color="white", hovercolor="yellow"
        )
        self.closebutton.on_clicked(close_button)

    def slider_input(self):
        # key, min, max, fmt, init
        self.dic = OrderedDict()

        for key in self.slider_keys:
            if key in ["raw"]:
                for n in range(self.calculator.sample_data.detectors):
                    self.dic["shift" + str(n)] = [
                        self.calculator.sample_data.shift[n] - 1.0,
                        self.calculator.sample_data.shift[n] + 1.0,
                        "%.4f",
                        self.calculator.sample_data.shift[n],
                        self.calculator.sample_data.shift[n] / 100.0,
                        "raw",
                    ]
                    self.dic["offset" + str(n)] = [
                        amin(self.calculator.sample_data.y) * -1,
                        amin(self.calculator.sample_data.y) * 1.0,
                        "%.4f",
                        self.calculator.sample_data.offset[n],
                        amin(self.calculator.sample_data.y) / 1000.0,
                        "raw",
                    ]
                    self.dic["broad" + str(n)] = [
                        0,
                        3,
                        "%.2f",
                        self.calculator.sample_data.broadening[n],
                        0.01,
                        "raw",
                    ]
                    self.dic["deadtime" + str(n)] = [
                        0.0,
                        50.0,
                        "%.1f",
                        self.calculator.sample_data.deadtime[n],
                        0.1,
                        "raw",
                    ]

            elif key == "iq":
                self.dic["zeroshift"] = [
                    -0.5,
                    0.5,
                    "%.3f",
                    self.calculator.par["zeroshift"],
                    0.005,
                    "iq",
                ]
                self.dic["qmin"] = [
                    0.0,
                    5.0,
                    "%.2f",
                    self.calculator.par["qmin"],
                    0.01,
                    "iq",
                ]
                self.dic["qmax"] = [
                    self.calculator.qraw[-1] / 2.0,
                    self.calculator.qraw[-1],
                    "%.2f",
                    self.calculator.par["qmax"],
                    0.01,
                    "iq",
                ]
                if self.calculator.par["ttfilter"] != None:
                    self.dic["ttfilter"] = [
                        0.0,
                        0.5,
                        "%.3f",
                        self.calculator.par["ttfilter"],
                        0.001,
                        "iq",
                    ]
                if self.calculator.par["qfilter"] != None:
                    self.dic["qfilter"] = [
                        0.0,
                        0.5,
                        "%.3f",
                        self.calculator.par["qfilter"],
                        0.001,
                        "iq",
                    ]

            elif key == "bg":
                bg_numbers = len(self.calculator.background_data)
                for n in range(bg_numbers):
                    self.dic["scale" + str(n)] = [
                        self.calculator.background_data[n].scale * 0.1,
                        self.calculator.background_data[n].scale * 10.0,
                        "%.3f",
                        self.calculator.background_data[n].scale,
                        self.calculator.background_data[n].scale / 1000.0,
                        "bg",
                    ]
                    self.dic["zeroshift" + str(n)] = [
                        -10.0
                        * abs(self.calculator.background_data[n].zeroshift),
                        10.0
                        * abs(self.calculator.background_data[n].zeroshift),
                        "%.3f",
                        self.calculator.background_data[n].zeroshift,
                        0.001,
                        "bg",
                    ]

            elif key == "ip":
                self.dic["mur"] = [
                    0.0,
                    3.0,
                    "%.2f",
                    self.calculator.par["mur"],
                    0.01,
                    "ip",
                ]
                self.dic["polar"] = [
                    -1.0,
                    1.0,
                    "%.2f",
                    self.calculator.par["polar"],
                    0.01,
                    "ip",
                ]
                # self.dic["alpha"] = [0.0,	4, "%.2f",	self.calculator.par["alpha, 0.01,"ip"]

            elif key == "ic":
                self.dic["qmin"] = [
                    0.0,
                    5.0,
                    "%.2f",
                    self.calculator.par["qmin"],
                    0.01,
                    "iq",
                ]
                self.dic["qmax"] = [
                    self.calculator.qraw[-1] / 2.0,
                    self.calculator.qraw[-1],
                    "%.2f",
                    self.calculator.par["qmax"],
                    0.01,
                    "iq",
                ]
                self.dic["fitmin"] = [
                    self.calculator.qraw[-1] / 4.0,
                    self.calculator.qraw[-1],
                    "%.2f",
                    self.calculator.par["fitmin"],
                    0.01,
                    "ic",
                ]
                self.dic["fitmax"] = [
                    self.calculator.qraw[-1] / 2.0,
                    self.calculator.qraw[-1],
                    "%.2f",
                    self.calculator.par["fitmax"],
                    0.01,
                    "ic",
                ]

                if self.calculator.par["basetype"] in ["spline", "alss"]:
                    self.dic["baseq"] = [
                        1,
                        20,
                        "%i",
                        self.calculator.par["baseq"],
                        1,
                        "ic",
                    ]

            elif key in ["sq", "fq"]:
                self.dic["qmin"] = [
                    0.0,
                    5.0,
                    "%.2f",
                    self.calculator.par["qmin"],
                    0.01,
                    "ip",
                ]
                self.dic["qmax"] = [
                    self.calculator.qraw[-1] / 2.0,
                    self.calculator.qraw[-1],
                    "%.2f",
                    self.calculator.par["qmax"],
                    0.01,
                    "ip",
                ]
                self.dic["fitmin"] = [
                    self.calculator.qraw[-1] / 4.0,
                    self.calculator.qraw[-1],
                    "%.2f",
                    self.calculator.par["fitmin"],
                    0.01,
                    "ic",
                ]
                self.dic["fitmax"] = [
                    self.calculator.qraw[-1] / 2.0,
                    self.calculator.qraw[-1],
                    "%.2f",
                    self.calculator.par["fitmax"],
                    0.01,
                    "ic",
                ]
                self.dic["lorch"] = [
                    0.0,
                    4.0,
                    "%.2f",
                    self.calculator.par["lorch"],
                    0.01,
                    "fq",
                ]

                if self.calculator.par["rfilter"] != None:
                    self.dic["rfilter"] = [
                        0.0,
                        4,
                        "%.2f",
                        self.calculator.par["rfilter"],
                        0.01,
                        "fq",
                    ]

            elif key in ["Gr", "tr"]:
                if self.calculator.par["rfilter"] != None:
                    self.dic["rfilter"] = [
                        0.0,
                        4,
                        "%.2f",
                        self.calculator.par["rfilter"],
                        0.01,
                        "fq",
                    ]

                self.dic["lorch"] = [
                    0.0,
                    4.0,
                    "%.2f",
                    self.calculator.par["lorch"],
                    0.01,
                    "fq",
                ]
                self.dic["padding"] = [
                    1,
                    6,
                    "%i",
                    self.calculator.par["padding"],
                    1,
                    "Gr",
                ]
                nd_par = self.calculator.par.get("number_density", self.calculator.par.get("ndensity"))
                self.dic["number_density"] = [
                    0,
                    1.0,
                    "%.3f",
                    nd_par,
                    0.001,
                    "Gr",
                ]

        self.vals = zeros(len(self.dic)).tolist()
        self.num_sliders = len(self.dic) + 1

    def update(self, val):
        def recalc(keys):
            if "raw" in keys:
                self.calculator.sample_data.calc()
                self.calculator.run()
                return

            elif "iq" in keys:
                self.calculator.run()
                return

            elif "bg" in keys:
                self.calculator.bg_subtraction()
                self.calculator.correction()
                # self.calculator.form_factor_compton()
                self.calculator.normalization()
                self.calculator.transform()
                return

            elif "ip" in keys:
                # self.calculator.bg_subtraction()
                self.calculator.correction()
                # self.calculator.form_factor_compton()
                self.calculator.normalization()
                self.calculator.transform()
                return

            elif "ic" in keys:
                # self.calculator.bg_subtraction()
                # self.calculator.correction()
                # self.calculator.form_factor_compton()
                self.calculator.normalization()
                self.calculator.transform()
                return

            elif "i" in keys:
                self.calculator.normalization()
                self.calculator.transform()
                return

            elif "fq" in keys:
                self.calculator.normalization()
                self.calculator.transform()
                return

            elif "Gr" in keys:
                # self.calculator.normalization()
                self.calculator.transform()
                return

        n = 0
        updates = []
        for key in list(self.dic.keys()):
            value = self.vals[n][0].val

            if value == val:
                self.update_value(key, value)
                updates += [self.vals[n][1]]
            n += 1

        recalc(set(updates))

        for x, key in enumerate(self.figure_keys):
            if key == "raw":
                self.update_raw()
            elif key == "bg":
                self.update_ib()
            elif key == "iq":
                self.update_iq()
            elif key == "ip":
                self.update_ip()
            elif key == "ic":
                self.update_ic()
            elif key == "i":
                self.update_i()
            elif key == "sq":
                self.update_sq()
            elif key == "fq":
                self.update_fq()
            elif key == "Gr":
                self.update_gr()
            elif key == "tr":
                self.update_tr()
        self.fig1.canvas.draw_idle()

    def update_value(self, key, value):
        if key == "zeroshift":
            self.calculator.par["zeroshift"] = value

        elif re.sub(r"[\d]+", "", key) in [
            "shift",
            "offset",
            "broad",
            "deadtime",
        ]:
            n = int(re.sub(r"[\D]+", "", key))
            self.calculator.sample_data[key][n] = value

        elif re.sub(r"[\d]+", "", key) in ["scale", "zeroshift"]:
            n = int(re.sub(r"[\D]+", "", key))
            self.calculator.sample_data[key] = value

        else:
            self.calculator.par[key] = value

    def save(self):
        plt.rcParams["font.size"] = 10
        plt.rcParams["axes.linewidth"] = 1.0
        plt.rcParams["font.family"] = "Arial"
        fig = plt.figure(num=3, figsize=(9, 4), dpi=200)

        for x, key in enumerate(self.figure_keys):
            if key == "iraw":
                self.plot_raw((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")

            elif key == "bg":
                self.plot_ib((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")

            elif key == "iq":
                self.plot_iq((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")

            elif key == "ip":
                self.plot_ip((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")

            elif key == "ic":
                self.plot_ic((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")

            elif key == "i":
                self.plot_i((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")

            elif key == "sq":
                self.plot_sq((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")

            elif key == "fq":
                self.plot_fq((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")

            elif key == "Gr":
                self.plot_gr((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")

            elif key == "tr":
                self.plot_tr((1, 1), (0, 0), 1)
                fig.tight_layout()
                plt.savefig(key + ".png")
