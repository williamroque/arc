printf 'Enter package path: '
read path

cp -R $path dist

zip -r package.apf dist

rm -rf dist
