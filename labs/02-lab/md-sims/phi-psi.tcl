set num_frames [molinfo 0 get numframes]
set resid [atomselect 0 "resid 3"] 
set file [open "phi-psi.out" w]

puts "frame,phi,psi"
for {set i 1} {$i < $num_frames} {incr i 1} {
        
    $resid frame $i

    set phi [lindex [$resid get phi] 1]
    set psi [lindex [$resid get psi] 1]

    puts $file "$i,$phi,$psi"

}
close $file
