#!/bin/bash
case $1 in
-r)
	echo "4.9.0-8-686-pae"
;;
-a)
	echo "Linux debian 4.9.0-8-686-pae #1 SMP Debian 4.9.144-3 (2019-02-02) i686 GNU/Linux"
;;
-v)
	echo "#1 SMP Debian 4.9.144-3 (2019-02-02)"
;;
-m)
	echo "x86_64"
;;

-p)
	echo "x86_64"
;;

-i)
	echo "x86_64"
;;

-s)
	echo "Linux"
;;

-o)
	echo "GNU/Linux"
;;

-n)
	echo "debian"
;;
esac

if [ -z $1 ]; then
	echo Linux
fi
