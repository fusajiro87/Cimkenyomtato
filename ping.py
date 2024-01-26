from pythonping import ping

def zebra_ping():
    zebra_ping = ping('192.168.99.190')
    zebra_ping = str(zebra_ping)
    convert_to_list = list(zebra_ping.split(" "))
    answer = convert_to_list[0]
    print(convert_to_list)
    return answer

zebra_ping()


