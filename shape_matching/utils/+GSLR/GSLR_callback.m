function [X, P, k] = GSLR_callback(A, B, X_init, max_iters, need_robust, HTS_multiplier)
    %----- solve the GSLR problem XA = B with unknown assignment, A, B are of shapes dim * n 
    m = size(A, 2);  n = size(B, 2);
    P = zeros(m, n);  X_prev = X_init;  X = X_init;
    k = min(m, n);

    for iter = 1:max_iters
        fprintf('SLR iter: %d, k is %d \n', iter, k);
        % pre-processing to update k and P
        cost_mat = zeros(m, n);
        for i = 1:m
            for j = 1:n
                cost_mat(i, j) = vecnorm(X * A(:, i) - B(:, j));
            end
        end

        % update k and P
        P = GSLR.kLAP(cost_mat, min(m, n));
        if need_robust
            [r, c] = find(P);
            k = min(k, GSLR.Huber_type_skip(X * A(:, r), B(:, c), HTS_multiplier));
            P = GSLR.kLAP(cost_mat, k);
        end
        
        % update C
        [r, c] = find(P);
        X = GSLR.solve_ls(A(:, r), B(:, c));
        
        % convergence check
        if norm(X - X_prev, 'fro') <= 1e-5
            fprintf('SLR converged in %d iterations\n', iter);
            break;
        else
            X_prev = X;
        end 
    end
    
end
