#include <stdio.h>

#define FLAG_LEN 78
#define N0 60
static const unsigned char enc_flag[] = {
    0x00, 0xd6, 0xa9, 0x7c, 0x01, 0x85, 0xea, 0x2a, 0x0a, 0x8f, 0xd4, 0x04,
    0xeb, 0x9c, 0xe7, 0x04, 0xad, 0x4a, 0x3a, 0x9e, 0x6f, 0xf4, 0x84, 0xdf,
    0xde, 0xb8, 0xfd, 0xe7, 0x1a, 0x7c, 0x88, 0xf2, 0x2a, 0xc5, 0xc7, 0xef,
    0x3d, 0x00, 0x80, 0xf2, 0x6c, 0xf8, 0x6b, 0x3b, 0xd6, 0x23, 0xdd, 0xfb,
    0xb4, 0xda, 0xe3, 0x3f, 0x47, 0xa1, 0x00, 0x74, 0x38, 0x5f, 0x39, 0xa4,
    0xab, 0x4d, 0xda, 0xb4, 0xe3, 0x00, 0x48, 0x8a, 0xb8, 0x2f, 0xb9, 0x74,
    0x36, 0x69, 0xbb, 0x16, 0xce, 0x99
};

unsigned long not_fibonacci(int n);   /* defined in asm below */

/* not Fibonacci
 *   +0  push rbp / push rbx / cmp $1,edi / jg 1f
 *   +12 1: push rdi / sub $1,edi / call not_fibonacci
 *   +21 mov rbx,rax / mov edi,[rsp] / sub $2,edi / call ...
 *   +27..29 = 83 EF 02  <- imm8 at +29 is patched by _start */
__asm__(
    ".text\n"
    ".globl not_fibonacci\n"
    ".type not_fibonacci,@function\n"
    "not_fibonacci:\n"
    "    push %rbp\n"
    "    push %rbx\n"
    "    cmp $1, %edi\n"
    "    jg 1f\n"
    "    mov %edi, %eax\n"
    "    pop %rbx\n"
    "    pop %rbp\n"
    "    ret\n"
    "1:  push %rdi\n"
    "    sub $1, %edi\n"
    "    call not_fibonacci\n"
    "    mov %rax, %rbx\n"
    "    mov (%rsp), %edi\n"
    "    sub $2, %edi\n"
    "    call not_fibonacci\n"
    "    add %rbx, %rax\n"
    "    pop %rdi\n"
    "    pop %rbx\n"
    "    pop %rbp\n"
    "    ret\n"
);

/* _start function*/
__asm__(
    ".text\n"
    ".globl _start\n"
    ".type _start,@function\n"
    "_start:\n"
    "    endbr64\n"
    "    mov %rdx, %r9\n"                /* rtld_fini from ld.so   */
    "    lea not_fibonacci(%rip), %rdi\n"
    "    and $-4096, %rdi\n"             /* page base              */
    "    mov $8192, %esi\n"              /* 2 pages: fn may straddle */
    "    mov $7, %edx\n"                /* PROT_READ|WRITE|EXEC  */
    "    mov $10, %eax\n"               /* mprotect               */
    "    syscall\n"
    "    movb $0x05, not_fibonacci+29(%rip)\n"   /* n-2 -> n-5, swap's here */
    "    xor %ebp, %ebp\n"
    "    lea main(%rip), %rdi\n"
    "    mov (%rsp), %rsi\n"            /* argc         useless now  */
    "    lea 8(%rsp), %rdx\n"           /* argv         useless now  */
    "    xor %ecx, %ecx\n"             
    "    xor %r8d, %r8d\n"             
    "    and $-16, %rsp\n"
    "    push %rax\n"
    "    push %rsp\n"                  
    "    call __libc_start_main@PLT\n"
    "    hlt\n"
);

int main(void) {
    for (int i = 0; i < FLAG_LEN; i++) {
        unsigned long f = not_fibonacci(N0 + i);
        unsigned char key = (unsigned char)(f & 0xFF);
        putchar(enc_flag[i] ^ key);
        fflush(stdout);
    }
    putchar('\n');
    return 0;
}
