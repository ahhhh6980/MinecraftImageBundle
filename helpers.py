import colorsys, cv2, os, numpy as np
script_dir = os.getcwd()

def compute_item_color(img, m, fname):
    img_channels = np.array([*cv2.split(cv2.resize(img,(18,18)))])
    img_channels = np.where(img_channels[3] == 0, 0, img_channels)
    colors = []
    for channel in img_channels[:3]:
        # Turn into 9 3x3 regions
        region = channel[4:-4, 4:-4]
        # Remove low frequency components
        frequency = np.fft.fft2(region)
        frequency = np.where(np.abs(frequency) < 6*6*m, complex(0), frequency)
        reduced_img = np.fft.ifft2(frequency).real.astype(np.uint8)
        # Return averaged regions
        region = reduced_img.real.astype(np.uint8)
        quant = 0
        for y in range(10):
            for x in range(10):
                quant += region[y][x]
        colors.append(int(quant / 100))
    return colors

def generate_palette(palette, m):
    colors = []

    # Go through every image and generate a 3x3 grid
    #   that represents the color at the center, and the color
    #   at its edges, this is so that we can approximate the
    #   change in color from one pixel to another with a better item
    palette_dir = script_dir+'/palettes/'+palette
    for image in os.listdir(palette_dir):
        item_name = image.split(".")[0]
        img_dir = palette_dir+"/"+image

        color = compute_item_color(cv2.imread(img_dir, cv2.IMREAD_UNCHANGED), m, item_name)
        colors.append([color, item_name])

    return colors

def bad_color_distance(c1, c2):
    c1 = np.abs(c1)
    c2 = np.abs(c2)
    dc = c2 - c1
    r = (c1[2] + c2[2]) / 2
    dr = ((2 + (r / 256)) * dc[2] * dc[2])
    dg = (4 * dc[1] * dc[1])
    db = ((2 + ((255 - r) / 256)) * dc[0] * dc[0])
    d_color = np.sqrt(db + dg + dr)
    return d_color

def compute_approx_color(color, palette, mode=0):
    min = 100000000
    found_color = []
    for colors in palette:
        dist = bad_color_distance(color, colors[0])
        if dist < min: 
            min = dist
            if mode:    found_color = colors[1]
            else:    found_color = colors[0]
    return found_color

def get_gamut_range(palette):
    minc = np.array([260,260,260])
    maxc = np.array([-1,-1,-1])
    for e in palette:
        color = e[0]
        for i in range(3):
            c = color[i]
            if c > maxc[i]: maxc[i] = c
            if c < minc[i]: minc[i] = c
    return [minc, maxc]

def floyd_steinberg_dithering(img, palette, cutoff):
    h,w,d = img.shape
    new_img = img.copy()
    r = get_gamut_range(palette)
    new_img = ((new_img / 255) * (min(r[1]) - max(r[0]))) + max(r[0])
    for y in range(h):
        for x in range(w):
            old_pixel = np.array(new_img[y][x])
            new_pixel = compute_approx_color(old_pixel, palette, 0)
            new_img[y][x] = new_pixel
            quant_error = (old_pixel - new_pixel) 
            if (quant_error.std() > cutoff): quant_error = quant_error / 2
            if x < 1 or x > w-2 or y > h-2: continue
            new_img[y  ][x+1] = (new_img[y  ][x+1] + (quant_error * 7/16))
            new_img[y+1][x  ] = (new_img[y+1][x  ] + (quant_error * 5/16))
            new_img[y+1][x-1] = (new_img[y+1][x-1] + (quant_error * 3/16))
            new_img[y+1][x+1] = (new_img[y+1][x+1] + (quant_error * 1/16))
    return new_img