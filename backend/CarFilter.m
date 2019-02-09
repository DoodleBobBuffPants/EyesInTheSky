function CarFilter()
    % MAIN PROGRAM
    obj = setupSysObjs(); %objects for IO, object detection
    
    filterParams = getDefaultParameters(); %params for Kalman Filter
    carTrack = createFirstTrack(filterParams); %Setup initial car location

    %flag for if we are still reliably tracking the car
    isLost = false;
    
    % Detect moving objects, and track them across video frames.
    while ~isDone(obj.reader) %while video stream exists
        frame = readFrame();
        [centroids, bboxes, mask] = detectObjects(frame); %detect objs in this frame
            %centroids are centers of detected objects, bboxes are bounding
            %boxes, mask is the fore/background split
        predictTracks();
        [assignments, unassignedTracks, unassignedDetections] = ...
            detectionToTrackAssignment();
        
        %update car tracking state
        carTrack.age = carTrack.age + 1;
        if isempty(assignments)
            %Nothing detected
            
            %Update given not detected in this frame
            carTrack.consecutiveInvisibleCount = ...
                carTrack.consecutiveInvisibleCount + 1;

            %Determine if we have lost the car based on how long its been
            %   invisible for. Threshold : 1 second/24 frames

            %TODO experiment with it
            timeThresh = 24;

            if carTrack.consecutiveInvisibleCount >= timeThresh
                isLost = true;
            end
        else
            %detected something
            
            %Update track if was detected in previous and current frame
            detectionIdx = assignments(1, 2);
            centroid = centroids(detectionIdx, :);
            bbox = bboxes(detectionIdx, :);

            % Correct the object's location using the new detection.
            correct(carTrack.kalmanFilter, centroid);

            % Replace predicted bounding box with detected bounding box.
            carTrack.bbox = bbox;

            % Update visibility
            carTrack.totalVisibleCount = carTrack.totalVisibleCount + 1;
            carTrack.consecutiveInvisibleCount = 0;


            %If we had lost the car and have now detected something,
            %   try to associate a blob with the car
            if isLost
                %get current detected blobs
                centroids = centroids(unassignedDetections, :);
                bboxes = bboxes(unassignedDetections, :);
                %Try to find the car in the detected objects
                bestCost = 9999999999;
                bestIndex = -1;
                for i = 1:size(centroids, 1)
                    centroid = centroids(i,:);
                    bbox = bboxes(i, :);

                    %Decide if car or trash
                    %TODO actually detect shit
                    %TODO only pass the part of the image in the box
                    isTrash = false;%detectObj(frame);
                    %todo update to use cost instead of i
                    %todo where are the costs?
                    if (~(isTrash) && (i < bestCost))
                        bestCost = curCost(i);
                        bestIndex = i;
                    end
                end
                if ~(-1 == bestIndex)
                        % Create a Kalman filter object for the new car
                        kalmanFilter = configureKalmanFilter('ConstantVelocity', ...
                            centroid, [200, 50], [100, 25], 100);

                        % Create a new track.
                        carTrack = struct(...
                            'id', "Car", ...
                            'bbox', bbox, ...
                            'kalmanFilter', kalmanFilter, ...
                            'age', 1, ...
                            'totalVisibleCount', 1, ...
                            'consecutiveInvisibleCount', 0);
                end
            end
        end
        
        displayTrackingResults();
    end

    %KALMAN FILTER FUNCTIONS
    %Default parameters for setup
    function filterParams = getDefaultParameters
        %choose from ConstantAcceleration, ConstantVelocity
        %TODO test with car. Each is better in different tests
        filterParams.motionModel = 'ConstantAcceleration';
        %Use position given by detection algorithm
        %TODO link with car detection
        filterParams.initLocation = [0,0]; %temp, configured later
        %error in first location. Small given accuracy of detection
        filterParams.initError = 1E5 * ones(1, 3);
        %noise for position, velocity, acceleration
        filterParams.motionNoise = [25, 10, 1];
        %Estimated inaccuracy in measuring
        filterParams.measurementNoise = 250;
        %theshold for detecting object: large may miss, small v noisy
        filterParams.segmentationThreshold = 0.005;
    end
    %create track for initial object
    function carTrack = createFirstTrack(filterParams)
        %TODO get from detector code
        centroid = [300,300];
        bbox = [0,0,0,0];
        filterParams.initError = 1E2 * ones(1,3);
        %todo get from detector code
        startLoc = centroid;
        % Create a Kalman filter object.
        kalmanFilter = configureKalmanFilter(filterParams.motionModel, ...
            startLoc, filterParams.initError, filterParams.motionNoise,...
            filterParams.measurementNoise);

        % Create a new track.
        carTrack = struct(...
            'id', "Car", ...
            'bbox', bbox, ...
            'kalmanFilter', kalmanFilter, ...
            'age', 72, ...  %larger to encourage this track to be preserved
            'totalVisibleCount', 72, ... %ditto
            'consecutiveInvisibleCount', 0);
    end

    %IO FUNCTIONS
    %Setup IO
    function obj = setupSysObjs()
        % Initialize Video I/O
        % Create objects for reading a video from a file, drawing the tracked
        % objects in each frame, and playing the video.

        %file setup
        addpath(strcat(pwd,'/TrainingData'));
        % Create a video file reader.
        %TODO link to drone video feed
        obj.reader = vision.VideoFileReader('data3.mp4');                   %DATA INPUT DEFINED HERE
        
        %TODO temporary. Remove for final project.
        % Create two video players, one to display the video,
        % and one to display the foreground mask.
        obj.maskPlayer = vision.VideoPlayer('Position', [740, 400, 700, 400]);
        obj.videoPlayer = vision.VideoPlayer('Position', [20, 400, 700, 400]);

        %split moving objects into foreground(1) and background(0) i.e. moving
        %and stationary
        obj.detector = vision.ForegroundDetector('NumGaussians', 3, ...
            'NumTrainingFrames', 40, 'MinimumBackgroundRatio', 0.7);

        %System to detect properties of moving objects
        %TODO mess with params
        obj.blobAnalyser = vision.BlobAnalysis('BoundingBoxOutputPort', true, ...
            'AreaOutputPort', true, 'CentroidOutputPort', true, ...
            'MinimumBlobArea', 100);
    end
    %advance video feed
    function frame = readFrame()
        frame = obj.reader.step();
    end
    
    %DETECTION
    %Detect items in current frame
    function [centroids, bboxes, mask] = detectObjects(frame)
        % Detect foreground.
        mask = obj.detector.step(frame);
        % Apply morphological operations to remove noise and fill in holes.
        mask = imopen(mask, strel('rectangle', [3,3]));
        mask = imclose(mask, strel('rectangle', [15, 15]));
        mask = imfill(mask, 'holes');
        % Perform blob analysis to find connected components.
        [~, centroids, bboxes] = obj.blobAnalyser.step(mask);
    end

    %TRACKING FUNCTIONS
    %predict next location for all known objects
    %TODO reduce to one object: the car
    function predictTracks()
        bbox = carTrack.bbox;

        % Predict the current location of the track.
        predictedCentroid = predict(carTrack.kalmanFilter);

        % Shift the bounding box so that its center is at
        % the predicted location.
        predictedCentroid = int32(predictedCentroid) - int32(bbox(3:4)) / 2;
        carTrack.bbox = [predictedCentroid, bbox(3:4)];
    end
    %Associate existing tracked objects with detected objects
    function [assignments, unassignedTracks, unassignedDetections] = ...
            detectionToTrackAssignment()

        nDetections = size(centroids, 1);

        %Compute the cost of assigning each detection to each track.
        %cost function = distance from previous location
        cost = zeros(1, nDetections);
        cost(1, :) = distance(carTrack.kalmanFilter, centroids);

        % Solve the assignment problem: cost to assign detection as nothing
        costOfNonAssignment = 100;
        [assignments, unassignedTracks, unassignedDetections] = ...
            assignDetectionsToTracks(cost, costOfNonAssignment);
    end

    %display results as final output
    %TODO temporary for demoing this module only.
    function displayTrackingResults()
        % Convert the frame and the mask to uint8 RGB.
        frame = im2uint8(frame);
        mask = uint8(repmat(mask, [1, 1, 3])) .* 255;

        % min to display on screen
        minVisibleCount = 8;
        if ~isLost
            % Noisy detections tend to result in short-lived tracks.
            % Only display tracks that have been visible for more than
            % a minimum number of frames.
            reliableTrack = carTrack.totalVisibleCount > minVisibleCount;

            % Display the objects. If an object has not been detected
            % in this frame, display its predicted bounding box.
            if reliableTrack
                % Create labels: id and if predicted or detected.
                labels = cellstr(carTrack.id);
                isPredicted = carTrack.consecutiveInvisibleCount > 0;
                if isPredicted
                    labels = strcat(labels, cellstr(" (Predicted)"));
                end

                % Draw the objects on the frame.
                frame = insertObjectAnnotation(frame, 'rectangle', ...
                    carTrack.bbox, labels);

                % Draw the objects on the mask.
                mask = insertObjectAnnotation(mask, 'rectangle', ...
                    carTrack.bbox, labels);
            end
        end

        % Display the mask and the frame.
        obj.maskPlayer.step(mask);
        obj.videoPlayer.step(frame);
  end
end