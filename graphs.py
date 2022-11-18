import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
from scipy.stats import linregress
import arviz as az

import matplotlib.dates as mdates
from numpyro.examples.datasets import SP500, load_dataset

from old import MMD
from benchmark_targets import *

tab_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']


### Plots for the paper ###



def bounce_frequency_full_bias():
    """ Figure 2 """

    def point_reduction(points, reduction_factor):
        """reduces the number of points for plotting purposes"""

        indexes = np.concatenate((np.arange(1, 1 + points // reduction_factor, dtype=int),
                                  np.arange(1 + points // reduction_factor, points, reduction_factor, dtype=int)))
        return indexes

    def ess_axis(ax, ff):

        steps_to_ess = lambda n: 200 / n
        ess_to_steps = lambda e: 200 / e

        ymin, ymax = plt.ylim()
        ax2 = ax.secondary_xaxis(np.log10(0.1 / ymin) / np.log10(ymax / ymin), functions=(steps_to_ess, ess_to_steps))
        plt.text(6e2, 0.05, 'ESS', fontsize = ff)

    length = ['2', '5', '30', '90', r'$\infty$']
    #length = [    2,     5,     10,   30,   50,    75,    80,   90,   100,  1000, 10000, 10000000]
    #mask_plot = [True, True, False, True, False, False, False, True, True, False, False, False]
    #mask_plot = len(length) * [True, ]

    X = np.load('Tests/data/full_bias.npy')
    indexes = point_reduction(len(X[0]), 100)


    ff, ff_title, ff_ticks = 26, 20, 26
    lw = 4
    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks
    plt.figure(figsize= (20, 8))
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    colors = plt.cm.coolwarm(np.linspace(0, 1, len(length)))[::-1]
    #colors = ['tab:red', 'tab:orange', 'gold', 'limegreen', 'seagreen']
    dash_size = [1, 5, 15, 25, 40, 80]
    for n in range(len(length)):
        plt.plot(indexes, X[n, indexes], lw = lw, linestyle='--', dashes=(dash_size[n], 2),  color = colors[n], label = r'$L = $' + length[n])

    # plt.plot([0, len(variance_bias)], [0.1, 0.1], ':', color='black', alpha = 0.5) #threshold for effective sample size 200
    plt.legend(fontsize = ff)
    plt.yscale('log')
    plt.xscale('log')
    plt.xlabel('# gradient evaluations', fontsize = ff)
    plt.ylabel('bias', fontsize = ff)
    plt.xlim(1, 1e6)
    ess_axis(ax, ff)
    plt.savefig('submission/FullBias.pdf')
    plt.show()



def dimension_dependence_with_peaks():

    generalized = False
    dimensions = [100, 300, 1000, 3000]

    df = pd.read_csv('Tests/data/dimensions/StandardNormal'+('_g' if generalized else '')+'_eps4.csv', sep='\t')

    skip_large = -1
    alpha = np.array(df['alpha'])[:skip_large]
    E, L = [], []

    ff, ff_title, ff_ticks = 20, 22, 18
    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks
    plt.figure(figsize= (20, 7))

    plt.subplot(1, 2, 1)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    #folder_name = 'Rosenbrock_precondition_t'
    factor = 1.0 #Leapfrog
    #factor = 0.25 #Yoshida
    for i in range(len(dimensions)):
        d = dimensions[i]
        #peak
        ess = factor * np.array(df['ess (d='+str(d)+')'])[:skip_large]
        ess_err = factor * np.array(df['err ess (d=' + str(d) + ')'])[:skip_large]
        plt.plot(alpha * np.sqrt(d), ess, '.:', color = tab_colors[i], alpha = 0.5)
        plt.fill_between(alpha * np.sqrt(d), ess - ess_err, ess + ess_err, color = tab_colors[i], alpha = 0.1)

        #highest point
        imax= np.argmax(ess)
        L.append(alpha[imax] * np.sqrt(d))
        E.append(ess[imax])
        plt.plot(L[-1], E[-1], 'o', markersize =10, color = tab_colors[i])
        plt.text(L[-1] * 1.06, E[-1]*1.07, 'd= '+str(d), color = tab_colors[i], alpha = 0.5, fontsize = ff) #dimension tag

    eps = 1.0
    l = np.linspace(np.min(L)*0.9, np.max(L)*1.1)

    coeff = np.dot(L, eps/np.array(E)) / np.dot(L, L)
    print(coeff)
    plt.plot(l, (eps/l) / coeff, color = 'black', alpha = 0.5)
    plt.xscale('log')
    plt.ylabel('ESS', fontsize = ff)
    if generalized:
        plt.xlabel(r'$L(\nu) = \epsilon / \log \sqrt{1 + \nu^2 d}$', fontsize = ff)
    else:
        plt.xlabel(r'$L$', fontsize=ff)

    ###  L ~ sqrt(d)  ###
    plt.subplot(1, 2, 2)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    for i in range(len(dimensions)):
        plt.plot(dimensions[i], L[i], 'o', markersize =10, color = tab_colors[i])

    skip = 0
    slope= np.dot(np.sqrt(dimensions[skip:]), L[skip:]) / np.sum(dimensions[skip:])
    print(slope)
    print(coeff*slope)
    plt.title(r'$L \approx$' +'{0:.4}'.format(slope) + r' $\sqrt{d}$', fontsize = ff)
    plt.plot(dimensions, slope * np.sqrt(dimensions), ':', color = 'black')
    plt.xlabel('d', fontsize = ff)
    plt.ylabel(r'optimal $L$', fontsize = ff)
    if generalized:
        plt.ylabel(r'optimal $L(\nu)$', fontsize=ff)

    plt.xscale('log')
    plt.yscale('log')


    # if generalized:
    #     plt.savefig('submission/GeneralizedTuning.pdf')
    # else:
    #     plt.savefig('submission/BounceTuning.pdf')

    plt.show()



def dimension_dependence():
    """Figure 3"""

    ff, ff_title, ff_ticks = 20, 22, 18
    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks
    plt.figure(figsize= (21, 8))


    dimensions = [100, 300, 1000, 3000, 10000]
    targets = ['Kappa1', 'Kappa100', 'Rosenbrock']
    colors= ['tab:blue', 'tab:orange', 'tab:red']
    names_targets = ['Standard Gaussian', r'Gaussian ($\kappa = 100$)', r'Rosenbrock ($Q = 0.5$)']
    method_marker = ['s', 'o']
    method_name = ['bounces', 'generalized']
    DF= [[pd.read_csv('Tests/data/dimensions_dependence/'+tar+method+'.csv') for tar in targets] for method in ['', 'g']]

    plt.subplot(1, 3, 1)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    for j in range(len(method_name)):
        for i in range(len(targets)):
            df = DF[j][i]
            plt.plot(dimensions, df['eps'], method_marker[j], color = colors[i])
            eps1 = np.dot(np.sqrt(dimensions), df['eps']) / np.sum(dimensions)
            print(eps1)
            plt.plot(dimensions, eps1 * np.sqrt(dimensions), color = colors[i], alpha= 0.2)

    plt.xlabel('d', fontsize= ff)
    plt.ylabel(r'$\epsilon$', fontsize= ff)
    plt.xscale('log')
    plt.yscale('log')
    plt.ylim(0.8, 1.1e2)


    plt.subplot(1, 3, 2)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    for j in range(len(method_name)):
        for i in range(len(targets)):
            df = DF[j][i]
            plt.plot(dimensions, df['alpha'] *np.sqrt(dimensions), method_marker[j], color = colors[i])
            alpha = np.dot(np.sqrt(dimensions), df['alpha'] * np.sqrt(dimensions)) / np.sum(dimensions)
            print(alpha)
            plt.plot(dimensions, alpha * np.sqrt(dimensions), color = colors[i], alpha= 0.2)
            plt.plot(dimensions, df['eps'] / df['ESS'], ':', color = colors[i])

    plt.xlabel('d', fontsize= ff)
    plt.ylabel('L', fontsize= ff)
    plt.xscale('log')
    plt.yscale('log')


    plt.subplot(2, 3, 3)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    for j in range(len(method_name)):
        for i in range(len(targets)):
            df = DF[j][i]
            plt.plot(dimensions, df['ESS'] / df['ESS'][2], method_marker[j], color = colors[i])
            print(df['ESS'][0])
            plt.plot(dimensions, np.ones(len(dimensions)), color = 'black')

    plt.xlabel('d', fontsize= ff)
    plt.ylabel('ESS / ESS(d = 1000)', fontsize= ff)
    plt.xscale('log')
    plt.ylim(0.8, 1.3)

    plt.subplot(2, 3, 6)
    plt.axis('off')
    [plt.plot([], [], color=colors[i], label = names_targets[i]) for i in range(len(names_targets))]
    plt.legend(loc = 3, fontsize= ff)

    [plt.plot([], [], method_marker[j], color = colors[0], label = method_name[j]) for j in range(len(method_name))]
    plt.legend(loc = 3, fontsize= ff)

    #plt.gca().add_artist(plt.legend(, names_targets, loc = 4))
    #plt.legend([plt.plot([], [], method_marker[j], color = 'black') for j in range(len(method_name))], method_name, loc = 3)


    plt.savefig('submission/dimension_scaling2.png')

    plt.show()




def esh_not_converging():
    """Figure 4"""

    data1 = np.load('ESH_not_converging/data/ESHexample_ESH.npy')
    data2 = np.load('ESH_not_converging/data/ESHexample_MCHMC.npy')
    color1, color2, color_target = 'tab:red', 'tab:blue', 'binary'

    target = IllConditionedESH()#IllConditionedGaussian(d = 50, condition_number= 1)
    sigma1, sigmad = np.sqrt(target.variance[0]), np.sqrt(target.variance[-1])

    bias_esh= [5.4, 0.64, 0.64, 0.64]
    bias_mchmc = [5.4, 0.64, 0.48, 0.05]

    exact_samples = np.array([target.draw(k) for k in jax.random.split(jax.random.PRNGKey(0), 5000)])

    plt.figure(figsize=(21, 7))

    ff, ff_title, ff_ticks = 24, 22, 20
    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks


    steps = [0, 100, 1000, 10000]
    times= [0, 1, 3]

    # MMD
    #mmd_avg = np.array([[MMD.mmd((data[t, :, :].T) / np.sqrt(target.variance), exact_samples / np.sqrt(target.variance))[0] for t in range(4)] for data in [data1, data2]])
    #print(mmd_avg)

    mmd_strings = [[r'$0.01$', r'$4.5 \cdot 10^{-4}$', '', r'$3.4 \cdot 10^{-5}$'],
                   [r'$0.01$', r'$ < 10^{-5}$', '', r'$ < 10^{-5}$']]

    shift = [0.8, -0.3, -0.3]
    shift2 = [0, -0.15, -0.15]

    for i in range(3):
        t = times[i]
        plt.subplot(1, 3, i+1)
        ax = plt.gca()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        plt.title('steps = ' + str(steps[t]), fontsize= ff_title)
        lim_x = 4#if i == 0 else 0.7
        lim_y = 4
        #lim_x, lim_y = 10, 10
        #lim_x = np.max(np.abs([data1[t, 0, :], data2[t, 0, :]]))*1.05
        #lim_y = np.max(np.abs([data1[t, -1, :], data2[t, -1, :]]))*1.05

        # background
        x = np.linspace(-lim_x, lim_x, 100)
        y = np.linspace(-lim_y, lim_y, 100)
        X, Y = np.meshgrid(x, y)
        Z = np.exp(- 0.5 * (np.square(X/sigma1) + np.square(Y/sigmad)))
        plt.contourf(X, Y, Z, cmap = color_target, levels = 100)


        plt.title('steps = ' + str(steps[t]), fontsize= ff_title)

        # MMD
        plt.text(0.2 + shift[i], 3.5, 'MMD = ', fontsize= ff_title, color = 'black')
        plt.text(2.0 + shift[i], 3.5, mmd_strings[0][t], fontsize= ff_title, color = color1)
        plt.text(2.0 + shift[i], 3.0, mmd_strings[1][t], fontsize=ff_title, color = color2)

        # bias
        plt.text(1.4 + shift2[i], -3.0, 'bias = ', fontsize=ff_title, color='black')
        plt.text(3 + shift2[i], -3.0, bias_esh[t], fontsize=ff_title, color= color1)
        plt.text(3 + shift2[i], -3.5, bias_mchmc[t], fontsize=ff_title, color= color2)

        plt.plot(data1[t, 0, :], data1[t, -1, :], '.', color= color1, markersize = 6 if t == 0 else 2)
        plt.plot(data2[t, 0, :], data2[t, -1, :], '.', color= color2, markersize = 3 if t == 0 else 2)

        plt.xlim(-lim_x, lim_x)
        plt.ylim(-lim_y, lim_y)
        plt.xlabel(r'$x_{1}$', fontsize= ff)

        if i == 0:
            plt.ylabel(r'$x_{50}$', fontsize= ff)
            plt.yticks([-3, -2, -1, 0, 1, 2, 3])
            plt.xticks([-2, 0, 2])

            plt.plot([], [], '.', markersize =10, color = color1, label = 'ESH')
            plt.plot([], [], '.', markersize=10, color= color2, label='MCHMC')
            plt.legend(fontsize = ff-2, loc= 2)


        else:
            plt.yticks([])
            plt.xticks([-2, 0, 2])



    plt.subplots_adjust(wspace=0, hspace=0)
    plt.savefig('submission/particles.pdf')
    plt.show()



def kappa_dependence_prelim():

    kappa = [1, 10, 100, 10000, 10000]
    factor = 1.0  # Leapfrog
    # factor = 0.25 #Yoshida
    E, L = [], []


    plt.figure(figsize=(15, 5))

    ###  peaks ESS(L) for different kappa  ###
    plt.subplot(1, 3, 1)

    for i in range(len(kappa)):
        K = kappa[i]
        X = np.load('Tests/data/kappa/'+str(K)+'.npy')
        #peak
        plt.plot(X[:, 1], factor*X[:, 0], color = tab_colors[i], alpha= 0.5)

        #highest point
        imax= np.argmax(factor*X[:, 0])
        L.append(X[imax, 1])
        E.append(X[imax, 0])
        plt.plot(X[imax, 1], factor*X[imax, 0], '.', color = tab_colors[i])
        plt.text(X[imax, 1] * 1.05, factor*X[imax, 0]*1.03, 'kappa = '+str(K), color = tab_colors[i], alpha = 0.5) #dimension tag


    plt.ylabel('ESS')
    plt.xlabel("orbit length between bounces")


    ###  optimal L as a function of kappa  ###
    plt.subplot(1, 3, 2)
    for i in range(len(kappa)):
        plt.plot(kappa[i], L[i], 'o', color = tab_colors[i])

    # skip = 1
    # slope= np.dot(np.sqrt(dimensions[skip:]), L[skip:]) / np.sum(dimensions[1:])
    # print(slope)
    # plt.title(r'$L \approx$' +'{0:.4}'.format(slope) + r' $\sqrt{d}$')
    # plt.plot(dimensions, slope * np.sqrt(dimensions), ':', color = 'black')
    plt.xlabel('condition number')
    plt.ylabel('optimal orbit length between bounces')
    plt.xscale('log')
    #plt.yscale('log')


    ###  optimal ESS as a function of kappa  ###
    plt.subplot(1, 3, 3)

    for i in range(len(kappa)):
        plt.plot(kappa[i], E[i], 'o', color= tab_colors[i])

    #from scipy.stats import linregress
    #res = linregress(np.log(dimensions[skip:]), np.log(E[skip:]))


    #plt.title(r'ESS $\propto d^{-\alpha}, \quad \alpha = $' + '{0}'.format(np.round(-res.slope, 2)))
    #plt.plot(dimensions, np.exp(res.intercept) * np.power(dimensions, res.slope), ':', color='black')
    plt.xlabel('condition number')
    plt.ylabel('ESS')
    plt.xscale('log')
    plt.yscale('log')

    #plt.savefig('Tests/bounce_dimension_dependence/'+folder_name+'.png')
    plt.show()




def ill_conditioned():
    """Figure 5"""


    ff, ff_title, ff_ticks = 34, 22, 34

    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks
    plt.figure(figsize= (20, 9))
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    kappa = np.logspace(0, 5, 18)


    # ess= [np.max(np.load('Tests/data/kappa/' + str(i) + '.npy')[:, 0]) for i in range(18)]
    # plt.plot(kappa, ess, 'o:', color = 'tab:purple',  label = 'MCHMC (fine tuned)')

    ess_mchmc = np.load('Tests/data/kappa/fine_tuned_l.npy')
    color = 'indigo'
    plt.plot(kappa, ess_mchmc[:, 0], 'o-', color=color, label='generalized MCHMC')
    plt.fill_between(kappa, ess_mchmc[:, 0] - ess_mchmc[:, 1], ess_mchmc[:, 0] + ess_mchmc[:, 1], color=color, alpha=0.07)

    ess_mchmc = np.load('Tests/data/kappa/fine_tuned_t.npy')
    color = 'cornflowerblue'
    plt.plot(kappa, ess_mchmc[:, 0], 'o-', color=color, label='MCHMC (fine tuning)')
    plt.fill_between(kappa, ess_mchmc[:, 0] - ess_mchmc[:, 1], ess_mchmc[:, 0] + ess_mchmc[:, 1], color=color, alpha=0.07)

    # ess_mchmc = np.load('Tests/data/kappa/fine_tuned.npy')
    # plt.plot(kappa, ess_mchmc[:, 0], 'o:', color='tab:blue', label='MCHMC (bounces in distance)')
    # plt.fill_between(kappa, ess_mchmc[:, 0] - ess_mchmc[:, 1], ess_mchmc[:, 0] + ess_mchmc[:, 1], color='tab:blue', alpha=0.07)

    # ess_mchmc = np.load('Tests/data/kappa/L1.5.npy')[:, 0]
    # plt.plot(kappa, ess_mchmc, 'o:', color = 'tab:blue', alpha = 0.5, label = 'MCHMC (tuning free)')
    ess_mchmc = np.load('Tests/data/kappa/no_tuning_t.npy')
    color = 'teal'
    plt.plot(kappa, ess_mchmc[:, 0], 'o-', color = color, label = 'MCHMC (tuning free)')
    plt.fill_between(kappa, ess_mchmc[:, 0] - ess_mchmc[:, 1], ess_mchmc[:, 0] + ess_mchmc[:, 1], color = color, alpha = 0.07)


    ess_nuts = np.load('Tests/data/kappa/NUTS.npy').T
    color = 'tab:orange'
    plt.plot(kappa, ess_nuts[:, 0], 'o-', color=color, label='NUTS')
    plt.fill_between(kappa, ess_nuts[:, 0] - ess_nuts[:, 1], ess_nuts[:, 0] + ess_nuts[:, 1], color=color, alpha=0.07)




    plt.ylabel('ESS', fontsize= ff)
    plt.xlabel('condition number', fontsize= ff)
    plt.xscale('log')
    plt.yscale('log')
    plt.legend(fontsize= ff)

    # 1/ sqrt(kappa) lines
    xlims = plt.gca().get_xlim()
    ylims = plt.gca().get_ylim()
    print(xlims)
    log_kappa_range = np.log(xlims)

    for log_ess0 in np.linspace(np.log(ylims[0]), np.log(ylims[1]) + 0.5 * (log_kappa_range[1] - log_kappa_range[0]), 20):
        plt.plot(np.exp(log_kappa_range), np.exp(log_ess0 - 0.5 * (log_kappa_range - log_kappa_range[0])), ':', color='black', alpha=0.15)

    plt.xlim(*xlims)
    plt.ylim(*ylims)

    plt.savefig('submission/kappa.pdf')
    plt.show()




def BimodalMarginal():
    """Figure 6"""

    #the problem parameters:
    d = 50
    mu1, sigma1= 0.0, 1.0 # the first Gaussian
    mu2, sigma2, f = 8.0, 1.0, 0.2 #the second Gaussian

    #plot parameters
    ff, ff_title, ff_ticks = 40, 20, 37
    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks
    plt.figure(figsize=(15, 11))
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


    #NUTS
    X = np.load('Tests/data/bimodal_marginal/NUTS_hard.npz')
    x0, steps = np.array(X['x0']), np.array(X['steps'])

    plt.hist(x0, density=True, bins = 30, alpha = 0.5, color = 'tab:orange', label = 'NUTS', zorder = 0)

    #MCHMC

    def my_hist(bins, count):
        probability = count / np.sum(count)
        print('probability outside of bins', probability[-1])

        for i in range(len(bins)):
            density = probability[i] / (bins[i][1] - bins[i][0])
            plt.fill_between(bins[i], np.zeros(2), density * np.ones(2), alpha = 0.5, color='tab:blue', zorder = 1)

        plt.fill_between([], [], [], alpha = 0.5, color = 'tab:blue', label = 'MCHMC')

    xmax = 3.5 #how many sigma away from the mean of the gaussians do we want to have bins

    def get_bins(mu, sigma, num_bins_per_mode):
        bins_mode = np.array([[- xmax + i * 2 * xmax / num_bins_per_mode, - xmax + (i+1) * 2 * xmax / num_bins_per_mode] for i in range(num_bins_per_mode)])

        bins = np.concatenate(( (bins_mode * sigma[0]) + mu[0], (bins_mode * sigma[1]) + mu[1]  ))

        return bins

    bins_per_mode = 20
    bins = get_bins([mu1, mu2], [sigma1, sigma2], bins_per_mode)
    P = np.load('Tests/data/bimodal_marginal/sep'+str(mu2)+'_f'+str(f)+'_sigma'+str(sigma2)+'.npy')

    my_hist(bins, P)
    f1, f2 = np.sum(P[:bins_per_mode]), np.sum(P[bins_per_mode : 2 * bins_per_mode])
    print('f = ' + str(f2 / (f1 + f2)) + '  (true f = ' + str(f) + ')')


    #exact
    t = np.linspace(-xmax*sigma1+mu1-0.5, xmax*sigma2 + mu2 + 0.5, 1000)
    plt.plot(t, (1- f)*norm.pdf(t, loc = mu1, scale = sigma1) + f * norm.pdf(t, loc = mu2, scale = sigma2), color = 'black', label = 'exact', zorder = 2)

    plt.legend(fontsize = ff)
    plt.xlim(t[0], t[-1])
    plt.ylim(0, 0.4)
    plt.yticks([0, 0.1, 0.2, 0.3, 0.4])
    plt.xticks([-2, 0, 2, 4, 6, 8, 10])
    plt.xlabel(r'$x_1$', fontsize = ff)
    plt.ylabel(r'$p(x_1)$', fontsize = ff)
    plt.savefig('submission/BimodalMarginal.pdf')
    plt.show()



def rosenbrock():
    """Figure 6"""

    xmin, xmax, ymin, ymax = -2.3, 3.9, -2, 16

    ff_ticks, ff = 29, 35
    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks
    plot = sns.JointGrid(height= 11, xlim= (xmin, xmax), ylim= (ymin, ymax))


    # MCHMC
    d = 36
    X = np.load('Tests/data/rosenbrock_funnel/rosenbrock.npz')
    x, y = X['samples'][:, 0], X['samples'][:, d // 2]
    w = X['w']
    sns.histplot(x=x, y=y, weights=w, bins=200, ax=plot.ax_joint)

    #sns.scatterplot(x=[], y=[], ax= plot.ax_joint, color = 'tab:blue')

    # # marginals
    sns.histplot(x= x, weights= w, bins= 40, fill= True, alpha = 0.5, linewidth= 0, ax= plot.ax_marg_x, stat= 'density', color= 'tab:blue', zorder = 2)
    sns.histplot(y= y, weights= w, bins= 40, fill= True, alpha = 0.5, linewidth= 0, ax= plot.ax_marg_y, stat= 'density', color= 'tab:blue', label= 'MCHMC', zorder = 2)


    # NUTS
    X= np.load('Tests/data/rosenbrock_funnel/rosenbrock_HMC.npz')
    x, y = X['x'][:, 0], X['y'][:, 0]

    sns.scatterplot(x, y, s= 6, linewidth= 0, ax= plot.ax_joint, alpha = 0.7, color= 'tab:orange')

    # marginals
    sns.histplot(x=x, bins= 40, fill= True, alpha = 0.5, linewidth= 0, ax= plot.ax_marg_x, stat= 'density', color= 'tab:orange', zorder = 1)
    sns.histplot(y=y, bins= 40, fill= True, alpha = 0.5, linewidth= 0, ax= plot.ax_marg_y, stat= 'density', color= 'tab:orange', label= 'NUTS', zorder = 1)


    #exact
    ros = Rosenbrock(d = 2)
    X = ros.draw(1000)
    x, y = X[:, 0], X[:, 1]

    sns.scatterplot(x, y, s= 6, linewidth= 0, ax= plot.ax_joint, color= 'black', alpha = 0.5)

    # marginals
    sns.lineplot(x, np.exp(-0.5 * np.square(x - 1)) / np.sqrt(2 * np.pi), linewidth= 1, ax= plot.ax_marg_x, color= 'black', alpha = 0.5)
    ros = Rosenbrock(d=2)
    X = ros.draw(5000000)
    x, y = X[:, 0], X[:, 1]
    sns.histplot(y=y, bins= 2000, fill= False, element= 'step', linewidth= 1, ax= plot.ax_marg_y, stat= 'density', color= 'black', alpha = 0.5, label= 'exact')


    #plot.ax_marg_y.legend(fontsize = ff)

    plot.set_axis_labels(r'$x_1$', r'$y_1$', fontsize= ff)
    plt.yticks([0, 5, 10, 15])
    plt.tight_layout()
    plt.savefig('submission/rosenbrock.pdf')
    plt.show()



def funnel():
    """Figure 7"""

    def gaussianize(z, theta):
        return (z.T * np.exp(-0.5 * theta)).T, theta / 3.0

    eps, free_time = 0.1, 6
    data = np.load('Tests/data/rosenbrock_funnel/funnel_free'+str(free_time) + '_eps'+str(eps)+'.npz')
    z, theta, w = data['z'], data['theta'], data['w']


    data = np.load('Tests/data/rosenbrock_funnel/funnel_HMC.npz')
    zHMC, thetaHMC = data['z'], data['theta']


    ff, ff_title, ff_ticks = 35, 36, 34
    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks
    plt.figure(figsize=(24, 8))


    ####   2d marginal in the original coordinates ####
    plt.subplot(1, 3, 1)
    plt.title('Original coordinates', fontsize = ff_title, y= 1.05)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.plot(zHMC[:, 0], thetaHMC, '.', ms= 1, color = 'tab:orange', label = 'NUTS')

    #plt.hist2d(z[:, 0], theta, cmap = 'Blues', weights= w, bins = 70, density=True, range= [[-30, 30], [-8, 8]], label ='MCHMC')
    plt.plot(z[::5000, 0], theta[::5000], '.', ms= 1, color = 'tab:blue', label = 'MCHMC')

    #plt.hist2d(z[:, 0], theta, weights= w, bins = 100, density=True, label = 'MCHMC')
    plt.xlim(-30, 30)
    plt.ylim(-8, 8)
    plt.xlabel(r'$z_1$', fontsize = ff)
    plt.ylabel(r'$\theta$', fontsize = ff)

    #### 2d marginal in the gaussianized coordinates ####
    plt.subplot(1, 3, 2)
    plt.title('Gaussianized coordinates', fontsize = ff_title, y= 1.05)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    Gz, Gtheta = gaussianize(z, theta)
    plt.hexbin(Gz[:, 0], Gtheta, C= w, cmap='Blues', gridsize=50, label='MCHMC', reduce_C_function=np.sum)

    GzHMC, GthetaHMC = gaussianize(zHMC, thetaHMC)
    plt.plot(GzHMC[:, 0], GthetaHMC, '.', ms= 7, color = 'tab:orange', alpha = 0.5, label= 'NUTS')

    #level sets
    p_level = np.array([0.6827, 0.9545])
    x_level = np.sqrt(-2 * np.log(1 - p_level))
    phi = np.linspace(0, 2* np.pi, 100)
    for i in range(2):
        plt.plot(x_level[i] * np.cos(phi), x_level[i] * np.sin(phi), lw= 2, color = 'black', alpha= ([1, 0.5])[i])

    plt.xlabel(r'$\widetilde{z}_1$', fontsize = ff)
    plt.ylabel(r'$\widetilde{\theta}$', fontsize = ff)
    plt.xlim(-3, 3)
    plt.ylim(-3, 3)


    #### 1d theta marginal####
    plt.subplot(1, 3, 3)
    plt.title(r'$\theta$-marginal', fontsize = ff_title, y= 1.05)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.hist(thetaHMC, color='tab:orange', density=True, bins = 20, alpha = 0.5, label = 'NUTS')
    plt.hist(theta, weights= w, color='tab:blue', density=True, bins = 20, alpha = 0.5,  label = 'MCHMC')

    t= np.linspace(-10, 10, 100)
    plt.plot(t, norm.pdf(t, scale= 3.0), lw = 3, color= 'black', label = 'exact')

    #xmax = np.min([np.max(thetaHMC), np.max(theta)])
    #plt.xlim(-xmax, xmax)
    #plt.ylim(0, 1)
    plt.yticks([0.00, 0.05, 0.10, 0.15])

    plt.legend(fontsize = 24)
    plt.xlabel(r'$\theta$', fontsize = ff)
    plt.ylabel(r'$p(\theta)$', fontsize = ff)
    plt.tight_layout()
    plt.savefig('submission/funnel.pdf')

    plt.show()




def german_credit():
    folder = 'Tests/data/german_credit/'

    mchmc_data = np.load(folder + 'mchmc.npz')
    X, W = mchmc_data['x'], mchmc_data['w']

    hmc_data = az.from_netcdf(folder + 'inference_data_german_credit_mcmc.nc')
    tuning_steps = np.loadtxt(folder + 'german_credit_warmup_n_steps.txt')

    # hmc_steps = np.array(hmc_data['sample_stats']['n_steps'])
    # print(np.shape(hmc_steps))


    ff, ff_title, ff_ticks = 19, 20, 17
    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks
    plt.figure(figsize=(20, 8))

    hmc_bins = 100
    mchmc_bins = 100

    plt.subplot(1, 3, 1)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    tau = np.concatenate(np.array(hmc_data['posterior']['tau']))
    print(np.average(tau))
    plt.hist(np.log(tau), bins = hmc_bins, density=True, alpha = 0.5, color= 'tab:orange', label = 'NUTS')

    tau = X[:, 0]
    plt.hist(np.log(tau), bins=mchmc_bins, weights= W, density=True, alpha=0.5, color='tab:blue', label='MCHMC')

    plt.xlabel(r'$\log \tau$', fontsize= ff)
    plt.ylabel('Density', fontsize= ff)


    plt.subplot(1, 3, 2)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    lambda1 = np.concatenate(np.array(hmc_data['posterior']['lam'])[:, :, 0])
    plt.hist(np.log(lambda1), bins = hmc_bins, density=True, alpha = 0.5, color= 'tab:orange', label = 'NUTS')

    lambda1 = X[:, 1]
    plt.hist(np.log(lambda1), bins=mchmc_bins, weights= W, density=True, alpha=0.5, color='tab:blue', label='MCHMC')

    plt.xlabel(r'$\log \lambda_1$', fontsize= ff)


    plt.subplot(1, 3, 3)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    beta1 = np.concatenate(np.array(hmc_data['posterior']['beta'])[:, :, 0])
    plt.hist(beta1, bins = hmc_bins, density=True, alpha = 0.5, color= 'tab:orange', label = 'NUTS')

    beta1 = X[:, 2]
    plt.hist(beta1, bins=mchmc_bins, weights= W, density=True, alpha=0.5, color='tab:blue', label='MCHMC')

    plt.xlabel(r'$\beta_1$', fontsize= ff)

    plt.savefig('submission/german_credit_posterior.pdf')
    plt.show()



def stohastic_volatility():
    """Figure 8"""

    from numpyro.examples.datasets import SP500, load_dataset

    _, fetch = load_dataset(SP500, shuffle=False)
    SP500_dates, SP500_returns = fetch()



    ff, ff_title, ff_ticks = 32, 26, 29
    plt.rcParams['xtick.labelsize'] = ff_ticks
    plt.rcParams['ytick.labelsize'] = ff_ticks
    plt.figure(figsize=(20, 8))


    #time series
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())

    #data
    dates = mdates.num2date(mdates.datestr2num(SP500_dates))
    plt.plot(dates, SP500_returns, '.', color= 'black')
    plt.plot([], [], 'o', markersize = 5, color = 'black', label= 'data')

    name= ['MCHMC', 'NUTS']

    for method_index in range(2):
        band = np.load('Tests/data/stochastic_volatility/'+name[method_index]+'_posterior_band.npy')
        plt.plot(dates, band[1], color=tab_colors[method_index])
        plt.fill_between(dates, band[0], band[2], color= tab_colors[method_index], alpha=0.5)
        plt.plot([], [], color = tab_colors[method_index], lw = 5, label = name[method_index]) #for the legend

    plt.legend(fontsize = ff)
    plt.xlabel('time', fontsize = ff)
    plt.ylabel('returns', fontsize = ff)
    plt.ylim(np.min(SP500_returns)-0.1, np.max(SP500_returns)+0.1)
    plt.savefig('submission/StochasticVolatility.pdf')
    plt.show()



def first_nonzero_decimal(x):
    """works for x>0"""
    if np.abs(x) > 1:
        return 0
    else:
        return 1 + first_nonzero_decimal(x*10)


def qspace():
    from scipy.stats import norm
    xmax = 4
    t = np.linspace(-xmax, xmax, 200)

    plt.figure(figsize = (20, 5))

    p = norm.pdf(t)


    plt.subplot(1, 4, 1)
    ax = plt.gca()
    #ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.title('Target')
    plt.plot(t, p, color = 'black')
    plt.xlabel('x')
    plt.yticks([])
    plt.xticks([])
    plt.xlim(-xmax, xmax)
    plt.ylim(0, 0.45)

    plt.subplot(1, 4, 2)
    ax = plt.gca()
    #ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.title('q > 0', color ='tab:blue')
    plt.plot(t, -p, color = 'tab:blue')
    plt.xlabel('x')

    plt.yticks([])
    plt.xticks([])
    plt.xlim(-xmax, xmax)
    plt.ylim(-0.4, 0.05)

    plt.subplot(1, 4, 3)
    ax = plt.gca()
    #ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.title('q = 0', color = 'tab:orange')
    plt.plot(t, np.square(t), color = 'tab:orange')
    plt.yticks([])
    plt.xticks([])

    plt.xlabel('x')
    plt.xlim(-xmax, xmax)
    plt.ylim(0, 9)

    plt.subplot(1, 4, 4)
    ax = plt.gca()
    #ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.title('q < 0', color = 'tab:red')
    plt.plot(t, 1/p, color = 'tab:red')
    plt.xlabel('x')
    plt.yticks([])
    plt.xticks([])

    plt.xlim(-xmax, xmax)
    plt.ylim(0, 50)


    plt.subplots_adjust(wspace=0, hspace=0)

    plt.show()


def epsilon_scaling():
    data = np.load('Tests/data/epsilon_scaling_kappa100.npy')
    dimensions = data[:, 0]
    ess = data[:, 1]
    eps = data[:, 2]
    cf = data[:, 3:].T


    #plt.fill_between(dimensions, low_scan, high_scan, color = 'tab:blue', alpha = 0.1)
    plt.fill_between(dimensions, cf[0], cf[1], color='tab:blue', alpha=0.5)

    plt.plot(dimensions, eps, 'o', color = 'tab:blue')

    res = linregress(np.log(dimensions), np.log(eps))

    plt.title(r'$\epsilon \propto d^{\beta}, \quad \beta = $' + '{0}'.format(np.round(res.slope, 2)))
    plt.plot(dimensions, np.exp(res.intercept) * np.power(dimensions, res.slope), color='black')

    plt.xlabel('dimensions')
    plt.ylabel(r'$\epsilon$')
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig('epsilon_scaling_kappa100.png')

    plt.show()



    plt.plot(dimensions, ess, 'o', color = 'tab:blue')

    res = linregress(np.log(dimensions), np.log(ess))

    plt.title(r'$ESS \propto d^{\beta}, \quad \beta = $' + '{0}'.format(np.round(res.slope, 2)))
    plt.plot(dimensions, np.exp(res.intercept) * np.power(dimensions, res.slope), color='black')

    plt.xlabel('dimensions')
    plt.ylabel(r'ESS')
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig('epsilon_ess_kappa100.png')

    plt.show()



#bounce_frequency_full_bias()
ill_conditioned()
#epsilon_scaling()

#dimension_dependence()

#esh_not_converging()

#BimodalMarginal()
#funnel()
#rosenbrock()
#stohastic_volatility()