import csv
import os

class CardsTableGenerator:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(BASE_DIR, "datasets", "dim_cards.csv")
        
        # 1. 基础配置（卡牌名称、总张数、类型）
        self.card_configs = [
            # --- 城市牌 (City Cards) ---
            {"name": "Belper", "count": 2, "type": "City"},
            {"name": "Birmingham", "count": 3, "type": "City"},
            {"name": "Burton-On-Trent", "count": 2, "type": "City"},
            {"name": "Cannock", "count": 2, "type": "City"},
            {"name": "Coalbrookdale", "count": 3, "type": "City"},
            {"name": "Coventry", "count": 3, "type": "City"},
            {"name": "Derby", "count": 3, "type": "City"},
            {"name": "Dudley", "count": 2, "type": "City"},
            {"name": "Kiddminster", "count": 2, "type": "City"},
            {"name": "Leek", "count": 2, "type": "City"},
            {"name": "Nuneaton", "count": 1, "type": "City"},
            {"name": "Redditch", "count": 1, "type": "City"},
            {"name": "Stafford", "count": 2, "type": "City"},
            {"name": "Stoke-On-Trent", "count": 3, "type": "City"},
            {"name": "Stone", "count": 2, "type": "City"},
            {"name": "Tamworth", "count": 1, "type": "City"},
            {"name": "Uttoxeter", "count": 2, "type": "City"},
            {"name": "Walsall", "count": 1, "type": "City"},
            {"name": "Wolverhampton", "count": 2, "type": "City"},
            {"name": "Worcester", "count": 2, "type": "City"},
            
            # --- 产业牌 (Industry Cards) ---
            {"name": "Iron Works", "count": 4, "type": "Industry"},
            {"name": "Coal Mine", "count": 3, "type": "Industry"},
            {"name": "Man.Goods / Cotton Mill", "count": 8, "type": "Industry"},
            {"name": "Pottery", "count": 3, "type": "Industry"},
            {"name": "Brewery", "count": 5, "type": "Industry"},
            
            # --- 万能牌 (Wild Cards) ---
            {"name": "Wild City", "count": 4, "type": "Wild"},
            {"name": "Wild Industry", "count": 4, "type": "Wild"}
        ]

        # 2. 颜色映射字典
        self.color_mapping = {}
        for c in ["Birmingham", "Coventry", "Nuneaton", "Redditch"]: self.color_mapping[c] = "Purple"
        for c in ["Coalbrookdale", "Dudley", "Kiddminster", "Wolverhampton", "Worcester"]: self.color_mapping[c] = "Yellow"
        for c in ["Stafford", "Burton-On-Trent", "Cannock", "Tamworth", "Walsall"]: self.color_mapping[c] = "Red"
        for c in ["Leek", "Stoke-On-Trent", "Stone", "Uttoxeter"]: self.color_mapping[c] = "Blue"
        for c in ["Belper", "Derby"]: self.color_mapping[c] = "Green"

    def run(self):
        print("==================================================")
        print("   黄铜：伯明翰 🃏 卡牌核心过滤维表自动构建工具   ")
        print("==================================================")
        
        headers = [
            "card_id", "card_contents", "card_color", "card_type",
            "used_in_2_players", "used_in_3_players", "used_in_4_players"
        ]
        
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        card_counter = 1
        rows_to_write = []
        
        for config in self.card_configs:
            name = config["name"]
            card_type = config["type"]
            total_count = config["count"]
            card_color = self.color_mapping.get(name, "N/A")
            
            # 针对同名卡牌，用循环索引 i (从 1 开始) 来分别控制每一张牌的去留
            for i in range(1, total_count + 1):
                card_id = f"C{card_counter:03d}"
                
                # 初始状态默认全可用
                used_2p = "Yes"
                used_3p = "Yes"
                used_4p = "Yes" # 4人局包含全牌，永远为 Yes
                
                # ==================== 🧠 核心人数过滤洗牌算法 ====================
                
                # 1. 城市牌过滤规则
                if card_type == "City":
                    if card_color in ["Purple", "Red", "Yellow"]:
                        pass # 2, 3, 4 人局全保留
                    elif card_color == "Green":
                        used_2p, used_3p = "No", "No" # 仅在 4 人局使用
                    elif card_color == "Blue":
                        if name in ["Leek", "Stoke-On-Trent", "Stone"]:
                            used_2p = "No" # 2人局不用，3/4人局用
                        elif name == "Uttoxeter":
                            used_2p = "No" # 2人局不用
                            if i == 2:     # 总共 2 张，第 2 张在 3 人局不用（从而实现 3 人局只用 1 张）
                                used_3p = "No"

                # 2. 产业牌过滤规则
                elif card_type == "Industry":
                    if name in ["Iron Works", "Brewery"]:
                        pass # 2, 3, 4 人局全保留
                    elif name == "Coal Mine":
                        if i == 3: # 总共 3 张，第 3 张在 2, 3 人局不用（从而实现 2/3人局用2张）
                            used_2p, used_3p = "No", "No"
                    elif name == "Man.Goods / Cotton Mill":
                        # 2人局不用(全部8张设为No)；3人局用6张(第7,8张设为No)
                        used_2p = "No"
                        if i in [7, 8]:
                            used_3p = "No"
                    elif name == "Pottery":
                        if i == 3: # 总共 3 张，第 3 张在 2, 3 人局不用（从而实现 2/3人局用2张）
                            used_2p, used_3p = "No", "No"

                # 3. 万能牌过滤规则
                elif card_type == "Wild":
                    # Wild City / Wild Industry 都是总共 4 张
                    # 2人局用2张 (第3,4张设为No)；3人局用3张 (第4张设为No)
                    if i in [3, 4]:
                        used_2p = "No"
                    if i == 4:
                        used_3p = "No"

                # =================================================================
                
                rows_to_write.append([
                    card_id, name, card_color, card_type,
                    used_2p, used_3p, used_4p
                ])
                card_counter += 1
                
        # 写入并覆盖 datasets/dim_cards.csv
        with open(self.file_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows_to_write)
            
        print(f"🎉 终极卡牌维表自动构建成功！")
        print(f"📊 4人局总牌张: {card_counter - 1} 张")
        print(f"💾 规范数据已存入: {self.file_path}")

if __name__ == "__main__":
    generator = CardsTableGenerator()
    generator.run()