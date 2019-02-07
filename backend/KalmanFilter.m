function KalmanFilter
    %get and modify params
    param = getDefaultParameters();         % get parameters that work well
    
    %START POSITION
    param.initialLocation = [0, 0];  % location that's not based on an actual detection
    param.initialEstimateError = 100*ones(1,3); % use relatively small values
    
    %MOTION MODEL
    param.motionModel = 'ConstantVelocity'; % switch from ConstantAcceleration to ConstantVelocity
    % After switching motion models, drop noise specification entries
    % corresponding to acceleration.
    param.initialEstimateError = param.initialEstimateError(1:2);
    param.motionNoise          = param.motionNoise(1:2);
    
    %NOISE DETECTION
    %larger value gives more accurate detection but too large will miss
    %   object. May need to dynamically change to keep detection
    param.segmentationThreshold = 0.005; % smaller value resulting in 
                                        %noisy detections
    %changes wrt above. Smaller value for larger threshold.
    %setting to near-0 will use measured value, large value will use
    %   predictions mostly
    param.measurementNoise      = 1250;  % increase the value to compensate
                                          % for the increase in measurement noise
    % vars used for tracking single object
    frame            = [];  % A video frame
    detectedLocation = [];  % The detected location
    trackedLocation  = [];  % The tracked location
    label            = '';  % Label for the ball
    utilities        = createUtilities(param);  % Utilities used to process the video

    trackSingleObject(param); % visualize the results

    %REQUIRED FUNCTS
    function param = getDefaultParameters
      %choose from ConstantAcceleration, ConstantVelocity
      param.motionModel           = 'ConstantAcceleration';
      %either where detected or some estimated position.
      param.initialLocation       = 'Same as first detection';
      %error in first location. Small for first detection, large for stated position
      param.initialEstimateError  = 1E5 * ones(1, 3);
      %noise for acceleration, velocity, position
      param.motionNoise           = [25, 10, 1];
      %Estimated inaccuracy in measuring
      param.measurementNoise      = 25;
      %theshold for detecting object: large may miss, small v noisy
      param.segmentationThreshold = 0.05;
    end

    function frame = readFrame()
      frame = step(utilities.videoReader);
    end

    function showDetections()
      param = getDefaultParameters();
      utilities = createUtilities(param);
      trackedLocation = [];

      idx = 0;
      while ~isDone(utilities.videoReader)
        frame = readFrame();
        detectedLocation = detectObject(frame);
        % Show the detection result for the current video frame.
        annotateTrackedObject();

        % To highlight the effects of the measurement noise, show the detection
        % results for the 40th frame in a separate figure.
        idx = idx + 1;
        if idx == 40
          combinedImage = max(repmat(utilities.foregroundMask, [1,1,3]), frame);
          figure, imshow(combinedImage);
        end
      end % while

      % Close the window which was used to show individual video frame.
      uiscopes.close('All');
    end

    function [detection, isObjectDetected] = detectObject(frame)
      grayImage = rgb2gray(frame);
      utilities.foregroundMask = step(utilities.foregroundDetector, grayImage);
      detection = step(utilities.blobAnalyzer, utilities.foregroundMask);
      if isempty(detection)
        isObjectDetected = false;
      else
        % To simplify the tracking process, only use the first detected object.
        detection = detection(1, :);
        isObjectDetected = true;
      end
    end

    function annotateTrackedObject()
      accumulateResults();
      % Combine the foreground mask with the current video frame in order to
      % show the detection result.
      combinedImage = max(repmat(utilities.foregroundMask, [1,1,3]), frame);

      if ~isempty(trackedLocation)
        shape = 'circle';
        region = trackedLocation;
        region(:, 3) = 5;
        combinedImage = insertObjectAnnotation(combinedImage, shape, ...
          region, {label}, 'Color', 'red');
      end
      step(utilities.videoPlayer, combinedImage);
    end

    function showTrajectory
      % Close the window which was used to show individual video frame.
      uiscopes.close('All');

      % Create a figure to show the processing results for all video frames.
      figure; imshow(utilities.accumulatedImage/2+0.5); hold on;
      plot(utilities.accumulatedDetections(:,1), ...
        utilities.accumulatedDetections(:,2), 'k+');

      if ~isempty(utilities.accumulatedTrackings)
        plot(utilities.accumulatedTrackings(:,1), ...
          utilities.accumulatedTrackings(:,2), 'r-o');
        legend('Detection', 'Tracking');
      end
    end

    function accumulateResults()
      utilities.accumulatedImage      = max(utilities.accumulatedImage, frame);
      utilities.accumulatedDetections ...
        = [utilities.accumulatedDetections; detectedLocation];
      utilities.accumulatedTrackings  ...
        = [utilities.accumulatedTrackings; trackedLocation];
    end

    function loc = computeInitialLocation(param, detectedLocation)
      if strcmp(param.initialLocation, 'Same as first detection')
        loc = detectedLocation;
      else
        loc = param.initialLocation;
      end
    end

    function utilities = createUtilities(param)
      %file setup
      CurDir = pwd;
      addpath(strcat(CurDir,'/TrainingData'));
      % Create System objects for reading video, displaying video, extracting
      % foreground, and analyzing connected components.
      utilities.videoReader = vision.VideoFileReader('/TrainingData/data3.mp4'); %NOTE TRAINING VIDEO SET HERE
      utilities.videoPlayer = vision.VideoPlayer('Position', [100,100,500,400]);
      utilities.foregroundDetector = vision.ForegroundDetector(...
        'NumTrainingFrames', 24, 'InitialVariance', param.segmentationThreshold);
      utilities.blobAnalyzer = vision.BlobAnalysis('AreaOutputPort', false, ...
        'MinimumBlobArea', 70, 'CentroidOutputPort', true);

      utilities.accumulatedImage      = 0;
      utilities.accumulatedDetections = zeros(0, 2);
      utilities.accumulatedTrackings  = zeros(0, 2);
    end

    function trackSingleObject(param)
      % Create utilities used for reading video, detecting moving objects,
      % and displaying the results.
      utilities = createUtilities(param);

      isTrackInitialized = false;
      while ~isDone(utilities.videoReader)
        frame = readFrame();

        % Detect the ball.
        [detectedLocation, isObjectDetected] = detectObject(frame);
        disp(detectedLocation);
        if ~isTrackInitialized
          if isObjectDetected
            % Initialize a track by creating a Kalman filter when the ball is
            % detected for the first time.
            initialLocation = computeInitialLocation(param, detectedLocation);
            kalmanFilter = configureKalmanFilter(param.motionModel, ...
              initialLocation, param.initialEstimateError, ...
              param.motionNoise, param.measurementNoise);

            isTrackInitialized = true;
            trackedLocation = correct(kalmanFilter, detectedLocation);
            label = 'Initial';
          else
            trackedLocation = [];
            label = '';
          end

        else
          % Use the Kalman filter to track the ball.
          if isObjectDetected % The ball was detected.
            % Reduce the measurement noise by calling predict followed by
            % correct.
            predict(kalmanFilter);
            trackedLocation = correct(kalmanFilter, detectedLocation);
            label = 'Corrected';
          else % The ball was missing.
            % Predict the ball's location.
            trackedLocation = predict(kalmanFilter);
            label = 'Predicted';
          end
        end

        annotateTrackedObject();
      end % while

      showTrajectory();
    end
end
