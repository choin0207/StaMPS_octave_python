function export_ps_txt(plot_type,outname)
%% == export data to txt ============
%plot_type='v-do';
ps_plot(plot_type,-1); %會把每個點的數值輸出到檔案 ps_plot_v-do.mat
ps_output;% 會輸出ps_data.xy 裡面有座標
load ps_data.xy;
% 輸入ph_disp這個變數 裡面就是z值
load(['ps_plot_' plot_type '.mat']);
lon=ps_data(:,1);
lat=ps_data(:,2);
z =ph_disp;
fid = fopen([outname '.txt'],'w');
fprintf(fid,'lon lat z\r\n');
fprintf(fid,'%.6f %.6f %.6f\r\n',[lon lat z]');
fclose(fid);
%figure; scatter(lon, lat, 0.1, ph_disp);
%colormap(flipud(jet));
end