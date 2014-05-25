import sys
import numpy
import pygame
import gc


SCALE_FACTOR = 4


def get_image_data(filename):
    im = pygame.image.load(filename)
    sz = im.get_size()
    im = pygame.transform.scale(im, (sz[0]/SCALE_FACTOR, sz[1]/SCALE_FACTOR))
    im2 = im.convert(8)
    a = pygame.surfarray.array2d(im2)
    hw1 = numpy.hamming(a.shape[0])
    hw2 = numpy.hamming(a.shape[1])
    a = a.transpose()
    a = a*hw1
    a = a.transpose()
    a = a*hw2
    return a


def transform_image(filename, pt):
    im = pygame.image.load(filename)
    sz = im.get_size()
    move_x = pt[0] * SCALE_FACTOR
    if move_x > sz[0] / 2:
        move_x -= sz[0]
    move_y = pt[1] * SCALE_FACTOR
    if move_y > sz[1] / 2:
        move_y -= sz[1]
    print 'Transforming %s to (%d,%d)' % (filename, move_x, move_y)
    new_im = im.copy()
    new_im.blit(im, (-move_x, -move_y))
    pygame.image.save(new_im, filename + '.transform.png')


def main(args):
    pygame.init()

    pygame.sndarray.use_arraytype('numpy')

    filename1 = args[1]
    filename2 = args[2]
    im1 = get_image_data(filename1)
    print 'Loaded: %s' % filename1
    im2 = get_image_data(filename2)
    print 'Loaded: %s' % filename2
    gc.collect()
    out1 = numpy.fft.fft2(im1)
    print 'FFT: %s' % filename1, out1.shape
    del im1
    gc.collect()
    out2 = numpy.fft.fft2(im2)
    print 'FFT: %s' % filename2, out2.shape
    del im2
    gc.collect()
    out1conj = out1.conjugate()
    print 'Conjugated: %s' % filename1, out1conj.shape
    out3 = out1conj * out2
    print 'Combined %s and %s' % (filename1, filename2), out3.shape
    del out1, out2
    gc.collect()
    correl = numpy.fft.ifft2(out3)
    print 'IFFT', correl.shape
    del out3
    gc.collect()
    maxs = correl.argmax()
    maxpt = maxs / correl.shape[1], maxs % correl.shape[1]
    print maxs, correl[maxpt], maxpt, (correl.shape[0] - maxpt[0], correl.shape[1] - maxpt[1])
    transform_image(filename2, maxpt)


if __name__ == '__main__':
    args = sys.argv
    exit(main(args))




# IMG_4106.JPG
# 1078 1584

# IMG_4107.JPG
# 1210 1287

# 132  297
# 66 148

# 371 121
# 742 242

# 1871 90
# 258 180
