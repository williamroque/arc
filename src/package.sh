cp -R $1 dist

zip -r "$2.apf" dist

rm -rf dist
