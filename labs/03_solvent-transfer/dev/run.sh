for x in ala*.pdb; do 
    sed 's/XXX/'"${x}"'/' get-area.pml > junk.pml;
    pymol junk.pml | grep Angs > junk.tmp
    total=`head -1 junk.tmp | awk '{print $2}'` 
    pol=`tail -1 junk.tmp | awk '{print $2}'` 

    echo ${x} ${total} ${pol}

    rm -f junk.pml junk.tmp

done 
