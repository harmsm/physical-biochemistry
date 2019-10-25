set c [measure sasa 1.4 [atomselect 0 {name "C.*"}]]
set s [measure sasa 1.4 [atomselect 0 {name "S.*"}]]
set n [measure sasa 1.4 [atomselect 0 {name "N.*"}]]
set o [measure sasa 1.4 [atomselect 0 {name "O.*"}]]

puts "c s n o"
puts "-> $c $s $n $o"

exit
