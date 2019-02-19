function [centroid] = locateCar(carImg, sceneImg)

    carNet = load("carNet.mat").net;
    net = carNet.net;

    [height, width, dim] = size(image);
    
    notFound = true;
    indx = 0;
    old_indx = 0;
    
    while (notFound)
        splitImg = mat2tiles(img, [3,3]);
        [YPred,scores] = classify(carNet,splitImg);
        
        
        old_indx = indx;
        maxScore = 0;
        indx = 0;
        
        for i=1:9
            score = scores(i);
            if score(1) >= maxScore
                indx = i;
            end
        end
        
        if maxScore <= 80.0
            centroid = old_indx;
            notFound = false;
        end
        
        img = splitImg(indx);
        
    end
   
end