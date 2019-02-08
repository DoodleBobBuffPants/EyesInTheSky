function [Y,Xf,Af] = myNeuralNetworkFunction(X,~,~)
%MYNEURALNETWORKFUNCTION neural network simulation function.
%
% Auto-generated by MATLAB, 07-Feb-2019 12:46:20.
%
% [Y] = myNeuralNetworkFunction(X,~,~) takes these arguments:
%
%   X = 1xTS cell, 1 inputs over TS timesteps
%   Each X{1,ts} = 21xQ matrix, input #1 at timestep ts.
%
% and returns:
%   Y = 1xTS cell of 1 outputs over TS timesteps.
%   Each Y{1,ts} = 3xQ matrix, output #1 at timestep ts.
%
% where Q is number of samples (or series) and TS is the number of timesteps.

%#ok<*RPMT0>

% ===== NEURAL NETWORK CONSTANTS =====

% Input 1
x1_step1.xoffset = [0.01;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0.0005;0.002;0.017;0.002];
x1_step1.gain = [2.08333333333333;2;2;2;2;2;2;2;2;2;2;2;2;2;2;2;3.77358490566038;11.142061281337;3.34448160535117;9.25925925925926;3.125];
x1_step1.ymin = -1;

% Layer 1
b1 = [1.671649315735421526;0.85009067925034065283;-0.98506334255226035701;0.69318758447324468897;-0.46008476942616899352;0.35966790872769627274;0.24945940529240231975;0.88592153239635273998;-1.2318594624239254109;1.4589539862210483268];
IW1_1 = [-0.058376273626524324833 0.55317566085108471619 -0.034359666052284590365 0.22403816760098052563 0.28955862054709452513 0.31980045399663231676 0.54515689888257834461 0.36078223442424300904 0.0094313703947606335881 0.065281365467602714414 0.36674202412950562824 0.24240766395711532688 -0.3193412749075634216 -0.15279885085692604396 0.08580144443735490678 -0.38176556220822221999 -0.040987055796680792186 0.3982056616315737263 -0.41085448806686042378 0.37444077830586397493 -0.45238447739319365137;-0.1307990143837991226 -0.28062916325820658203 0.32173282257171659237 -0.037030551924342652859 0.15346697429427716419 0.37705409566706027391 -0.17401518154712034003 -0.037988178851942534797 -0.27746814180979423314 0.20911569241845495704 -0.18225536353497095998 0.18371898504347111691 0.1845252020519565217 0.24681178411860685284 0.65039599055492858248 0.090102520017309534195 2.3198090965498572302 -0.31798046780704813941 -1.7402017254377135647 0.2074430695859097451 -1.3992464555245835989;0.15342564794433449782 0.5494076015391907708 -0.30019125644886829329 -0.50044419309195664614 0.37910850329830592109 0.49669687852586563714 0.17737601782579087706 -0.084549997527888498539 -0.23186777076141112941 -0.033124737958009090044 0.63248751359928867544 0.33370139961443201493 -0.052793052853676969427 0.29324337939957939581 -0.10132357256472315776 -0.022216583547221155359 0.10118078556339292484 0.52968265727417007671 -0.44431619081302120566 -0.26932244400588967181 0.53061943590979832042;-0.0014432795859681503067 0.18095288410494619891 0.083077864859972441747 0.34212866169176819886 0.13868918148659578615 0.15037853194603811868 0.030188444952691771 0.28121072606327418564 0.10514553178396332522 0.0050935756855226598308 -0.043719909585444013955 0.013097216364406872799 0.5547310065455234307 0.016216687821210998971 -0.66162300648229432909 0.15589957372043239392 -3.1009071970326091972 1.3939110325073067465 1.4056314055283500863 -0.59139783552615199369 1.1894559931527401986;0.12776059400643480224 0.52566138393134564932 -0.67429856587725978123 0.6301959935356351572 0.21587373104998289208 0.13689072788751308063 -0.38435174218757794939 -0.5739785166967743546 0.21735516867955503861 0.006440031683390461982 -0.34959194584154051899 -0.35752997035966888051 -0.43393793287900722655 0.18723275999483479648 -0.16651540099012460128 -0.023678525211781722981 1.7160985149412761874 -0.088052047822799794918 -0.42796963823750966416 0.11123812682895653503 -0.53352856324904862628;0.68735752367075353408 0.063259171911163633584 0.31990469207207650193 0.18286890593963089913 -0.84833545012766087279 -0.28940489406259395366 -0.10124573873155508219 -0.080911739343333413665 0.2507749057754175559 -0.064511664336769011796 -0.18258926935525998658 -0.054728056783721827638 -0.27068184696976610448 -0.35018397902694242685 -0.48860097367559629511 -0.31558033529012674556 -0.25135620422058485568 -0.47660221395231677777 0.21718033325708371861 0.35927458214485552546 -0.10502569113402683565;0.021825115083265091837 0.068336096826457512488 -0.61154718048389056229 -0.27207262293549899779 -0.091366277443762008992 -0.38964373428223209039 -0.05326042388216006146 0.41228041275618182437 -0.17000610185047326794 -0.09736529218657132001 0.15008363995236009836 -0.080435943429458978127 0.23147270396167632378 -0.30330693802195168862 0.47500953662527312105 -0.14889119264546668564 2.5849121148187332864 -0.29594311094986253119 -0.43198305819892834911 0.32904850903402810269 -0.98317641075168693554;0.053000345080362477879 0.30213717333784867458 -0.76489789899789706329 0.27409819636921095576 0.19663740472386764813 0.03719315812330138693 -0.57153497172238909574 -0.41471142786368370148 -0.1544554952551981386 -0.29530900748940136502 0.4281464787601489963 0.56720506124865899267 -0.26499271317422151695 -0.19789900705950036475 -0.3951469839095297365 0.17578065523475444598 0.024263645028558610689 0.70878530979815301816 0.049195068909618271114 0.34196066641059708058 0.27271789228946136108;-0.60185169186046916234 0.20285606521098778487 -0.14701868655716796019 0.39369635820678161586 -0.26839347697725024489 0.6291085637452517032 -0.48601278113076651355 -0.51926224823298616773 0.075307414770540800908 0.80628088315267210096 0.023458602413257912539 0.19062360298245412116 -0.12314708340853931789 0.11961501527793483302 -0.056315374060840174553 0.42781853677148218296 0.43056184598476443526 -0.43678731969224132703 -0.19055443434176844164 0.32891341019130759804 -0.072572299913821011752;0.27339919264024453716 -0.38512489877126110382 -0.92151566857376832065 0.56320088742080631761 0.04631133611806547562 0.31534341270034421667 -0.38756573751530914995 -0.31275602918901856953 -0.56623935444213346901 0.34110663397629203963 0.17840662005597485162 0.32225331082604485866 -0.069697591549242918219 0.13058795471472098293 0.60168249870167800353 0.024267979856786095483 0.43472656905987955289 0.046539432641725289597 0.58433988880610565619 -0.17820860310995126352 0.51335199293488553707];

% Layer 2
b2 = [-0.049301400368678478803;-0.35081343811042342562;1.1822844826247722594];
LW2_1 = [0.33201589335718029172 2.9821949996489567347 0.57683735466727326102 -3.0848176772001028034 0.75853183121873379857 -0.88458009274947935197 1.8770578038406819932 -0.20254079944945180269 -0.1280165070716828557 -1.1131618067525483884;-0.0093070357490120849547 -0.28475452445336141283 0.058327835378563085145 -0.54083352540339413306 0.41597655522731769029 0.79338930933126239342 0.42861649213045049933 1.1324535652495830718 0.88452518066606611313 0.84949646312241811064;0.65803298607112903351 -1.3658136209749325296 -1.0911400858183673002 2.6544515702999760265 -1.7408254217313852141 -0.25128901899125072328 -2.1217990417080772048 0.31609669793889777489 -0.53866113737948784213 -0.78760288512115328441];

% ===== SIMULATION ========

% Format Input Arguments
isCellX = iscell(X);
if ~isCellX
    X = {X};
end

% Dimensions
TS = size(X,2); % timesteps
if ~isempty(X)
    Q = size(X{1},2); % samples/series
else
    Q = 0;
end

% Allocate Outputs
Y = cell(1,TS);

% Time loop
for ts=1:TS
    
    % Input 1
    Xp1 = mapminmax_apply(X{1,ts},x1_step1);
    
    % Layer 1
    a1 = tansig_apply(repmat(b1,1,Q) + IW1_1*Xp1);
    
    % Layer 2
    a2 = softmax_apply(repmat(b2,1,Q) + LW2_1*a1);
    
    % Output 1
    Y{1,ts} = a2;
end

% Final Delay States
Xf = cell(1,0);
Af = cell(2,0);

% Format Output Arguments
if ~isCellX
    Y = cell2mat(Y);
end
end

% ===== MODULE FUNCTIONS ========

% Map Minimum and Maximum Input Processing Function
function y = mapminmax_apply(x,settings)
y = bsxfun(@minus,x,settings.xoffset);
y = bsxfun(@times,y,settings.gain);
y = bsxfun(@plus,y,settings.ymin);
end

% Competitive Soft Transfer Function
function a = softmax_apply(n,~)
if isa(n,'gpuArray')
    a = iSoftmaxApplyGPU(n);
else
    a = iSoftmaxApplyCPU(n);
end
end
function a = iSoftmaxApplyCPU(n)
nmax = max(n,[],1);
n = bsxfun(@minus,n,nmax);
numerator = exp(n);
denominator = sum(numerator,1);
denominator(denominator == 0) = 1;
a = bsxfun(@rdivide,numerator,denominator);
end
function a = iSoftmaxApplyGPU(n)
nmax = max(n,[],1);
numerator = arrayfun(@iSoftmaxApplyGPUHelper1,n,nmax);
denominator = sum(numerator,1);
a = arrayfun(@iSoftmaxApplyGPUHelper2,numerator,denominator);
end
function numerator = iSoftmaxApplyGPUHelper1(n,nmax)
numerator = exp(n - nmax);
end
function a = iSoftmaxApplyGPUHelper2(numerator,denominator)
if (denominator == 0)
    a = numerator;
else
    a = numerator ./ denominator;
end
end

% Sigmoid Symmetric Transfer Function
function a = tansig_apply(n,~)
a = 2 ./ (1 + exp(-2*n)) - 1;
end
