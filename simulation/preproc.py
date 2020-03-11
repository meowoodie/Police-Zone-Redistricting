import arrow

with open("/Users/woodie/Desktop/APD_Data/other/911calls.txt", "r", encoding='utf-8', errors='ignore') as f:
    no_line = 0
    for line in f:
        try:
            if no_line > 0: 
                data     = line.strip("\n").split("\t")
                off_id   = data[1]
                lat, lng = data[8], data[9]
                beat     = data[16]
                call_t   = data[38]
                disp_t   = data[40]
                arv_t    = data[42] 
                clr_t    = data[45]
                date     = data[55]
                if lat != "" and lng != "" and beat != "" and call_t != "" and disp_t != "" and arv_t != "" and clr_t != "" and date != "":
                    date   = arrow.get(date[:-4], "YYYY-MM-DD HH:mm:ss").timestamp
                    lat    = float(lat) / (10 ** (len(lat) - 3))
                    lng    = float(lng) / (10 ** (len(lng) - 3))
                    call_t = date + float(call_t[:2])*3600 + float(call_t[2:4])*60 + float(call_t[4:])
                    disp_t = date + float(disp_t[:2])*3600 + float(disp_t[2:4])*60 + float(disp_t[4:])
                    arv_t  = date + float(arv_t[:2])*3600 + float(arv_t[2:4])*60 + float(arv_t[4:])
                    clr_t  = date + float(clr_t[:2])*3600 + float(clr_t[2:4])*60 + float(clr_t[4:])
                    if disp_t >= call_t and arv_t >= disp_t and clr_t >= arv_t:
                        print("\t".join([off_id, str(lat), str(lng), beat, str(call_t), str(disp_t), str(arv_t), str(clr_t)]))
        except Exception as e:
            # print("catch: %s" % e)
            pass
        no_line += 1