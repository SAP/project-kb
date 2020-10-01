PROJECT_ROOT=/home/i064196/devel/project-kb

nano $PROJECT_ROOT/kaybee/VERSION

echo "Enter to proceed releasing version: `cat $PROJECT_ROOT/kaybee/VERSION`"
# echo $1 > $PROJECT_ROOT/kaybee/VERSION
read

RELEASE=`cat $PROJECT_ROOT/kaybee/VERSION`

echo "Building..."
make -C kaybee check build-all || exit 1

echo "Tagging as \"v$RELEASE\"..."
git tag v$RELEASE -f

echo "Creating changelog..."
> NEW-CHANGELOG.md
head -n1 CHANGELOG.md >> NEW-CHANGELOG.md
echo >> NEW-CHANGELOG.md
$PROJECT_ROOT/scripts/changelog-gen.py >> CHANGELOG-${RELEASE}.md
cat CHANGELOG-${RELEASE}.md >> NEW-CHANGELOG.md
tail -n +2 CHANGELOG.md >> NEW-CHANGELOG.md
mv NEW-CHANGELOG.md CHANGELOG.md

echo "Creating commit for new release..."
git add CHANGELOG.md kaybee/VERSION
git commit -m "release $RELEASE"

echo "Updating tag..."
git tag v$RELEASE -f

echo "Pushing..."
git push
git push --tags

gh release create v$RELEASE \
    kaybee/dist/kaybee-${RELEASE}_linux-amd64 \
    kaybee/dist/kaybee-${RELEASE}_darwing-amd64 \
    kaybee/dist/kaybee-${RELEASE}_win-amd64 \
    --notes-file CHANGELOG-${RELEASE}.md \
    --prerelease \
    --draft


echo "Update the version for the next relase cycle (Enter to proceed)"
read
nano $PROJECT_ROOT/kaybee/VERSION

echo "Do not forget to create a release on GitHub"
echo "Done"
