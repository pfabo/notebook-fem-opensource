// This code was created by pygmsh v4.3.6.
SetFactory("OpenCASCADE");
Mesh.CharacteristicLengthMin = 0.1;
Mesh.CharacteristicLengthMax = 0.1;
s6 = news;
Rectangle(s6) = {-1.0, -1.0, 0.0, 2.0, 2.0};
s7 = news;
Disk(s7) = {-1.2, 0.0, 0.0, 0.5};
s8 = news;
Disk(s8) = {1.2, 0.0, 0.0, 0.5};
bo1[] = BooleanUnion{ Surface{s6}; Delete; } { Surface{s7};Surface{s8}; Delete;};
s9 = news;
Disk(s9) = {0.0, -0.9, 0.0, 0.5};
s10 = news;
Disk(s10) = {0.0, 0.9, 0.0, 0.5};
pts_s10[] = PointsOf{Surface{s10};};
Characteristic Length{pts_s10[]} = 0.1;
bo2[] = BooleanDifference{ Surface{bo1[]}; Delete; } { Surface{s9};Surface{s10}; Delete;};
ex1[] = Extrude{0,0,0.8}{Surface{bo2[]};};