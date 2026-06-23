import csv
import os

def load_industry_level_list(for_develop=False):
    """
    加载去重后的产业等级列表。
    :param for_develop: 如果为 True，则过滤掉不可被研发的板块 (如 Pottery Lv1, Lv3)
    :return: 干净的 list [('Cotton Mill', 1), ('Cotton Mill', 2), ...]
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tiles_path = os.path.join(base_dir, "datasets", "dim_industry_tiles.csv")
    
    unique_levels = set()
    
    with open(tiles_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 🌟 如果是为了研发行动，前置检查：如果 is_developable 为 False，直接跳过
            if for_develop and row["is_developable"] == "False":
                continue
                
            industry = row["industry"]
            level = int(row["industry_level"])
            unique_levels.add((industry, level))
            
    return sorted(list(unique_levels), key=lambda x: (x[0], x[1]))

# ==========================================
# 🌟 运行时你直接拥有这两个完美解耦的全局常量
# ==========================================

# 1. 建造行动的合法选择 (包含全部 29 个产业等级组合)
BUILDABLE_OPTIONS = load_industry_level_list(for_develop=False)

# 2. 研发行动的合法选择 (自动剔除 Pottery Lv1 和 Lv3，共 27 个组合)
DEVELOPABLE_OPTIONS = load_industry_level_list(for_develop=True)


# --- 🔍 测试打印验证 ---
if __name__ == "__main__":
    print(f"🏗️ 建造行动可选池 (共 {len(BUILDABLE_OPTIONS)} 条)")
    for ind, lvl in BUILDABLE_OPTIONS:
        print(f"  - {ind} : Lv.{lvl}")
    print(f"🧪 研发行动可选池 (共 {len(DEVELOPABLE_OPTIONS)} 条)")
    for ind, lvl in DEVELOPABLE_OPTIONS:
        print(f"  - {ind} : Lv.{lvl}")
    
    # 验证 Pottery 是不是被精准拦截了
    pottery_dev = [lvl for ind, lvl in DEVELOPABLE_OPTIONS if ind == "Pottery"]
    print(f"  - 研发池中的 Pottery 剩余等级: {pottery_dev}  (Lv.1 和 Lv.3 已被完美剃除！)")