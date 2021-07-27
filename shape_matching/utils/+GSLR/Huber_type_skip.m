function [k] = Huber_type_skip(A, B, multiplier)
    %----- A, B are of shapes dim * n -----

    dis = vecnorm(A - B);
    med = median(dis);
    MAD = mad(dis, 1);
    ratio = abs(1.0 / MAD * (dis - med));
    k = sum(ratio <= multiplier);
end