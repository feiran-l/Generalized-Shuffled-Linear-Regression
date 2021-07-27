function [S] = myreadOff(filename)

if length(strsplit(filename,'.')) > 1
    fid = fopen(filename,'r');
else % without file extension
    fid = fopen([filename, '.off'],'r');
end

if( fid==-1 )
    error('Cannot open the file: %s\n',filename);
end

str = fgets(fid);   % -1 if eof

if strcmp(str(1:4), 'COFF')
    [X,T,~] = readCoff(filename,4); % assume 4 color channels
    return;
end

if ~strcmp(str(1:3), 'OFF')
    error('The file is not a valid OFF one.');
end

str = fgets(fid);
sizes = sscanf(str, '%d %d', 2);
while length(sizes) ~= 2
    str = fgets(fid);
    sizes = sscanf(str, '%d %d', 2);
end
nv = sizes(1);
nf = sizes(2);

% Read vertices
[X,cnt] = fscanf(fid,'%lf %lf %lf\n', [3,nv]);
if cnt~=3*nv
    warning('Problem in reading vertices.');
end
X = X';

[T,cnt] = fscanf(fid,'3 %ld %ld %ld\n', [3,inf]);
if isempty(T)
    [T,cnt] = fscanf(fid,'4 %ld %ld %ld %ld\n', [4,inf]);
end
T = double(T'+1);


S.surface.TRIV = double(T);
S.surface.X = X(:,1);
S.surface.Y = X(:,2);
S.surface.Z = X(:,3);
S.surface.VERT = X;
S.nf = size(T,1);
S.nv = size(X,1);


fclose(fid);