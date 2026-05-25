%BATCHJOB initial script invoked for all background jobs
%
%   Andy Hooper, Sep 2001
% modifications
% DB    10/2014     Clean up command line output
% Octave 2024      Replace deprecated textread with textscan (Octave compatible)

% Read up to 12 tokens + rest-of-line using textscan (works in both MATLAB and Octave)
fid_bj = fopen('matbgparms.txt', 'r');
raw_bj = textscan(fid_bj, '%s%s%s%s%s%s%s%s%s%s%s%s%[^\n]', 1);
fclose(fid_bj);
for i_bj = 1:12
    p{i_bj} = raw_bj{i_bj}{1};
end
therest = raw_bj{13};

%if funcname(end-1)=='.' 
%  funcname=funcname(1:end-2);
%end

parmarray{1}=char(p{1});

j=1;
for i=2:length(p)
    switch isempty(p{i})
    case 0
        j=j+1;
        pnum=str2num(p{i});
        switch isempty(pnum)
        case 1
             parmarray{j}=p{i};
        otherwise
             parmarray{j}=pnum;
        end
    end
end

parmarray;


% getting which machine is being ran
[a,b] = system('hostname >temp');
text = fileread('temp');
fprintf(['Running on : ' text '\n'])

tic
feval(parmarray{:});
toc

