function [S] = build_mesh(v, f)

    S.surface.TRIV = double(f);
    S.surface.X = v(:,1);
    S.surface.Y = v(:,2);
    S.surface.Z = v(:,3);
    S.surface.VERT = v;
    S.nf = size(f,1);
    S.nv = size(v,1);

end