\ Model bilp
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize multi-objectives
  OBJ0: Priority=1 Weight=1 AbsTol=1e-06 RelTol=0
   4 x_a1 + 8 x_a2 + 16 x_a3 + 8 x_a4 + 100 x_a5
  OBJ1: Priority=0 Weight=1 AbsTol=1e-06 RelTol=0
   2 x_d1 + 4 x_d2
Subject To
 root_is_reached: x_AND = 1
 OR1_upper_bound: - x_a1 - x_a2 + x_OR1 <= 0
 OR2_upper_bound: - x_a1 - x_a4 + x_OR2 <= 0
 INH_inactive_if_OR1_inactive: - x_OR1 + x_INH_OR1_d1 <= 0
 INH_inactive_if_OR2_inactive: - x_OR2 + x_INH_OR2_d2 <= 0
 INH_inactive_if_d1_inactive: - x_d1 + x_INH_d1_a3 <= 0
 INH_inactive_if_d1_inactive: - x_d2 + x_INH_d2_a5 <= 0
 INH_OR1_d1_success: - x_OR1 + x_INH_OR1_d1 + [ x_OR1 * x_INH_d1_a3 ] = 0
 INH_OR2_d2_success: - x_OR2 + x_INH_OR2_d2 + [ x_OR2 * x_INH_d2_a5 ] = 0
 INH_d1_a3_success: - x_d1 + x_INH_d1_a3 + [ x_a3 * x_d1 ] = 0
 INH_d2_a5_success: - x_d2 + x_INH_d2_a5 + [ x_a5 * x_d2 ] = 0
 GC0: x_AND = 1 -> x_INH_OR1_d1 + x_INH_OR2_d2 = 2
Bounds
Binaries
 x_a1 x_a2 x_a3 x_a4 x_a5 x_d1 x_d2 x_OR1 x_OR2 x_INH_OR1_d1 x_INH_OR2_d2
 x_INH_d1_a3 x_INH_d2_a5 x_AND
End
