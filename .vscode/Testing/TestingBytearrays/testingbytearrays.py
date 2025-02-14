import uctypes

c = bytearray(0b11)
print(id(c))
print(c)
print(int.from_bytes(c))


## Testing Ustructs
PositionRegisters = {
    "read1": 0 | uctypes.INT32,
    "write1": 4 | uctypes.INT32,
    "read2": 8 | uctypes.INT32,
    "write2": 12 | uctypes.INT32,
    "read3": 16 | uctypes.INT32,
    "write3": 20 | uctypes.INT32,
    "nullData": 32 | uctypes.INT32,
    "nullDestination": 36 | uctypes.INT32
}

## Simpler Test
TestStruct = {
    "int1": 0 | uctypes.INT32,
    "int2": 4 | uctypes.INT32
}

array = bytearray(8)
struct1 = uctypes.struct(uctypes.addressof(array), TestStruct)

struct1.int1 = 0b00000000000000000000000000000001
struct1.int2 = 1
print(struct1.int1)
print(struct1.int2)
# print(bin(struct1.int2))
#print("address of int1: ", uctypes.addressof(struct1))
#print("address of int2: ", uctypes.addressof(struct1)+4)
print(array)
print(uctypes.addressof(array))