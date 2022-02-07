# MinecraftImageBundle
Convert images to mc bundles! :)


pip install -r requirements.txt


example usage:
python main.py -f lobster.png -s 32x32 -p other --preview

-f lobster.png: load file "lobster.png" 
-s 32x32: set bundle size for 32x32 (items)
-p other: operate on the palette "other"
--preview: save a preview of what to expect ingame

other sizes and palettes are available, this even supports texturepacks
just make a collection of the item images and their id's ingame, and make a new folder under "palettes"

![](output/lobster128x128_preview.png)
