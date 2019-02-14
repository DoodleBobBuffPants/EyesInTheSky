
[auimds, auimdsValidation, unauimdsValidation] = imageAugmenter();

net = alexnet;
layersTransfer = net.Layers(1:end-3);
numClasses = 2;

layers = [
    layersTransfer
    fullyConnectedLayer(numClasses,'WeightLearnRateFactor',50,'BiasLearnRateFactor',30)
    softmaxLayer
    classificationLayer
 ];

options = trainingOptions('sgdm', ...
    'MiniBatchSize',168, ...
    'MaxEpochs',9, ...
    'InitialLearnRate',5e-4, ...
    'Shuffle','every-epoch', ...
    'ValidationData',auimdsValidation, ...
    'ValidationFrequency',3, ...
    'Verbose',false, ...
    'Plots','training-progress');

netTransfer = trainNetwork(auimds,layers,options);

[YPred,scores] = classify(netTransfer,auimdsValidation);

YValidation = unauimdsValidation.Labels;
accuracy = mean(YPred == YValidation);


save carNet;


figure
for i = 1:14
    subplot(4,4,i)
    I = readimage(unauimdsValidation,i);
    imshow(I)
    label = scores(i);
    disp(scores(i));
    title(string(label));
end



