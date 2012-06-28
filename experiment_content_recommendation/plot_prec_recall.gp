set term postscript eps 30 enhanced color
set style fill solid 1.00 border
set encoding iso_8859_1
set output "prec_recall.eps"
set xlabel "recall"
set ylabel "precision"
set xtics 0.2
set ytics 0.1
set key outside
set key font ",20"
plot "fiat-profilerank_precision_recall.dat" using 2:1 title "PR" with linespoints lt 1 lw 4 pt 5 ps 1,"fiat-WRMF_precision_recall.dat" using 2:1 title "WRMF" with linespoints lt 2 lw 4 pt 13 ps 1,"fiat-WeightedUserKNN_precision_recall.dat" using 2:1 title "WUKNN" with linespoints lt 7 lw 4 pt 2 ps 1,"fiat-WeightedItemKNN_precision_recall.dat" using 2:1 title "WIKNN" with linespoints lt 6 lw 4 pt 1 ps 1,"fiat-UserKNN_precision_recall.dat" using 2:1 title "USERKNN" with linespoints lt 4 lw 4 pt 9 ps 1,"fiat-WeightedBPRMF_precision_recall.dat" using 2:1 title "WBRMF" with linespoints lt 8 lw 4 pt 11 ps 1,"fiat-MostPopular_precision_recall.dat" using 2:1 title "POPULAR" with linespoints lt 5 lw 4 pt 15 ps 1,"fiat-BPRMF_precision_recall.dat" using 2:1 title "BPRMF" with linespoints lt 3 lw 4 pt 7 ps 1,"fiat-SoftMarginRankingMF_precision_recall.dat" using 2:1 title "SMRMF" with linespoints lt 8 lw 4 pt 3 ps 1
