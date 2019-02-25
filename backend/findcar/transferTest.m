
[auimds, auimdsValidation, unauimdsValidation] = imageAugmenter();

net = alexnet;
layersTransfer = net.Layers(1:end-3);
numClasses = 2;

layers = [
    layersTransfer
    fullyConnectedLayer(numClasses,'WeightLearnRateFactor',30,'BiasLearnRateFactor',40)
    softmaxLayer
    classificationLayer
 ];

options = trainingOptions('sgdm', ...
    'MiniBatchSize',750, ...
    'MaxEpochs',12, ...
    'InitialLearnRate',5e-5, ...
    'Shuffle','every-epoch', ...
    'ValidationData',auimdsValidation, ...
    'ValidationFrequency',3, ...
    'Verbose',false, ...
    'Plots','training-progress');

netTransfer = trainNetwork(auimds,layers,options);

[YPred,scores] = classify(netTransfer,auimdsValidation);

YValidation = unauimdsValidation.Labels;
accuracy = mean(YPred == YValidation);

carNet1 = netTransfer;

save carNet1;

%{

figure
for i = 1:14
    subplot(4,4,i)
    I = readimage(unauimdsValidation,i);
    imshow(I)
    label = YPred(i);
    disp(scores(i));
    title(string(label));
end

%}

