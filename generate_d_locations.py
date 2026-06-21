import csv
import os

class LocationsTableGenerator:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(BASE_DIR, "datasets", "dim_locations.csv")
        
        # 🗺️ 严格依据你提供的事实版图进行重构映射（已修正拼写并统一产业命名）
        # 缩写规范：
        # "Iron Works", "Coal Mine", "Man.Goods", "Cotton Mill", "Pottery", "Brewery"
        self.location_configs = [
            # --- 紫色区域 (Purple) ---
            {
                "name": "Birmingham", "color": "Purple", 
                "slots": [["Iron Works"], ["Man.Goods"], ["Man.Goods"], ["Man.Goods", "Cotton Mill"]]
            },
            {
                "name": "Coventry", "color": "Purple", 
                "slots": [["Pottery"], ["Man.Goods", "Coal Mine"], ["Iron Works", "Man.Goods"]]
            },
            {
                "name": "Redditch", "color": "Purple", 
                "slots": [["Man.Goods", "Coal Mine"], ["Iron Works"]]
            },
            {
                "name": "Nuneaton", "color": "Purple", 
                "slots": [["Man.Goods", "Brewery"], ["Cotton Mill", "Coal Mine"]]
            },

            # --- 黄色区域 (Yellow) ---
            {
                "name": "Worcester", "color": "Yellow", 
                "slots": [["Man.Goods", "Coal Mine"], ["Iron Works"]]
            },
            {
                "name": "Kiddminster", "color": "Yellow", 
                "slots": [["Cotton Mill"], ["Cotton Mill", "Coal Mine"]]  # 已补全为2个slots
            },
            {
                "name": "Dudley", "color": "Yellow", 
                "slots": [["Coal Mine"], ["Iron Works"]]
            },
            {
                "name": "Coalbrookdale", "color": "Yellow", 
                "slots": [["Iron Works"], ["Iron Works", "Brewery"], ["Coal Mine"]]
            },
            {
                "name": "Wolverhampton", "color": "Yellow", 
                "slots": [["Man.Goods"], ["Man.Goods", "Coal Mine"]]
            },

            # --- 红色区域 (Red) ---
            {
                "name": "Walsall", "color": "Red", 
                "slots": [["Iron Works", "Man.Goods"], ["Brewery", "Man.Goods"]]
            },
            {
                "name": "Tamworth", "color": "Red", 
                "slots": [["Cotton Mill", "Coal Mine"], ["Cotton Mill", "Coal Mine"]]
            },
            {
                "name": "Cannock", "color": "Red", 
                "slots": [["Coal Mine"], ["Coal Mine", "Man.Goods"]]
            },
            {
                "name": "Burton-On-Trent", "color": "Red", 
                "slots": [["Brewery"], ["Coal Mine", "Man.Goods"]]
            },

            # --- 蓝色区域 (Blue) ---
            {
                "name": "Stafford", "color": "Blue",  # 版图修正：Stafford实际属于蓝绿接壤或蓝区
                "slots": [["Man.Goods", "Brewery"], ["Pottery"]]
            },
            {
                "name": "Stone", "color": "Blue", 
                "slots": [["Cotton Mill", "Brewery"], ["Man.Goods", "Coal Mine"]]
            },
            {
                "name": "Uttoxeter", "color": "Blue", 
                "slots": [["Cotton Mill", "Brewery"], ["Man.Goods", "Brewery"]]
            },
            {
                "name": "Stoke-On-Trent", "color": "Blue", 
                "slots": [["Pottery", "Iron Works"], ["Man.Goods"], ["Man.Goods", "Cotton Mill"]]
            },
            {
                "name": "Leek", "color": "Blue", 
                "slots": [["Man.Goods", "Cotton Mill"], ["Coal Mine", "Cotton Mill"]]
            },

            # --- 绿色区域 (Green) ---
            {
                "name": "Derby", "color": "Green", 
                "slots": [["Man.Goods", "Cotton Mill"], ["Cotton Mill", "Brewery"], ["Iron Works"]]
            },
            {
                "name": "Belper", "color": "Green", 
                "slots": [["Cotton Mill", "Man.Goods"], ["Coal Mine"], ["Pottery"]]
            },
            
            # --- 🌟 按照你的要求：新增的外围独立外放酿酒厂 (Country Brewery) ---
            {
                "name": "Country-Brewery-1", "color": "N/A", 
                "slots": [["Brewery"]]
            },
            {
                "name": "Country-Brewery-2", "color": "N/A", 
                "slots": [["Brewery"]]
            }
        ]

    def run(self):
        print("==================================================")
        print("  黄铜：伯明翰 🗺️ 建造地点维表自动构建 (终极事实版) ")
        print("==================================================")
        
        headers = [
            "location_id",          # 城市 ID (LOC01, LOC02...)
            "location_name",        # 城市名称
            "location_color",       # 城市颜色
            "total_slots_count",    # 该城市物理格子的总数量
            "slot_id",              # 物理格子唯一 ID (LOC01_S1, LOC01_S2...)
            "slot_industry"         # 拆解后的原子级合法产业
        ]
        
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        rows_to_write = []
        loc_counter = 1
        total_rows_recorded = 0
        
        for config in self.location_configs:
            name = config["name"]
            color = config["color"]
            slots = config["slots"]
            total_slots = len(slots)
            
            # 生成唯一的城市 ID
            location_id = f"LOC{loc_counter:02d}"
            
            # 1. 遍历该城市的每一个物理格子位置 (Slot)
            for slot_index, industries in enumerate(slots, start=1):
                # 生成物理格子唯一 ID
                slot_id = f"{location_id}_S{slot_index}"
                
                # 2. 遍历该格子里支持的所有产业，分行“炸开”（方案2）
                for industry in industries:
                    rows_to_write.append([
                        location_id,
                        name,
                        color,
                        total_slots,
                        slot_id,
                        industry
                    ])
                    total_rows_recorded += 1
                
            loc_counter += 1
            
        # 写入并覆盖 datasets/dim_locations.csv
        with open(self.file_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows_to_write)
            
        print(f"🎉 终极城市格子维度表自动生成成功！")
        print(f"🏙️ 总计导入城市地点: {loc_counter - 1} 个")
        print(f"📊 方案2爆炸衍生总行数: {total_rows_recorded} 行")
        print(f"💾 数据已安全存入: {self.file_path}")

if __name__ == "__main__":
    generator = LocationsTableGenerator()
    generator.run()