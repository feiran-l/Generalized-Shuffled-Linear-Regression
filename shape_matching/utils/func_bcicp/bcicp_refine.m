% 2018-01-10
function [C12, T21, T12] = bcicp_refine(S1, S2, B1, B2, T21_ini, T12_ini, num_iter)

    compute_coverage = @(T) length(unique(T))/length(T);
    T12 = T12_ini; T21 = T21_ini;

    % smooth the map in functional space
    for iter = 1:5
        C12 = B2\B1(T21,:);
        C21 = B1\B2(T12,:);
        T12 = knnsearch(B2*C21', B1);
        T21 = knnsearch(B1*C12', B2);
    end
    
    [T21, T12] = refine_pMap(T21, T12, S1, S2, 4);
    C12_prev = C12; 
    C21_prev = C21;
    
    
    for iter = 1:num_iter
        fprintf('bcicp_refine iter %d \n', iter);
        C12 = B2\B1(T21,:);
        C21 = B1\B2(T12,:);
        % the projection step can be modified/removed
        C12 = C12*mat_projection(C21*C12);
        C21 = C21*mat_projection(C12*C21);
        Y1 = [B1*C12',B1];
        Y2 = [B2, B2*C21'];
        d2 = dist_xy(Y1,Y2); % cost matrix S1 -> S2
        [~,T12] = min(d2,[],2);
        [~,T21] = min(d2',[],2);
        [T21, T12] = refine_pMap(T21, T12, S1, S2, 4);
        
        % bijective ICP
        C1 = B1\B1(T21(T12),:);
        C1 = mat_projection(C1);
        C2 = B2\B2(T12(T21),:);
        C2 = mat_projection(C2);

        Y2 = [B1(T21,:)*C1',B2];
        Y1 = [B1, B2(T12,:)*C2'];
        d2 = dist_xy(Y2,Y1);
        [~,T21] = min(d2,[],2);
        [~,T12] = min(d2',[],2);
        [T21, T12] = refine_pMap(T21,T12,S1,S2,4);
       
        % smooth the complete map: slow if #vtx is large!
        if S1.nv <= 2e3 && S2.nv <= 2e3
            T12 = smooth_complete_pMap(T12,S1,S2,1);
            T21 = smooth_complete_pMap(T21,S2,S1,1);
        end
        
         % convergence check
        if norm(C12_prev - C12, 'fro') <= 1e-5 && norm(C21_prev - C21, 'fro') <= 1e-5
            fprintf('SLR converged in %d iterations\n', iter);
            break;
        else
            C12_prev = C12; 
            C21_prev = C21;
        end 

    end
end

