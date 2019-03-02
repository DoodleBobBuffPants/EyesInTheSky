

imds = imageDatastore('New folder', ...
    'IncludeSubfolders',true, ...
    'LabelSource','foldernames');

imageSize = [227 227 3]; % size required by alexnet
auimds = augmentedImageDatastore(imageSize,imds);
[YPred,scores] = classify(carNet1,auimds);

figure
for i=1:14
    subplot(4,4,i)
    I = readimage(imds, i);
    imshow(I)
    label = YPred(i);
    title(scores(i));
end
