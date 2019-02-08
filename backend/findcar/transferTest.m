
[auimds, auimdsValidation, unauimdsValidation] = imageAugmenter();

net = alexnet;
layersTransfer = net.Layers(1:end-3);
numClasses = 2;

layers = [
    layersTransfer
    fullyConnectedLayer(numClasses,'WeightLearnRateFactor',20,'BiasLearnRateFactor',20)
    softmaxLayer
    classificationLayer];

options = trainingOptions('sgdm', ...
    'MiniBatchSize',128, ...
    'MaxEpochs',8, ...
    'InitialLearnRate',1e-4, ...
    'Shuffle','every-epoch', ...
    'ValidationData',auimdsValidation, ...
    'ValidationFrequency',2, ...
    'Verbose',false, ...
    'Plots','training-progress');

netTransfer = trainNetwork(auimds,layers,options);

[YPred,scores] = classify(netTransfer,auimdsValidation);

YValidation = unauimdsValidation.Labels;
accuracy = mean(YPred == YValidation);

idx = randperm(numel(unauimdsValidation.Files),10);
figure
for i = 1:10
    subplot(4,4,i)
    I = readimage(unauimdsValidation,idx(i));
    imshow(I)
    label = YPred(idx(i));
    title(string(label));
end


