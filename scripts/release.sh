PROJECT_ROOT=/home/i064196/devel/project-kb

echo $1 > $PROJECT_ROOT/kaybee/VERSION

make -C kaybee build-all

git tag v$1 -f

> NEW-CHANGELOG.md
head -n1 CHANGELOG.md >> NEW-CHANGELOG.md
echo >> NEW-CHANGELOG.md
$PROJECT_ROOT/scripts/changelog-gen.py >> NEW-CHANGELOG.md
tail -n +2 CHANGELOG.md >> NEW-CHANGELOG.md

mv NEW-CHANGELOG.md CHANGELOG.md

git add CHANGELOG.md kaybee/VERSION
git commit -m "release $1"

git tag v$1 -f
git push --tags