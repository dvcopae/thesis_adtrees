\ Model bilp
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize multi-objectives
  OBJ0: Priority=1 Weight=1 AbsTol=1e-06 RelTol=0
   C0 + 2 C1
  OBJ1: Priority=0 Weight=1 AbsTol=1e-06 RelTol=0
   10 C2 + 10 C3
Subject To
 R0: C6 = 1
 R1: - C4 + C6 >= 0
 R2: - C5 + C6 >= 0
 R3: - C4 - C5 + C6 <= 0
 R4: - C0 + C4 <= 0
 R5: - C1 + C5 <= 0
 qc0: - C0 + C4 + [ C0 * C2 ] = 0
 qc1: - C1 + C5 + [ C1 * C3 ] = 0
Bounds
Binaries
 C0 C1 C2 C3 C4 C5 C6
End
