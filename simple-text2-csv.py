# As seen in
#https://twitter.com/LuciferOnKodi/status/1463210815511793666

from csv import Reader, Writer

txt_file = "infile.txt"
csv_file = "output.txt"
delimiter = "|"

with open(txt_file, 'r') as txt_fh, \
open(csv_file, 'w'i, newline="", encoding="utf-8") as csv_fh:
    writer(csv_fh).writerows(reader(txt_fh, delimiter=delimiter))

# A bit of context:
#I used this to convert a 10gb txt file in a matter of ~15 seconds (IIRC) on a machine with 16gb RAM.

#Explanation on memory-friendliness:
#csv.reader() provides an iterator of rows, so it does not load the entire txt file into memory
#csv.writer's writerows accepts an iterator. 
#Combine the two and they simply yield a steady stream from reader to writer keeping memory-usage low and steady.

