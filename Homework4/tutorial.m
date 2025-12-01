% Importing comma-separated edge list in Matlab
E = csvread("dataset/example1.dat")

% Converting Edge list to the adjacency matrix
col1 = E(:,1);
col2 = E(:,2);
max_ids = max(max(col1, col2));
As = sparse(col1, col2, 1, max_ids, max_ids);
A = full(As)

% Getting the eigenvalues
[v, D] = eig(A)

% Sort eigenvalues
sort(diag(D))

[V D] = eigs(L, 2, 'SA');
