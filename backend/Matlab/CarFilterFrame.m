classdef CarFilterFrame < handle
    properties (SetAccess = public)
        % flags for if we are still reliably tracking the car
        isDetected = true;
        isLost = false;

        % neural network
        net;

        % stuff in initial set up
        obj;
        filterParams;
        carTrack;

        % originally in while loop
        mask;
        centroids;
        bboxes;

        frame;
        framenumber;
    end

    methods 
        function CF = CarFilterFrame();
            CF.obj = setupSysObjs(); % objects for IO, object detection
            carNet = load("carNet.mat"); % load network
            CF.net = carNet.netTransfer;
            
            CF.filterParams = getDefaultParams(); %params for Kalman Filter
            CF.carTrack = createFirstTrack(CF.filterParams); %Setup initial car location

            CF.framenumber=0;
        end

        function pixelCoords = run(CF, frame);
            % MAIN PROGRAM

            % Detect moving objects, and track them across video frames.
            % CF.frame = readFrame(CF);
            CF.frame = imread(frame);
            [CF.centroids, CF.bboxes, CF.mask] = detectObjects(CF, CF.frame);
            CF.framenumber = CF.framenumber + 1;
            % disp([CF.framenumber])

            predictTracks(CF);
            [assignments, unassignedDetections, costs] = detectionToTrackAssignment(CF, CF.centroids);
            
            % update car tracking state
            CF.carTrack.age = CF.carTrack.age + 1;
            CF.isDetected = ~isempty(assignments);
                
            if ~CF.isDetected && isempty(unassignedDetections)
                % Nothing detected
                % Update given not detected in this frame
                CF.carTrack.consecutiveInvisibleCount = ...
                    CF.carTrack.consecutiveInvisibleCount + 1;

                % Determine if we have lost the car based on how long its been invisible for
                % try to keep track of car if we cannot see it because it is stationary.
                timeThresh = 30;
                if CF.carTrack.consecutiveInvisibleCount >= timeThresh
                    CF.isLost = true;
                end
            else
                
                if CF.isDetected % Able to assume it is the car

                    % detected something
                
                    % Update track if was detected in previous and current frame
                    detectionIdx = assignments(1, 2);       % find car's detection
                    centroid = CF.centroids(detectionIdx, :);  % find assoc. center
                    bbox = CF.bboxes(detectionIdx, :);         % find assoc. bbox

                    % Limit growth of bbox
                    growthRate = 1.1;
                    maxWidth = growthRate * CF.carTrack.bbox(3);
                    maxHeight = growthRate * CF.carTrack.bbox(4);
                    if bbox(3)>maxWidth
                       bbox(3) = maxWidth;
                    end
                    if bbox(4)>maxHeight
                       bbox(4) = maxHeight;
                    end
                    
                    % Correct the object's location using the new detection.
                    correct(CF.carTrack.kalmanFilter, centroid);
                    % Update the bbox location
                    CF.carTrack.bbox = bbox;

                    % Update visibility
                    CF.carTrack.totalVisibleCount = CF.carTrack.totalVisibleCount + 1;
                    CF.carTrack.consecutiveInvisibleCount = 0;
                    CF.isLost = false;
                else
                    % Try to associate a blob with the car
                    % Get current detected blob info
                    CF.centroids = centroids(unassignedDetections, :);
                    CF.bboxes = bboxes(unassignedDetections, :);
                    % Try to find the car in the detected objects by looking for
                    %   lowest valid cost
                    bestCost = 9999999;
                    bestIndex = -1;
                    for i = 1:size(CF.centroids, 1)
                        centroid = CF.centroids(i,:);
                        bbox = CF.bboxes(i, :);

                        % Decide if car or trash
                        % Get image in just this bbox to pass to classifier
                        cropBbox = bbox;
                        cropBbox(3) = cropBbox(3) + 20;
                        cropBbox(4) = cropBbox(4) + 20;
                        
                        croppedObj = imcrop(CF.frame, cropBbox);
                        toClassify = imresize(croppedObj, [227 227]);
                        %Classify
                        [~, scores] = classify(CF.net, toClassify);
                        isTrash = (scores(1) < 0.6);
                        % Must be car & better than current best cost
                        % If not lost and not detected, need low cost
                        costThresh = 100;
                        if (~isTrash && (costs(1,i) < bestCost) && ...
                                (CF.isLost || (costs(1,i) < costThresh)))
                            bestCost = costs(1,i);
                            bestIndex = i;
                        end
                    end
                    %If we found a car
                    if ~(-1 == bestIndex)
                        % Create a Kalman filter object for the new car
                        filterParams = getDefaultParams();
                        kalmanFilter = configureKalmanFilter(filterParams.motionModel, ...
                            centroid, filterParams.initError, filterParams.motionNoise,...
                            filterParams.measurementNoise);

                        % If we were lost, create a new track.
                        if CF.isLost
                            CF.carTrack = struct(...
                                'id', "Car", ...
                                'bbox', bbox, ...
                                'kalmanFilter', kalmanFilter, ...
                                'age', 1, ...
                                'totalVisibleCount', 1, ...
                                'consecutiveInvisibleCount', 0);
                        %if not lost, update the current track
                        else
                            CF.carTrack.kalmanFilter = kalmanFilter;
                            CF.carTrack.consecutiveInvisibleCount = 0;                        
                        end
                        CF.isLost = false;
                    end
                end
            end
            displayTrackingResults(CF);
            pixelCoords = CF.centroids;
        end

        %DETECTION
        %Detect items in current frame
        function [centroids, bboxes, mask] = detectObjects(CF, frame)
            % Detect foreground.
            mask = CF.obj.detector.step(frame);
            % Apply morphological operations to remove noise and fill in holes.
            mask = imopen(mask, strel('rectangle', [3,3]));
            mask = imclose(mask, strel('rectangle', [15, 15]));
            mask = imfill(mask, 'holes');
            % Perform blob analysis to find connected components.
            [~, centroids, bboxes] = CF.obj.blobAnalyser.step(mask);
        end

        % TRACKING FUNCTIONS
        % predict next location
        function predictTracks(CF)
            bbox = CF.carTrack.bbox;

            % Predict the current location of the track.
            predictedCentroid = predict(CF.carTrack.kalmanFilter);
            
            % Shift the bounding box so that its center is at the predicted location.
            predictedCentroid = int32(predictedCentroid) - int32(bbox(3:4)) / 2;
            CF.carTrack.bbox = [predictedCentroid, bbox(3:4)];
        end
        %Associate existing tracked objects with detected objects
        function [assignments, unassignedDetections, costs] = ...
                detectionToTrackAssignment(CF, centroids)
            
            nDetections = size(centroids, 1);

            %Compute the cost of assigning each detection to each track.
            %cost function = distance from previous location
            costs = zeros(1, nDetections);
            costs(1, :) = distance(CF.carTrack.kalmanFilter, centroids);

            % Modify cost of anything that is trash, if we don't know where the
            % car is (too slow to check constantly)
            if ~CF.isDetected || CF.isLost
                for j = 1:size(centroids, 1)
                    bbox = CF.bboxes(j, :);
                    %Decide if car or trash
                    %Get image in just this bbox (with some cushioning) to pass to classifier
                    cropBbox = bbox;
                    cropBbox(3) = cropBbox(3) + 50;
                    cropBbox(4) = cropBbox(4) + 50;
                    croppedObj = imcrop(CF.frame, cropBbox);
                    toClassify = imresize(croppedObj, [227 227]);
                    %Classify
                    [YPred, scores] = classify(CF.net, toClassify);
                    isTrash = strcmp(char(YPred),"trash");
                    disp(scores);
                    if isTrash
                        %penalise for not being a car
                        costs(1,j) = costs(1,j) + (scores(2) * 100);
                    else
                        %reward for being a car
                        costs(1,j) = costs(1,j) - (scores(1) * 100);
                    end
                end
            end
            
            % cost to assign detection as nothing
            costOfNonAssignment = 200;
            [assignments, ~, unassignedDetections] = ...
                assignDetectionsToTracks(costs, costOfNonAssignment);
        end

        % display results as final output
        % TODO DEMO ONLY
        function displayTrackingResults(CF)
            % Convert the frame and the mask to uint8 RGB.
            CF.frame = im2uint8(CF.frame);
            CF.mask = uint8(repmat(CF.mask, [1, 1, 3])) .* 255;

            % min to display on screen
            minVisibleCount = 8;
            if ~CF.isLost
                % Only display tracks that have been visible for more than
                % a minimum number of frames.
                reliableTrack = CF.carTrack.totalVisibleCount > minVisibleCount;

                % Display the objects. If an object has not been detected
                % in this frame, display its predicted bounding box.
                if reliableTrack
                    % Create labels: id and if predicted or detected.
                    labels = cellstr(CF.carTrack.id');
                    isPredicted = CF.carTrack.consecutiveInvisibleCount > 0;
                    if isPredicted
                        labels = strcat(labels, cellstr(" (Predicted)"));
                    end

                    % Draw the objects on the frame.
                    CF.frame = insertObjectAnnotation(CF.frame, 'rectangle', ...
                        CF.carTrack.bbox, labels);

                    % Draw the objects on the mask.
                    CF.mask = insertObjectAnnotation(CF.mask, 'rectangle', ...
                        CF.carTrack.bbox, labels);
                end
            end

            % Display the mask and the frame.
            CF.obj.maskPlayer.step(CF.mask);
            CF.obj.videoPlayer.step(CF.frame);
        end
    end
end


%KALMAN FILTER FUNCTIONS
%Default parameters for setup
function filterParams = getDefaultParams
    %CV prevents prediction from flying off as much
    filterParams.motionModel = 'ConstantVelocity';
    filterParams.initError = ones(1, 2); %error in first location
    %noise for position, velocity
    filterParams.motionNoise = [25, 10];
    %Estimated inaccuracy in measuring
    filterParams.measurementNoise = 1250;
    %theshold for detecting object: large may miss, small v noisy
    filterParams.segmentationThreshold = 0.05;
end

% create track for initial object
function carTrack = createFirstTrack(filterParams)
    % At start, car will not be detected. Need to classify detections
    % later.
    startLoc = [0,0];
    bbox = [startLoc,10,10]; % bbox format: center, width, height
    filterParams.initError = ones(1,2);

    % Create a Kalman filter object.
    kalmanFilter = configureKalmanFilter(filterParams.motionModel, ...
        startLoc, filterParams.initError, filterParams.motionNoise,...
        filterParams.measurementNoise);

    % Create a new track.
    carTrack = struct(...
        'id', "Car", ...
        'bbox', bbox, ...
        'kalmanFilter', kalmanFilter, ...
        'age', 24, ...  % larger to encourage this track to be preserved
        'totalVisibleCount', 24, ... % ditto
        'consecutiveInvisibleCount', 0);
end

%IO FUNCTIONS
%Setup IO
function obj = setupSysObjs()
    % Initialize Video I/O
    %file setup
    % addpath(strcat(pwd,'/TrainingData'));
    % Create a video file reader.
    %Training data reader. Comment if reading from drone.
    % obj.reader = vision.VideoFileReader('droneData2.mp4');
    
    %DEMO ONLY
    % Create two video players, one to display the video,
    % and one to display the foreground mask.
    obj.maskPlayer = vision.VideoPlayer('Position', [740, 400, 700, 400]);
    obj.videoPlayer = vision.VideoPlayer('Position', [20, 400, 700, 400]);

    %split moving objects into moving(1) and stationary(0)
    obj.detector = vision.ForegroundDetector('NumGaussians', 5, ...
        'NumTrainingFrames', 30, 'MinimumBackgroundRatio', 0.5);

    %System to detect properties of moving objects
    obj.blobAnalyser = vision.BlobAnalysis('BoundingBoxOutputPort', true, ...
        'AreaOutputPort', true, 'CentroidOutputPort', true, ...
        'MinimumBlobArea', 2500, 'MaximumBlobArea', 10000);
end

%advance video feed
function frame = readFrame(CF)
    %Version for demos: requires object.reader
    frame = obj.reader.step();
    %Version for use on drone: disable object.reader
    % frame = imread('../frame.jpg');
end