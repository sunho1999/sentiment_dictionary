import csv


with open('/setiment_dictionary_project/잡화 review.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    f = open("/setiment_dictionary_project/review.txt", 'w')
    for row in reader:
        for key,value in row.items():
            if len(value) == 1:
                f.write(value+",")
            else:
                f.write(value)
        f.write("\n")
    f.close()
