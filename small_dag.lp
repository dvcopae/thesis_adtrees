\ Model bilp
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize multi-objectives
  attack_cost: Priority=1 Weight=1 AbsTol=1e-06 RelTol=0
   4 a1 + 8 a2 + 16 a3 + 8 a4 + 100 a5
  defense_cost: Priority=0 Weight=1 AbsTol=1e-06 RelTol=0
   2 d1 + 4 d2
Subject To
 root_is_reached: root = 1
 OR_1_a1: - a1 + OR_1 >= 0
 OR_1_a2: - a2 + OR_1 >= 0
 OR_1_bound: - a1 - a2 + OR_1 <= 0
 OR_2_a1: - a1 + OR_2 >= 0
 OR_2_a4: - a4 + OR_2 >= 0
 OR_2_bound: - a1 - a4 + OR_2 <= 0
 INH_OR_1_d1_OFF: - OR_1 + x_INH_OR_1_d1 <= 0
 INH_OR_2_d2_OFF: - OR_2 + x_INH_OR_2_d2 <= 0
 INH_d1_a3_OFF: - d1 + x_INH_d1_a3 <= 0
 INH_d2_a5_OFF: - d2 + x_INH_d2_a5 <= 0
 root_INH_OR_1_d1: - x_INH_OR_1_d1 + root <= 0
 root_INH_OR_2_d2: - x_INH_OR_2_d2 + root <= 0
 R13: - x_INH_OR_1_d1 - x_INH_OR_2_d2 + root >= -1
 INH_OR_1_d1_ON: - OR_1 + x_INH_OR_1_d1 + [ OR_1 * x_INH_d1_a3 ] = 0
 INH_OR_2_d2_ON: - OR_2 + x_INH_OR_2_d2 + [ OR_2 * x_INH_d2_a5 ] = 0
 INH_d1_a3_ON: - d1 + x_INH_d1_a3 + [ a3 * d1 ] = 0
 INH_d2_a5_ON: - d2 + x_INH_d2_a5 + [ a5 * d2 ] = 0
Bounds
Binaries
 a1 a2 a3 a4 a5 d1 d2 OR_1 OR_2 x_INH_OR_1_d1 x_INH_OR_2_d2 x_INH_d1_a3
 x_INH_d2_a5 root
End
