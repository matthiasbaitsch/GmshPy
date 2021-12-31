SetFactory("OpenCASCADE");

// Element size
k = 6;
h = 0.5 / 2^k;

// Geometry
Rectangle(1) = {0, 0, 0, 1.5, 1, 0};

// Physical names
Physical Curve("C1") = {1, 2, 4};
Physical Curve("C2") = {1, 3};
Physical Curve("C3") = {2, 3};
Physical Surface("S1") = {1};

// Mesh
MeshSize{:} = h;
Mesh 2;

// Save different versions of the mesh
Save Sprintf("rectangle-%1.0f.msh", k);

