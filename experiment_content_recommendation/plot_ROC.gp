set term postscript eps 30 enhanced color
set style fill solid 1.00 border
set encoding iso_8859_1
set output "ROC.eps"
set xlabel "false positive rate"
set ylabel "true positive rate"
set xrange[-0.01:1.01]
set yrange[-0.01:1.01]
set xtics 0.2
set ytics 0.2
set key outside
set key font ",20"
plot "fiat-profilerank_ROC.dat" using 1:2 title "PR" with linespoints lt 1 lw 4 pt 5 ps 1,"fiat-WRMF_ROC.dat" using 1:2 title "WRMF" with linespoints lt 2 lw 4 pt 13 ps 1,"fiat-WeightedUserKNN_ROC.dat" using 1:2 title "WUKNN" with linespoints lt 7 lw 4 pt 2 ps 1,"fiat-WeightedItemKNN_ROC.dat" using 1:2 title "WIKNN" with linespoints lt 6 lw 4 pt 1 ps 1,"fiat-UserKNN_ROC.dat" using 1:2 title "USERKNN" with linespoints lt 4 lw 4 pt 9 ps 1,"fiat-WeightedBPRMF_ROC.dat" using 1:2 title "WBRMF" with linespoints lt 8 lw 4 pt 11 ps 1,"fiat-MostPopular_ROC.dat" using 1:2 title "POPULAR" with linespoints lt 5 lw 4 pt 15 ps 1,"fiat-BPRMF_ROC.dat" using 1:2 title "BPRMF" with linespoints lt 3 lw 4 pt 7 ps 1,"fiat-SoftMarginRankingMF_ROC.dat" using 1:2 title "SMRMF" with linespoints lt 8 lw 4 pt 3 ps 1
