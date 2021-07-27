import numpy as np
import cv2
from gslr import GSLR_homography


def find_kps_and_homo(src, dst):
    feat = cv2.SIFT_create(nfeatures=500)
    kp_src, des_src = feat.detectAndCompute(src, None)
    kp_dst, des_dst = feat.detectAndCompute(dst, None)
    des_src, des_dst = np.float32(des_src), np.float32(des_dst)
    # prepare the 3 * n homogeneous coordinate for return
    kp_src_return, kp_dst_return = cv2.KeyPoint_convert(kp_src).T, cv2.KeyPoint_convert(kp_dst).T
    kp_src_return = np.concatenate((kp_src_return, np.ones(kp_src_return.shape[1]).reshape(1, -1)), axis=0)
    kp_dst_return = np.concatenate((kp_dst_return, np.ones(kp_dst_return.shape[1]).reshape(1, -1)), axis=0)
    # get the GT homography via ratio test and ransac
    matches = cv2.BFMatcher().knnMatch(des_src, des_dst, k=2)
    good_matches = [m for m, n in matches if m.distance < 0.8 * n.distance] # ratio test
    kp_src = np.float32([kp_src[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    kp_dst = np.float32([kp_dst[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(kp_src, kp_dst, cv2.RANSAC, 5.0)
    return kp_src_return, kp_dst_return, H


if __name__ == '__main__':
    # prepare data
    src, dst = cv2.imread('./data/homo/book2.png'), cv2.imread('./data/homo/book1.png')
    kp_src, kp_dst, H_gt = find_kps_and_homo(src, dst)

    # do estimation
    H_SLR, _, _ = GSLR_homography(kp_src, kp_dst, need_robust=False)
    H_GSLR, P_GSLR, _ = GSLR_homography(kp_src, kp_dst, need_robust=True)

    # plot results
    cv2.imwrite('./GSLR.png', cv2.warpPerspective(src, H_GSLR, (dst.shape[1], dst.shape[0])))
    cv2.imwrite('./SLR.png', cv2.warpPerspective(src, H_SLR, (dst.shape[1], dst.shape[0])))
    cv2.imwrite('./GT.png', cv2.warpPerspective(src, H_gt, (dst.shape[1], dst.shape[0])))

    # plot paired images with detected inliers and outliers
    r, c = np.nonzero(P_GSLR)
    inlier_src, inlier_dst = kp_src[:, r], kp_dst[:, c]
    out_id_src, out_id_dst = np.arange(kp_src.shape[1]).astype(int), np.arange(kp_dst.shape[1]).astype(int)
    out_id_src, out_id_dst = out_id_src[~np.isin(out_id_src, r)], out_id_dst[~np.isin(out_id_dst, c)]
    outlier_src, outlier_dst = kp_src[:, out_id_src], kp_dst[:, out_id_dst]
    outlier_src = [cv2.KeyPoint(x[0], x[1], 1) for x in outlier_src.T]
    src = cv2.drawKeypoints(src, outlier_src, None, color=(0, 0, 255), flags=0)
    outlier_dst = [cv2.KeyPoint(x[0], x[1], 1) for x in outlier_dst.T]
    dst = cv2.drawKeypoints(dst, outlier_dst, None, color=(0, 0, 255), flags=0)
    matches = []
    for i in range(r.shape[0]):
        if i % 5 != 0:  # plot only a part of matches to make the figure easy to see
            continue
        match = cv2.DMatch()
        match.queryIdx, match.trainIdx, match.distance = r[i], c[i], 10000
        matches.append(match)
    kp_src = [cv2.KeyPoint(x[0], x[1], 1) for x in kp_src.T]
    kp_dst = [cv2.KeyPoint(x[0], x[1], 1) for x in kp_dst.T]
    res = cv2.drawMatches(src, kp_src, dst, kp_dst, matches, None, singlePointColor=(0, 255, 0), matchColor=(0, 255, 0), flags=2)
    cv2.imwrite('./paired.png', res)