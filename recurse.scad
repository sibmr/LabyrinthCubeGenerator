
function ngon(num, r) = 
  [for (i=[0:num-1], a=i*360/num) [ r*cos(a), r*sin(a) ]];

// Area of a triangle with the 3rd vertex in the origin
function triarea(v0, v1) = cross(v0, v1) / 2;

// Area of a polygon using the Shoelace formula
function area(vertices) =
  let (areas = [let (num=len(vertices))
                  for (i=[0:num-1]) 
                    triarea(vertices[i], vertices[(i+1)%num])
               ])
      sum(areas);

// Recursive helper function: Sums all values in a list.
// In this case, sum all partial areas into the final area.
function sum(values,s=0) =
  s == len(values) - 1 ? values[s] : values[s] + sum(values,s+1);


module base(num, r) {
    circle(10);
}

base(10,20);