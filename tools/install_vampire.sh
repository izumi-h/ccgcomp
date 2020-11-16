#!/bin/bash
#
# Download Vampire (Version 4.3.0) from https://github.com/vprover/vampire
#

# if [ ! -d vampire-4.3.0 ]; then
#   # curl -LO $vampire_url
#   # tar -zxvf $vampire_basename
#   git clone https://github.com/vprover/vampire.git vampire-4.3.0
#   cd vampire-4.3.0
#   cp Lib/Recycler.hpp Recycler.hpp
#   git checkout d0ea23653dd51c741483774bcb90c8ff4e377818
#   mv Recycler.hpp Lib/Recycler.hpp
# fi

# # Set path to vampire-4.3.0 directory
# vampire_dir=`pwd`"/"vampire-4.3.0
# echo $vampire_dir > scripts/vampire_dir.txt

# rm -f $vampire_basename

# # Make release version
# cd ${vampire_dir}
# # make vampire_rel
# # cp vampire_rel_* vampire
# make vampire

#
# Download Vampire (Version 4.4) from https://github.com/vprover/vampire
#

vampire_url="https://github.com/vprover/vampire/archive/4.4.tar.gz"
vampire_basename=`basename $vampire_url`

if [ ! -d vampire ]; then
  curl -LO $vampire_url
  tar -zxvf $vampire_basename
fi

# Set path to vampire-4.4 directory
vampire_dir=`pwd`"/"vampire-4.4
echo $vampire_dir > scripts/vampire_dir.txt

rm -f $vampire_basename

# Make release version
cd ${vampire_dir}
make vampire_rel
cp vampire_rel_* vampire
