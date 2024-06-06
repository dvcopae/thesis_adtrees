\ Model bilp
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize multi-objectives
  attack_cost: Priority=1 Weight=1 AbsTol=1e-06 RelTol=0
   2 a2 + a1 + 3 a3
  defense_cost: Priority=0 Weight=1 AbsTol=1e-06 RelTol=0
   10 d1 + 10 d2
Subject To
 root_is_reached: A_OR_1 = 1
 D_OR_1_d1: - d1 + D_OR_1 >= 0
 D_OR_1_d2: D_OR_1 - d2 >= 0
 D_OR_1_bound: - d1 + D_OR_1 - d2 <= 0
 INH_a3_d2_ON: INH_a3_d2 + d2 <= 1
 INH_a3_d2_IDK: - a3 + INH_a3_d2 + d2 >= 0
 INH_a3_d2_OFF: - a3 + INH_a3_d2 <= 0
 INH_a1_D_OR_1_ON: INH_a1_D_OR_1 + D_OR_1 <= 1
 INH_a1_D_OR_1_IDK: - a1 + INH_a1_D_OR_1 + D_OR_1 >= 0
 INH_a1_D_OR_1_OFF: - a1 + INH_a1_D_OR_1 <= 0
 INH_a2_d1_ON: INH_a2_d1 + d1 <= 1
 INH_a2_d1_IDK: - a2 + INH_a2_d1 + d1 >= 0
 INH_a2_d1_OFF: - a2 + INH_a2_d1 <= 0
 A_OR_1_a2: A_OR_1 - INH_a2_d1 >= 0
 A_OR_1_a1: A_OR_1 - INH_a1_D_OR_1 >= 0
 A_OR_1_a3: A_OR_1 - INH_a3_d2 >= 0
 A_OR_1_bound: A_OR_1 - INH_a2_d1 - INH_a1_D_OR_1 - INH_a3_d2 <= 0
Bounds
Binaries
 A_OR_1 a2 INH_a2_d1 a1 INH_a1_D_OR_1 a3 INH_a3_d2 d1 D_OR_1 d2
End
