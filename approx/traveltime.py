from collections import defaultdict

traces = defaultdict(list)
with open("patrol.trace.txt", "r") as f:
    for line in f.readlines():
        data   = line.strip().split("\t")
        off_id = data[0]
        lat, lng, call_t, disp_t, arv_t, clr_t = [ float(d) for d in data[1:] ]
        print(off_id, lat, lng, call_t, disp_t, arv_t, clr_t)