import csv

sample_dict = [
{'key1': 1, 'key2': 2, 'key3': 3},
{'key1': 4, 'key2': 5, 'key3': 6},
{'key1': 7, 'key2': 8, 'key3': 9},
]
col_name=["key1","key2","key3"]
with open("export.csv", 'w') as csvFile:
        wr = csv.DictWriter(csvFile, fieldnames=col_name)
        wr.writeheader()
        for ele in sample_dict:
                wr.writerow(ele)