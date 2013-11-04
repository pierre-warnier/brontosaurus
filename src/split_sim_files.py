import sys
import codecs

for f in sys.argv[1:]:
    rad = f[:-4]
    fd_w, fd_mat = open(rad + u'.rows', 'wb', 'UTF-8'), open(rad + u'.sr', 'wb', 'UTF-8')
    for line in open(f):
        word, coeff = line.strip().split('\t', 1)
        fd_w.write(word + "\n")
        fd_mat.write(coeff + "\n")
    fd_w.close()
    fd_mat.close()
