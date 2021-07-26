from scipy.spatial.transform import Rotation as Rot
from gslr import GSLR_rotation
import open3d as o3d
import numpy as np
from sklearn.neighbors import BallTree


def T_err(R1, t1, R2, t2):
    T1, T2 = np.identity(4), np.identity(4)
    T1[:3, :3], T2[:3, :3] = R1, R2
    T1[:3, 3], T2[:3, 3] = t1, t2
    return np.linalg.norm(T1 @ np.linalg.inv(T2) - np.identity(4))


def ICP(src, dst,  max_iter=100):
    R_prev = R = np.identity(src.shape[0])
    t_prev = t = np.mean(dst, axis=1) - np.mean(src, axis=1)
    tree = BallTree(dst.T)
    for iteration in range(max_iter):
        # update NN
        inds = tree.query(np.transpose((R @ src + t.reshape(-1, 1))))[1].flatten()
        NN = dst[:, inds]
        # update R
        u, _, vT = np.linalg.svd(src @ (NN - t.reshape(-1, 1)).T, full_matrices=True)
        diags = [1.0] * vT.shape[0]
        diags[-1] = np.linalg.det(u @ vT)
        R = vT.T @ np.diag(diags) @ u.T
        t = np.mean(NN - R @ src, axis=1)
        # check convergence
        if np.linalg.norm(R_prev - R) <= 1e-5 and np.linalg.norm(t_prev - t) <= 1e-5:
            break
        else:
            R_prev, t_prev = R, t
    return R, t


if __name__ == '__main__':
    # prepare data
    A = o3d.io.read_point_cloud('data/dragon1.ply')
    B = o3d.io.read_point_cloud('data/dragon2.ply')
    A, B = np.asarray(A.points).T, np.asarray(B.points).T
    R_gt, t_gt = Rot.from_euler('xyz', [30, 30, 30], degrees=True).as_matrix(), 0.1 * np.random.rand(3)
    B = R_gt @ B + t_gt.reshape(-1, 1)

    # do registration
    print('sizes of pcds are {} and {}'.format(A.shape[1], B.shape[1]))
    R_GSLR, t_GSLR, _, _ = GSLR_rotation(A, B)
    R_ICP, t_ICP = ICP(A, B)
    print('GSLR err is {}'.format(T_err(R_GSLR, t_GSLR, R_gt, t_gt)))
    print('ICP err is {}'.format(T_err(R_ICP, t_ICP, R_gt, t_gt)))

