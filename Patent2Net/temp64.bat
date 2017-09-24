
pyinstaller -y --noupx --specpath=specs --clean --version-file=version-IPC-Abstracts-Augment.txt IPC-Abstracts-Augment.py
pyinstaller -y --noupx --specpath=specs --clean --version-file=version-ClusterPreProcess.txt ClusterPreProcess.py
pyinstaller -y --noupx --specpath=specs --clean --version-file=version-P2N-Cluster.txt P2N-Cluster.py

pyinstaller -y --noupx --version-file=version-IPC-Abstracts-Augment.txt specs\IPC-Abstracts-Augment.spec
pyinstaller -y --noupx --version-file=version-ClusterPreProcess.txt specs\ClusterPreProcess.spec
pyinstaller -y --noupx --version-file=version-P2N-Cluster.txt specs\P2N-Cluster.spec
xcopy /S /Y dist\IPC-Abstracts-Augment dist\Patent2Net64\
xcopy /S /Y dist\ClusterPreProcess dist\Patent2Net64\
xcopy /S /Y dist\P2N-Cluster dist\Patent2Net64\

rmdir /S /Q dist\IPC-Abstracts-Augment
rmdir /S /Q dist\ClusterPreProcess
rmdir /S /Q dist\P2N-Cluster

