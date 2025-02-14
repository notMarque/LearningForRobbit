from ibusreciever import IBusReceiver
import utime

rcv = IBusReceiver(14)

while True:
    try:
        rcv.ReadReceiver()
        utime.sleep_ms(5)
        print(rcv.MappedChannel(0, 1, -1), "\t", rcv.MappedChannel(1, -1, 1), "\t", rcv.MappedChannel(2, -1, 1), "\t", rcv.MappedChannel(3, 1, -1))
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        break

    # 1, 3