import numpy as np
import jax.numpy as jnp
import jax
import matplotlib.pyplot as plt
import pandas as pd
import ESH
import myHMC
from benchmark_targets import *

from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage


### to get movies of the trajectories ###


def movie(time, X, duration):
    # get the trajectory

    fig, ax = plt.subplots()

    # background
    num = 100
    lim = 5.0
    x = np.linspace(-lim, lim, num)
    y = np.linspace(-lim, lim, num)
    xmesh, ymesh = np.meshgrid(x, y)
    condition_number = 100.0
    zmesh = np.exp(- 0.5 * (np.square(xmesh) * np.sqrt(condition_number)  + np.square(ymesh) /np.sqrt(condition_number)))
    ax.contourf(xmesh, ymesh, zmesh, cmap= 'cividis')

    # ax.colorbar()

    # method to get frames
    def make_frame(t):
        mask = time < t / duration
        ax.plot(X[mask, 0], X[mask, -1], '.', color='red')
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        # returning numpy image
        return mplfig_to_npimage(fig)

    # creating animation
    animation = VideoClip(make_frame, duration=duration)

    # displaying animation with auto play and looping
    #animation.ipython_display(fps=30, loop=True, autoplay=True)
    animation.write_gif('HMC.gif', fps=3)



def MCHMC():
    total_time, eps= 60, 1.5
    sampler = ESH.Sampler(target, eps=eps)

    X, W = sampler.sample(x0, 40, total_time, key)

    time = np.arange(len(X))
    return time / time[-1], X


def samples():
    steps = 40

    #sampler = ESH.Sampler(target, eps=1.5)
    sampler = myHMC.Sampler(target, eps=0.1)

    X = sampler.sample(x0, steps, 1.5, key)

    time = np.arange(len(X))
    return time / time[-1], X


target= IllConditionedGaussian(50, 100.0)

key = jax.random.PRNGKey(0)
np.random.seed(1)
x0 = np.random.normal(size= target.d)*2

T, X = samples()
movie(T, X, 10)