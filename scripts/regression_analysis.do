* =============================================================================
* 实证分析do文件
* 研究主题：企业的供应链风险对供应链数字化的影响研究
* =============================================================================

* ========== 路径设置 ==========
cd "C:/Users/86139/.claude/skills/STATA数据回归分析和结果撰写/data/"
global resultspath "C:/Users/86139/.claude/skills/STATA数据回归分析和结果撰写/results/"

* ========== 导入数据 ==========
use "数据1.dta", clear

* ========== 定义控制变量 ==========
global controls size LEV MB Shrcr age TobinQ big4

* ========== 设置面板数据 ==========
xtset firm_id year

* ========== 阶段1: 描述性统计 ==========
log using "$resultspath/descriptive_stats.log", replace
estpost summarize Digital Srisk $controls
esttab using "$resultspath/descriptive_stats.rtf", ///
    cells("count mean sd min max") ///
    replace
log close

* ========== 阶段2: 基准回归分析 ==========
log using "$resultspath/baseline_regression.log", replace

* 第一列：仅包含被解释变量和核心解释变量
reg Digital Srisk, vce(cluster firm_id)
est store m1

* 第二列：加入控制变量
reg Digital Srisk $controls, vce(cluster firm_id)
est store m2

* 第三列：加入控制变量和企业固定效应
reghdfe Digital Srisk $controls, absorb(firm_id) vce(cluster firm_id)
est store m3

* 第四列：加入控制变量、企业固定效应和年份固定效应
reghdfe Digital Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
est store m4

* 导出回归结果表格
esttab m1 m2 m3 m4 using "$resultspath/baseline_regression.rtf", ///
    r2 ar2 scalars(F) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap ///
    mtitles("Model1" "Model2" "Model3" "Model4")

log close

* ========== 阶段3: 稳健性检验（含内生性分析） ==========

* 稳健性检验1：替换核心解释变量
log using "$resultspath/robustness_substitute.log", replace
reghdfe Digital Srisk_cw $controls, absorb(firm_id year) vce(cluster firm_id)
est store r1
esttab r1 using "$resultspath/robustness_substitute.rtf", ///
    r2 ar2 scalars(F) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap
log close

* 稳健性检验2：考虑滞后效应
log using "$resultspath/robustness_lag.log", replace
reghdfe Digital L.Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
est store r2
esttab r2 using "$resultspath/robustness_lag.rtf", ///
    r2 ar2 scalars(F) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap
log close

* 稳健性检验3：考虑极端值
log using "$resultspath/robustness_winsor2.log", replace
preserve
    winsor2 Digital Srisk $controls, cuts(1 99) replace
    reghdfe Digital Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
    est store r3
    esttab r3 using "$resultspath/robustness_winsor2.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap
restore
log close

* 稳健性检验4：考虑一带一路政策影响
log using "$resultspath/robustness_belt_silk.log", replace
reghdfe Digital Srisk $controls Belt_Silk, absorb(firm_id year) vce(cluster firm_id)
est store r4
esttab r4 using "$resultspath/robustness_belt_silk.rtf", ///
    r2 ar2 scalars(F) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap
log close

* 稳健性检验5：工具变量法（内生性分析）
log using "$resultspath/endogeneity_iv.log", replace

* 第一阶段回归
reghdfe Srisk IV $controls, absorb(firm_id year) vce(cluster firm_id)
est store iv_first

* 第二阶段回归（2SLS）
ivreghdfe Digital (Srisk=IV) $controls, absorb(firm_id year) r
est store iv_second

esttab iv_first iv_second using "$resultspath/endogeneity_iv.rtf", ///
    r2 ar2 scalars(F idstat rkf) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap

log close

* ========== 阶段4: 异质性检验 ==========
log using "$resultspath/heterogeneity.log", replace

* 异质性1：高国际化 vs 低国际化
reghdfe Digital Srisk $controls if 高国际化 == 1, absorb(firm_id year) vce(cluster firm_id)
est store h1_1

reghdfe Digital Srisk $controls if 高国际化 == 0, absorb(firm_id year) vce(cluster firm_id)
est store h1_2

* 异质性2：资本密集 vs 非资本密集
reghdfe Digital Srisk $controls if 资本密集 == 1, absorb(firm_id year) vce(cluster firm_id)
est store h2_1

reghdfe Digital Srisk $controls if 资本密集 == 0, absorb(firm_id year) vce(cluster firm_id)
est store h2_2

* 异质性3：高依赖 vs 低依赖
reghdfe Digital Srisk $controls if 高依赖 == 1, absorb(firm_id year) vce(cluster firm_id)
est store h3_1

reghdfe Digital Srisk $controls if 高依赖 == 0, absorb(firm_id year) vce(cluster firm_id)
est store h3_2

* 导出异质性检验结果
esttab h1_1 h1_2 using "$resultspath/heterogeneity_internationalization.rtf", ///
    r2 ar2 scalars(F) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap ///
    mtitles("高国际化" "低国际化")

esttab h2_1 h2_2 using "$resultspath/heterogeneity_capital.rtf", ///
    r2 ar2 scalars(F) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap ///
    mtitles("资本密集" "非资本密集")

esttab h3_1 h3_2 using "$resultspath/heterogeneity_dependence.rtf", ///
    r2 ar2 scalars(F) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap ///
    mtitles("高依赖" "低依赖")

log close

* ========== 阶段5: 机制检验 ==========
log using "$resultspath/mechanism.log", replace

* 机制检验1：Continuity（中介变量）
* 总效应
reghdfe Digital Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
est store m1_total

* 中介变量回归
reghdfe Continuity Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
est store m1_med1

* 加入中介变量
reghdfe Digital Srisk Continuity $controls, absorb(firm_id year) vce(cluster firm_id)
est store m1_med2

* 机制检验2：Cost（中介变量）
* 中介变量回归
reghdfe Cost Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
est store m2_med1

* 加入中介变量
reghdfe Digital Srisk Cost $controls, absorb(firm_id year) vce(cluster firm_id)
est store m2_med2

* 导出机制检验结果
esttab m1_total m1_med1 m1_med2 using "$resultspath/mechanism_continuity.rtf", ///
    r2 ar2 scalars(F) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap ///
    mtitles("总效应" "Continuity" "Digital")

esttab m1_total m2_med1 m2_med2 using "$resultspath/mechanism_cost.rtf", ///
    r2 ar2 scalars(F) ///
    b(%12.3f) se(%12.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) ///
    replace nogap ///
    mtitles("总效应" "Cost" "Digital")

log close

* ========== 所有实证分析完成 ==========
display "所有实证分析完成！"
