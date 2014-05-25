import sys
import numpy
import numpy.linalg


class BaseImage(object):
    def __init__(self):
        self.points = {}
    
    def add_point(self, name, px, py):
        self.points[name] = px, py
    
    def union_points(self, other):
        d = dict(self.points)
        d.update(other.points)
        return d
    
    def interesect_points(self, other):
        d = {}
        for k in self.points:
            if k in other.points:
                d[k] = other.points[k]
        return d

    def get_images(self):
        return [self]


class Image(BaseImage):
    def __init__(self, filename, width, height):
        super(Image, self).__init__()
        self.filename = filename
        self.width = width
        self.height = height


class CombinedImage(BaseImage):
    def __init__(self, im1, im2):
        super(CombinedImage, self).__init__()
        self.im1 = im1
        self.im2 = im2
        self.points = im1.union_points(im2)
    
    def get_images(self):
        return self.im1.get_images() + self.im2.get_images()


def matrix_sqrt(m):
    ev, evv = numpy.linalg.eig(m)
    d = numpy.diag(numpy.sqrt(ev))
    evvi = numpy.linalg.inv(evv)
    m2 = evv * d * evvi
    return m2

class Montage(object):
    def __init__(self):
        self.images = set()
    
    def add_image(self, image):
        self.images.add(image)
    
    def combine(self, im1, im2):
        common_points = im1.interesect_points(im2)
        
        a_rows = [[], [], []]
        b_rows = [[], [], []]
        for name in common_points:
            a_rows[0].append(im1.points[name][0])
            a_rows[1].append(im1.points[name][1])
            a_rows[2].append(1)
            
            b_rows[0].append(im2.points[name][0])
            b_rows[1].append(im2.points[name][1])
            b_rows[2].append(1)
        
        a = numpy.matrix(a_rows)
        b = numpy.matrix(b_rows)
        
        m = b * numpy.linalg.inv(a)
        m2 = matrix_sqrt(m)
    
        im1.transform = m2
        im2.transform = numpy.linalg.inv(m2)
        
        #print a
        #print b
        #print m
        #print m * a
        #print m * [[0.0], [0.0], [1.0]]
        #print m * [[im1.width], [im1.height], [1.0]]
        #print (m * [[im1.width], [im1.height], [1.0]]) - (m * [[0.0], [0.0], [1.0]])
        
        new_im = CombinedImage(im1, im2)
        
        return new_im
    
    def process_image(self):
        for im1 in self.images:
            for im2 in self.images:
                if im1 == im2:
                    continue
                common_points = im1.interesect_points(im2)
                if len(common_points) >= 3:
                    self.images.remove(im1)
                    self.images.remove(im2)
                    new_im = self.combine(im1, im2)
                    self.images.add(new_im)
                    return True
        return False
    
    def process(self):
        while len(self.images) > 1:
            if not self.process_image():
                raise Exception('Cannot find image pair to combine')
    
    def get_images(self):
        all_images = []
        for im in self.images:
            all_images.extend(im.get_images())
        return all_images


def save_svg(montage, filename):
    image_parts = []
    
    for image in montage.get_images():
        try:
            m = image.transform
            extra = """transform="matrix(%f, %f, %f, %f, %f, %f)" """ % (m[0,0], m[1,0], m[0,1], m[1,1], m[0,2], m[1,2])
        except AttributeError:
            extra = ''
        image_svg = """<image y="0.0" x="0.0" xlink:href="%s" width="%d" height="%d" %s />""" % (image.filename, image.width, image.height, extra)
        image_parts.append(image_svg)
    
    svg = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
    %s
</svg>
""" % '\n    '.join(image_parts)
    with open(filename, 'wt') as f:
        f.write(svg)


def main():
    montage = Montage()
    im1 = Image('test1.jpg', 2592, 1936)
    im1.add_point('a', 2566, 1510)
    im1.add_point('b', 1982, 1397)
    #im1.add_point('c', 2402, 826)
    im1.add_point('d', 1993, 620)
    montage.add_image(im1)
    im2 = Image('test2.jpg', 2592, 1936)
    im2.add_point('a', 610, 1752)
    im2.add_point('b', 33, 1648)
    #im2.add_point('c', 456, 1075)
    im2.add_point('d', 49, 868)
    montage.add_image(im2)
    montage.process()
    save_svg(montage, 'output.svg')


if __name__ == '__main__':
    main()
