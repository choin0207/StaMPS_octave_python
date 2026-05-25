function []=export_StaMPS2Visualizer(plot_type,outname)
%[Export custom data from StaMPS]
%1. process StaMPS until step 6 or further
%2. use the following lines in Matlab to export the data. Run the code line by line and follow the instructions in the comments:
%For StaMPS 4.x:
%---------------------------------------------------------------------
% the 'v-doa' parameter is an example you can change it to your needs
ps_plot(plot_type, 'ts'); 
fprintf('Press any key to continue ... \n')
pause;
% a new window will open
% in the new window select a radius and location of the radius center to select the PS to export

load parms.mat;

% the 'v-do' parameter is an example you can change it to your needs
% but be sure that you use the same paramters as above in the ps_plot()!
ps_plot(plot_type, -1);

eval(['load ps_plot_' plot_type '.mat']);
lon2_str = cellstr(num2str(lon2));
lat2_str = cellstr(num2str(lat2));
lonlat2_str = strcat(lon2_str, lat2_str);

lonlat_str = strcat(cellstr(num2str(lonlat(:,1))), cellstr(num2str(lonlat(:,2))));
ind = ismember(lonlat_str, lonlat2_str);

disp = ph_disp(ind);
disp_ts = ph_mm(ind,:);
export_res = [lonlat(ind,1) lonlat(ind,2) disp disp_ts];

%{
colname={'lon' 'lat' 'vel'};
for i=1:length(day)
    colname{i+3}=['D' datestr(day(i),'yyyymmdd')];
end
export_res2 = array2table(num2cell(export_res),...
'VariableName',colname);
%}

metarow = [ref_centre_lonlat NaN transpose(day)-1];
k = 0;
export_res = [export_res(1:k,:); metarow; export_res(k+1:end,:)];

export_res = table(export_res);

% you can specify the location and name of the .csv export by renaming the second parameter
writetable(export_res,['stamps_ts_' outname '.csv']);
%writetable(export_res2,['stamps_ts_' outname '_qgis.csv']);