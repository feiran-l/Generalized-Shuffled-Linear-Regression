import numpy as np
from scipy.optimize import linear_sum_assignment  # input C, return P that min tr(C^T*P) with regard to P
from scipy import stats
from tqdm import tqdm


def solve_se3(A, B, t):
    H = A @ (B - t.reshape(-1, 1)).T
    u, _, vT = np.linalg.svd(H, full_matrices=True)
    R = vT.T @ np.diag([1, 1, np.linalg.det(u @ vT)]) @ u.T
    t = np.mean(B - R @ A, axis=1)
    return R, t


def solve_ols(A, B):
    return np.linalg.lstsq(A.T, B.T, rcond=None)[0].T


def Huber_type_skipping(A, B, multiplier=3.5):
    dis = np.linalg.norm(A - B, axis=0)
    med = np.median(dis)
    MAD = stats.median_abs_deviation(dis, scale='normal')
    if abs(MAD) > 1e-5:
        return np.sum(np.abs((dis - med) / MAD) <= multiplier)
    else:
        return min(A.shape[1], B.shape[1])


def kLAP(cost, k):
    """ solve the k-cardinality LAP by converting it to a standard one """
    m, n = cost.shape
    k = int(k)
    res = np.zeros((m, m + n - k))
    if min(m, n) == k:
        r, c = linear_sum_assignment(cost)
        res[r, c] = 1
        return res
    else:
        if m > n:
            cost, m, n, trans_flag = cost.T, n, m, True
        else:
            trans_flag = False
        cost -= np.min(cost) * np.ones(cost.shape)
        # transform the kLAP to an standard LAP
        diag_vec = np.min(cost, axis=1)[:m - k] - np.ones(m - k)
        right_up = m * n * np.max(cost) * np.ones((m - k, m - k))
        np.fill_diagonal(right_up, diag_vec)
        right_down = np.tile(diag_vec, (k, 1))
        dummy = np.concatenate((right_up, right_down), axis=0)
        cost = np.concatenate((cost, dummy), axis=1)
        # solve the transformed LAP
        r, c = linear_sum_assignment(cost)
        res[r, c] = 1
        return res[:m, :n].T if trans_flag else res[:m, :n]


def GSLR_rotation(A, B, HTS_multiplier=3.5, max_iter=100, need_robust=True):
    """
        A and B       : (3 * n) source and target point clouds
        HTS_multiplier: threshold of the huber-skip estimator
        need_robust   : switch between SLR and GSLR
        return        : rotation R, translation t, correspondences P, and num_inliers k
    """
    dim, m, n = A.shape[0], A.shape[1], B.shape[1]
    P, k = np.empty((m, n)), min(m, n)
    # initialization rotation and translation
    R_prev = R = np.identity(dim)
    t_prev = t = np.mean(B, axis=1) - np.mean(A, axis=1)
    for i in tqdm(range(max_iter)):
        # pre-processing for update k and P
        A_tmp = np.repeat(np.expand_dims((R @ A + t.reshape(-1, 1)).T, axis=1), n, axis=1)
        B_tmp = np.repeat(np.expand_dims(B, axis=0).transpose(0, 2, 1), m, axis=0)
        cost_mat = np.linalg.norm(A_tmp - B_tmp, axis=2)
        # update k and P
        P = kLAP(cost_mat, min(m, n))
        if need_robust:
            r, c = np.nonzero(P)
            k = min(k, Huber_type_skipping(R @ A[:, r], B[:, c], multiplier=HTS_multiplier))
            P = kLAP(cost_mat, k)
        # update R, t
        r, c = np.nonzero(P)
        R, t = solve_se3(A[:, r], B[:, c], t)
        # convergence check
        if np.linalg.norm(R - R_prev) < 1e-5 and np.linalg.norm(t - t_prev) < 1e-5:
            break
        else:
            R_prev, t_prev = R, t
    return R, t, P, k


def GSLR_homography(A, B, HTS_multiplier=3.5, max_iter=100, need_robust=True):
    """
        A and B       : (3 * n) image homogeneous coordinates
        HTS_multiplier: threshold of the huber-skip estimator
        need_robust   : switch between SLR and GSLR
        return        : homography H, correspondences P, and num_inliers k
    """
    dim, m, n = A.shape[0], A.shape[1], B.shape[1]
    P, k = np.empty((m, n)), min(m, n)
    H_prev = H = np.identity(dim)

    for i in tqdm(range(max_iter)):
        # pre-processing for update k and P
        A_tmp = np.repeat(np.expand_dims(A.T @ H.T, axis=1), n, axis=1)
        B_tmp = np.repeat(np.expand_dims(B, axis=0).transpose(0, 2, 1), m, axis=0)
        cost_mat = np.linalg.norm(A_tmp - B_tmp, axis=2)
        # update k and P
        P = kLAP(cost_mat, min(m, n))
        if need_robust:
            r, c = np.nonzero(P)
            k = min(k, Huber_type_skipping(H @ A[:, r], B[:, c], multiplier=HTS_multiplier))
            P = kLAP(cost_mat, k)
        # update H
        r, c = np.nonzero(P)
        H = solve_ols(A[:, r], B[:, c])
        # convergence check
        if np.linalg.norm(H - H_prev) < 1e-5:
            break
        else:
            H_prev = H
    return H, P, k


