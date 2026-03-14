"""
修改该文件并运行,使用stata.run('传入STATA命令') 就可以通过python执行STATA命令并得到对应回归结果
研究主题：企业的供应链风险对供应链数字化的影响研究
"""

import stata_setup
import yaml


# 从文件读取配置
with open('C:/Users/86139/.claude/skills/STATA数据回归分析和结果撰写/scripts/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 配置Stata
stata_setup.config(path=r'{}'.format(config['app']['path']), edition=config['app']['version'])

# 导入pystata
from pystata import stata

# ========== 上面配置不需要修改 ========


# ========== 阶段1: 导入数据 ==========

# 定义数据存放路径的全局路径并跳转到该路径
stata.run('''
    cd "C:/Users/86139/.claude/skills/STATA数据回归分析和结果撰写/data/"
''')

# 定义结果存放的全局路径
stata.run('''
    global resultspath "C:/Users/86139/.claude/skills/STATA数据回归分析和结果撰写/results/"
''')

# 导入数据
stata.run('''
    use "数据1.dta", clear
''')

# 显示数据基本信息
stata.run('''
    describe
''')

# 显示数据前5行
stata.run('''
    list in 1/5
''')

print("="*50)
print("数据导入完成！")
print("="*50)


# ========== 阶段2: 定义控制变量全局变量 ==========
stata.run('''
    global controls size LEV MB Shrcr age TobinQ big4
''')

print("="*50)
print("控制变量定义完成！")
print("="*50)


# ========== 阶段3: 描述性统计 ==========
stata.run('''
    log using "$resultspath/descriptive_stats.log", replace
''')

stata.run('''
    estpost summarize Digital Srisk $controls
''')

stata.run('''
    esttab using "$resultspath/descriptive_stats.rtf", ///
        cells("count mean sd min max") ///
        replace
''')

stata.run('''
    log close
''')

print("="*50)
print("描述性统计分析完成！")
print("="*50)


# ========== 阶段4: 基准回归分析 ==========
stata.run('''
    log using "$resultspath/baseline_regression.log", replace
''')

# 设置面板数据
stata.run('''
    xtset firm_id year
''')

# 第一列：仅包含被解释变量和核心解释变量
stata.run('''
    reg Digital Srisk, vce(cluster firm_id)
    est store m1
''')

# 第二列：加入控制变量
stata.run('''
    reg Digital Srisk $controls, vce(cluster firm_id)
    est store m2
''')

# 第三列：加入控制变量和企业固定效应
stata.run('''
    reghdfe Digital Srisk $controls, absorb(firm_id) vce(cluster firm_id)
    est store m3
''')

# 第四列：加入控制变量、企业固定效应和年份固定效应
stata.run('''
    reghdfe Digital Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
    est store m4
''')

# 导出回归结果表格
stata.run('''
    esttab m1 m2 m3 m4 using "$resultspath/baseline_regression.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap ///
        mtitles("Model1" "Model2" "Model3" "Model4")
''')

stata.run('''
    log close
''')

print("="*50)
print("基准回归分析完成！")
print("="*50)


# ========== 阶段5: 稳健性检验（含内生性分析） ==========

# 稳健性检验1：替换核心解释变量
stata.run('''
    log using "$resultspath/robustness_substitute.log", replace
''')

stata.run('''
    reghdfe Digital Srisk_cw $controls, absorb(firm_id year) vce(cluster firm_id)
    est store r1
''')

stata.run('''
    esttab r1 using "$resultspath/robustness_substitute.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap
''')

stata.run('''
    log close
''')

print("="*50)
print("稳健性检验1（替换核心解释变量）完成！")
print("="*50)


# 稳健性检验2：考虑滞后效应
stata.run('''
    log using "$resultspath/robustness_lag.log", replace
''')

stata.run('''
    reghdfe Digital L.Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
    est store r2
''')

stata.run('''
    esttab r2 using "$resultspath/robustness_lag.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap
''')

stata.run('''
    log close
''')

print("="*50)
print("稳健性检验2（滞后效应）完成！")
print("="*50)


# 稳健性检验3：考虑极端值
stata.run('''
    log using "$resultspath/robustness_winsor2.log", replace
''')

stata.run('''
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
''')

stata.run('''
    log close
''')

print("="*50)
print("稳健性检验3（极端值）完成！")
print("="*50)


# 稳健性检验4：考虑一带一路政策影响
stata.run('''
    log using "$resultspath/robustness_belt_silk.log", replace
''')

stata.run('''
    reghdfe Digital Srisk $controls Belt_Silk, absorb(firm_id year) vce(cluster firm_id)
    est store r4
''')

stata.run('''
    esttab r4 using "$resultspath/robustness_belt_silk.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap
''')

stata.run('''
    log close
''')

print("="*50)
print("稳健性检验4（一带一路政策影响）完成！")
print("="*50)


# 稳健性检验5：工具变量法（内生性分析）
stata.run('''
    log using "$resultspath/endogeneity_iv.log", replace
''')

# 第一阶段回归
stata.run('''
    reghdfe Srisk IV $controls, absorb(firm_id year) vce(cluster firm_id)
    est store iv_first
''')

# 第二阶段回归（2SLS）
stata.run('''
    ivreghdfe Digital (Srisk=IV) $controls, absorb(firm_id year) r
    est store iv_second
''')

stata.run('''
    esttab iv_first iv_second using "$resultspath/endogeneity_iv.rtf", ///
        r2 ar2 scalars(F idstat rkf) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap
''')

stata.run('''
    log close
''')

print("="*50)
print("稳健性检验5（工具变量法/内生性分析）完成！")
print("="*50)


# ========== 阶段6: 异质性检验 ==========
stata.run('''
    log using "$resultspath/heterogeneity.log", replace
''')

# 异质性1：高国际化 vs 低国际化
stata.run('''
    reghdfe Digital Srisk $controls if 高国际化 == 1, absorb(firm_id year) vce(cluster firm_id)
    est store h1_1
''')

stata.run('''
    reghdfe Digital Srisk $controls if 高国际化 == 0, absorb(firm_id year) vce(cluster firm_id)
    est store h1_2
''')

# 异质性2：资本密集 vs 非资本密集
stata.run('''
    reghdfe Digital Srisk $controls if 资本密集 == 1, absorb(firm_id year) vce(cluster firm_id)
    est store h2_1
''')

stata.run('''
    reghdfe Digital Srisk $controls if 资本密集 == 0, absorb(firm_id year) vce(cluster firm_id)
    est store h2_2
''')

# 异质性3：高依赖 vs 低依赖
stata.run('''
    reghdfe Digital Srisk $controls if 高依赖 == 1, absorb(firm_id year) vce(cluster firm_id)
    est store h3_1
''')

stata.run('''
    reghdfe Digital Srisk $controls if 高依赖 == 0, absorb(firm_id year) vce(cluster firm_id)
    est store h3_2
''')

# 导出异质性检验结果
stata.run('''
    esttab h1_1 h1_2 using "$resultspath/heterogeneity_internationalization.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap ///
        mtitles("高国际化" "低国际化")
''')

stata.run('''
    esttab h2_1 h2_2 using "$resultspath/heterogeneity_capital.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap ///
        mtitles("资本密集" "非资本密集")
''')

stata.run('''
    esttab h3_1 h3_2 using "$resultspath/heterogeneity_dependence.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap ///
        mtitles("高依赖" "低依赖")
''')

stata.run('''
    log close
''')

print("="*50)
print("异质性检验完成！")
print("="*50)


# ========== 阶段7: 机制检验 ==========
stata.run('''
    log using "$resultspath/mechanism.log", replace
''')

# 机制检验1：Continuity（中介变量）
stata.run('''
    * 总效应
    reghdfe Digital Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
    est store m1_total
''')

stata.run('''
    * 中介变量回归
    reghdfe Continuity Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
    est store m1_med1
''')

stata.run('''
    * 加入中介变量
    reghdfe Digital Srisk Continuity $controls, absorb(firm_id year) vce(cluster firm_id)
    est store m1_med2
''')

# 机制检验2：Cost（中介变量）
stata.run('''
    * 中介变量回归
    reghdfe Cost Srisk $controls, absorb(firm_id year) vce(cluster firm_id)
    est store m2_med1
''')

stata.run('''
    * 加入中介变量
    reghdfe Digital Srisk Cost $controls, absorb(firm_id year) vce(cluster firm_id)
    est store m2_med2
''')

# 导出机制检验结果
stata.run('''
    esttab m1_total m1_med1 m1_med2 using "$resultspath/mechanism_continuity.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap ///
        mtitles("总效应" "Continuity" "Digital")
''')

stata.run('''
    esttab m1_total m2_med1 m2_med2 using "$resultspath/mechanism_cost.rtf", ///
        r2 ar2 scalars(F) ///
        b(%12.3f) se(%12.3f) ///
        star(* 0.1 ** 0.05 *** 0.01) ///
        replace nogap ///
        mtitles("总效应" "Cost" "Digital")
''')

stata.run('''
    log close
''')

print("="*50)
print("机制检验完成！")
print("="*50)


print("="*50)
print("所有实证分析完成！")
print("="*50)
