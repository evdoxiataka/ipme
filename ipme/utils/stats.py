from scipy.stats.kde import gaussian_kde
from scipy.interpolate import griddata
from scipy.signal import savgol_filter, unit_impulse
from numpy.linalg import LinAlgError

from .functions import get_finite_samples

import numpy as np
import arviz as az

def kde_support(bw, bin_range=(0,1), n_samples=100, cut=3, clip=(None,None)):
    """
        Establish support for a kernel density estimate.
    """
    kmin, kmax = bin_range[0] - bw * cut, bin_range[1] + bw * cut
    if clip[0] is not None and np.isfinite(clip[0]):
        kmin = max(kmin, clip[0])
    if clip[1] is not None and np.isfinite(clip[1]):
        kmax = max(kmax, clip[1])
    return np.linspace(kmin, kmax, n_samples)

def find_x_range(data):
    samples = data.flatten()
    if ~np.isfinite(samples).all():
        samples = get_finite_samples(samples)
    min=0
    max=0
    if samples.size:
        min = np.amin(samples)
        max = np.amax(samples)
    return (min - 0.1*(max-min),max + 0.1*(max-min))

def kde(samples, filled = False):
    try:
        if len(samples) == 0:
            return dict(x = np.array([]), y = np.array([]))
        samples = samples.flatten()
        if ~np.isfinite(samples).all():
            samples = get_finite_samples(samples)
        kde = gaussian_kde(samples)
        bw = kde.scotts_factor() * samples.std(ddof=1)
        #x = _kde_support(bw, bin_range=(samples.min(),samples.max()), clip=(samples.min(),samples.max()))
        x = kde_support(bw, bin_range=(samples.min(),samples.max()))      
        y = kde(x)
        if filled:
            x = np.append(x, x[-1])
            x = np.insert(x, 0, x[0], axis=0)
            y = np.append(y, 0.0)
            y = np.insert(y, 0, 0.0, axis=0)
        return dict(x = x,y = y)
    except ValueError:
        print("KDE cannot be estimated because {} samples were provided to kde".format(len(samples)))
        return dict(x=np.array([]),y=np.array([])) 
    except LinAlgError as err:
        if 'singular matrix' in str(err):
            print("KDE: singular matrix")
            y = unit_impulse(100,'mid')
            x = np.arange(-50, 50) 
            if filled:
                x=np.append(x,x[-1])
                x=np.insert(x, 0, x[0], axis=0)
                y=np.append(y,0.0)
                y=np.insert(y, 0, 0.0, axis=0)
            return dict(x=x,y=y)
        else:
            raise

def pmf(samples):
    """
        Estimate probability mass function.
    """
    # samples = np.asarray(samples, dtype=np.float64).flatten()
    samples = samples.flatten()
    if ~np.isfinite(samples).all():
        samples = get_finite_samples(samples)
    x = np.sort( np.unique(samples))
    y = np.asarray([ np.count_nonzero(samples == xi) / len(samples) for xi in x])
    return dict(x=x,y=y,y0=np.zeros(len(x)))

def hist(x, density=True, bins=20, range=()):    
    return np.histogram(x, range=range, density=density, bins=bins)

def hpd_area(x, y, credible_interval=0.94, smooth = True):
        """
            Returns the x-,y-coordinates of the highest posterior density area 
            of the predicted values.

            Parameters:
            -----------
                x                   The x-coordinate of the data.
                y                   The predicted values of y-coordinate of the data.
                credible_interval   The credible_interval for the hpd
            Returns:
            --------
                A Tuple (x,y) of the x-,y-coordinates of the hpd area.
        """
        x = np.asarray(x)
        y = np.asarray(y)

        x_shape = x.shape
        y_shape = y.shape

        if 0 in x_shape or 0 in y_shape:
            return (np.array([]),np.array([]))

        if y_shape[-len(x_shape) :] != x_shape:
            msg = "Dimension mismatch for x: {} and y: {}."
            msg += " y-dimensions should be (chain, draw, *x.shape) or"
            msg += " (draw, *x.shape)"
            raise TypeError(msg.format(x_shape, y_shape))

        if len(y_shape[: -len(x_shape)]) > 1:
            new_shape = tuple([-1] + list(x_shape))
            y = y.reshape(new_shape)

        hpd_ = az.hpd(y, credible_interval=credible_interval, circular=False, multimodal=False)

        if smooth:
            x_data = np.linspace(x.min(), x.max(), 200)
            x_data[0] = (x_data[0] + x_data[1]) / 2
            hpd_interp = griddata(x, hpd_, x_data)
            y_data = savgol_filter(hpd_interp, axis=0, window_length=55, polyorder=2)
            return (np.concatenate((x_data, x_data[::-1])),np.concatenate((y_data[:, 0], y_data[:, 1][::-1])))
        else:
            return (np.concatenate((x, x[::-1])),np.concatenate((hpd_[:,0], hpd_[:, 1][::-1])))

def hpd(y, credible_interval=0.94):
    y = np.asarray(y)
    y_shape = y.shape
    if 0 in y_shape:
        return (np.array([]),np.array([]))    
    hpd_ = az.hpd(y, credible_interval=credible_interval, circular=False, multimodal=False)
    if hpd_.ndim == 1:
        hpd_ = np.expand_dims(hpd_, axis=0)
    return (hpd_[:,0],hpd_[:,1])