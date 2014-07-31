import pygame
import numpy
import math

RGB_FORMULA = numpy.array((16, 8, 0))

def vertical(color_tuple, length=255):
    arrays = numpy.array(map(numpy.float32, color_tuple))
    offset = arrays.size / 3 - 1
    difference = length % offset
    if difference != 0:
        length += offset - difference
    
    depth = length / offset    
    surface = pygame.Surface((1, length))
    surface_array = pygame.surfarray.pixels2d(surface)
    
    location = 0
    for x in xrange(offset):
        color = arrays[x]
        offset_color = (arrays[x] - arrays[x + 1]) / depth
        for d in xrange(depth):
            if d + location < length:
                surface_array[0][d + location] = sum(color.astype(numpy.int32) << RGB_FORMULA)
                color -= offset_color
        location += depth
    return surface
        
def horizontal(color_tuple, length=255):
    arrays = numpy.array(map(numpy.float32, color_tuple))
    offset = arrays.size / 3 - 1
    difference = length % offset
    if difference != 0:
        length += offset - difference
    
    depth = length / offset    
    surface = pygame.Surface((length, 1))
    surface_array = pygame.surfarray.pixels2d(surface)
    
    location = 0
    for x in xrange(offset):
        color = arrays[x]
        offset_color = (arrays[x] - arrays[x + 1]) / depth
        for d in xrange(depth):
            if d + location < length:
                surface_array[d + location][0] = sum(color.astype(numpy.int32) << RGB_FORMULA)
                color -= offset_color
        location += depth
    return surface

# in_colors has 1 more argument then in_lengths
def vertical_length(in_colors, in_lengths):
    colors = numpy.array(map(numpy.float32, in_colors))
    lengths = numpy.array(in_lengths)
    
    surface = pygame.Surface((1, sum(lengths)))
    surface_array = pygame.surfarray.pixels2d(surface)
    
    location = 0
    depth = 0
    for length in lengths:
        color = colors[location]
        offset_color = (colors[location] - colors[location + 1]) / length
        for l in xrange(length):
            surface_array[0][l + depth] = sum(color.astype(numpy.int32) << RGB_FORMULA)
            color -= offset_color
        depth += length
        location += 1
    return surface
    
def horizontal_length(in_colors, in_lengths):
    colors = numpy.array(map(numpy.float32, in_colors))
    lengths = numpy.array(in_lengths)
    
    surface = pygame.Surface((sum(lengths), 1))
    surface_array = pygame.surfarray.pixels2d(surface)
    
    location = 0
    depth = 0
    for length in lengths:
        color = colors[location]
        offset_color = (colors[location] - colors[location + 1]) / length
        for l in xrange(length):
            surface_array[l + depth][0] = sum(color.astype(numpy.int32) << RGB_FORMULA)
            color -= offset_color
        depth += length
        location += 1
    return surface

def distance(pointa, pointb):
    a = (pointa[0] - pointb[0]) ** 2
    b = (pointa[1] - pointb[1]) ** 2
    return int(math.sqrt(a + b))
    
def get_index(pyint, pylist):
    length = len(pylist) - 1
    for i in xrange(length):
        if pylist[i] <= pyint < pylist[i + 1]:
            return i
    return None
    
def box(color_tuple, rect, point, depth=None, fill=None):
    colors = numpy.array(map(numpy.float32, color_tuple))
    if fill is None:
        fill = numpy.array(color_tuple[-1])
    else:
        fill = numpy.array(fill)
        
    size = len(color_tuple)
    length = max(rect.size)
    if depth is None:
        depth = int(length / (size - 1))
    color_range = [depth * i for i in xrange(size)]
    
    surface = pygame.Surface(rect.size)
    surface_array = pygame.surfarray.pixels2d(surface)
    
    for w in xrange(rect.w):
        for h in xrange(rect.h):
            dist = distance((w,h), point)
            n = get_index(dist, color_range)
            
            if n is None:
                surface_array[w][h] = sum(fill << RGB_FORMULA)
            else:
                offset_color = (colors[n] - colors[n + 1]) / depth 
                offset_color *= (dist - color_range[n])
                surface_array[w][h] = sum((colors[n] - offset_color).astype(numpy.int32) << RGB_FORMULA)
    
    return surface
    
def box_points(color_tuple, rect, pointlist, depth, fill=None):
    colors = numpy.array(map(numpy.float32, color_tuple))
    if fill is None:
        fill = numpy.array(color_tuple[-1])
    else:
        fill = numpy.array(fill)
        
    size = len(color_tuple)
    length = max(rect.size)
    color_range = [depth * i for i in xrange(size)]
    
    surface = pygame.Surface(rect.size)
    surface_array = pygame.surfarray.pixels2d(surface)
    
    for w in xrange(rect.w):
        for h in xrange(rect.h):
            dist = min([distance((w,h), point) for point in pointlist])
            n = get_index(dist, color_range)
            
            if n is None:
                surface_array[w][h] = sum(fill << RGB_FORMULA)
            else:
                offset_color = (colors[n] - colors[n + 1]) / depth 
                offset_color *= (dist - color_range[n])
                surface_array[w][h] = sum((colors[n] - offset_color).astype(numpy.int32) << RGB_FORMULA)
    
    return surface    
