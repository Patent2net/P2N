echo off
type welcome.txt
cd Patent2Net
parallel3.exe
cd ..
echo on
echo "DO NOT CLOSE THIS TERMINAL. Launch Firefox and catch the URL http://localhost. "
Patent2Net\web.exe 80
