# Labyrinth Cube Generator

This generates a multi-level labyrinth that is occluded by a casing that the levels are placed into.  
Any spherical object can be placed at the top corner. The Goal is to navigate the sphere through the labyrinth to the bottom corner by using gravity.   
Multiple Parameters can be adusted:  
* Sphere Size
* Wall and Floor Thickness
* Number of Cells n: n*n\*n cube
* Casing Thickness and Tolerance

## Dependecies
* python: solidpython, numpy
* openscad for STL file generation    

## Usage
      python3 main.py