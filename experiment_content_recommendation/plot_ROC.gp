set term postscript eps 30 enhanced color
set style fill solid 1.00 border
set encoding iso_8859_1
set output "ROC.eps"
set xlabel "False positive rate"
set ylabel "True positive rate"
set xrange[-0.01:1.01]
set yrange[-0.01:1.01]
set xtics 0.2
set ytics 0.2
set key bottom
plot "_ROC.dat" using 1:2 title "profilerank" with linespoints lt 1 lw 4 pt 4 ps 1
#, "WIKNN_ROC.dat"  title "WIKNN" with lines lw 5 lc 4
