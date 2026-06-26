import os
import pandas as pd

def generate_industry_dim_table():
    # 1. 定义标准表头（Columns）
    columns = [
        "ID", "industry_name_level", "industry_type", "level", "price", 
        "coal_cost", "iron_cost", "coal_produce", "iron_produce", 
        "income_level_change", "available_era", "points", "link_points"
    ]
    
    records = []
    global_id = 1
    
    # =========================================================================
    # 2. 🧱 规则 3：Iron Works (钢铁厂) 数据填充
    # =========================================================================
    iron_works_data = {
        "levels": [1, 2, 3, 4],
        "prices": [5, 7, 9, 12],
        "coal_costs": [1, 1, 1, 1],
        "iron_costs": [0, 0, 0, 0],
        "coal_produces": [0, 0, 0, 0],
        "iron_produces": [4, 4, 5, 6],
        "income_changes": [3, 3, 2, 1],
        "eras": ["Canal Era", "Both", "Both", "Both"],
        "vp_points": [3, 5, 7, 9],
        "link_vps": [1, 1, 1, 1]
    }
    
    for i in range(4):
        lvl = iron_works_data["levels"][i]
        record = {
            "ID": f"IND_{global_id:03d}",
            "industry_name_level": f"Iron {lvl}",
            "industry_type": "Iron Works",
            "level": lvl,
            "price": iron_works_data["prices"][i],
            "coal_cost": iron_works_data["coal_costs"][i],
            "iron_cost": iron_works_data["iron_costs"][i],
            "coal_produce": iron_works_data["coal_produces"][i],
            "iron_produce": iron_works_data["iron_produces"][i],
            "income_level_change": iron_works_data["income_changes"][i],
            "available_era": iron_works_data["eras"][i],
            "points": iron_works_data["vp_points"][i],
            "link_points": iron_works_data["link_vps"][i]
        }
        records.append(record)
        global_id += 1

    # =========================================================================
    # 3. 🧱 规则 4：Coal Mine (煤矿) 数据填充
    # =========================================================================
    coal_mine_data = {
        "levels": [1, 2, 2, 3, 3, 4, 4],
        "prices": [5, 7, 7, 8, 8, 10, 10],
        "coal_costs": [0, 0, 0, 0, 0, 0, 0],
        "iron_costs": [0, 0, 0, 1, 1, 1, 1],  # Lvl 3-4 需要 1 个铁
        "coal_produces": [2, 3, 3, 4, 4, 5, 5],
        "iron_produces": [0, 0, 0, 0, 0, 0, 0],
        "income_changes": [4, 7, 7, 6, 6, 5, 5],
        "eras": ["Canal Era", "Both", "Both", "Both", "Both", "Both", "Both"],
        "vp_points": [1, 2, 2, 3, 3, 4, 4],
        "link_vps": [2, 1, 1, 1, 1, 1, 1]       # Lvl 1 是 2 分，其余是 1 分
    }
    
    for i in range(7):
        lvl = coal_mine_data["levels"][i]
        record = {
            "ID": f"IND_{global_id:03d}",
            "industry_name_level": f"Coal {lvl}",
            "industry_type": "Coal Mine",
            "level": lvl,
            "price": coal_mine_data["prices"][i],
            "coal_cost": coal_mine_data["coal_costs"][i],
            "iron_cost": coal_mine_data["iron_costs"][i],
            "coal_produce": coal_mine_data["coal_produces"][i],
            "iron_produce": coal_mine_data["iron_produces"][i],
            "income_level_change": coal_mine_data["income_changes"][i],
            "available_era": coal_mine_data["eras"][i],
            "points": coal_mine_data["vp_points"][i],
            "link_points": coal_mine_data["link_vps"][i]
        }
        records.append(record)
        global_id += 1

    # =========================================================================
    # 4. 🧱 规则 5：Cotton Mill (纺织厂) 数据填充
    # =========================================================================
    cotton_mill_data = {
        "levels": [1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 4],
        "prices": [12, 12, 12, 14, 14, 16, 16, 16, 18, 18, 18],
        "coal_costs": [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        "iron_costs": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],  # Lvl 3-4 需要 1 个铁
        "coal_produces": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "iron_produces": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "income_changes": [5, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2],
        "eras": ["Canal Era", "Canal Era", "Canal Era", "Both", "Both", "Both", "Both", "Both", "Both", "Both", "Both", "Both"],
        "vp_points": [5, 5, 5, 5, 5, 9, 9, 9, 13, 13, 13],
        "link_vps": [1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1]       # Lvl 1 是 2 分，其余是 1 分
    }
    
    for i in range(11):
        lvl = cotton_mill_data["levels"][i]
        record = {
            "ID": f"IND_{global_id:03d}",
            "industry_name_level": f"Cotton {lvl}",
            "industry_type": "Cotton Mill",
            "level": lvl,
            "price": cotton_mill_data["prices"][i],
            "coal_cost": cotton_mill_data["coal_costs"][i],
            "iron_cost": cotton_mill_data["iron_costs"][i],
            "coal_produce": cotton_mill_data["coal_produces"][i],
            "iron_produce": cotton_mill_data["iron_produces"][i],
            "income_level_change": cotton_mill_data["income_changes"][i],
            "available_era": cotton_mill_data["eras"][i],
            "points": cotton_mill_data["vp_points"][i],
            "link_points": cotton_mill_data["link_vps"][i]
        }
        records.append(record)
        global_id += 1

    # =========================================================================
    # 4. 🧱 规则 5：Pottery (陶器厂) 数据填充
    # =========================================================================
    pottery_data = {
        "levels": [1, 2, 3, 4, 5],
        "prices": [17, 0, 22, 0, 24],
        "coal_costs": [0, 1, 2, 1, 2],
        "iron_costs": [1, 0, 0, 0, 0],
        "coal_produces": [0, 0, 0, 0, 0],
        "iron_produces": [0, 0, 0, 0, 0],
        "income_changes": [5, 1, 5, 1, 5],
        "eras": ["Both", "Both", "Both", "Both", "Rail Only"],
        "vp_points": [10, 1, 11, 1, 20],
        "link_vps": [1, 1, 1, 1, 1]       # Lvl 1 是 2 分，其余是 1 分
    }
    
    for i in range(5):
        lvl = pottery_data["levels"][i]
        record = {
            "ID": f"IND_{global_id:03d}",
            "industry_name_level": f"Pottery {lvl}",
            "industry_type": "Pottery",
            "level": lvl,
            "price": pottery_data["prices"][i],
            "coal_cost": pottery_data["coal_costs"][i],
            "iron_cost": pottery_data["iron_costs"][i],
            "coal_produce": pottery_data["coal_produces"][i],
            "iron_produce": pottery_data["iron_produces"][i],
            "income_level_change": pottery_data["income_changes"][i],
            "available_era": pottery_data["eras"][i],
            "points": pottery_data["vp_points"][i],
            "link_points": pottery_data["link_vps"][i]
        }
        records.append(record)
        global_id += 1

    # =========================================================================
    # 4. 🧱 规则 5：Brewery (酿酒厂) 数据填充
    # =========================================================================
    brewery_data = {
        "levels": [1, 1, 2, 2, 3, 3, 4],
        "prices": [5, 5, 7, 7, 9, 9, 9],
        "coal_costs": [0, 0, 0, 0, 0, 0, 0],
        "iron_costs": [1, 1, 1, 1, 1, 1, 1],
        "coal_produces": [0, 0, 0, 0, 0, 0, 0],
        "iron_produces": [0, 0, 0, 0, 0, 0, 0],
        "income_changes": [4, 4, 5, 5, 5, 5, 5],
        "eras": ["Canal Only", "Canal Only", "Both", "Both", "Both", "Both", "Rail Only"],
        "vp_points": [4, 4, 5, 5, 7, 7, 10],
        "link_vps": [2, 2, 2, 2, 2, 2, 2]       # Lvl 1 是 2 分，其余是 1 分
    }
    
    for i in range(7):
        lvl = brewery_data["levels"][i]
        record = {
            "ID": f"IND_{global_id:03d}",
            "industry_name_level": f"Brewery {lvl}",
            "industry_type": "Brewery",
            "level": lvl,
            "price": brewery_data["prices"][i],
            "coal_cost": brewery_data["coal_costs"][i],
            "iron_cost": brewery_data["iron_costs"][i],
            "coal_produce": brewery_data["coal_produces"][i],
            "iron_produce": brewery_data["iron_produces"][i],
            "income_level_change": brewery_data["income_changes"][i],
            "available_era": brewery_data["eras"][i],
            "points": brewery_data["vp_points"][i],
            "link_points": brewery_data["link_vps"][i]
        }
        records.append(record)
        global_id += 1

    # =========================================================================
    # 4. 🧱 规则 5：Man.Goods (商品) 数据填充
    # =========================================================================
    mangoods_data = {
        "levels": [1, 2, 2, 3, 4, 5, 5, 6, 7, 8, 8],
        "prices": [8, 10, 10, 12, 8, 16, 16, 20, 16, 20, 20],
        "coal_costs": [1, 0, 0, 2, 0, 1, 1, 0, 1, 0, 0],
        "iron_costs": [0, 1, 1, 0, 1, 0, 0, 0, 1, 2, 2],
        "coal_produces": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "iron_produces": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "income_changes": [5, 1, 1, 4, 6, 2, 2, 6, 4, 1, 1],
        "eras": ["Canal Only", "Both", "Both", "Both", "Both", "Both", "Both", "Both", "Both", "Both", "Both"],
        "vp_points": [3, 5, 5, 4, 3, 8, 8, 7, 9, 11, 11],
        "link_vps": [2, 1, 1, 0, 1, 2, 2, 1, 0, 1, 1]       # Lvl 1 是 2 分，其余是 1 分
    }
    
    for i in range(11):
        lvl = mangoods_data["levels"][i]
        record = {
            "ID": f"IND_{global_id:03d}",
            "industry_name_level": f"Man.Goods {lvl}",
            "industry_type": "Man.Goods",
            "level": lvl,
            "price": mangoods_data["prices"][i],
            "coal_cost": mangoods_data["coal_costs"][i],
            "iron_cost": mangoods_data["iron_costs"][i],
            "coal_produce": mangoods_data["coal_produces"][i],
            "iron_produce": mangoods_data["iron_produces"][i],
            "income_level_change": mangoods_data["income_changes"][i],
            "available_era": mangoods_data["eras"][i],
            "points": mangoods_data["vp_points"][i],
            "link_points": mangoods_data["link_vps"][i]
        }
        records.append(record)
        global_id += 1

    # =========================================================================
    # 4. 🖨️ 转换为 DataFrame 并导出 CSV
    # =========================================================================
    df = pd.DataFrame(records, columns=columns)
    
    output_filename = "dim_industry_tile.csv"
    df.to_csv(output_filename, index=False, encoding="utf-8-sig")
    print(f"🎉 维度表生成成功！已安全落盘至: {os.path.abspath(output_filename)}")
    
    # 预览生成的数据
    print("\n📊 维度表数据预览:")
    print(df)  # 显示前 10 行
    print(df[["ID", "industry_name_level", "price", "income_level_change", "available_era"]])

if __name__ == "__main__":
    generate_industry_dim_table()