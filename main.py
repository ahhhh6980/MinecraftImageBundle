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

from helpers import *
import sys, os, cv2, shutil, time, numpy as np
script_dir = os.getcwd()

def generate_nbt_data(img, fname, pname, palette, preview, dithered, limit_magnitude):
    height, width, channels = img.shape
    palette_dir = script_dir+'/palettes/'+pname
    nbt_data = ''
    if preview:
        visualizer = [[[0]*((width)*16)]*((height)*16)]*3
        visualizer = np.zeros((3, height*16,width*16))
    for j in range(1,height-1):
        for i in range(1,width-1):
            region = img[j,i]
            item_name = compute_approx_color(region, palette, 1)
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
        end = "_preview"
        if dithered: end += "_dithered"
        cv2.imwrite('output/'+fname+end+"_"+str(limit_magnitude)+".png", imgnew)
    return nbt_data

def time_func(text, func, *args):
    start = time.time()
    output = func(*args)
    end = time.time()
    print(text, "Finished In", end - start, "Seconds!")
    return output

def generate_datapack(fname, pname, size, preview, dithered, cutoff):
    print("Starting "+fname+" at "+size+" using palette '"+pname+"'!")
    size = list(map(int, size.split("x")))

    start = time.time()
    bname = fname.split(".")[0]+str(size[0])+"x"+str(size[1])
    image = cv2.resize(cv2.imread('input/'+fname), (size[0], size[1]))

    try:
        os.mkdir(script_dir+"/output")
        print("Generated",script_dir+"/output")
    except: pass

    # Used for filtering which colors to use in averaging regions
    limit_magnitude = 24
    palette = time_func( "Palette Gen", generate_palette, pname, limit_magnitude)

    if dithered:
        image = time_func( "Dithering", floyd_steinberg_dithering, image, palette, cutoff)

    command = 'give @p bundle{Items:[' + time_func("Command Gen", generate_nbt_data, image, bname, pname, palette, preview, dithered, limit_magnitude)[:-1] + ']}'
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
    cutoff = '50'
    preview = True
    dithered = False

    for i,e in enumerate(args):
        if '-f' == e: fname = args[i+1]
        if '-s' == e: size = args[i+1]
        if '-p' == e: pname = args[i+1]
        if '--preview' == e: preview = True
        if '--dither' == e: dithered = True
        if '-d' == e:   cutoff = args[i+1]

    cutoff = int(cutoff)
    generate_datapack(fname, pname, size, preview, dithered, cutoff)

if __name__ == "__main__":
    sys.exit(main())
