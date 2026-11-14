# slow alby

- **Category:** Rev


## Description

An evil slow printer for a speedrun, pls remember this is not fibonacci

## Details
The challenge is a slow flag printer that looks like is using a strange unoptimized version of fibonacci, however reimplementing that algorithm results in garbage as output.


## Solution
There were multiple possible solution to find out what was happening to not_fibonacci function:
- first it was possible to notice that the `_start` function, was doing something different than usual, in fact as we can see
```C
void __fastcall __noreturn start(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6, char *ubp_av)
{
  signed __int64 v7; // rax
  void (*v8)(); // r9
  signed __int64 v9; // [rsp-8h] [rbp-8h] BYREF
  _UNKNOWN *retaddr; // [rsp+0h] [rbp+0h]

  v7 = sys_mprotect(not_fibonacci & 0xFFFFFFFFFFFFF000LL, 0x2000u, 7u);
  *(&loc_40036B + 2) = 5;
  v9 = v7;
  __libc_start_main(main: main, argc: retaddr, &ubp_av, init: nullptr, fini: nullptr, rtld_fini: v8, stack_end: &v9);
  __halt();
}
```

what it does is making .text writeable and modifies the byte at ```*(&loc_40036B + 2)```, that location consists of
```
.text:000000000040036B loc_40036B:                             ; DATA XREF: _start+26↓w
.text:000000000040036B                 sub     edi, 2
.text:000000000040036E                 call    not_fibonacci
```
so ```sub     edi, 2``` becomes ```sub     edi, 5``` effectvely changing the second argument of `not_fibonacci`

- second solution was to debug the binary with gdb and notice the byte change

after seeing this it was possible to change the original script and retrieve the flag 
```python
enc = bytes.fromhex('00d6a97c0185ea2a0a8fd404eb9ce704ad4a3a9e6ff484dfdeb8fde71a7c88f22ac5c7ef3d0080f26cf86b3bd623ddfbb4dae33f47a10074385f39a4ab4ddab4e300488ab82fb9743669bb16ce99')
print(len(enc))
from functools import lru_cache
@lru_cache(None)
def f(n):
    if n <= 1:
        return n & 0xffffffff # needed because it might go negative
    return (f(n-1) + f(n-5)) & 0xffffffffffffffff
out = bytes(enc[i] ^ (f(i+60) & 0xff) for i in range(len(enc)))
print(out)

# also original fib for comparison
@lru_cache(None)
def g(n):
    if n<=1: return n & 0xffffffff # needed because it might go negative
    return (g(n-1)+g(n-2)) & 0xffffffffffffffff
print(bytes(enc[i] ^ (g(i+60)&0xff) for i in range(len(enc))))
```

**srdnlen{i_d0nt_l1k3_F1b0nacci_th4Ts_why_1_d3c1d3d_to_Impl3menT_my_0wn_v3rs1On}**