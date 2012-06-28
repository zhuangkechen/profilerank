set term postscript eps 25 enhanced color
set style fill solid 1.00 border
set encoding iso_8859_1
set output "recall_fallout.eps"
set xlabel "rank"
set ylabel "recall / fallout"
#set xrange[-0.01:1.01]
#set yrange[-0.01:1.01]
set xrange[0:100]
#plot "profile_rank_precision_recall.dat" using 2:1 title "profilerank" with lines lw 5 lc 3, "WIKNN_precision_recall.dat"  using 2:1 title "WIKNN" with lines lw 5 lc 4
#plot "profilerank_recall_fallout.dat" using 1:2 title "profilerank" with lines lw 5 lc 3
plot "_recall_fallout.dat" using 1:2 title "recall / fallout"  with linespoints lt 1 lw 4 pt 4 ps 0.5
#, "_recall_fallout.dat" using 1:3 title "volume" with lines lw 5 lc 1 axes x1y2
