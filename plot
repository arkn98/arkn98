set terminal dumb
set yrange [0:6]
set ytics 0,1,6
set lmargin 10
set ylabel "Problems\nsolved"
set xdata time
set xlabel 'Days'
set format x '%d/%m'
set timefmt '%d/%m'
set key off
plot "data.csv" using 1:2 with impulses
