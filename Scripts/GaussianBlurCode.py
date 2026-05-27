# This script creates a script that applies a Gaussian blur to an image. Very dirty, but it works.
# border condition is not handled.

import numpy as np

print('//inputs')
print('//int2 Coords')
print('//ImageSampler Sampler')


def gkern(l=5, sig=1.):
    """
    creates gaussian kernel with side length `l` and a sigma of `sig`
    """
    ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
    gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
    kernel = np.outer(gauss, gauss)
    return kernel, np.sum(kernel)


# kernel,sum = gkern(5,1)
kernel = np.zeros((10, 10))
sum = 0
for x in range(kernel.shape[0]):
    for y in range(kernel.shape[1]):
        coordx = x-kernel.shape[0]//2
        coordy = y-kernel.shape[1]//2

        kernelWeight = 1-(np.sqrt(coordx**2 + coordy**2)/kernel.shape[0])

        print(f'Result +=  Sampler.read(Sampler.texelCoordsToID(Coords + int2({coordx}, {coordy}))) * {kernelWeight};')
        sum += kernelWeight

print(f'Result /= {sum};')
