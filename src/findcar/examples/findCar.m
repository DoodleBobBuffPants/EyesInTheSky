function[centroid] = findCar() 

hBlob = vision.BlobAnalysis('AreaOutputPort',false,'BoundingBoxOutputPort',false, ...
                            'MinimumBlobArea', 2, 'MaximumCount', 1);

                        
img = imread('testimg.JPG');

%img = logical([0 0 0 0 0 0; ...
%               0 1 0 1 1 0; ...
%               0 0 0 1 1 0; ...
%               0 1 1 1 1 0; ...
%               0 0 0 0 0 0]);
    
centroid = hBlob(img);
disp(centroid);

end