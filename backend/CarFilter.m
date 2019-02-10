function CarFilter()
    % MAIN PROGRAM
    obj = setupSysObjs(); %objects for IO, object detection
    
    filterParams = getDefaultParams(); %params for Kalman Filter
    carTrack = createFirstTrack(filterParams); %Setup initial car location

    %flag for if we are still reliably tracking the car
    isDetected = true;
    isLost = false;
    
    % Detect moving objects, and track them across video frames.
    while ~isDone(obj.reader) %while video stream exists
        frame = readFrame();
        [centroids, bboxes, mask] = detectObjects(frame); %detect objs in this frame

        predictTracks();
        [assignments, unassignedDetections, costs] = detectionToTrackAssignment();
        
        %update car tracking state
        carTrack.age = carTrack.age + 1;
        isDetected = ~isempty(assignments);
        if ~isDetected && isempty(unassignedDetections)
            %Nothing detected
            %Update given not detected in this frame
            carTrack.consecutiveInvisibleCount = ...
                carTrack.consecutiveInvisibleCount + 1;

            %Determine if we have lost the car based on how long its been invisible for
            timeThresh = 30;
            if carTrack.consecutiveInvisibleCount >= timeThresh
                isLost = true;
            end
        else
            %detected something
            if isDetected %if we know it was the car
                %Update track if was detected in previous and current frame
                detectionIdx = assignments(1, 2);       %find car's detection
                centroid = centroids(detectionIdx, :);  %find assoc. center
                bbox = bboxes(detectionIdx, :);         %find assoc. bbox
                % Correct the object's location using the new detection.
                correct(carTrack.kalmanFilter, centroid);
                % Replace predicted bounding box with detected bounding box.
                %TODO slow growth
                carTrack.bbox = bbox;

                % Update visibility
                carTrack.totalVisibleCount = carTrack.totalVisibleCount + 1;
                carTrack.consecutiveInvisibleCount = 0;
                isLost = false;
            else
                %Try to associate a blob with the car
                %Get current detected blob info
                centroids = centroids(unassignedDetections, :);
                bboxes = bboxes(unassignedDetections, :);
                % Try to find the car in the detected objects by looking for
                %   lowest valid cost
                bestCost = 9999999999;
                bestIndex = -1;
                for i = 1:size(centroids, 1)
                    centroid = centroids(i,:);
                    bbox = bboxes(i, :);

                    %Decide if car or trash
                    %Get image in just this bbox to pass to classifier
                    croppedObj = imcrop(frame, bbox);

                    %Classify TODO use actual classifier
                    isTrash = false;%detectObj(croppedObj);
                    
                    % Must be car & better than current best cost
                    % If not lost and not detected, need low cost
                    costThresh = 30;
                    if (~isTrash && (costs(1,i) < bestCost) && ...
                            (isLost || (costs(1,i) < costThresh)))
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
                    if isLost
                        carTrack = struct(...
                            'id', "Car", ...
                            'bbox', bbox, ...
                            'kalmanFilter', kalmanFilter, ...
                            'age', 1, ...
                            'totalVisibleCount', 1, ...
                            'consecutiveInvisibleCount', 0);
                    %if not lost, update the current track
                    else
                        carTrack.kalmanFilter = kalmanFilter;
                        carTrack.consecutiveInvisibleCount = 0;                        
                    end
                    isLost = false;
                end
            end
        end
        displayTrackingResults();
    end

    %KALMAN FILTER FUNCTIONS
    %Default parameters for setup
    function filterParams = getDefaultParams
        %choose from ConstantAcceleration, ConstantVelocity
        %TODO test with car. Each is better in different tests
        filterParams.motionModel = 'ConstantAcceleration';
        %filterParams.initLocation = TODO link with car detection
        filterParams.initError = 1E5 * ones(1, 3); %error in first location
        %noise for position, velocity, acceleration
        filterParams.motionNoise = [25, 10, 1];
        %Estimated inaccuracy in measuring
        filterParams.measurementNoise = 250;
        %theshold for detecting object: large may miss, small v noisy
        filterParams.segmentationThreshold = 0.05;
    end
    %create track for initial object
    function carTrack = createFirstTrack(filterParams)
        %TODO get from detector code
        startLoc = [300,300];
        bbox = [startLoc,50,10]; %bbox format: center, width, height
        filterParams.initError = ones(1,3);

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
        %file setup
        addpath(strcat(pwd,'/TrainingData'));
        % Create a video file reader.
        %TODO link to drone video feed
        obj.reader = vision.VideoFileReader('data1.mp4');                 %DATA INPUT DEFINED HERE
        
        %TODO DEMO ONLY
        % Create two video players, one to display the video,
        % and one to display the foreground mask.
        obj.maskPlayer = vision.VideoPlayer('Position', [740, 400, 700, 400]);
        obj.videoPlayer = vision.VideoPlayer('Position', [20, 400, 700, 400]);

        %split moving objects into moving(1) and stationary(0)
        obj.detector = vision.ForegroundDetector('NumGaussians', 3, ...
            'NumTrainingFrames', 40, 'MinimumBackgroundRatio', 0.7);

        %System to detect properties of moving objects
        
        obj.blobAnalyser = vision.BlobAnalysis('BoundingBoxOutputPort', true, ...
            'AreaOutputPort', true, 'CentroidOutputPort', true, ...
            'MinimumBlobArea', 900);%TODO mess with blob area param
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
    %predict next location
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
    function [assignments, unassignedDetections, costs] = ...
            detectionToTrackAssignment()

        nDetections = size(centroids, 1);

        %Compute the cost of assigning each detection to each track.
        %cost function = distance from previous location
        costs = zeros(1, nDetections);
        costs(1, :) = distance(carTrack.kalmanFilter, centroids);

        % cost to assign detection as nothing high so we try to track car
        costOfNonAssignment = 20;
        [assignments, ~, unassignedDetections] = ...
            assignDetectionsToTracks(costs, costOfNonAssignment);
    end

    %display results as final output
    %TODO DEMO ONLY
    function displayTrackingResults()
        % Convert the frame and the mask to uint8 RGB.
        frame = im2uint8(frame);
        mask = uint8(repmat(mask, [1, 1, 3])) .* 255;

        % min to display on screen
        minVisibleCount = 16;
        if ~isLost
            % Only display tracks that have been visible for more than
            % a minimum number of frames.
            reliableTrack = carTrack.totalVisibleCount > minVisibleCount;

            % Display the objects. If an object has not been detected
            % in this frame, display its predicted bounding box.
            if reliableTrack
                % Create labels: id and if predicted or detected.
                labels = cellstr(carTrack.id');
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