set term postscript eps 30 enhanced color
set style fill solid 1.00 border
set encoding iso_8859_1
set output "prec_recall.eps"
set xlabel "recall"
set ylabel "precision"
#set xrange[-0.01:1.01]
#set yrange[-0.01:1.01]
set xtics 0.2
set ytics 0.2
set key top
#plot "profile_rank_precision_recall.dat" using 2:1 title "profilerank" with lines lw 5 lc 3, "WIKNN_precision_recall.dat"  using 2:1 title "WIKNN" with lines lw 5 lc 4
plot "content_recommendation_WRMF_precision_recall.dat" using 2:1 title "WRMF" with lines lw 5 lc 3, "content_recommendation_profilerank_precision_recall.dat" using 2:1 title "profilerank" with lines lw 5 lc 1
