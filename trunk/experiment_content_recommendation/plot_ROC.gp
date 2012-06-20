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
plot "profile_rank_ROC.dat" title "profilerank" with lines lw 5 lc 3, "WIKNN_ROC.dat"  title "WIKNN" with lines lw 5 lc 4
