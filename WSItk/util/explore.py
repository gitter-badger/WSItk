"""
EXPLORE: implements various strategies for "exploring" an image: i.e. scanning an
image with a sliding window at different scales.
"""
__version__ = "0.0.1"
__author__ = 'vlad'
__all__ = ['sliding_window', 'sliding_window_on_regions']

import numpy as np
import numpy.random as rnd 

def sliding_window(image_shape, w_size, start=(0,0), step=(1,1)):
    """Yield sub-images of the given image.

    Parameters
    ----------
    image_shape : tuple (nrows, ncols)
        Image shape (img.shape).
    w_size : tuple (width, height)
        Window size as a pair of width and height values.
    start : tuple (x0, y0)
        Top left corner of the first window. Defaults to (0,0).
    step : tuple (x_step, y_step)
        Step size for the sliding window, as a pair of horizontal
        and vertical steps. Defaults to (1,1).

    Returns
    -------
    sliding_window : generator
        Generator yielding sub-images from the original image.
        Data is not copied, rather a restricted view into the image
        is returned. Any changes to the returned view will be propagated
        to the original image.
    """

    img_h, img_w = image_shape

    if w_size[0] < 2 or w_size[1] < 2:
        raise ValueError('Window size too small.')

    if img_w < start[0] + w_size[0] or img_h < start[1] + w_size[1]:
        raise ValueError('Start position and/or window size out of image.')

    x, y = np.meshgrid(np.arange(start[0], img_w-w_size[0]+1, step[0]),
                       np.arange(start[1], img_h-w_size[1]+1, step[1]))

    top_left_corners = zip(x.reshape((-1,)).tolist(),
                           y.reshape((-1,)).tolist())

    for x0, y0 in top_left_corners:
        x1, y1 = x0 + w_size[0], y0 + w_size[1]
        yield (y0, y1, x0, x1)

## end sliding_window


def sliding_window_on_regions(image_shape, roi, w_size, step=(1,1)):
    """
    Yield sub-images of the given image, restricted to a set of regions of interest (ROI).
    In each ROI, the sliding window is used.

    Parameters
    ----------
    image_shape : tuple (nrows, ncols)
        Image shape (img.shape).
    roi : list
        A list of regions of interest in the image: [(r_min, r_max, c_min, c_max),...]
        with "row min", "row max", "column min" and "column max" coordinates.
    w_size : tuple (width, height)
        Window size as a pair of width and height values.
    step : tuple (x_step, y_step)
        Step size for the sliding window, as a pair of horizontal
        and vertical steps. Defaults to (1,1).

    Returns
    -------
    sliding_window_on_regions : generator
        Generator yielding sub-images from the original image.
        Data is not copied, rather a restricted view into the image
        is returned. Any changes to the returned view will be propagated
        to the original image.
    """

    img_h, img_w = image_shape

    if w_size[0] < 2 or w_size[1] < 2:
        raise ValueError('Window size too small.')

    top_left_corners = []
    for r in roi:
        # the ROI r must be completely inside the image:
        if r[0] < 0 or r[2] < 0 or r[1] >= img_h or r[3] >= img_w:
            continue
        x, y = np.meshgrid(np.arange(r[2], r[3]-w_size[0]+1, step[0]),
                           np.arange(r[0], r[1]-w_size[1]+1, step[1]))
        top_left_corners.extend(zip(x.reshape((-1,)).tolist(),
                                    y.reshape((-1,)).tolist()))

    for x0, y0 in top_left_corners:
        x1, y1 = x0 + w_size[0], y0 + w_size[1]
        yield (y0, y1, x0, x1)

## end sliding_window_on_regions


def random_window(image_shape, w_size, n):
    """Yield randomly placed sub-images of the given image.

    Parameters
    ----------
    image_shape : tuple (nrows, ncols)
        Image shape (img.shape).
    w_size : tuple (width, height)
        Window size as a pair of width and height values.
    n : int
        Number of sub-images to generate. If negative, then each call
        will yield a new sub-image.

    Returns
    -------
    random_window : generator
        Generator yielding sub-images from the original image.
        Data is not copied, rather a restricted view into the image
        is returned. Any changes to the returned view will be propagated
        to the original image.
    """

    img_h, img_w = image_shape

    if w_size[0] < 2 or w_size[1] < 2:
        raise ValueError('Window size too small.')
    if w_size[0] > img_w or w_size[1] > img_h:
        raise StopIteration()
    
    if n < 0:
        while True:
            rs = rnd.random_integers(low=0, high=img_h-w_size[1])
            cs = rnd.random_integers(low=0, high=img_w-w_size[0])
            yield (rs, rs+w_size[1], cs, cs+w_size[0])
    else:
        while n > 0:
            n -= 1
            rs = rnd.random_integers(low=0, high=img_h-w_size[1])
            cs = rnd.random_integers(low=0, high=img_w-w_size[0])
            yield (rs, rs+w_size[1], cs, cs+w_size[0])
            
## end random_window



def random_window_on_regions(image_shape, roi, w_size, n):
    """Yield randomly placed sub-images of the given image.

    Parameters
    ----------
    image_shape : tuple (nrows, ncols)
        Image shape (img.shape).
    roi : list
        A list of regions of interest in the image: [(r_min, r_max, c_min, c_max),...]
        with "row min", "row max", "column min" and "column max" coordinates.
    w_size : tuple (width, height)
        Window size as a pair of width and height values.
    n : int
        Number of sub-images to generate. If negative, then each call
        will yield a new sub-image.

    Returns
    -------
    random_window_on_regions : generator
        Generator yielding sub-images from the original image.
        Data is not copied, rather a restricted view into the image
        is returned. Any changes to the returned view will be propagated
        to the original image.
    """

    img_h, img_w = image_shape

    if w_size[0] < 2 or w_size[1] < 2:
        raise ValueError('Window size too small.')
    
    nr = len(roi)
    if nr == 0:
        raise ValueError('At least one ROI should be given.')

    if w_size[0] > img_w or w_size[1] > img_h:
        raise StopIteration()
    
    # check the ROIs are large enough:
    for r in range(len(roi)):
        if roi[r][0] < 0 or roi[r][1] < 0 or roi[r][2] < 0 or roi[r][3] < 0:
            # unsuitable roi:
            del roi[r]
        if roi[r][0] >= img_h or roi[r][1] >= img_h or roi[r][2] >= img_w or roi[r][3] >= img_w:
            # unsuitable roi:
            del roi[r]
        if roi[r][1] - roi[r][0] <= w_size[1] or roi[r][3] - roi[r][2] <= w_size[0]:
            # unsuitable roi:
            del roi[r]
            
    nr = len(roi)
    if nr == 0:
        raise ValueError('No suitable ROIs found.')
    
    if n < 0:
        while True:
            r = rnd.random_integers(low=0, high=nr-1)   # randomly select a ROI
            rs = rnd.random_integers(low=roi[r][0], high=roi[r][1]-w_size[1])
            cs = rnd.random_integers(low=roi[r][2], high=roi[r][3]-w_size[0])
            yield (rs, rs+w_size[1], cs, cs+w_size[0])
    else:
        while n > 0:
            n -= 1
            r = rnd.random_integers(low=0, high=nr-1)   # randomly select a ROI
            rs = rnd.random_integers(low=roi[r][0], high=roi[r][1]-w_size[1])
            cs = rnd.random_integers(low=roi[r][2], high=roi[r][3]-w_size[0])
            yield (rs, rs+w_size[1], cs, cs+w_size[0])
            
## end random_window_on_regions
