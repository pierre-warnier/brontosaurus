import sys

for f in sys.argv[1:]:
    rad = f[:-4]
    fd_w, fd_mat = open(rad + '.rows', 'wb'), open(rad + '.sr', 'wb')
    for line in open(f):
        word, coeff = line.strip().split('\t', 1)
        fd_w.write(word + "\n")
        fd_mat.write(coeff + "\n")
    fd_w.close()
    fd_mat.close()
