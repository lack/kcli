export HOME=.
export PATH=/usr/local/bin:$PATH
export DEB_BUILD_OPTIONS=nocheck debuild
export VERSION="$(date +%y.%m).0"
sed -i "s/99.0/$VERSION/" setup.py
export MINOR=0
find . -name *pyc -exec rm {} \;
GIT_VERSION="$(curl -s https://github.com/karmab/kcli/commits/master | grep 'https://github.com/karmab/kcli/commits/master?' | sed 's@.*=\(.......\).*+.*@\1@') $(date +%Y/%m/%d)"
echo $GIT_VERSION > kvirt/version/git
python3 setup.py --command-packages=stdeb.command sdist_dsc --debian-version $MINOR --depends python3-dateutil,python3-prettytable,python3-flask,python3-libvirt,python3-requests,genisoimage,python3-distutils bdist_deb
deb=$(realpath $(find . -name *.deb))
cloudsmith push deb karmab/kcli/any-distro/any-version $deb