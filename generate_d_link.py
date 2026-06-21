import csv
import os

# 1. 严格锁定你提供的 26 个官方/周边扩展城市列表
CITIES = [
    "Belper", "Birmingham", "Burton-On-Trent", "Cannock", "Coalbrookdale", 
    "Coventry", "Country Brewery", "Derby", "Dudley", "Gloucester", 
    "Kiddminster", "Leek", "Nottingham", "Nuneaton", "Oxford", 
    "Redditch", "Shrewbury", "Stafford", "Stoke-On-Trent", "Stone", 
    "Tamworth", "Uttoxeter", "Walsall", "Warrington", "Wolverhampton", "Worcester"
]

# 2. 6 种城市颜色
COLORS = ["Purple", "Yellow", "Red", "Blue", "Green", "N/A"]

# 3. 连接类型
LINK_TYPES = ["Canal", "Rail", "Both"]

class LinkTableGenerator:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(BASE_DIR, "data", "dim_board_links.csv")
        self.existing_links = set()
        self.next_id_num = 1
        
        # 加载已有数据防止编号冲突或重复录入
        self._load_existing_data()

    def _load_existing_data(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # 跳过表头
                for row in reader:
                    if row and len(row) >= 5:
                        # 直接读取独立的 start_city 和 end_city 字段来进行去重校验
                        s_city = row[2]
                        e_city = row[4]
                        self.existing_links.add((s_city, e_city))
                        try:
                            current_id = int(row[0].replace("L", ""))
                            if current_id >= self.next_id_num:
                                self.next_id_num = current_id + 1
                        except ValueError:
                            pass

    def get_choice(self, options, prompt):
        """通用的带有原地 Y/N 确认的交互选择器"""
        print(f"\n--- {prompt} ---")
        for i, opt in enumerate(options):
            print(f"[{i+1:2d}] {opt}")
        while True:
            user_input = input("请选择对应数字: ").strip()
            try:
                idx = int(user_input) - 1
                if 0 <= idx < len(options):
                    chosen = options[idx]
                    confirm = input(f" 👉 确认选择 【{chosen}】 吗？[Y/N] (默认 Y): ").strip().upper()
                    if confirm == 'N':
                        print("↩️ 已取消，请重新输入数字。")
                        continue
                    return chosen
            except ValueError:
                pass
            print("❌ 输入无效，请重新选择。")

    def run(self):
        print("=========================================")
        print("   黄铜：伯明翰 🗺️ 道路连接维表构建工具   ")
        print("=========================================")
        print(f"当前已录入路线数: {len(self.existing_links)} 条")
        print(f"下一条生成编号将从: 【L{self.next_id_num:03d}】 开始")
        
        # 🌟 完美的宽表架构：既保留复合的 link 列，又保留独立的起点和终点列
        headers = [
            "link_id", 
            "link", 
            "start_city", 
            "start_city_color", 
            "end_city", 
            "end_city_color", 
            "link_type"
        ]
        
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        file_exists = os.path.isfile(self.file_path)

        with open(self.file_path, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)

            while True:
                print(f"\n--- 🛰️ 开始录入新道路 [ 当前自动编号: L{self.next_id_num:03d} ] ---")
                
                # 1. 选择起点城市及颜色
                start_city = self.get_choice(CITIES, "选择 [起点城市]")
                start_color = self.get_choice(COLORS, f"选择 【{start_city}】 的城市颜色")
                
                # 2. 选择终点城市及颜色
                while True:
                    end_city = self.get_choice(CITIES, "选择 [终点城市]")
                    if end_city == start_city:
                        print("❌ 错误：起点城市和终点城市不能是同一个！请重新选择。")
                        continue
                    break
                end_color = self.get_choice(COLORS, f"选择 【{end_city}】 的城市颜色")
                
                # 3. 选择连接类型
                link_type = self.get_choice(LINK_TYPES, "选择 [连接类型]")
                
                # 4. 全局唯一性去重校验
                if (start_city, end_city) in self.existing_links or (end_city, start_city) in self.existing_links:
                    print(f"\n⚠️ 警告：【{start_city}】与【{end_city}】之间的连线已经存在！本次录入取消。")
                    continue
                
                # 5. 格式化生成数据
                link_string = f"{start_city},{end_city}"
                link_id = f"L{self.next_id_num:03d}"
                
                # 6. 顺畅写入 CSV
                writer.writerow([
                    link_id, 
                    link_string, 
                    start_city, 
                    start_color, 
                    end_city, 
                    end_color, 
                    link_type
                ])
                f.flush()  # 确保数据实时落盘
                
                self.existing_links.add((start_city, end_city))
                print(f"\n✅ 成功将 【{link_id} | {link_string} | 类型: {link_type}】 写入维表！")
                
                self.next_id_num += 1
                
                # 7. 询问流转
                cont = input("\n[回车] 继续录入下一条 | [输入 Q] 保存并退出: ").strip().upper()
                if cont == "Q":
                    print("\n💾 维表保存成功！文件路径: ", self.file_path)
                    break

if __name__ == "__main__":
    generator = LinkTableGenerator()
    generator.run()