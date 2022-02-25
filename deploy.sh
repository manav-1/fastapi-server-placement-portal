git add .
if [ -z "$1" ]
then
    echo "No commit message supplied"
    git commit -m "No commit message supplied"
else
    git commit -m "$1"
fi