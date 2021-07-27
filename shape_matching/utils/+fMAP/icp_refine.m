function [C, matches] = icp_refine(src, dst, P_init, max_iter)
%     C_prev = C_init;
%     C = C_init;
    C_prev = eye(size(src, 2));
    matches = P_init;

    for k=1:max_iter
         % update C   
        [u, ~, v] = svd(src(matches, :)' * dst);
        C = v * u';
        
         % update matches
        matches = knnsearch((C *src')', dst); %  finds the nearest neighbor in (C * L1') for each query point in L2  
       
        % convergence check
         if norm(C_prev - C, 'fro') < 1e-5
             fprintf('\nICP converges in %d iterations\n', k); 
             break;
        else
            C_prev = C;
         end
    end
end

% 
% function [C, matches] = icp_refine(src, dst, C_init, max_iter)
%     C_prev = C_init;
%     C = C_init;
%     
%     for k=1:max_iter
%         % update matches
%         matches = knnsearch(dst', (C * src)');  %  finds the nearest neighbor in dst for each query point in (C * src)'
%         
%         % update C
%         [u, ~, v] = svd(src * dst(:, matches)');
%         C = v * u';
%             
%         % convergence check
%         if norm(C_prev - C, 'fro') < 1e-5
%             fprintf('ICP converges in %d iterations', k);
%             break;
%         else
%             C_prev = C;
%         end
%     end
% end




