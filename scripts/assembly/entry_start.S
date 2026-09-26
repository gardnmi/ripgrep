/* Preserve the x86-64 process entry contract: initial stack and rtld_fini in
 * RDX. Other general registers are unspecified at ELF process entry. The C
 * router obeys the SysV callee-save rule for R12/R13/R14 and has no runtime.
 * Flags are also restored before upstream starts.
 */
.section .text.rg_entry,"ax",@progbits
.global rg_entry
.type rg_entry,@function
rg_entry:
    endbr64
    mov %rsp, %r12
    mov %rdx, %r13
    pushfq
    pop %r14
    mov (%r12), %edi
    lea 8(%r12), %rsi
    lea 16(%r12,%rdi,8), %rdx
    and $-16, %rsp
    call rg_route
    mov %r12, %rsp
    push %r14
    popfq
    mov %r13, %rdx
    jmp rg_upstream_entry
.size rg_entry, .-rg_entry
.section .note.GNU-stack,"",@progbits
