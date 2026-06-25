import csv
import os
import sys
from datetime import datetime
import uuid
import pandas as pd

# 基础常量定义
CITIES = ["斯托克", "汉利", "利克", "乌托克塞特", "伯顿", "德比", "贝尔珀", "诺丁汉", "塔姆沃思", "伯明翰", "华沙尔", "武弗汉普顿", "达德利", "斯塔福德",[...] ]
INDUSTRIES = ["箱子", "酒厂", "棉花厂", "陶瓷", "铁厂", "煤炭厂"]
ACTION_TYPES = ["贷款", "连接-运河", "连接-铁路", "建造", "研发", "换牌", "销售", "弃牌跳过", "运河时代算分", "铁路时代算分"]
AVAILABLE_COLORS = ["红色", "紫色", "黄色", "白色"]

class BrassTracker:
    def __init__(self):
        self.match_id = ""
        self.players = []
        self.era = "运河时代"
        self.round_id = 1
        self.current_player_idx = 0
        self.action_num = 1 # 每个回合的第几次行动 (1 或 2)
        
        # 路径绝对绑定
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.file_match = os.path.join(BASE_DIR, "data", "fact_match_players.csv")
        self.file_actions = os.path.join(BASE_DIR, "data", "fact_action_events.csv")

    def init_match(self):
        print("=========================================")
        print("   《工业革命：伯明翰》硬核动作录入系统 v1.3   ")
        print("=========================================")
        
        # 1. 读取已有 ID 用于去重和计算下一个自增 ID
        existing_ids = set()
        max_id_num = 0  # 用来记录当前最大的 ID 数字数字

        if os.path.isfile(self.file_match):
            # Prefer pandas for robust CSV handling
            try:
                df_matches = pd.read_csv(self.file_match, dtype=str, encoding='utf-8-sig')
                if 'match_id' in df_matches.columns:
                    existing_ids = set(df_matches['match_id'].dropna().astype(str).tolist())
                    max_num = pd.to_numeric(df_matches['match_id'], errors='coerce').max()
                    max_id_num = int(max_num) if not pd.isna(max_num) else 0
            except Exception:
                # Fallback to csv.reader for maximum compatibility
                with open(self.file_match, mode="r", encoding="utf-8-sig") as f:
                    reader = csv.reader(f)
                    next(reader, None)  # 跳过表头
                    for row in reader:
                        if row and row[0]:
                            existing_ids.add(row[0])
                            try:
                                id_int = int(row[0])
                                if id_int > max_id_num:
                                    max_id_num = id_int
                            except ValueError:
                                pass

        # 2. 自动生成全新、不重复的 4 位数字对局 ID
        next_id_num = max_id_num + 1
        m_id = f"{next_id_num:04d}"
        while m_id in existing_ids:
            next_id_num += 1
            m_id = f"{next_id_num:04d}"

        self.match_id = m_id
        print(f"🤖 系统已自动为您创建全新对局，ID 分配为: 【{self.match_id}】")

        # 3. 校验玩家人数
        while True:
            try:
                num_players = int(input("请输入玩家人数 (2-4): ").strip())
                if 2 <= num_players <= 4:
                    break
                print("❌ 人数限制！《黄铜：伯明翰》只支持 2 到 4 人游戏。")
            except ValueError:
                print("❌ 输入无效！请输入数字 2、3 或 4。")

        # 4. 输入昵称并选择颜色（使用结构化字典）
        self.players = []
        # 使用局部颜色列表，避免修改全局常量 AVAILABLE_COLORS
        local_colors = AVAILABLE_COLORS.copy()
        
        for i in range(num_players):
            name = input(f"\n[顺位 {i+1}] 请输入玩家昵称: ").strip()
            
            print(f"请选择 【{name}】 的玩家颜色:")
            for idx, color in enumerate(local_colors):
                print(f"[{idx+1}] {color}")
            while True:
                try:
                    c_choice = int(input("选择对应数字: ")) - 1
                    if 0 <= c_choice < len(local_colors):
                        chosen_color = local_colors.pop(c_choice)
                        break
                except ValueError:
                    pass
                print("❌ 输入无效，请选择当前列表中剩余的颜色序号。")
            
            self.players.append({"name": name, "color": chosen_color})
            
        # 5. 写入表一：对局玩家表
        headers = [
            "match_id", "date", 
            "player_1_name", "player_1_color", 
            "player_2_name", "player_2_color", 
            "player_3_name", "player_3_color", 
            "player_4_name", "player_4_color"
        ]
        
        row_data = [self.match_id, datetime.now().strftime("%Y-%m-%d")]
        for p in self.players:
            row_data.append(p["name"])
            row_data.append(p["color"])
        
        slot_needed = 10 - len(row_data)
        if slot_needed > 0:
            row_data.extend([""] * slot_needed)
            
        # 确保 data 文件夹存在
        os.makedirs(os.path.dirname(self.file_match), exist_ok=True)

        # Use pandas to write/append the match row for consistency
        row_dict = dict(zip(headers, row_data))
        if os.path.isfile(self.file_match):
            try:
                df_existing = pd.read_csv(self.file_match, dtype=str, encoding='utf-8-sig')
                df_new = pd.concat([df_existing, pd.DataFrame([row_dict])], ignore_index=True)
            except Exception:
                # Fallback: write using csv
                with open(self.file_match, mode="a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(row_data)
            else:
                df_new.to_csv(self.file_match, index=False, encoding='utf-8-sig')
        else:
            df_new = pd.DataFrame([row_dict], columns=headers)
            df_new.to_csv(self.file_match, index=False, encoding='utf-8-sig')
            
        # 将 self.players 变为简单的名字列表，便于后续使用 player_id 字段
        self.players = [p["name"] for p in self.players]
        print(f"\n🎉 对局 {self.match_id} 初始化成功！")

    def get_choice(self, options, prompt):
            print(f"\n--- {prompt} ---")
            for i, opt in enumerate(options):
                print(f"[{i+1}] {opt}")
            while True:
                user_input = input("选择对应数字: ").strip()
                try:
                    idx = int(user_input) - 1
                    if 0 <= idx < len(options):
                        chosen_opt = options[idx]
                        
                        # 🌟 核心确认步骤：如果手抖按错，输入 N 即可原地重选
                        confirm = input(f" 👉 确认选择 【{chosen_opt}】 吗？[Y/N] (默认 Y): ").strip().upper()
                        if confirm == 'N':
                            print("↩️ 已取消选择，请重新输入数字。")
                            continue  # 跳回循环开头，原地重新选择
                        
                        return chosen_opt
                except ValueError:
                    pass
                print("❌ 输入无效，请重新选择。")

    def numeric_input(self, prompt, default=0, allow_negative=True):
        """统一的数字输入 + 确认交互。
        prompt: 提示文字（不包含确认）
        default: 回车时的默认值
        allow_negative: 是否允许负数（例如收入变动可能为负）
        """
        while True:
            s = input(prompt).strip()
            try:
                val = int(s or default)
            except ValueError:
                print("❌ 请输入整数。")
                continue
            if not allow_negative and val < 0:
                print("❌ 不允许负数，请重新输入。")
                continue
            confirm = input(f" 👉 确认为 【{val}】 吗？[Y/N] (默认 Y): ").strip().upper()
            if confirm == 'N':
                continue
            return val

    def record_action(self):
            if not self.players:
                self.init_match()
                
            player = self.players[self.current_player_idx]
            print("\n" + "="*80)
            print(f"当前状态: 【{self.era}】|【第 {self.round_id} 轮】|【{player}】的第【{self.action_num}】次行动")
            print("="*80)
            
            # 1. 录入行动前现金（带确认）
            pre_cash = self.numeric_input("💰 行动前现金数量: ", default=0, allow_negative=False)
                
            # 2. 录入行动前收入（带确认）
            pre_income = self.numeric_input("📈 行动前收入等级: ", default=0, allow_negative=True)
            
            # 3. 录入大行动内容
            action_type = self.get_choice(ACTION_TYPES, "请选择行动内容")
            
            canal_link = ""
            rail_link_1 = ""
            rail_link_2 = ""
            build = ""
            industry_level = ""
            develop_count = ""
            developed_industry_1 = ""
            developed_industry_2 = ""
            
            # ==================== 优化后的核心分支逻辑 ====================
            if action_type == "连接-运河":
                p1 = self.get_choice(CITIES, "选择起点城市")
                p2 = self.get_choice(CITIES, "选择终点城市")
                canal_link = f"{p1}-{p2}"
                
            elif action_type == "连接-铁路":
                is_double = input("是否为双连行动(Double Link)？[Y/N]: ").strip().upper() == "Y"
                if is_double:
                    print("【输入第一条铁路】")
                    r1_p1 = self.get_choice(CITIES, "起点1")
                    r1_p2 = self.get_choice(CITIES, "终点1")
                    print("【输入第二条铁路】")
                    r2_p1 = self.get_choice(CITIES, "起点2")
                    r2_p2 = self.get_choice(CITIES, "终点2")
                    rail_link_1 = f"{r1_p1}-{r1_p2}"
                    rail_link_2 = f"{r2_p1}-{r2_p2}"
                else:
                    r1_p1 = self.get_choice(CITIES, "起点")
                    r1_p2 = self.get_choice(CITIES, "终点")
                    rail_link_1 = f"{r1_p1}-{r1_p2}"
                    
            elif action_type == "建造":
                industry = self.get_choice(INDUSTRIES, "选择建造的产业类型")
                level = self.numeric_input(f"请输入 {industry} 的建造等级: ", default=0, allow_negative=False)
                
                # 严格对应你的字段命名：build 记录产业+城市，industry_level 记录等级
                build_city = self.get_choice(CITIES, "选择建造地点")
                build = f"{industry}-{build_city}"
                industry_level = str(level)
                
            elif action_type == "研发":
                while True:
                    num = input("进行几次研发？(1 或 2): ").strip()
                    if num in ["1", "2"]: break
                    print("❌ 输入无效，研发次数只能是 1 或 2。")
                    
                develop_count = num
                developed_industry_1 = self.get_choice(INDUSTRIES, "第一次研发的产业")
                developed_industry_2 = self.get_choice(INDUSTRIES, "第二次研发的产业(若只有1次直接回车)") if num == "2" else ""

            # 4. 录入弃牌信息
            card_type, card_detail = "无", "无"
            if "算分" not in action_type:
                card_input = input("\n🃏 弃牌类型 [1] 城市牌 [2] 产业牌/其他: ").strip()
                card_type = "城市牌" if card_input == "1" else "产业牌"
                if card_type == "城市牌":
                    card_detail = self.get_choice(CITIES, "选择弃掉的城市牌")
                else:
                    while True:
                        card_detail = input("请输入弃掉的产业牌或标记(如 万能/贷款弃牌): ").strip()
                        confirm = input(f" 👉 确认弃牌明细为 【{card_detail}】 吗？[Y/N] (默认 Y): ").strip().upper()
                        if confirm != 'N': break

    # 5. 财务清算
            print("\n--- 财务结算 ---")
            cost_cash = self.numeric_input("本次行动产生的【花费/支出】: ", default=0, allow_negative=False)
            round_gain = self.numeric_input("回合内即时【收益】(贷款填30/无填0): ", default=0, allow_negative=False)
            income_shift = self.numeric_input("收入轨变动(贷款填-9，无变动填0): ", default=0, allow_negative=True)
            
            post_cash = pre_cash - cost_cash + round_gain
            post_income = pre_income + income_shift
            print(f"-> 自动算账：行动后现金 = {post_cash} 元，新收入等级 = {post_income}")

            # 6. 🌟 核心重构：定义符合你新数据结构的表头 (Headers)
            headers = [
                "action_uuid", "match_id", "player_id", "era", "round_id", "action_num", 
                "pre_cash", "pre_income", "action_type", 
                "canal_link", "rail_link_1", "rail_link_2", 
                "build", "industry_level", 
                "develop_count", "developed_industry_1", "developed_industry_2",
                "card_type", "card_detail", "cost_cash", "post_cash", "post_income"
            ]
            
            os.makedirs(os.path.dirname(self.file_actions), exist_ok=True)
        
            # 7. 🌟 核心重构：将专属列的值精准映射到 CSV 字典中
            action_row = {
                # use hex short id for better randomness than slicing the string form
                "action_uuid": uuid.uuid4().hex[:8],
                "match_id": self.match_id,
                "player_id": player,
                "era": self.era,
                "round_id": self.round_id,
                "action_num": self.action_num,
                "pre_cash": pre_cash,
                "pre_income": pre_income,
                "action_type": action_type,
                "canal_link": canal_link,
                "rail_link_1": rail_link_1,
                "rail_link_2": rail_link_2,
                "build": build,
                "industry_level": industry_level,
                "develop_count": develop_count,
                "developed_industry_1": developed_industry_1,
                "developed_industry_2": developed_industry_2,
                "card_type": card_type,
                "card_detail": card_detail,
                "cost_cash": cost_cash,
                "post_cash": post_cash,
                "post_income": post_income,
            }

            # Append using pandas for consistency (fallback to csv append on failure)
            if os.path.isfile(self.file_actions):
                try:
                    df_actions = pd.read_csv(self.file_actions, dtype=str, encoding='utf-8-sig')
                    # ensure columns exist
                    for h in headers:
                        if h not in df_actions.columns:
                            df_actions[h] = ""
                    df_actions = pd.concat([df_actions, pd.DataFrame([action_row])], ignore_index=True)
                    df_actions.to_csv(self.file_actions, index=False, encoding='utf-8-sig')
                except Exception:
                    with open(self.file_actions, mode="a", newline="", encoding="utf-8-sig") as f:
                        writer = csv.DictWriter(f, fieldnames=headers)
                        try:
                            if os.path.getsize(self.file_actions) == 0:
                                writer.writeheader()
                        except OSError:
                            writer.writeheader()
                        writer.writerow(action_row)
            else:
                df_new = pd.DataFrame([action_row], columns=headers)
                df_new.to_csv(self.file_actions, index=False, encoding='utf-8-sig')

            print("\n=== 行动成功记录到事实表！ ===")
            
            self.advance_state()

    def advance_state(self):
        is_canal_first_round = (self.era == "运河时代" and self.round_id == 1)
        max_actions = 1 if is_canal_first_round else 2
        
        if self.action_num < max_actions:
            self.action_num += 1
        else:
            self.action_num = 1
            if self.current_player_idx < len(self.players) - 1:
                self.current_player_idx += 1
            else:
                self.current_player_idx = 0
                print(f"\n🎉 第 {self.round_id} 轮全部玩家行动录入完毕。")
                cmd = input("[回车] 进入下一轮 | [输入 E] 切换时代 | [输入 Q] 退出系统: ").strip().upper()
                if cmd == "E":
                    self.era = "铁路时代" if self.era == "运河时代" else "运河时代"
                    self.round_id = 1
                elif cmd == "Q":
                    # prefer a clean exit
                    raise SystemExit(0)
                else:
                    self.round_id += 1

    def run(self):
        try:
            self.init_match()
            print("\n⚡ === 核心行动录入循环已启动（防手抖单向确认模式） ===")
            while True:
                self.record_action()
        except KeyboardInterrupt:
            print("\n🛑 已收到中断 (Ctrl+C)，程序退出。")
            return

if __name__ == "__main__":
    tracker = BrassTracker()
    tracker.run()
