import csv
import os

class IndustryTilesGenerator:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(BASE_DIR, "datasets", "dim_industry_tiles.csv")
        
        # 📊 严格依据你的板块张数事实配置
        self.tile_configs = [
            {"industry": "Cotton Mill", "levels": {1: 3, 2: 2, 3: 3, 4: 3}},
            {"industry": "Coal Mine", "levels": {1: 1, 2: 2, 3: 2, 4: 2}},
            {"industry": "Iron Works", "levels": {1: 1, 2: 1, 3: 1, 4: 1}},
            {"industry": "Brewery", "levels": {1: 2, 2: 2, 3: 2, 4: 1}},
            {"industry": "Pottery", "levels": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1}},
            {"industry": "Man.Goods", "levels": {1: 1, 2: 2, 3: 1, 4: 1, 5: 2, 6: 1, 7: 1, 8: 2}}
        ]
        
        # 💰 成本矩阵映射
        # 格式: {产业名: {等级: (金钱, 铁, 煤)}}
        self.cost_matrix = {
            "Cotton Mill": {1: (12, 0, 0), 2: (14, 0, 1), 3: (16, 1, 1), 4: (18, 1, 1)},
            "Coal Mine":   {1: (5, 0, 0),  2: (7, 0, 0),  3: (8, 1, 0),  4: (10, 1, 0)},
            "Iron Works":  {1: (5, 0, 1),  2: (7, 0, 1),  3: (9, 0, 1),  4: (12, 0, 1)},
            "Brewery":     {1: (5, 1, 0),  2: (7, 1, 0),  3: (9, 1, 0),  4: (9, 1, 0)},
            "Pottery":     {1: (17, 0, 1), 2: (0, 0, 1),  3: (22, 0, 2), 4: (0, 0, 1), 5: (24, 0, 2)},
            "Man.Goods":   {
                1: (8, 0, 1), 2: (10, 1, 0), 3: (8, 1, 0), 4: (8, 1, 0),
                5: (16, 0, 2), 6: (20, 0, 0), 7: (16, 1, 1), 8: (20, 2, 0)
            }
        }

        # 🏆 🌟 算分与经济回报矩阵（基于官方原版伯明翰科技树参数）
        # 格式: {产业名: {等级: (胜利分数VP, 收入提升格数, 附加路分)}}
        self.reward_matrix = {
            "Cotton Mill": {1: (5, 5, 1),  2: (5, 4, 2),  3: (9, 3, 1), 4: (12, 2, 1)},
            "Coal Mine":   {1: (1, 4, 2),  2: (2, 7, 1),  3: (3, 6, 1),  4: (4, 5, 1)},
            "Iron Works":  {1: (3, 3, 1),  2: (5, 3, 1),  3: (7, 2, 1),  4: (9, 1, 1)},
            "Brewery":     {1: (4, 4, 2),  2: (5, 5, 2),  3: (7, 5, 2),  4: (10, 5, 2)}, 
            "Pottery":     {1: (10, 5, 1), 2: (1, 1, 1), 3: (11, 5, 1), 4: (1, 1, 1), 5: (20, 5, 1)},
            "Man.Goods":   {
                1: (3, 5, 2),  2: (5, 1, 1),  3: (4, 4, 0),  4: (3, 6, 1),
                5: (8, 2, 2), 6: (7, 6, 1), 7: (9, 4, 0), 8: (11, 1, 1)
            }
        }

    def _determine_allowed_era(self, industry, level):
        """核心规则自动判定允许建造的时代"""
        if level == 1 and industry in ["Cotton Mill", "Man.Goods", "Brewery", "Iron Works", "Coal Mine"]:
            return "Canal Only"
        if (level == 4 and industry == "Brewery") or (level == 5 and industry == "Pottery"):
            return "Rail Only"
        return "Both"

    def _determine_is_developable(self, industry, level):
        """判定板块是否可以被 Develop (研发)"""
        if industry == "Pottery" and level in [1, 3]:
            return False
        return True

    def run(self):
        print("==================================================")
        print("   黄铜：伯明翰 🏭 产业板块维表自动构建 (完全体)   ")
        print("==================================================")
        
        headers = [
            "tile_id",          # 自动生成的唯一物理板块 ID (T001, T002...)
            "industry",         # 产业类别
            "industry_level",   # 产业等级 (数字)
            "tile_instance_no", # 同级板块副本编号
            "allowed_era",      # 允许建造的时代 (Canal Only / Rail Only / Both)
            "is_developable",   # 是否可以通过研发行动移除 (True / False)
            "coin_cost",        # 建造花费金钱数量
            "iron_cost",        # 建造花费铁资源数量
            "coal_cost",        # 建造花费煤资源数量
            "victory_points",   # 🌟 新增：翻面后的纯胜利分数 (VP)
            "income_progress",  # 🌟 新增：翻面后在经济轨向前推进的格数 (Steps)
            "link_points"       # 🌟 新增：翻面后为周边网络提供的路分贡献 (0-2)
        ]
        
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        rows_to_write = []
        tile_counter = 1
        
        for config in self.tile_configs:
            industry_name = config["industry"]
            levels_dict = config["levels"]
            
            for level in sorted(levels_dict.keys()):
                tile_count_for_level = levels_dict[level]
                
                # 读取全部静态判定逻辑与数值参数
                allowed_era = self._determine_allowed_era(industry_name, level)
                is_developable = self._determine_is_developable(industry_name, level)
                coin, iron, coal = self.cost_matrix[industry_name][level]
                vp, income, link = self.reward_matrix[industry_name][level]
                
                for instance_no in range(1, tile_count_for_level + 1):
                    tile_id = f"T{tile_counter:03d}"
                    
                    rows_to_write.append([
                        tile_id,
                        industry_name,
                        level,
                        instance_no,
                        allowed_era,
                        is_developable,
                        coin,
                        iron,
                        coal,
                        vp,
                        income,
                        link
                    ])
                    tile_counter += 1
                    
        with open(self.file_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows_to_write)
            
        print(f"🎉 产业板块全维度完全体静态维表生成成功！")
        print(f"📊 总板块数验证: {tile_counter - 1} 张")
        print(f"💾 数据已成功存入: {self.file_path}")

if __name__ == "__main__":
    generator = IndustryTilesGenerator()
    generator.run()