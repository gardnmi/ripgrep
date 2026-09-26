# Linux x86-64 SysV ABI. Only caller-saved registers are modified.
# AVX-512F/BW and POPCNT are checked by the Rust entry points.
.section .text.rg_asm_count,"ax",@progbits
.p2align 5
.global rg_asm_count
.hidden rg_asm_count
.type rg_asm_count,@function
rg_asm_count:
    xor eax, eax
    vpbroadcastb zmm0, edx
    cmp rsi, 256
    jb .Lcount64
.p2align 5
.Lcount256:
    vpcmpeqb k1, zmm0, [rdi]
    vpcmpeqb k2, zmm0, [rdi + 64]
    vpcmpeqb k3, zmm0, [rdi + 128]
    vpcmpeqb k4, zmm0, [rdi + 192]
    kmovq r8, k1
    kmovq r9, k2
    kmovq r10, k3
    kmovq r11, k4
    popcnt r8, r8
    popcnt r9, r9
    popcnt r10, r10
    popcnt r11, r11
    add r8, r9
    add r10, r11
    add rax, r8
    add rax, r10
    add rdi, 256
    sub rsi, 256
    cmp rsi, 256
    jae .Lcount256
.Lcount64:
    cmp rsi, 64
    jb .Lcount_tail
    vpcmpeqb k1, zmm0, [rdi]
    kmovq r8, k1
    popcnt r8, r8
    add rax, r8
    add rdi, 64
    sub rsi, 64
    jmp .Lcount64
.Lcount_tail:
    test rsi, rsi
    jz .Lcount_done
    mov ecx, esi
    mov r8, -1
    shl r8, cl
    not r8
    kmovq k2, r8
    vmovdqu8 zmm1{k2}{z}, [rdi]
    vpcmpeqb k1{k2}, zmm0, zmm1
    kmovq r8, k1
    popcnt r8, r8
    add rax, r8
.Lcount_done:
    vzeroupper
    ret
.size rg_asm_count, .-rg_asm_count

# rdi: haystack, rsi: legal candidate positions, rdx/rcx: byte offsets,
# r8d: first byte in bits 0..7, second byte in bits 8..15.
# Returns the first pair's start offset or usize::MAX. The caller verifies
# the complete literal. No load extends outside the declared candidates.
.section .text.rg_asm_pair,"ax",@progbits
.p2align 5
.global rg_asm_pair
.hidden rg_asm_pair
.type rg_asm_pair,@function
rg_asm_pair:
    lea rdx, [rdi + rdx]
    lea r10, [rdi + rcx]
    vpbroadcastb zmm0, r8d
    shr r8d, 8
    vpbroadcastb zmm1, r8d
    xor eax, eax
    cmp rsi, 64
    jb .Lpair_tail
.Lpair64:
    vpcmpeqb k1, zmm0, [rdx + rax]
    vpcmpeqb k2, zmm1, [r10 + rax]
    kandq k1, k1, k2
    kortestq k1, k1
    jnz .Lpair_found
    add rax, 64
    sub rsi, 64
    cmp rsi, 256
    jae .Lpair256
.Lpair_short:
    cmp rsi, 64
    jae .Lpair64
    jmp .Lpair_tail
.p2align 5
.Lpair256:
    vpcmpeqb k1, zmm0, [rdx + rax]
    vpcmpeqb k2, zmm1, [r10 + rax]
    vpcmpeqb k3, zmm0, [rdx + rax + 64]
    vpcmpeqb k4, zmm1, [r10 + rax + 64]
    vpcmpeqb k5, zmm0, [rdx + rax + 128]
    vpcmpeqb k6, zmm1, [r10 + rax + 128]
    kandq k1, k1, k2
    kandq k3, k3, k4
    kandq k5, k5, k6
    vpcmpeqb k2, zmm0, [rdx + rax + 192]
    vpcmpeqb k4, zmm1, [r10 + rax + 192]
    kandq k2, k2, k4
    korq k4, k1, k3
    korq k6, k5, k2
    kortestq k4, k6
    jnz .Lpair256_found
    add rax, 256
    sub rsi, 256
    cmp rsi, 256
    jae .Lpair256
    jmp .Lpair_short
.Lpair256_found:
    kortestq k1, k1
    jnz .Lpair_found
    add rax, 64
    kmovq k1, k3
    kortestq k1, k1
    jnz .Lpair_found
    add rax, 64
    kmovq k1, k5
    kortestq k1, k1
    jnz .Lpair_found
    add rax, 64
    kmovq k1, k2
    jmp .Lpair_found
.Lpair_tail:
    test rsi, rsi
    jz .Lpair_none
    mov ecx, esi
    mov r9, -1
    shl r9, cl
    not r9
    kmovq k3, r9
    vmovdqu8 zmm2{k3}{z}, [rdx + rax]
    vmovdqu8 zmm3{k3}{z}, [r10 + rax]
    vpcmpeqb k1{k3}, zmm0, zmm2
    vpcmpeqb k2{k3}, zmm1, zmm3
    kandq k1, k1, k2
    kortestq k1, k1
    jz .Lpair_none
.Lpair_found:
    kmovq rsi, k1
    bsf rsi, rsi
    add rax, rsi
    vzeroupper
    ret
.Lpair_none:
    mov rax, -1
    vzeroupper
    ret
.size rg_asm_pair, .-rg_asm_pair
.section .note.GNU-stack,"",@progbits
