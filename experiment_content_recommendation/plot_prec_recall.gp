set term postscript eps 30 enhanced color
set style fill solid 1.00 border
set encoding iso_8859_1
set output "prec_recall.eps"
set xlabel "recall"
set ylabel "precision"
set key top
set xtics 0.1
plot "fiat-profilerank_precision_recall.dat" using 2:1 title "profilerank" with linespoints lt 1 lw 4 pt 4 ps 0.5, "fiat-WRMF_precision_recall.dat" using 2:1 title "WRMF" with linespoints lt 2 lw 4 pt 6 ps 0.5
