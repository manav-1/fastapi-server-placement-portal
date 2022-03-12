git add . 
echo 'Enter the commit message: '
read commitMessage
if [ -z "$commitMessage" ]
then
    echo "No commit message supplied"
    exit 1
else
    git commit -m "$commitMessage"
fi
echo 'Enter the Branch Name'
read branchName
if [ -z "$branchName" ]
then
    echo "No branch supplied, pushing to master"
    git push origin master
else
    git push origin $branchName
fi
echo "Deployed"