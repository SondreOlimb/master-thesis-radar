import numpy as np
from . import Utils

def DopplerProcessing(adc_data, window_type_1d=None, axis=1, fft_size=256, isClutterRemoval=False,removeArtifacts=True):
    """Doppler processing of the input data.

    Parameters
    ----------
    adc_data : ndarray
        Input data.
    window_type_1d : str, optional
        Window type for 1D FFT.
    axis : int, optional
        Axis along which to perform the doppler processing.

    Returns
    -------
    ndarray
        Doppler processed data.

    """
   
    if window_type_1d is not None:
        window = np.hanning(adc_data.shape[axis])
        adc_data = adc_data * window
    if isClutterRemoval:
        adc_data = Utils.ClutterRemoval(adc_data, axis=axis)
    fft = np.fft.fft(adc_data, axis=axis,n=fft_size)
    result = np.fft.fftshift(fft , axes=axis)
    result[result == 0] = 1e-10
    
    
    return result