set term postscript eps 30 enhanced color
set style fill solid 1.00 border
set encoding iso_8859_1
set output "precision_at.eps"
set xlabel "n"
set ylabel "precision"
set key top
set xrange [4.5:20.5]
set xtics 5
set key outside
set key font ",20"
set key reverse
plot "brasileirao-profilerank_precision_at.dat" using 1:2 title "PR" with linespoints lt 1 lw 4 pt 5 ps 2,"brasileirao-WRMF_precision_at.dat" using 1:2 title "WRMF" with linespoints lt 2 lw 4 pt 13 ps 2,"brasileirao-WeightedUserKNN_precision_at.dat" using 1:2 title "WUKNN" with linespoints lt 7 lw 4 pt 2 ps 2,"brasileirao-WeightedItemKNN_precision_at.dat" using 1:2 title "WIKNN" with linespoints lt 6 lw 4 pt 1 ps 2,"brasileirao-UserKNN_precision_at.dat" using 1:2 title "USERKNN" with linespoints lt 4 lw 4 pt 9 ps 2,"brasileirao-WeightedBPRMF_precision_at.dat" using 1:2 title "WBRMF" with linespoints lt 8 lw 4 pt 11 ps 2,"brasileirao-MostPopular_precision_at.dat" using 1:2 title "POPULAR" with linespoints lt 5 lw 4 pt 15 ps 2,"brasileirao-BPRMF_precision_at.dat" using 1:2 title "BPRMF" with linespoints lt 3 lw 4 pt 7 ps 2,"brasileirao-SoftMarginRankingMF_precision_at.dat" using 1:2 title "SMRMF" with linespoints lt 8 lw 4 pt 3 ps 2
