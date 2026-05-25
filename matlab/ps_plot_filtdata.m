%ps_plot('plot_type','ts');
%remove trand line
h = get(gca,'children');
x =  h(1).XData;
los2 =  h(1).YData;
los2=double(los2);
los2_filt = Movavg(los2,5);

figure('color',[1 1 1]);
plot(x,los2,'ko-');
hold on;
plot(x,los2_filt,'r-');
grid on;
datetick_auto('yyyy/mm/dd');ylabel('mm');
