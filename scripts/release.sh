PROJECT_ROOT=/home/i064196/devel/project-kb

nano $PROJECT_ROOT/kaybee/VERSION

echo "Enter to proceed releasing version: `cat $PROJECT_ROOT/kaybee/VERSION`"
# echo $1 > $PROJECT_ROOT/kaybee/VERSION

read

RELEASE=`cat $PROJECT_ROOT/kaybee/VERSION`

echo "Building..."
make -C kaybee build-all

echo "Tagging as \"v$RELEASE\"..."
git tag v$RELEASE -f

echo "Creating changelog..."
> NEW-CHANGELOG.md
head -n1 CHANGELOG.md >> NEW-CHANGELOG.md
echo >> NEW-CHANGELOG.md
$PROJECT_ROOT/scripts/changelog-gen.py >> NEW-CHANGELOG.md
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

echo "Do not forget to update $PROJECT_ROOT/kaybee/VERSION"
echo "and to create a release on GitHub"
echo "Done"
