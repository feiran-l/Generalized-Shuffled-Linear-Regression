%% solve CA = B with C being an orthogonal matrix

function [X] = solve_ls(A, B)
        H = A * B';
        [U, ~, V] = svd(H);
        X = V * U';
end
