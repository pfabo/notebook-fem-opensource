Merge "elektroda_03.brep";


// Physical Line("e1") = {1,2,3,4,5,6};
Physical Line("e1") = {2,3,4,5,6};

// Physical Line("e2") = {12,13,14,15,16,17};
Physical Line("e2") = {12,13,14,15,16};

//Physical Line("ex") = { 7,8,9,10,11};

Physical Line("ex") = { 7,8,9,10,11,18};

Line Loop(1) = {2,3,4,5,6,7,8,9,10,11,12,13,14,15,16, 18};
Plane Surface(2) = {1};
Physical Surface("air") = {2};
