python -m pipenv run pyinstaller Omegar.spec
mv -f dist/Omegar .
rm -rf dist
rm -rf build