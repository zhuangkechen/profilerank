set term postscript eps 30 enhanced color
set style fill solid 1.00 border
set encoding iso_8859_1
set output "correlations.eps"
set xlabel "profilerank"
set ylabel "WIKNN"
set log xy
#plot "_correlation_wrong.dat"  title "wrong" with points
plot "_correlation_right.dat" title "right" with points
