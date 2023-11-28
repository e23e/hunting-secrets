mkdir -p tmp/reports/trufflehog tmp/reports/gitleaks tmp/cloned

while read p; do
    repo_full_name=$(echo "$p" | awk -F':' '{print $2}' | sed 's/\.git$//')
    repo_fullname_without_slash=$(echo "$repo_full_name" | sed 's;/;-;')
    trufflehog_report_path=$(echo "tmp/reports/trufflehog/$repo_fullname_without_slash.json")
    gitleaks_report_path=$(echo "tmp/reports/gitleaks/$repo_fullname_without_slash.json")

    git clone $p tmp/cloned/$repo_fullname_without_slash
    trufflehog git --no-verification --json file://tmp/cloned/$repo_fullname_without_slash >> $trufflehog_report_path
    gitleaks detect -s tmp/cloned/$repo_fullname_without_slash -r $gitleaks_report_path

    rm -rf  tmp/cloned/$repo_fullname_without_slash

done < repo_list_out.txt
