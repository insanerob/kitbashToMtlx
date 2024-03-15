# kitbashToMTLX
Houdini - Python Converts Kitbash Cargo principled Materials to MTLX Materials for use in Karma XPU

## Setup
### Add to Shelf
Right-click on the shelf and then New Tool
Options - set name and label, I call mine KB3D2MTLX
Script - Make sure the language is python and then paste in the context of the .py in the repo
.. apply, accept.

## Use - in SOPs !

### Convert Materials
Select the /obj node containing your kitbash model and its matnet (after importing it from Kitbash3D Cargo
Click the tool you created (KB3D2MTLX).
It will now look for all principled shaders within that node and convert them to a new node /obj/MTLXmatnet which contains the 3delight materials

### Update Material references
In the kitbash object geo node add a Primivite Wrangle node before the Output node.
Add this vex (example for Mission To Minerva kit), change the KB3D_MTM to your geo name e.g. '/obj/KB3D_HOK/matnet' for Hong Kong kit )

primitive wrangle:
```
@shop_materialpath = replace(s@shop_materialpath , '/obj/KB3D_MTM/matnet' , '/obj/MTLXmatnet') ;
```

## Import OBJ to Stage 

### In Stage (Solaris)
Create a Scene Import node
  Root Object: /obj
  Objects: /obj/KB3D_MTM

The Scene Import node will automatically bring in the materials and assign them

.. let me know if you find any issues

rOb :)
