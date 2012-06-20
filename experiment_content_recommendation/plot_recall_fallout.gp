set term postscript eps 30 enhanced color
set style fill solid 1.00 border
set encoding iso_8859_1
set output "recall_fallout.eps"
set xlabel "threshold"
set ylabel "recall / fallout"
#set xrange[-0.01:1.01]
#set yrange[-0.01:1.01]
set key bottom
#plot "profile_rank_precision_recall.dat" using 2:1 title "profilerank" with lines lw 5 lc 3, "WIKNN_precision_recall.dat"  using 2:1 title "WIKNN" with lines lw 5 lc 4
#plot "profilerank_recall_fallout.dat" using 1:2 title "profilerank" with lines lw 5 lc 3
plot "WRMF_recall_fallout.dat" using 1:2 title "WRMF" with lines lw 5 lc 4
