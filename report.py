import os
import json
import csv



class Report:
    def __init__(self,mode) -> None:
        self.mode = mode
        self.report_dir = None
    
    def main(self):
        if self.mode == "trufflehog":
            self.report_dir = "tmp/reports/trufflehog"
            self._process_trufflehog()
        elif self.mode == "gitleaks":
            self.report_dir = "tmp/reports/gitleaks"
            self._process_gitleaks()

    def _process_gitleaks(self):
        self._write_csv_column_names(filename="gitleaks_report.csv",
                                     col_names=["repo_full_name","secret","file_name",
                                                "commit_url","timestamp","description"])
        files = os.listdir(self.report_dir)
        for file in files:
            full_path = f"{self.report_dir}/{file}"
            content = self._read_content(full_path).strip()
            if content == "":
                continue
            content = json.loads(content)
            repo_full_name = file.removesuffix(".json").replace("-","/",1)
            for finding in content:
                secret = finding.get("Match")
                if len(secret) > 100:
                    secret = secret[:100]
                file_name = finding.get("File")
                commit_sha = finding.get("Commit")
                commit_url = f"https://github.com/{repo_full_name}/commit/{commit_sha}"
                timestamp = finding.get("Date")
                description = finding.get("Description")
                self._write_csv_content(filename="gitleaks_report.csv",
                                        content=[repo_full_name,secret,file_name,
                                         commit_url,timestamp,description])


    def _process_trufflehog(self):
        self._write_csv_column_names(filename="trufflehog_report.csv",
                                     col_names=["repo_full_name","secret","file_name",
                                      "commit_url","timestamp","commit_sha",
                                      "detector_name"])
        files = os.listdir(self.report_dir)
        for file in files:
            full_path = f"{self.report_dir}/{file}"
            content = self._read_content(full_path).strip()
            if content == "" or content == None or content == "[]":
                continue
            all_findings = content.split("\n")
            for finding in all_findings:
                finding = finding.strip()
                finding = json.loads(finding)
                repo_full_name = file.removesuffix(".json").replace("-","/",1)
                git_details = finding.get("SourceMetadata").get("Data").get("Git")
                timestamp = git_details.get("timestamp")
                file_name = git_details.get("file")
                commit_sha = git_details.get("commit")
                DetectorName = finding.get("DetectorName")
                secret = finding.get("Raw")
                commit_url = f"https://github.com/{repo_full_name}/commit/{commit_sha}"
                if len(secret) >= 100:
                    secret = secret[:100]
                self._write_csv_content(filename="trufflehog_report.csv",
                                        content=[repo_full_name,secret,
                                        file_name,commit_url,timestamp,
                                        commit_sha,DetectorName])

    def _read_content(self,path: str) -> str:
        with open(path, "r") as f:
            content = f.read()
            return content
        
    def _write_csv_content(self, filename: str, content: list):
        with open(filename, "a") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(content)


    def _write_csv_column_names(self, filename: str, col_names: list):
        with open(filename, "w") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(col_names)


obj_1 = Report("trufflehog")
obj_2 = Report("gitleaks")
obj_1.main()
obj_2.main()
