function [P] = kLAP(cost_mat, k)
    [m, n] = size(cost_mat);
    
    if min(m, n) == k
        pairs = matchpairs(cost_mat, max(cost_mat(:)));
        P = zeros(size(cost_mat));
        LinIdx = sub2ind(size(P), pairs(:,1), pairs(:,2));          
        P(LinIdx) = 1;
      
    else
        if m > n
            cost_mat = cost_mat';
            trans_flag = true;
            [n, m] = deal(m, n);
        else
            trans_flag = false;
        end
        % prepare the extended cost_mat
        diagvec = zeros(1,m-k);
        for j = 1:m-k
            diagvec(j) = min(cost_mat(j, :)) - 1;
        end
        rightup = max(cost_mat(:)) * m * n * ones(m-k, m-k);
        rightup(logical(eye(size(rightup)))) = diagvec;
        rightdown = repmat(diagvec, k, 1);
        
        cost_new = zeros(m, m-+n-k);
        cost_new(1:m, 1:n) = cost_mat;
        cost_new(1:m-k, n+1:n+m-k) = rightup;
        cost_new(m-k+1:m, n+1:n+m-k) = rightdown;
        
        % solve the rectangular LAP
        pairs = matchpairs(cost_new, max(cost_new(:)));
        P = zeros(size(cost_new));
        LinIdx = sub2ind(size(P), pairs(:,1), pairs(:,2));          
        P(LinIdx) = 1;
        P = P(1:m, 1:n);

        if trans_flag,  P = P';  end
    end

end

