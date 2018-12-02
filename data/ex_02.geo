// This code was created by pygmsh v4.3.6.
SetFactory("OpenCASCADE");
Mesh.CharacteristicLengthMin = 0.1;
Mesh.CharacteristicLengthMax = 0.1;
s0 = news;
Rectangle(s0) = {-1.0, -1.0, 0.0, 2.0, 2.0};
s1 = news;
Disk(s1) = {-1.2, 0.0, 0.0, 0.5};
s2 = news;
Disk(s2) = {1.2, 0.0, 0.0, 0.5};
bo1[] = BooleanUnion{ Surface{s0}; Delete; } { Surface{s1};Surface{s2}; Delete;};
s3 = news;
Disk(s3) = {0.0, -0.9, 0.0, 0.5};
s4 = news;
Disk(s4) = {0.0, 0.9, 0.0, 0.5};
pts_s4[] = PointsOf{Surface{s4};};
Characteristic Length{pts_s4[]} = 0.1;
bo2[] = BooleanDifference{ Surface{bo1[]}; Delete; } { Surface{s3};Surface{s4}; Delete;};
ex1[] = Extrude{0,0,0.3}{Surface{bo2[]};};