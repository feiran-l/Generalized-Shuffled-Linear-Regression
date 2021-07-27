clc; close all; clear;
addpath(genpath('utils/'))
num_eigs = 50;          % LB on source and target shape
num_times = 100;    % time-scale parameter to compute WKS descriptors
para.beta = 1e-1;      % weight for the orientataion term

%% load meshes and pre-processing
mesh1 = MESH.preprocess('david12.off',   'IfComputeLB', true,    'numEigs', num_eigs,    'IfComputeGeoDist', false,    'IfComputeNormals', true);
mesh2 = MESH.preprocess('david13.off',   'IfComputeLB', true,    'numEigs', num_eigs,    'IfComputeGeoDist', false,    'IfComputeNormals', true);                                                         

%% STEP 1: compute the WKS descriptors
evecs1 = mesh1.evecs(:, 1:num_eigs);   evals1 = mesh1.evals(1:num_eigs);
evecs2 = mesh2.evecs(:, 1:num_eigs);   evals2 = mesh2.evals(1:num_eigs);
wks1 = waveKernelSignature(evecs1, evals1, mesh1.A, num_times);  
wks2 = waveKernelSignature(evecs2, evals2, mesh2.A, num_times);  
fprintf('WKS extraction done \n');

%% STEP 2: compute the initial C with the wks and do functional map
C_fmap = compute_fMap_regular_with_orientationOp(mesh1, mesh2, evecs1, evecs2, evals1, evals2, wks1, wks2, 'direct', para);
P_fmap = fMAP.fMap2pMap(evecs1, evecs2, C_fmap);
fprintf('functional map done \n');

%% STEP 3: do GSLR
num_iter = 5;   hse_threshold = 3.5;    need_robust = true;
[C_GSLR, P_GSLR, ~] = GSLR.GSLR_callback(evecs1', evecs2', C_fmap, num_iter, need_robust, hse_threshold);
[r, c] = find(P_GSLR);    P_GSLR = NaN(1, size(P_GSLR, 2));    P_GSLR(c) = r;    P_GSLR = P_GSLR';
P_ICP_tmp = fMAP.fMap2pMap(evecs1, evecs2, C_GSLR);    [row, ~] = find(isnan(P_GSLR));    P_GSLR(row) = P_ICP_tmp(row);  

%% visualization
plotOptions = {'cameraPos', [-30,10]};
MESH.PLOT.visualize_map_colors(mesh2, mesh1, P_GSLR, plotOptions{:});
rotate3d on

   
    


