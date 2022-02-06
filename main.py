# Minecraft Image to bundle tool
# Main File
# (C) 2022 by Jacob (ahhhh6980@gmail.com)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys, os, cv2, shutil, colorsys, time, numpy as np
script_dir = os.getcwd()

def compute_item_color(img):
    img_channels = np.array([*cv2.split(cv2.resize(img,(18,18)))])
    colors = [[[],[],[]],
              [[],[],[]],
              [[],[],[]]]
    for channel in img_channels:
        # Turn into 9 3x3 regions
        regions = channel.reshape(3, 6, -1, 6).swapaxes(1,2).reshape(-1, 6, 6)
        for i,region in enumerate(regions):
            w = i%3
            h = i//3
            # Remove low frequency components
            frequency = np.fft.fft2(region)
            frequency = np.where(np.abs(frequency) < 6*6*32, complex(0), frequency)
            reduced_img = np.fft.ifft2(frequency).real.astype(np.uint8)
            # Return averaged regions
            colors[h][w].append(int(np.average(np.average(reduced_img))))
    return colors

def generate_palette(palette):
    colors = []

    # Go through
    palette_dir = script_dir+'/palettes/'+palette
    for image in os.listdir(palette_dir):
        item_name = image.split(".")[0]
        img_dir = palette_dir+"/"+image

        color = compute_item_color(cv2.imread(img_dir))
        colors.append([color, item_name])

    return colors

def bgr_to_hsv(bgr):
    rgb = np.array(bgr)
    rgb_f = rgb / 255
    return np.array([*colorsys.hsv_to_rgb(*rgb_f)])

neighbors = True
def region_distance(mat1, mat2):
    approx = 0
    weights = 1 / np.array([[25,12,25],[12,1,12],[25,12,25]])
    for j in range(3):
        for i in range(3):
            color_mat1 = bgr_to_hsv(mat1[j][i])
            color_mat2 = bgr_to_hsv(mat2[j][i])
            color_mat2[2] = (0.3 + color_mat2[2]) / 2
            d_color = color_mat1 - color_mat2
            d_color = sum(d_color * d_color) / 3
            if i == j == 1: approx += d_color
            elif neighbors: approx += d_color * weights[j][i]
    return approx

def floyd_steinberg_dithering(img, palette):
    pass

def compute_approx_color(region, palette):
    min = 10
    color = []
    for colors in palette:
        dist = region_distance(region, colors[0])
        if dist < min: 
            min = dist
            color = colors[0]
    return color

def compute_approx_item(region, palette):
    min = 10
    item = ''
    for colors in palette:
        dist = region_distance(region, colors[0])
        if dist < min: 
            min = dist
            item = colors[1]
    return item

def generate_nbt_data(img, fname, pname, palette, preview=False):
    height, width, channels = img.shape
    palette_dir = script_dir+'/palettes/'+pname
    nbt_data = ''
    if preview:
        visualizer = [[[0]*((width)*16)]*((height)*16)]*3
        visualizer = np.zeros((3, height*16,width*16))
    for j in range(1,height-1):
        for i in range(1,width-1):
            region = img[j-1:j+2, i-1:i+2]
            item_name = compute_approx_item(region, palette)
            if preview:
                item_image = np.array([*cv2.split(cv2.imread(palette_dir+"/"+item_name+".png"))])
                for k in range(3):
                    for r in range(16):
                        for c in range(16):
                            visualizer[k][(16*j):(16*j)+16, (16*i):(16*i)+16] = item_image[k]
            nl = r'{Count:1b,id:"' + item_name + r'"},'
            if j == height-2 and i == width-2: break
            nbt_data += nl
    if preview:   
        visualizer = np.array(visualizer)
        imgnew = cv2.merge(np.array(visualizer))
        cv2.imwrite('output/'+fname+"_preview.png", imgnew)
    return nbt_data

def generate_datapack(fname, pname, size, preview):
    print("Starting "+fname+" at "+size+" using palette '"+pname+"'!")
    size = list(map(int, size.split("x")))

    start = time.time()
    bname = fname.split(".")[0]+str(size[0])+"x"+str(size[1])
    image = cv2.resize(cv2.imread('input/'+fname), (size[0], size[1]))
    #image = ordered_dither(image)

    try:
        os.mkdir(script_dir+"/output")
        print("Generated",script_dir+"/output")
    except: pass

    palette = generate_palette(pname)
    command = 'give @p bundle{Items:[' + generate_nbt_data(image, bname, pname, palette, preview)[:-1] + ']}'

    cDir = script_dir+"/datapacks"
    
    try:
        os.mkdir(cDir)
        print("Generated",cDir)
    except: pass
    
    cDir += "/"+bname
    
    try:
        os.mkdir(cDir)
        print("Generated",cDir)
    except: pass

    with open(cDir+"/"+"pack.mcmeta", "w+") as file:
        file.write(r'{"pack": {"pack_format": 8,"description": "bundle"}}')

    cDir += "/"+"data"
    
    try:
        os.mkdir(cDir)
        print("Generated",cDir)
    except: pass
    
    cDir += "/"+bname
    
    try:
        os.mkdir(cDir)
        print("Generated",cDir)
    except: pass
    cDir += "/functions"
    
    try:
        os.mkdir(cDir)
        print("Generated",cDir)
    except: pass

    with open(cDir+"/"+bname+".mcfunction", "w+") as file:
        file.write(command)

    shutil.make_archive('output/'+bname, 'zip', script_dir+"/datapacks/"+bname)

    end = time.time()
    time_to_run = end - start
    print("Ran in "+str(time_to_run)+" seconds")

def main():
    args = sys.argv[1:]
    fname = 'lobster.png'
    size = '32x32'
    pname = 'other'
    preview = True

    for i,e in enumerate(args):
        if '-f' == e: fname = args[i+1]
        if '-s' == e: size = args[i+1]
        if '-p' == e: pname = args[i+1]
        if '--preview' == e: preview = True

    generate_datapack(fname, pname, size, preview)

if __name__ == "__main__":
    sys.exit(main())
