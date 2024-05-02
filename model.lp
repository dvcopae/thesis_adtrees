\ Model bilp
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize multi-objectives
  attack_cost: Priority=1 Weight=1 AbsTol=1e-06 RelTol=0
   35 SDK + 100 BU + 15 PA + 5 ESV + 10 ACV + 0 INH_SU_DNS + 10 DNS
  defense_cost: Priority=0 Weight=1 AbsTol=1e-06 RelTol=0
   20 SKO + 5 APUT + 10 SU
Subject To
 root_is_reached: Steal_user_data = 1
 INH_SU_DNS_OFF: - SU + INH_SU_DNS <= 0
 INH_SU_DNS_OFF: - SU + INH_SU_DNS <= 0
 INH_ACV_SU_OFF: - ACV + INH_ACV_SU <= 0
 INH_ESV_SU_OFF: - ESV + INH_ESV_SU <= 0
 INH_PA_APUT_OFF: - PA + INH_PA_APUT <= 0
 INH_SDK_SKO_OFF: - SDK + INH_SDK_SKO <= 0
 Steal_credentials_BU: Steal_credentials - BU >= 0
 Steal_credentials_INH_PA_APUT: Steal_credentials - INH_PA_APUT >= 0
 Steal_credentials_INH_ESV_SU: Steal_credentials - INH_ESV_SU >= 0
 Steal_credentials_INH_ACV_SU: Steal_credentials - INH_ACV_SU >= 0
 Steal_credentials_bound: Steal_credentials - BU - INH_PA_APUT - INH_ESV_SU
   - INH_ACV_SU <= 0
 Steal_user_data_Steal_credentials: Steal_user_data - Steal_credentials
   <= 0
 Steal_user_data_INH_SDK_SKO: Steal_user_data - INH_SDK_SKO <= 0
 Steal_user_data_bound: Steal_user_data - Steal_credentials - INH_SDK_SKO
   >= -1
 INH_SU_DNS_ON: - SU + INH_SU_DNS + [ SU * DNS ] = 0
 INH_SU_DNS_ON: - SU + INH_SU_DNS + [ SU * DNS ] = 0
 INH_ACV_SU_ON: - ACV + INH_ACV_SU + [ ACV * INH_SU_DNS ] = 0
 INH_ESV_SU_ON: - ESV + INH_ESV_SU + [ ESV * INH_SU_DNS ] = 0
 INH_PA_APUT_ON: - PA + INH_PA_APUT + [ PA * APUT ] = 0
 INH_SDK_SKO_ON: - SDK + INH_SDK_SKO + [ SDK * SKO ] = 0
Bounds
Binaries
 Steal_user_data Steal_credentials SDK INH_SDK_SKO BU PA INH_PA_APUT ESV
 INH_ESV_SU ACV INH_ACV_SU SKO APUT SU INH_SU_DNS INH_SU_DNS DNS
End
