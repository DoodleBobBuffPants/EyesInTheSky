
testimg = imread("findcartester.jpg");
newBoxPolygon = locateCar(testimg);
disp(newBoxPolygon);
