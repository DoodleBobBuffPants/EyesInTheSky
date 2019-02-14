function[auimds, augimdsValidation, imdsValidation] = imageAugmenter()

augmenter = imageDataAugmenter('RandXReflection', true, 'RandYReflection', true, ...
    'RandRotation',[0 360], 'RandScale',[0.5 1.5],...
    'RandXTranslation', [-30 30], 'RandYTranslation', [-30 30]); % translation in pixels

imds = imageDatastore('data', ...
    'IncludeSubfolders',true, ...
    'LabelSource','foldernames');

[imdsTrain,imdsValidation] = splitEachLabel(imds,0.8, 'randomized');
imageSize = [227 227 3]; % size required by alexnet
auimds = augmentedImageDatastore(imageSize,imdsTrain,'DataAugmentation',augmenter);
augimdsValidation = augmentedImageDatastore(imageSize,imdsValidation);

end
